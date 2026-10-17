"""First milestone: see graph-driven triage WITHOUT an LLM or live website."""
import json
import sys
from graph_tools import get_finding, trace_impact, get_evidence, score_priority


def run(finding_id: str):
    result = {
        "finding": get_finding(finding_id),
        "potential_impact_paths": trace_impact(finding_id),
        "supporting_evidence": get_evidence(finding_id),
        "triage": score_priority(finding_id),
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else "F-001")
