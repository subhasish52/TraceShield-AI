"""Persist synthetic-user authorization test results into the existing graph.

Uses the same IDs as seed_graph.py, so related findings actually share
an endpoint/service/database and graph correlation can discover them.
"""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from graph_db import get_graph


def save_bola_test(observed: str, owner_http: int, other_http: int) -> dict:
    """observed: CONFIRMED, DENIED, or INCONCLUSIVE. No credentials stored."""
    if observed not in {"CONFIRMED", "DENIED", "INCONCLUSIVE"}:
        raise ValueError("Invalid test result")
    graph = get_graph()
    checked_at = datetime.now(timezone.utc).isoformat()
    test_id = "TEST-" + uuid4().hex[:12].upper()
    summary = (
        f"Local synthetic-account authorization test: owner HTTP {owner_http}; "
        f"other user HTTP {other_http}; outcome={observed}. No real user data."
    )
    # Connect to existing seeded infrastructure rather than creating an isolated graph.
    graph.query("""
        MERGE (w:Website {id:'shop-demo'})
        SET w.name='DemoShop', w.environment='local-only'
        MERGE (ep:Endpoint {id:'ep-orders'})
        SET ep.path='/api/orders/{id}', ep.method='GET'
        MERGE (s:Service {id:'orders'})
        SET s.name='Orders Service'
        MERGE (d:Database {id:'shop-db'})
        SET d.name='Shop Database'
        MERGE (a:DataAsset {id:'customer-orders'})
        SET a.name='Customer Orders', a.classification='sensitive'
        MERGE (w)-[:EXPOSES]->(ep)
        MERGE (ep)-[:ROUTES_TO]->(s)
        MERGE (s)-[:QUERIES]->(d)
        MERGE (d)-[:STORES]->(a)
    """)

    if observed == "CONFIRMED":
        graph.query("""
            MATCH (ep:Endpoint {id:'ep-orders'})
            MERGE (f:Finding {id:'F-004'})
            SET f.title='Confirmed synthetic-account cross-user order access',
                f.type='BOLA', f.severity_level=4,
                f.status='CONFIRMED',
                f.source='synthetic_account_http_test',
                f.last_checked_at=$at
            MERGE (ev:Evidence {id:'EV-004'})
            SET ev.summary=$summary, ev.confirmed=true,
                ev.kind='cross_user_http_observation'
            MERGE (f)-[:AFFECTS]->(ep)
            MERGE (f)-[:SUPPORTED_BY]->(ev)
        """, params={"at": checked_at, "summary": summary})
    elif observed == "DENIED":
        existing = graph.ro_query(
            "MATCH (f:Finding {id:'F-004'}) RETURN f.status"
        ).result_set
        if existing:
            # The scanner verifies the fixed behavior. We retain earlier evidence.
            graph.query("""
                MATCH (f:Finding {id:'F-004'})
                SET f.status='REMEDIATED', f.last_checked_at=$at
                MERGE (ev:Evidence {id:'EV-004-VERIFY'})
                SET ev.summary=$summary, ev.confirmed=true,
                    ev.kind='verified_ownership_enforcement'
                MERGE (f)-[:SUPPORTED_BY]->(ev)
            """, params={"at": checked_at, "summary": summary})

    graph.query("""
        MATCH (ep:Endpoint {id:'ep-orders'})
        CREATE (t:TestResult {
            id:$id, kind:'synthetic_account_bola_check',
            outcome:$outcome, owner_http:$owner,
            other_http:$other, checked_at:$at,
            summary:$summary
        })
        CREATE (t)-[:TESTED]->(ep)
    """, params={
        "id": test_id, "outcome": observed, "owner": owner_http,
        "other": other_http, "at": checked_at, "summary": summary,
    })
    # Link test to finding only if it exists, so a clean initial scan
    # doesn't manufacture a vulnerability that wasn't observed.
    graph.query("""
        MATCH (t:TestResult {id:$id})
        MATCH (f:Finding {id:'F-004'})
        MERGE (t)-[:EVALUATES]->(f)
    """, params={"id": test_id})
    return {"test_id": test_id, "outcome": observed,
            "finding_id": "F-004" if observed == "CONFIRMED" else None}


def get_bola_history():
    graph = get_graph()
    rows = graph.ro_query("""
        MATCH (t:TestResult {kind:'synthetic_account_bola_check'})
        RETURN t.checked_at, t.id, t.outcome, t.owner_http, t.other_http
        ORDER BY t.checked_at DESC
    """).result_set
    return [dict(zip(("checked_at", "test_id", "outcome", "owner_http", "other_http"), row)) for row in rows]
