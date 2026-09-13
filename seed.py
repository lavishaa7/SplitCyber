import urllib.request
import json

BASE = "http://127.0.0.1:8000/api"

def post(url, data):
    req = urllib.request.Request(
        f"{BASE}{url}",
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    res = urllib.request.urlopen(req)
    return json.loads(res.read().decode())

def seed():
    print("[+] Seeding demo users...")
    u1 = post("/users", {"name": "Alice Vance", "email": "alice@cyber.io", "avatar_color": "#8B5CF6"})
    u2 = post("/users", {"name": "Bob Smith", "email": "bob@cyber.io", "avatar_color": "#06B6D4"})
    u3 = post("/users", {"name": "Charlie Day", "email": "charlie@cyber.io", "avatar_color": "#10B981"})
    u4 = post("/users", {"name": "Diana Prince", "email": "diana@cyber.io", "avatar_color": "#F43F5E"})

    print("[+] Seeding demo group...")
    g = post("/groups", {
        "name": "Tokyo Tech Hackathon Trip",
        "category": "Trip",
        "description": "Travel, Villa stay, and dining expenses for the Tokyo Trip",
        "initial_member_ids": [u1["id"], u2["id"], u3["id"], u4["id"]]
    })
    group_id = g["id"]

    print("[+] Seeding group expenses...")
    # Expense 1: Luxury Villa $800 paid by Alice (Equal split)
    post(f"/groups/{group_id}/expenses", {
        "title": "Akihabara Luxury Suite Stay",
        "amount": 800.0,
        "paid_by_id": u1["id"],
        "category": "Housing",
        "split_type": "EQUAL"
    })

    # Expense 2: Sushi & Ramen Banquet $240 paid by Bob (Exact split)
    post(f"/groups/{group_id}/expenses", {
        "title": "Ginza Omakase Dinner",
        "amount": 240.0,
        "paid_by_id": u2["id"],
        "category": "Dining",
        "split_type": "EXACT",
        "splits": [
            {"user_id": u1["id"], "amount": 60.0},
            {"user_id": u2["id"], "amount": 60.0},
            {"user_id": u3["id"], "amount": 60.0},
            {"user_id": u4["id"], "amount": 60.0}
        ]
    })

    # Expense 3: Shinkansen High-Speed Rail $400 paid by Charlie (Percentage split)
    post(f"/groups/{group_id}/expenses", {
        "title": "Shinkansen Bullet Train Passes",
        "amount": 400.0,
        "paid_by_id": u3["id"],
        "category": "Transport",
        "split_type": "PERCENTAGE",
        "splits": [
            {"user_id": u1["id"], "percentage": 25.0},
            {"user_id": u2["id"], "percentage": 25.0},
            {"user_id": u3["id"], "percentage": 25.0},
            {"user_id": u4["id"], "percentage": 25.0}
        ]
    })

    print("[+] Sample demo data seeded successfully!")

if __name__ == "__main__":
    seed()
