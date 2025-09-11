terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.46"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

locals {
  name_prefix = "${var.project}-${var.environment}"
  tags = merge(
    {
      Project     = var.project
      Environment = var.environment
      ManagedBy   = "terraform"
    },
    var.extra_tags,
  )
}

# --- Networking (VPC) ---
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.7"

  name = local.name_prefix
  cidr = var.vpc_cidr

  azs             = var.azs
  private_subnets = var.private_subnets
  public_subnets  = var.public_subnets

  enable_nat_gateway   = true
  single_nat_gateway   = true
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = local.tags
}

# --- ECR (for images) ---
module "ecr" {
  source  = "terraform-aws-modules/ecr/aws"
  version = "~> 1.7"

  repositories = {
    backend  = { name = "${local.name_prefix}-backend" }
    frontend = { name = "${local.name_prefix}-frontend" }
  }
  tags = local.tags
}

# --- ECS Cluster ---
module "ecs" {
  source  = "terraform-aws-modules/ecs/aws"
  version = "~> 5.11"

  cluster_name = "${local.name_prefix}-cluster"
  tags         = local.tags
}

# --- ALB for backend ---
module "alb" {
  source  = "terraform-aws-modules/alb/aws"
  version = "~> 9.9"

  name               = "${local.name_prefix}-alb"
  load_balancer_type = "application"
  vpc_id             = module.vpc.vpc_id
  subnets            = module.vpc.public_subnets

  security_groups = [aws_security_group.alb.id]

  http_tcp_listeners = [
    {
      port               = 80
      protocol           = "HTTP"
      target_group_index = 0
    }
  ]

  target_groups = [
    {
      name_prefix      = "be-"
      backend_protocol = "HTTP"
      backend_port     = 8000
      target_type      = "ip"
      health_check = {
        path                = "/"
        healthy_threshold   = 3
        unhealthy_threshold = 3
        timeout             = 5
        interval            = 30
        matcher             = "200"
      }
    }
  ]

  tags = local.tags
}

# --- Security groups ---
resource "aws_security_group" "alb" {
  name        = "${local.name_prefix}-alb-sg"
  description = "ALB ingress"
  vpc_id      = module.vpc.vpc_id

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = var.alb_ingress_cidrs
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = local.tags
}

resource "aws_security_group" "ecs_service" {
  name        = "${local.name_prefix}-svc-sg"
  description = "ECS service"
  vpc_id      = module.vpc.vpc_id

  ingress {
    description     = "ALB to service"
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = local.tags
}

resource "aws_security_group" "rds" {
  name        = "${local.name_prefix}-rds-sg"
  description = "RDS"
  vpc_id      = module.vpc.vpc_id

  ingress {
    description     = "ECS to Postgres"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_service.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = local.tags
}

# --- RDS (PostgreSQL) ---
module "db" {
  source  = "terraform-aws-modules/rds/aws"
  version = "~> 6.8"

  identifier = "${local.name_prefix}-db"

  engine         = "postgres"
  engine_version = var.db_engine_version
  family         = var.db_parameter_group_family
  instance_class       = var.db_instance_class

  allocated_storage     = var.db_allocated_storage
  max_allocated_storage = var.db_max_allocated_storage

  db_name  = var.db_name
  username = var.db_username
  password = var.db_password

  port = 5432

  manage_master_user_password = false

  multi_az               = var.db_multi_az
  publicly_accessible    = false
  deletion_protection    = var.db_deletion_protection
  skip_final_snapshot    = var.db_skip_final_snapshot
  backup_window          = "03:00-06:00"
  maintenance_window     = "sun:07:00-sun:09:00"
  backup_retention_period = 7

  vpc_security_group_ids = [aws_security_group.rds.id]
  subnet_ids             = module.vpc.private_subnets

  create_db_subnet_group = true

  tags = local.tags
}

output "alb_dns_name" {
  value       = module.alb.lb_dns_name
  description = "Public ALB DNS for backend"
}

output "rds_endpoint" {
  value       = module.db.db_instance_endpoint
  description = "PostgreSQL endpoint"
}

output "ecr_repositories" {
  value = module.ecr.repository_urls
}

# --- Optional: store secrets in SSM Parameter Store ---
resource "aws_ssm_parameter" "jwt_secret" {
  count       = var.create_ssm_parameters && length(var.jwt_secret) > 0 ? 1 : 0
  name        = "/${var.project}/${var.environment}/SECRET_KEY"
  description = "JWT signing secret for backend"
  type        = "SecureString"
  value       = var.jwt_secret
  tags        = local.tags
}

output "jwt_secret_ssm_path" {
  value       = try(aws_ssm_parameter.jwt_secret[0].name, null)
  description = "SSM path for JWT secret (if created)"
}
