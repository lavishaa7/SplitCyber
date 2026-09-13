import sys
import os
import uvicorn

# Add backend directory to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "backend")))

if __name__ == "__main__":
    print("[+] Starting SplitCyber Group Expense Splitter Server...")
    print("[+] Dashboard UI: http://localhost:8000")
    print("[+] API Documentation: http://localhost:8000/api/docs")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
