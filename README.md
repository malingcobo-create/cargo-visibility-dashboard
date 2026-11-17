# Cargo Visibility Dashboard

A simulated vehicle-logistics dashboard for a multi-port South African operation (Durban, Gqeberha, East London). It shows which cars are at each terminal, which are running late, which were damaged, and the full timeline of any car.

**Live demo:** https://app-cargo-malil.azurewebsites.net

All data is generated. This is a demo, not a real company's system.

![Dashboard](dashboard.png)

## What it does

- Cars at each terminal right now
- Late cars (not dispatched and past the latest planned departure)
- Damaged cars, and where the damage was first noticed
- A timeline for each car, including reschedules and their reasons

Late and damaged status are calculated from the events, not stored.

## How it's built

- `generator.py` creates about 500 fake cars and their journeys and saves them to MySQL.
- `schema.sql` defines one `cargo_events` table with one row per event, so a car's full history is kept.
- `app.py` is a Flask app that reads the table and serves the dashboard.
- `terraform/` builds the Azure setup as code: resource group, MySQL flexible server, firewall rules, Linux App Service, and an email alert for server errors.
- `.github/workflows/deploy.yml` is the CI/CD pipeline. Every push that changes the app is syntax-checked and deployed to Azure automatically.

## Architecture

GitHub (push) -> GitHub Actions (check + deploy) -> Azure App Service (Flask) -> Azure Database for MySQL (South Africa North)

Secrets (database password, deploy key) live in Azure app settings and GitHub secrets, never in the code or the repo.

## Run it locally

1. Install Python and MySQL.
2. Run `schema.sql` in MySQL, then create a user:
   `CREATE USER 'cargo_user'@'localhost' IDENTIFIED BY 'your_password';`
   `GRANT ALL PRIVILEGES ON cargo_demo.* TO 'cargo_user'@'localhost';`
3. `pip install -r requirements.txt`
4. `python generator.py` and enter the password when asked.
5. `set CARGO_DB_PASSWORD=your_password` then `python app.py`
6. Open http://127.0.0.1:5000

## Known limits

- The dashboard has no login, which is fine for fake data but not for a real client.
- The pipeline checks syntax only. There are no automated tests yet.
