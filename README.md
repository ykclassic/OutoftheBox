# OutoftheBox

OutoftheBox is a Streamlit-based collection of AI and productivity tools being evolved into a unified workspace. The current repository contains a home hub, 20 numbered tool pages, and a background-removal tool. Authentication, durable projects, usage metering, subscriptions, and connected workflows are **not yet implemented** and must not be represented as available features.

## Run locally

Requires Python 3.12.

```bash
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell
# .venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
streamlit run Home.py
```

Configure provider credentials in Streamlit secrets or deployment environment variables. Never commit `.streamlit/secrets.toml`, API keys, access tokens, or production data.

### Background removal

Set `REMOVE_BG_API_KEY` in the deployment environment or Streamlit secrets. The key previously embedded in the background-removal source must be considered compromised: revoke it at remove.bg and issue a replacement. Removing it from the current source does not erase it from Git history or revoke the provider credential.

Other AI pages currently expect `GEMINI_API_KEY` in Streamlit secrets. Review each provider integration before deployment and configure only the credentials actually required by enabled tools.

## Quality checks

```bash
python -m compileall -q Home.py pages tests
python -m pytest -q
```

Pull requests and pushes to `main` run source checks and a repository-history secret scan. A secret-scan finding must be investigated; do not suppress it merely to get a green check. Rotate affected credentials first. History rewriting may be required to remove sensitive values from old commits, but history cleanup is not a substitute for rotation.

## Production-readiness roadmap

The work is intentionally incremental. Do not launch public paid access until the security, reliability, ownership, billing, and recovery gates below have been verified.

1. **Security baseline:** rotate exposed credentials; audit current source and Git history; enforce secret scanning; validate and bound uploads; establish safe provider error handling.
2. **Reproducible builds:** resolve dependency conflicts, add a dependency lock with a documented update process, and test clean installs and primary workflows.
3. **Shared platform services:** app registry and contracts, provider gateway, common file processing, consistent errors, cost/usage controls, observability.
4. **Workspace and persistence:** authentication, server-side authorization, saved projects and jobs, object storage, retention/export/deletion controls.
5. **Commercial controls:** server-enforced entitlements, atomic usage accounting, verified idempotent billing webhooks, cancellation and failed-payment states.
6. **Connected workflows:** prioritize two or three workflows built from existing tools; add durable job status, retries, and cost limits before batch/scheduled execution.
7. **Closed beta:** task success, latency, provider cost, retention, conversion, and gross margin measured before expanding the catalogue.

## Merge and release gates

- CI and secret scanning pass; all findings are triaged.
- Dependency installation works in a clean Python 3.12 environment.
- Each supported app's main journey and provider-failure behavior has automated coverage.
- Upload limits and untrusted AI input handling are tested.
- Authorization, usage accounting, billing webhooks, and data deletion are tested before enabling accounts or paid access.
- Deployment health, rollback, backups, and restore procedures are verified against the actual hosting environment.

Passing CI or seeing the homepage load is not, by itself, evidence of production readiness.
