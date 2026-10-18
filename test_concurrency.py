import sys
import threading
import requests

BASE = "http://127.0.0.1:5000"

def login(email, password):
    s = requests.Session()
    r = s.post(f"{BASE}/login",
               data={"role": "team", "email": email, "password": password})
    if "Invalid email" in r.text:
        sys.exit(f"Login failed for {email}")
    return s

def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python test_concurrency.py <slot_id>")
    slot_id = sys.argv[1]

    sessions = [login(e, p) for e, p in TEAMS]
    barrier = threading.Barrier(len(sessions))
    results = {}

    def attempt(idx, sess):
        barrier.wait()          # all threads fire at the same instant
        r = sess.post(f"{BASE}/team/book/{slot_id}", data={"reason": "concurrency test"})
        if "booked successfully" in r.text:
            results[idx] = "WON  (slot booked)"
        elif "just taken" in r.text:
            results[idx] = "LOST (slot already taken)"
        else:
            results[idx] = "OTHER (check the page)"

    threads = [threading.Thread(target=attempt, args=(i, s)) for i, s in enumerate(sessions)]
    for t in threads: t.start()
    for t in threads: t.join()

    for i in sorted(results):
        print(f"Team {i + 1} ({TEAMS[i][0]}): {results[i]}")
    winners = sum(1 for v in results.values() if v.startswith("WON"))
    print("\nPASS: exactly one team got the slot." if winners == 1
          else f"FAIL: {winners} winners (expected 1).")

main()
