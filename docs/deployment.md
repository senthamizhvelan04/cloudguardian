# Deployment

## 1. Local verification

```bash
cd backend
pip install -r requirements.txt
pytest -q
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 2. Docker

```bash
cp .env.example .env
docker compose up --build -d
curl http://localhost:8000/health
```

## 3. AWS

Review `terraform/environments/dev/terraform.tfvars.example`. Run Terraform only after checking CIDRs, IAM permissions, region and expected costs.

## 4. CI/CD

Configure GitHub repository variables/secrets required by the workflow. The recommended AWS authentication mechanism is GitHub OIDC.

## 5. Production hardening

Use PostgreSQL, HTTPS, secret management, centralized logs, restricted CORS, a private deployment subnet where appropriate, and explicit IAM boundaries.
