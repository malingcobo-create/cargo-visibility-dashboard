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
resource "azurerm_service_plan" "main" {
  name                = "plan-cargo-demo"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  os_type             = "Linux"
  sku_name            = "B1"
}

resource "azurerm_linux_web_app" "main" {
  name                = "app-cargo-malil"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  service_plan_id     = azurerm_service_plan.main.id

  site_config {
    app_command_line = "gunicorn --bind=0.0.0.0 --timeout 600 app:app"
    application_stack {
      python_version = "3.12"
    }
  }

  app_settings = {
    DB_HOST                        = azurerm_mysql_flexible_server.main.fqdn
    DB_USER                        = "cargoadmin"
    CARGO_DB_PASSWORD              = var.db_password
    SCM_DO_BUILD_DURING_DEPLOYMENT = "true"
  }
}

output "app_url" {
  value = "https://${azurerm_linux_web_app.main.default_hostname}"
}