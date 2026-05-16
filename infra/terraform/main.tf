# Terraform configuration for AWS deployment
# Will provision: EC2, RDS PostgreSQL, ElastiCache Redis, ECR, ALB, IAM

terraform {
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
}

resource "aws_ecs_cluster" "fraud_cluster" {
  name = "fraud-detection-cluster"
}

resource "aws_ecs_task_definition" "fraud_api" {
  family                   = "fraud-detection-api"
  requires_compatibilities = ["FARGATE"]
  network_mode            = "awsvpc"
  cpu                     = "1024"
  memory                  = "2048"
  execution_role_arn      = aws_iam_role.ecs_execution.arn
  container_definitions   = jsonencode([
    {
      name  = "api"
      image = "${aws_ecr_repository.fraud_api.repository_url}:latest"
      portMappings = [{ containerPort = 8000 }]
      environment = [
        { name = "DATABASE_URL", value = "postgresql+asyncpg://${aws_db_instance.fraud.endpoint}" },
        { name = "REDIS_URL", value = "redis://${aws_elasticache_cluster.fraud.cache_nodes[0].address}:6379" },
      ]
    }
  ])
}

resource "aws_ecr_repository" "fraud_api" {
  name = "fraud-detection-api"
}

resource "aws_db_instance" "fraud" {
  engine         = "postgres"
  engine_version = "16"
  instance_class = "db.t3.medium"
  db_name        = "fraud_detection"
  username       = "fraud_admin"
  skip_final_snapshot = true
}

resource "aws_elasticache_cluster" "fraud" {
  cluster_id           = "fraud-redis"
  engine               = "redis"
  node_type            = "cache.t3.micro"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
}

resource "aws_iam_role" "ecs_execution" {
  name = "fraud-ecs-execution"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
      Action = "sts:AssumeRole"
    }]
  })
}
