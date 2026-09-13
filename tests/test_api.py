import os
import sys
import unittest
from fastapi.testclient import TestClient

# Add root and backend directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.main import app

class TestSplitCyberAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_01_health(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["status"], "ok")

    def test_02_users_and_groups_flow(self):
        import uuid
        tag = uuid.uuid4().hex[:6]
        # Create users Alice, Bob, Charlie
        u1 = self.client.post("/api/users", json={"name": "Alice Vance", "email": f"alice_{tag}@test.com", "avatar_color": "#8B5CF6"}).json()
        u2 = self.client.post("/api/users", json={"name": "Bob Smith", "email": f"bob_{tag}@test.com", "avatar_color": "#06B6D4"}).json()
        u3 = self.client.post("/api/users", json={"name": "Charlie Brown", "email": f"charlie_{tag}@test.com", "avatar_color": "#10B981"}).json()

        self.assertIn("id", u1)
        self.assertIn("id", u2)
        self.assertIn("id", u3)

        # Create group
        g = self.client.post("/api/groups", json={
            "name": "Miami Beach Trip",
            "category": "Trip",
            "description": "Summer getaway",
            "initial_member_ids": [u1["id"], u2["id"], u3["id"]]
        }).json()
        self.assertIn("id", g)
        group_id = g["id"]

        # Add Expense 1: Villa Rental $300 paid by Alice (EQUAL split -> $100 each)
        e1 = self.client.post(f"/api/groups/{group_id}/expenses", json={
            "title": "Villa Rental",
            "amount": 300.0,
            "paid_by_id": u1["id"],
            "category": "Housing",
            "split_type": "EQUAL"
        }).json()
        self.assertEqual(e1["amount"], 300.0)

        # Check balances
        b1 = self.client.get(f"/api/groups/{group_id}/balances").json()
        self.assertEqual(b1["total_group_spending"], 300.0)
        # Alice paid 300, share 100 => net +200
        # Bob paid 0, share 100 => net -100
        # Charlie paid 0, share 100 => net -100

        # Simplified transactions should show Bob pays Alice $100 and Charlie pays Alice $100
        self.assertEqual(len(b1["simplified_transactions"]), 2)

        # Add Expense 2: Dinner $90 paid by Bob (EXACT split -> Alice $30, Bob $30, Charlie $30)
        e2 = self.client.post(f"/api/groups/{group_id}/expenses", json={
            "title": "Seafood Dinner",
            "amount": 90.0,
            "paid_by_id": u2["id"],
            "category": "Dining",
            "split_type": "EXACT",
            "splits": [
                {"user_id": u1["id"], "amount": 30.0},
                {"user_id": u2["id"], "amount": 30.0},
                {"user_id": u3["id"], "amount": 30.0}
            ]
        }).json()
        self.assertEqual(e2["amount"], 90.0)

        # Settle up: Bob pays Alice $70
        s1 = self.client.post(f"/api/groups/{group_id}/settlements", json={
            "payer_id": u2["id"],
            "payee_id": u1["id"],
            "amount": 70.0,
            "notes": "Partial settlement"
        }).json()
        self.assertEqual(s1["amount"], 70.0)

        # Re-fetch balance summary
        b2 = self.client.get(f"/api/groups/{group_id}/balances").json()
        self.assertGreater(len(b2["member_balances"]), 0)

if __name__ == "__main__":
    unittest.main()
