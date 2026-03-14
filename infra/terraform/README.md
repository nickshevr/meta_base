# Terraform infrastructure for Telegram bot in Yandex Cloud

This folder provisions infra to run the bot on a VM and deploy/update it on merges to `trunk`.

## Structure

- `modules/bot_vm` — reusable VM module with cloud-init bootstrap + systemd service.
- `envs/dev` — dev environment.
- `envs/prod` — prod environment.

## Prerequisites

1. Terraform `>=1.6`.
2. Service account key with permissions for VPC + Compute.
3. Existing Git repo URL reachable from VM.
4. Telegram bot token.

## Quick start (local)

```bash
cd infra/terraform/envs/dev
cp terraform.tfvars.example terraform.tfvars
# optionally create backend.hcl with your Object Storage settings
terraform init -backend-config=backend.hcl
terraform plan
terraform apply
```

Outputs include VM public IP.

## Backend example (`backend.hcl`)

```hcl
bucket                      = "<tf-state-bucket>"
region                      = "ru-central1"
endpoint                    = "storage.yandexcloud.net"
key                         = "personal-assistant/dev/terraform.tfstate"
access_key                  = "<access-key>"
secret_key                  = "<secret-key>"
skip_region_validation      = true
skip_credentials_validation = true
```

## CI/CD

GitHub Actions workflow `.github/workflows/infra-deploy.yml`:
- runs `terraform fmt -check`, `init`, `validate`, `plan` on PRs and trunk pushes;
- runs `apply` automatically on `push` to `trunk` for `prod` environment.

### Required repository secrets

- `YC_SA_KEY_JSON` — service account key json content.
- `YC_TF_BACKEND_BUCKET`
- `YC_TF_BACKEND_ACCESS_KEY`
- `YC_TF_BACKEND_SECRET_KEY`
- `YC_CLOUD_ID`
- `YC_FOLDER_ID`
- `YC_ZONE`
- `YC_IMAGE_ID`
- `TG_BOT_TOKEN`
- `APP_REPO_URL` (for VM bootstrap clone)

You can also add separate values for dev/prod by splitting workflow if needed.
