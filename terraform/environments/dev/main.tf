terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "aws-eks-devops-sre-platform"
      Environment = "dev"
      ManagedBy   = "Terraform"
    }
  }
}

module "vpc" {
  source = "../../modules/vpc"

  name               = "devops-sre-dev"
  vpc_cidr           = var.vpc_cidr
  availability_zones = var.availability_zones
  public_subnets     = var.public_subnets
}

module "iam" {
  source = "../../modules/iam"
  name   = "devops-sre-dev"
}

module "eks" {
  source = "../../modules/eks"

  cluster_name       = "devops-sre-dev"
  kubernetes_version = "1.36"
  cluster_role_arn   = module.iam.cluster_role_arn
  node_role_arn      = module.iam.node_role_arn
  subnet_ids         = module.vpc.public_subnet_ids
  node_instance_type = "t3.small"
  node_desired_size  = 1
  node_min_size      = 1
  node_max_size      = 2
}
