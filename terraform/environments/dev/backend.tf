terraform {
  backend "s3" {
    bucket       = "devops-sre-terraform-state-207567788625-ap-south-1"
    key          = "dev/terraform.tfstate"
    region       = "ap-south-1"
    use_lockfile = true
  }
}
