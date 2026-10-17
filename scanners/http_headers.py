
"""Scan our authorized local DemoShop for a missing CSP header."""

from urllib.parse import urlsplit
from urllib.request import urlopen

from ingestion.normalizer import normalize_missing_csp
from ingestion.graph_writer import save_finding
from graph_tools import get_finding, get_evidence, score_priority


TARGET_URL = "http://127.0.0.1:8000/"


def scan():
    parsed = urlsplit(TARGET_URL)

    # This starter scanner must only target local demo services.
    if parsed.hostname not in ("localhost", "127.0.0.1"):
        raise ValueError("Only localhost scanning is allowed")

    print("\n[TraceShield] Starting HTTP header scan...")
    print(f"[Target] {TARGET_URL}")

    with urlopen(TARGET_URL, timeout=5) as response:
        status = response.status
        csp = response.headers.get("Content-Security-Policy")

    print(f"[HTTP Status] {status}")

    if csp:
        print("[PASS] Content-Security-Policy header is present")
        print("[Info] No new missing-CSP finding created")
        return

    print("[FINDING] Content-Security-Policy header missing")

    finding = normalize_missing_csp(TARGET_URL, status)

    finding_id = save_finding(finding)

    print(f"\n[Saved to FalkorDB] {finding_id}")

    print("\nFinding:")
    print(get_finding(finding_id))

    print("\nEvidence:")
    print(get_evidence(finding_id))

    print("\nGraph-based priority:")
    print(score_priority(finding_id))

    print("\n[NEXT] Run:")
    print(f'python agent.py "Investigate {finding_id}"')


if __name__ == "__main__":
    try:
        scan()
    except Exception as error:
        print(f"\n[ERROR] {type(error).__name__}: {error}")
        raise SystemExit(1)
