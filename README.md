# Cargo Visibility Dashboard

A simulated vehicle-logistics dashboard for a multi-port South African operation (Durban, Gqeberha, East London). It shows which cars are at each terminal, which are running late, which were damaged, and the full timeline of any car.

All data is generated. It is a demo, not a real company's system.



## How it works

- `generator.py` creates about 500 fake cars and their journeys (arrived, cleared, moved, transferred, rescheduled, dispatched) and saves them to MySQL.
- `schema.sql` creates the database. It has one `cargo_events` table with one row per event, so a car's full history is kept.
- `app.py` is a Flask web app that reads the table and shows:
  - cars at each terminal right now
  - late cars (not dispatched and past the latest planned departure)
  - damaged cars
  - a timeline page for each car, including reschedules and their reasons

Late and damaged status are calculated from the events, not stored.

## Run it locally

1. Install Python and MySQL.
2. Run `schema.sql` in MySQL, then create a user:
   `CREATE USER 'cargo_user'@'localhost' IDENTIFIED BY 'your_password';`
   `GRANT ALL PRIVILEGES ON cargo_demo.* TO 'cargo_user'@'localhost';`
3. `pip install mysql-connector-python flask`
4. `python generator.py` and enter the password when asked.
5. Set the password for the app and start it:
   `set CARGO_DB_PASSWORD=your_password`
   `python app.py`
6. Open http://127.0.0.1:5000

## Next steps

Deploy to Azure with Terraform, add a CI/CD pipeline and monitoring.
