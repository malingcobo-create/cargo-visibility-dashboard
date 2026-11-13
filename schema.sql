CREATE DATABASE IF NOT EXISTS cargo_demo;
USE cargo_demo;

CREATE TABLE IF NOT EXISTS cargo_events (
    id                 INT AUTO_INCREMENT PRIMARY KEY,
    vin                VARCHAR(17) NOT NULL,
    terminal           VARCHAR(50) NOT NULL,
    status             ENUM('arrived','cleared','moved','transferred','rescheduled','dispatched') NOT NULL,
    event_time         DATETIME NOT NULL,
    cargo_condition    VARCHAR(50),
    planned_departure  DATETIME,
    reason             VARCHAR(100),
    from_terminal      VARCHAR(50),
    INDEX idx_vin_time (vin, event_time)
);