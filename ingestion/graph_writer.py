
"""Create or update scanner findings in FalkorDB."""

from graph_db import get_graph


def save_finding(finding: dict) -> str:
    required = [
        "finding_id", "title", "type", "severity_level",
        "status", "source", "website_name",
        "endpoint_id", "endpoint_path", "evidence_id",
        "evidence_summary", "evidence_confirmed",
    ]

    missing = [key for key in required if key not in finding]

    if missing:
        raise ValueError(f"Missing finding fields: {missing}")

    graph = get_graph()

    query = """
    MERGE (w:Website {name: $website_name})

    MERGE (e:Endpoint {id: $endpoint_id})
    SET e.path = $endpoint_path

    MERGE (w)-[:EXPOSES]->(e)

    MERGE (f:Finding {id: $finding_id})
    SET f.title = $title,
        f.type = $type,
        f.severity_level = $severity_level,
        f.status = $status,
        f.source = $source

    MERGE (f)-[:AFFECTS]->(e)

    MERGE (ev:Evidence {id: $evidence_id})
    SET ev.summary = $evidence_summary,
        ev.confirmed = $evidence_confirmed

    MERGE (f)-[:SUPPORTED_BY]->(ev)

    RETURN f.id
    """

    result = graph.query(query, params=finding)

    if not result.result_set:
        raise RuntimeError("FalkorDB did not return the finding ID")

    return result.result_set[0][0]
