
"""Convert an HTTP security observation into a standard finding."""

from urllib.parse import urlsplit


def normalize_missing_csp(url: str, http_status: int) -> dict:
    parsed = urlsplit(url)
    path = parsed.path or "/"

    return {
        "finding_id": "F-003",
        "title": "Missing Content Security Policy",
        "type": "MISSING_CSP",
        "severity_level": 2,
        "status": "UNVERIFIED",
        "source": "http_header_scanner",
        "website_name": "DemoShop",
        "endpoint_id": f"demoshop:{path}",
        "endpoint_path": path,
        "evidence_id": "EV-003",
        "evidence_summary": (
            f"HTTP GET {url} returned status {http_status}. "
            "The Content-Security-Policy response header was absent. "
            "This is an observed configuration issue, not proof "
            "of successful exploitation."
        ),
        "evidence_confirmed": True,
    }
