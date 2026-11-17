terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }
}

provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "main" {
  name     = "rg-cargo-demo"
  location = "southafricanorth"
}
variable "db_password" {
  type      = string
  sensitive = true
}

resource "azurerm_mysql_flexible_server" "main" {
  name                   = "mysql-cargo-malil"
  resource_group_name    = azurerm_resource_group.main.name
  location               = azurerm_resource_group.main.location
  administrator_login    = "cargoadmin"
  administrator_password = var.db_password
  sku_name               = "B_Standard_B1ms"
  version                = "8.0.21"

  storage {
    size_gb = 20
  }
}

resource "azurerm_mysql_flexible_database" "cargo" {
  name                = "cargo_demo"
  resource_group_name = azurerm_resource_group.main.name
  server_name         = azurerm_mysql_flexible_server.main.name
  charset             = "utf8mb4"
  collation           = "utf8mb4_unicode_ci"
}
variable "my_ip" {
  type = string
}

resource "azurerm_mysql_flexible_server_firewall_rule" "my_pc" {
  name                = "my-pc"
  resource_group_name = azurerm_resource_group.main.name
  server_name         = azurerm_mysql_flexible_server.main.name
  start_ip_address    = var.my_ip
  end_ip_address      = var.my_ip
}

resource "azurerm_mysql_flexible_server_firewall_rule" "azure_services" {
  name                = "allow-azure-services"
  resource_group_name = azurerm_resource_group.main.name
  server_name         = azurerm_mysql_flexible_server.main.name
  start_ip_address    = "0.0.0.0"
  end_ip_address      = "0.0.0.0"
}