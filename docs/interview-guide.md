# Interview Story

## Problem

Cloud infrastructure incidents require monitoring, investigation, diagnosis and safe remediation.

## Solution

CloudGuardian connects AWS observability with an incident engine, runbook retrieval, AI-assisted diagnosis and bounded remediation.

## Important engineering decisions

- IAM roles instead of instance access keys
- SSM instead of unrestricted SSH for operational actions
- allowlisted tools instead of arbitrary commands
- human approval for risky actions
- deterministic fallback when AI is unavailable
- verification after remediation
- audit trail for every decision/action

## Questions to prepare

- Why FastAPI?
- Why SSM?
- Why IAM roles?
- How does RAG help incident diagnosis?
- How do you prevent an AI agent from executing dangerous commands?
- How would you scale the incident store?
- How would you calculate MTTR?
- How would you deploy without long-lived AWS credentials?
