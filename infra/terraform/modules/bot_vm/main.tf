terraform {
  required_providers {
    yandex = {
      source  = "yandex-cloud/yandex"
      version = "~> 0.140"
    }
  }
}

resource "yandex_compute_disk" "boot" {
  name     = "${var.name_prefix}-boot"
  type     = var.boot_disk_type
  zone     = var.zone
  size     = var.boot_disk_size_gb
  image_id = var.image_id
}

resource "yandex_vpc_address" "nat" {
  name = "${var.name_prefix}-nat"
  external_ipv4_address {
    zone_id = var.zone
  }
}

resource "yandex_compute_instance" "bot" {
  name        = "${var.name_prefix}-bot"
  platform_id = var.platform_id
  zone        = var.zone

  resources {
    cores  = var.cores
    memory = var.memory_gb
  }

  boot_disk {
    disk_id = yandex_compute_disk.boot.id
  }

  network_interface {
    subnet_id      = var.subnet_id
    nat            = true
    nat_ip_address = yandex_vpc_address.nat.external_ipv4_address[0].address
  }

  metadata = {
    user-data = templatefile("${path.module}/cloud-init.yaml.tftpl", {
      repo_url           = var.repo_url
      repo_ref           = var.repo_ref
      app_dir            = var.app_dir
      data_dir           = var.data_dir
      telegram_bot_token = var.telegram_bot_token
      service_user       = var.service_user
    })
  }
}
