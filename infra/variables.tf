variable "project" {
  description = "Project name for tagging and naming"
  type        = string
  default     = "expense-app"
}

variable "environment" {
  description = "Deployment environment (e.g., prod, staging)"
  type        = string
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "extra_tags" {
  description = "Additional resource tags"
  type        = map(string)
  default     = {}
}

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}

variable "azs" {
  description = "Availability zones"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b", "us-east-1c"]
}

variable "public_subnets" {
  description = "Public subnets"
  type        = list(string)
  default     = ["10.0.0.0/24", "10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnets" {
  description = "Private subnets"
  type        = list(string)
  default     = ["10.0.10.0/24", "10.0.11.0/24", "10.0.12.0/24"]
}

variable "alb_ingress_cidrs" {
  description = "CIDR blocks allowed to access ALB"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t4g.micro"
}

variable "db_engine_version" {
  description = "RDS Postgres engine version"
  type        = string
  default     = "16.4"
}


variable "db_parameter_group_family" {
  description = "RDS parameter group family"
  type        = string
  default     = "postgres16"
}

variable "db_allocated_storage" {
  description = "Initial storage (GB)"
  type        = number
  default     = 20
}

variable "db_max_allocated_storage" {
  description = "Max storage autoscaling (GB)"
  type        = number
  default     = 100
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "app"
}

variable "db_username" {
  description = "Database username"
  type        = string
  default     = "app"
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

variable "db_deletion_protection" {
  description = "Enable deletion protection on RDS"
  type        = bool
  default     = true
}

variable "db_skip_final_snapshot" {
  description = "Skip final snapshot on RDS deletion"
  type        = bool
  default     = false
}
variable "create_ssm_parameters" {
  description = "Whether to create SSM parameters for secrets"
  type        = bool
  default     = false
}

variable "jwt_secret" {
  description = "JWT secret for signing tokens (used if creating SSM parameters)"
  type        = string
  sensitive   = true
  default     = ""
}
