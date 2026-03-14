output "instance_id" {
  value = yandex_compute_instance.bot.id
}

output "public_ip" {
  value = yandex_vpc_address.nat.external_ipv4_address[0].address
}
