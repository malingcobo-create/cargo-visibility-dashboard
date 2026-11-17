import os
import mysql.connector
from getpass import getpass
import random
from datetime import datetime, timedelta

PORTS = {
    "Durban":      {"weight": 65, "roro": "Durban RoRo",      "yard": "Durban Vehicle Yard"},
    "Gqeberha":    {"weight": 25, "roro": "Gqeberha RoRo",    "yard": "Gqeberha Vehicle Yard"},
    "East London": {"weight": 10, "roro": "East London RoRo", "yard": "East London Vehicle Yard"},
}

NUM_CARS = 500


def make_vin():
    chars = "ABCDEFGHJKLMNPRSTUVWXYZ0123456789"
    return "".join(random.choices(chars, k=17))


def normal_journey(vin, port, extra_delay=0):
    p = PORTS[port]
    arrived = datetime.now() - timedelta(hours=random.randint(1, 30 * 24))
    planned = arrived + timedelta(days=3)
    cleared = arrived + timedelta(hours=random.randint(4, 12))
    moved = cleared + timedelta(hours=random.randint(6, 24))
    dispatched = moved + timedelta(hours=random.randint(12, 36) + extra_delay)
    # order: vin, terminal, status, time, condition, planned_departure, reason, from_terminal
    return [
        (vin, p["roro"], "arrived",    arrived,    "good", planned, None, None),
        (vin, p["roro"], "cleared",    cleared,    "good", None,    None, None),
        (vin, p["yard"], "moved",      moved,      "good", None,    None, None),
        (vin, p["yard"], "dispatched", dispatched, "good", None,    None, None),
    ]

def make_transfer(events, port):
    other = random.choice([n for n in PORTS if n != port])
    o = PORTS[other]
    vin = events[0][0]
    cleared = events[1]
    t_time = cleared[3] + timedelta(hours=random.randint(10, 30))
    d_time = t_time + timedelta(hours=random.randint(12, 36))
    return events[:2] + [
        (vin, o["roro"], "transferred", t_time, cleared[4], None, None, cleared[1]),
        (vin, o["yard"], "dispatched", d_time, cleared[4], None, None, None),
    ]


def add_damage(events):
    start = random.randint(1, len(events) - 1)
    damage = random.choice(["scratched", "dented", "cracked windscreen"])
    return [e if i < start else e[:4] + (damage,) + e[5:] for i, e in enumerate(events)]
REASONS = ["weather", "transport delay", "port congestion", "customs hold"]


def add_reschedules(events):
    vin, terminal, condition, planned, first = events[0][0], events[0][1], events[0][4], events[0][5], events[0][3]
    span = (events[-1][3] - first).total_seconds()
    times = sorted(first + timedelta(seconds=random.uniform(0, span)) for _ in range(random.randint(1, 3)))
    extra = []
    for when in times:
        planned = planned + timedelta(days=random.randint(1, 2))
        extra.append((vin, terminal, "rescheduled", when, condition, planned, random.choice(REASONS), None))
    return sorted(events + extra, key=lambda e: e[3])
names = list(PORTS)
weights = [PORTS[n]["weight"] for n in names]
picks = random.choices(names, weights=weights, k=NUM_CARS)

journeys = []
for port in picks:
    delay = random.randint(24, 120) if random.random() < 0.15 else 0
    events = normal_journey(make_vin(), port, delay)
    if random.random() < 0.08:
        events = make_transfer(events, port)
    if random.random() < 0.10:
        events = add_reschedules(events)
    if random.random() < 0.05:
        events = add_damage(events)
    events = [e for e in events if e[3] <= datetime.now()]
    journeys.append(events)
transfers = sum(1 for j in journeys if any(e[2] == "transferred" for e in j))
damaged = sum(1 for j in journeys if any(e[4] != "good" for e in j))
rescheduled = sum(1 for j in journeys if any(e[2] == "rescheduled" for e in j))
print("Rescheduled cars:", rescheduled)
print("Transferred cars:", transfers)
print("Damaged cars:", damaged)
still_here = sum(1 for j in journeys if j[-1][2] != "dispatched")
print("Still at a port:", still_here)
late = 0
for j in journeys:
    planned = max(e[5] for e in j if e[5] is not None)
    last = j[-1]
    if last[2] == "dispatched":
        if last[3] > planned:
            late += 1
    elif datetime.now() > planned:
        late += 1
print("Late cars:", late)
print("Cars:", len(journeys))
for event in journeys[0]:
    print(event)
conn = mysql.connector.connect(
    host=os.environ.get("DB_HOST", "localhost"),
    user=os.environ.get("DB_USER", "cargo_user"),
    password=getpass("Password: "),
    database="cargo_demo",
)
cur = conn.cursor()
cur.execute("TRUNCATE TABLE cargo_events")

rows = [event for journey in journeys for event in journey]
cur.executemany(
    "INSERT INTO cargo_events (vin, terminal, status, event_time, cargo_condition, planned_departure, reason, from_terminal) "
    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
    rows,
)
conn.commit()
print("Saved", len(rows), "events to MySQL")
conn.close()