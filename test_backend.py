import main
from fastapi.testclient import TestClient

client = TestClient(main.app)

# 1. Root & Health
r_root = client.get("/")
assert r_root.status_code == 200, f"Root failed: {r_root.text}"
r_health = client.get("/health")
assert r_health.status_code == 200 and r_health.json() == {"ok": True}, f"Health failed: {r_health.text}"
print("[PASS] Health check")

# 2. Search cached
prof = {
    "branch": "CSE",
    "year": "2nd Year",
    "skills": ["Python", "Machine Learning"],
    "interests": ["AI"],
    "location": "Bangalore"
}
r_search = client.post("/search?live=false", json=prof)
assert r_search.status_code == 200, f"Search failed: {r_search.text}"
data = r_search.json()
assert data["count"] > 0, "No opportunities returned"
assert len(data["results"]) == data["count"]
top_title = data["results"][0]["title"]
top_score = data["results"][0]["match_score"]
print(f"[PASS] Search (cache): {data['count']} opportunities returned, top match: {top_title} ({top_score}%)")

# 3. Search kinds
for k in ["internship", "hackathon", "scholarship"]:
    res = client.post(f"/search?live=false&kind={k}", json=prof).json()
    assert all(o["type"] == k for o in res["results"]), f"Kind filter failed for {k}"
    print(f"[PASS] Filter kind={k}: {res['count']} items")

# 4. Search live without key
r_live = client.post("/search?live=true", json=prof)
assert r_live.status_code == 200
live_data = r_live.json()
assert live_data["count"] > 0
assert "warning" in live_data and live_data["warning"] is not None
print(f"[PASS] Search (live fallback): warning=\"{live_data['warning']}\"")

print("\nALL BACKEND TESTS PASSED SUCCESSFULLY!")
