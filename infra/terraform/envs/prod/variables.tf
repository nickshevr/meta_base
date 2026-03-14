variable "cloud_id" { type = string }
variable "folder_id" { type = string }
variable "service_account_key_file" { type = string }
variable "zone" { type = string }
variable "name_prefix" { type = string }
variable "subnet_cidr" { type = string }
variable "image_id" { type = string }
variable "repo_url" { type = string }
variable "repo_ref" {
  type    = string
  default = "trunk"
}
variable "telegram_bot_token" {
  type      = string
  sensitive = true
}
variable "service_user" {
  type    = string
  default = "assistant"
}
variable "app_dir" {
  type    = string
  default = "/opt/personal-assistant"
}
variable "data_dir" {
  type    = string
  default = "/opt/personal-assistant/data"
}
variable "cores" {
  type    = number
  default = 2
}
variable "memory_gb" {
  type    = number
  default = 2
}
variable "boot_disk_size_gb" {
  type    = number
  default = 20
}
