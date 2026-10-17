"""Idempotently seed a small, EXPLICITLY SYNTHETIC website-security graph."""
from graph_db import get_graph


def seed():
    graph = get_graph()
    statements = [
        ("MERGE (w:Website {id:'shop-demo'}) SET w.name='DemoShop', w.environment='local-only'", {}),
        ("MERGE (e:Endpoint {id:'ep-orders'}) SET e.path='/api/orders/{id}', e.method='GET'", {}),
        ("MERGE (e:Endpoint {id:'ep-catalog'}) SET e.path='/api/products', e.method='GET'", {}),
        ("MERGE (s:Service {id:'orders'}) SET s.name='Orders Service'", {}),
        ("MERGE (s:Service {id:'catalog'}) SET s.name='Catalog Service'", {}),
        ("MERGE (d:Database {id:'shop-db'}) SET d.name='Shop Database'", {}),
        ("MERGE (a:DataAsset {id:'customer-orders'}) SET a.name='Customer Orders', a.classification='sensitive'", {}),
        ("MERGE (a:DataAsset {id:'product-list'}) SET a.name='Public Products', a.classification='public'", {}),
        ("MERGE (f:Finding {id:'F-001'}) SET f.title='Possible broken order authorization', f.type='BOLA', f.severity_level=4, f.status='UNVERIFIED', f.source='synthetic_fixture'", {}),
        ("MERGE (f:Finding {id:'F-002'}) SET f.title='Missing Content Security Policy', f.type='MISSING_CSP', f.severity_level=2, f.status='UNVERIFIED', f.source='synthetic_fixture'", {}),
        ("MERGE (ev:Evidence {id:'EV-001'}) SET ev.summary='Demo fixture: ownership check requires verification', ev.confirmed=false", {}),
        ("MATCH (w:Website {id:'shop-demo'}), (e:Endpoint {id:'ep-orders'}) MERGE (w)-[:EXPOSES]->(e)", {}),
        ("MATCH (w:Website {id:'shop-demo'}), (e:Endpoint {id:'ep-catalog'}) MERGE (w)-[:EXPOSES]->(e)", {}),
        ("MATCH (e:Endpoint {id:'ep-orders'}), (s:Service {id:'orders'}) MERGE (e)-[:ROUTES_TO]->(s)", {}),
        ("MATCH (e:Endpoint {id:'ep-catalog'}), (s:Service {id:'catalog'}) MERGE (e)-[:ROUTES_TO]->(s)", {}),
        ("MATCH (s:Service {id:'orders'}), (d:Database {id:'shop-db'}) MERGE (s)-[:QUERIES]->(d)", {}),
        ("MATCH (d:Database {id:'shop-db'}), (a:DataAsset {id:'customer-orders'}) MERGE (d)-[:STORES]->(a)", {}),
        ("MATCH (f:Finding {id:'F-001'}), (e:Endpoint {id:'ep-orders'}) MERGE (f)-[:AFFECTS]->(e)", {}),
        ("MATCH (f:Finding {id:'F-002'}), (e:Endpoint {id:'ep-catalog'}) MERGE (f)-[:AFFECTS]->(e)", {}),
        ("MATCH (f:Finding {id:'F-001'}), (ev:Evidence {id:'EV-001'}) MERGE (f)-[:SUPPORTED_BY]->(ev)", {}),
    ]
    for cypher, params in statements:
        graph.query(cypher, params=params)
    print(f"Seeded {len(statements)} statements. Graph: traceshield (configurable).")
    print("Synthetic findings: F-001 (possible authorization flaw); F-002 (missing CSP)")


if __name__ == "__main__":
    seed()
