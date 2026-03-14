variable "name_prefix" {
  type = string
}

variable "zone" {
  type = string
}

variable "subnet_id" {
  type = string
}

variable "platform_id" {
  type    = string
  default = "standard-v3"
}

variable "cores" {
  type    = number
  default = 2
}

variable "memory_gb" {
  type    = number
  default = 2
}

variable "boot_disk_type" {
  type    = string
  default = "network-ssd"
}

variable "boot_disk_size_gb" {
  type    = number
  default = 20
}

variable "image_id" {
  type        = string
  description = "Ubuntu image id"
}

variable "repo_url" {
  type = string
}

variable "repo_ref" {
  type    = string
  default = "trunk"
}

variable "app_dir" {
  type    = string
  default = "/opt/personal-assistant"
}

variable "data_dir" {
  type    = string
  default = "/opt/personal-assistant/data"
}

variable "telegram_bot_token" {
  type      = string
  sensitive = true
}

variable "service_user" {
  type    = string
  default = "assistant"
}
