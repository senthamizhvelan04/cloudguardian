# Backend

FastAPI control-plane for CloudGuardian.

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The service defaults to deterministic/local mode. Set `AWS_ENABLED=true` only when the runtime has appropriate IAM permissions.
