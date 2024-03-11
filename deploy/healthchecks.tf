data "healthchecksio_channel" "email" {
  kind = "email"
}

data "healthchecksio_channel" "discord" {
  kind = "discord"
}

data "healthchecksio_channel" "sms" {
  kind = "sms"
}

resource "healthchecksio_check" "austastic_check" {
  name = "Austastic"
  desc = "Austastic Discord bot aliveness check"

  timeout = 15 * 60 # 15 minutes
  grace   = 35 * 60 # 35 minutes

  channels = [
    data.healthchecksio_channel.sms.id,
    data.healthchecksio_channel.email.id,
    data.healthchecksio_channel.discord.id,
  ]
}