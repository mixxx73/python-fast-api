Production-ready Terraform (AWS)

What this includes
- Versioned providers and common tags
- VPC with public/private subnets and NAT
- Security groups for ALB, ECS service, and RDS
- ALB (HTTP) with target group on 8000 (backend)
- ECR repositories (backend, frontend) for container images
- ECS Cluster (Fargate-ready) — service/task wiring can be added next
- RDS PostgreSQL with backups, Multi-AZ toggle, deletion protection
- Outputs for ALB DNS, RDS endpoint, and ECR URLs

Remote state and locking (recommended)
- Create an S3 bucket and DynamoDB table for state/locks.
- Copy backend.hcl.example to backend.hcl and fill values.
- Initialize: terraform init -backend-config=backend.hcl

Usage
1) Choose an environment name (e.g., prod) and region.
   Create env file: cat > prod.auto.tfvars <<EOF
   environment    = "prod"
   aws_region     = "us-east-1"
   db_password    = "<secure-password>"
   alb_ingress_cidrs = ["0.0.0.0/0"]
   EOF

2) Initialize and pick workspace
   terraform init -backend-config=backend.hcl
   terraform workspace new prod || terraform workspace select prod

3) Plan/apply
   terraform plan -var-file=prod.auto.tfvars
   terraform apply -var-file=prod.auto.tfvars

4) Build and push images (outside Terraform)
   - Build backend and push to module.ecr.repository_urls["backend"]
   - Build frontend (static) and deploy via your chosen strategy (S3/CloudFront not included here)

Next steps (optional hardening)
- Add ACM + HTTPS listener on the ALB
- Add ECS task definitions and services (Fargate) wired to ALB target group
- Parameterize secrets with AWS SSM Parameter Store / Secrets Manager
- Add CloudFront + S3 for frontend hosting and WAF
- Use least-privilege IAM roles for ECS tasks with task execution role
- Add CloudWatch alarms/dashboards and log retention
- Restrict alb_ingress_cidrs to your ranges

