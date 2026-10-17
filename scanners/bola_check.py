"""Local synthetic-user test for Broken Object Level Authorization.

Only requests the fixed 127.0.0.1 demo target; no destructive operations.
"""
import argparse
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from ingestion.bola_writer import get_bola_history, save_bola_test

URL = "http://127.0.0.1:8000/api/orders/101"


def request_order(fake_token):
    request = Request(URL, headers={"Authorization": f"Bearer {fake_token}"})
    try:
        with urlopen(request, timeout=5) as response:
            return response.status, response.read(4096)
    except HTTPError as exc:
        return exc.code, exc.read(4096)


def scan():
    print("[TraceShield] Authorized local synthetic-user BOLA check")
    print(f"[Endpoint] {URL}")
    try:
        owner_http, owner_body = request_order("demo-alice")
        other_http, other_body = request_order("demo-bob")
    except (URLError, TimeoutError) as exc:
        raise RuntimeError("DemoShop not reachable. Run python demoshop\\app.py") from exc

    print(f"[Owner (Alice)] HTTP {owner_http}")
    print(f"[Other user (Bob)] HTTP {other_http}")
    owner_is_alice = False
    other_reads_alice = False
    try:
        owner_is_alice = owner_http == 200 and json.loads(owner_body).get("owner") == "alice"
        other_reads_alice = other_http == 200 and json.loads(other_body).get("owner") == "alice"
    except (ValueError, AttributeError, UnicodeDecodeError):
        pass

    if owner_is_alice and other_reads_alice:
        observed = "CONFIRMED"
        print("[FAIL] Cross-user access observed on synthetic order 101.")
    elif owner_is_alice and other_http in (403, 404):
        observed = "DENIED"
        print("[PASS] Order ownership enforced: non-owner access denied.")
    else:
        observed = "INCONCLUSIVE"
        print("[INCONCLUSIVE] Check the local DemoShop route and test accounts.")

    outcome = save_bola_test(observed, owner_http, other_http)
    print(f"[FalkorDB] Stored TestResult: {outcome['test_id']}")
    if observed == "CONFIRMED":
        print('[Next] python agent.py "Investigate F-004"')
    elif observed == "DENIED":
        print("[Next] Review F-004 status (REMEDIATED if previously confirmed)")
    print("[Note] Only fake users/orders were used; this is a demo test.")
    return 0 if observed != "INCONCLUSIVE" else 2


def main():
    parser = argparse.ArgumentParser(description="Local synthetic BOLA check")
    parser.add_argument("--history", action="store_true", help="List saved graph test results")
    args = parser.parse_args()
    if args.history:
        print(json.dumps(get_bola_history(), indent=2))
        return 0
    return scan()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, ConnectionError) as exc:
        print(f"[ERROR] {exc}")
        raise SystemExit(1)
