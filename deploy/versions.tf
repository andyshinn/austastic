terraform {
  required_providers {
    healthchecksio = {
      source = "kristofferahl/healthchecksio"
      version = "2.0.0"
    }
  }
}

provider "healthchecksio" {}