# AWS Setup

Target region used by the project examples: `ap-south-1`.

Manual prerequisites:

1. VPC and subnet.
2. EC2 instance with an IAM instance role.
3. SSM Managed Instance Core.
4. CloudWatch Agent and metrics.
5. CloudWatch alarms for CPU, memory and disk.
6. SSM connectivity.
7. Allow only the required network access.

The existing CloudGuardian environment can be used as the learning/demo environment. Review Terraform before importing or recreating existing resources.
