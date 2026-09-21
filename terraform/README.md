# Terraform

This is a safe reference networking stack. It intentionally does not automatically replace the existing CloudGuardian AWS resources.

```bash
cd terraform/environments/dev
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform fmt -recursive
terraform validate
terraform plan
```

Review the plan before applying. Extend the modules for EC2, IAM, CloudWatch, ECR, EventBridge and GitHub OIDC after validating account-specific requirements.
