# Security

## IAM

Use an EC2 instance role with only the permissions required for CloudWatch Agent and SSM. Do not place access keys on the instance.

## Application

- Never accept arbitrary shell commands.
- Validate all action names against the allowlist.
- Require approval for restart operations.
- Keep secrets in environment/secret management.
- Restrict CORS in production.
- Put the API behind HTTPS and an authenticated gateway/reverse proxy.

## CI/CD

Prefer GitHub OIDC short-lived AWS credentials over long-lived AWS access keys.
