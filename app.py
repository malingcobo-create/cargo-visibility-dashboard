import os
import mysql.connector
from flask import Flask

app = Flask(__name__)


def get_conn():
    return mysql.connector.connect(
        host="localhost",
        user="cargo_user",
        password=os.environ["CARGO_DB_PASSWORD"],
        database="cargo_demo",
    )


AT_PORT_SQL = """
SELECT terminal, COUNT(*) AS cars_here
FROM (
    SELECT vin, terminal, status,
           ROW_NUMBER() OVER (PARTITION BY vin ORDER BY event_time DESC, id DESC) AS rn
    FROM cargo_events
) latest
WHERE rn = 1 AND status <> 'dispatched'
GROUP BY terminal
ORDER BY terminal
"""

STYLE = """
<style>
  body { font-family: Arial, sans-serif; background: #f4f6f8; margin: 0; padding: 24px; }
  h1 { color: #1f2d3d; }
  .grid { display: flex; flex-wrap: wrap; gap: 16px; }
  .card { background: white; border-radius: 10px; padding: 16px 24px; min-width: 200px;
          box-shadow: 0 2px 6px rgba(0,0,0,0.1); }
  .place { color: #5b6b7b; font-size: 14px; }
  .count { font-size: 36px; font-weight: bold; color: #1f2d3d; }
</style>
"""
LATE_SQL = """
SELECT l.vin, l.terminal, p.planned
FROM (
    SELECT vin, terminal, status,
           ROW_NUMBER() OVER (PARTITION BY vin ORDER BY event_time DESC, id DESC) AS rn
    FROM cargo_events
) l
JOIN (
    SELECT vin, MAX(planned_departure) AS planned
    FROM cargo_events
    GROUP BY vin
) p ON p.vin = l.vin
WHERE l.rn = 1 AND l.status <> 'dispatched' AND NOW() > p.planned
ORDER BY p.planned
"""
DAMAGED_SQL = """
SELECT vin, terminal, cargo_condition, event_time
FROM (
    SELECT vin, terminal, cargo_condition, event_time,
           ROW_NUMBER() OVER (PARTITION BY vin ORDER BY event_time, id) AS rn
    FROM cargo_events
    WHERE cargo_condition <> 'good'
) d
WHERE rn = 1
ORDER BY event_time DESC
"""
@app.route("/")
def home():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(AT_PORT_SQL)
    rows = cur.fetchall()
    cur.execute(LATE_SQL)
    late = cur.fetchall()
    cur.execute(DAMAGED_SQL)
    damaged = cur.fetchall()
    conn.close()

    html = STYLE + "<h1>Cars at each place</h1><div class='grid'>"
    for terminal, count in rows:
        html += f"<div class='card'><div class='place'>{terminal}</div><div class='count'>{count}</div></div>"
    html += "</div>"

    html += f"<h1>Late cars ({len(late)})</h1><div class='grid'>"
    for vin, terminal, planned in late:
        html += (
            "<div class='card' style='border-left: 4px solid #d64545;'>"
            f"<div class='place'>{terminal}</div>"
            f"<div style='font-size:18px; font-weight:bold;'><a href='/car/{vin}'>{vin}</a></div>"
            f"<div class='place'>Planned: {planned:%d %b %H:%M}</div>"
            "</div>"
        )
    html += "</div>"

    html += f"<h1>Damaged cars ({len(damaged)})</h1><div class='grid'>"
    for vin, terminal, condition, when in damaged:
        html += (
            "<div class='card' style='border-left: 4px solid #e08a1e;'>"
            f"<div class='place'>{terminal}</div>"
            f"<div style='font-size:18px; font-weight:bold;'><a href='/car/{vin}'>{vin}</a></div>"
            f"<div class='place'>{condition.capitalize()}, noticed {when:%d %b %H:%M}</div>"
            "</div>"
        )
    html += "</div>"
    return html
@app.route("/car/<vin>")
def car(vin):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT event_time, status, terminal, from_terminal, cargo_condition, planned_departure, reason "
        "FROM cargo_events WHERE vin = %s ORDER BY event_time, id",
        (vin,),
    )
    events = cur.fetchall()
    conn.close()

    html = STYLE + f"<p><a href='/'>&larr; Back</a></p><h1>{vin}</h1><div class='grid' style='flex-direction:column;'>"
    for when, status, terminal, from_terminal, condition, planned, reason in events:
        line = f"{status.capitalize()} at {terminal}"
        if from_terminal:
            line += f" (transferred from {from_terminal})"
        extra = f"Condition: {condition}"
        if planned:
            extra += f" | Planned departure: {planned:%d %b %H:%M}"
        if reason:
            extra += f" | Reason: {reason}"
        html += (
            "<div class='card'>"
            f"<div class='place'>{when:%d %b %Y, %H:%M}</div>"
            f"<div style='font-size:18px; font-weight:bold;'>{line}</div>"
            f"<div class='place'>{extra}</div>"
            "</div>"
        )
    html += "</div>"
    return html
if __name__ == "__main__":
    app.run(debug=True) 