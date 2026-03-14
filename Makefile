TF_ENV ?= dev
TF_DIR := infra/terraform/envs/$(TF_ENV)

.PHONY: infra-fmt infra-init infra-validate infra-plan infra-apply infra-destroy

infra-fmt:
	terraform -chdir=$(TF_DIR) fmt -recursive

infra-init:
	terraform -chdir=$(TF_DIR) init

infra-validate: infra-init
	terraform -chdir=$(TF_DIR) validate

infra-plan: infra-init
	terraform -chdir=$(TF_DIR) plan

infra-apply: infra-init
	terraform -chdir=$(TF_DIR) apply -auto-approve

infra-destroy: infra-init
	terraform -chdir=$(TF_DIR) destroy -auto-approve
