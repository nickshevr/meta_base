terraform {
  required_version = ">= 1.6.0"

  required_providers {
    yandex = {
      source  = "yandex-cloud/yandex"
      version = "~> 0.140"
    }
  }

  backend "s3" {}
}

provider "yandex" {
  cloud_id                 = var.cloud_id
  folder_id                = var.folder_id
  zone                     = var.zone
  service_account_key_file = var.service_account_key_file
}

resource "yandex_vpc_network" "main" {
  name = "${var.name_prefix}-network"
}

resource "yandex_vpc_subnet" "main" {
  name           = "${var.name_prefix}-subnet"
  zone           = var.zone
  network_id     = yandex_vpc_network.main.id
  v4_cidr_blocks = [var.subnet_cidr]
}

module "bot_vm" {
  source = "../../modules/bot_vm"

  name_prefix           = var.name_prefix
  zone                  = var.zone
  subnet_id             = yandex_vpc_subnet.main.id
  image_id              = var.image_id
  repo_url              = var.repo_url
  repo_ref              = var.repo_ref
  telegram_bot_token    = var.telegram_bot_token
  service_user          = var.service_user
  app_dir               = var.app_dir
  data_dir              = var.data_dir
  cores                 = var.cores
  memory_gb             = var.memory_gb
  boot_disk_size_gb     = var.boot_disk_size_gb
}
