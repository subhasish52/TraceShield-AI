"""Single, reusable FalkorDB connection for all TraceShield components."""
import os
from dotenv import load_dotenv
from falkordb import FalkorDB

load_dotenv()


def get_graph():
    client = FalkorDB(
        host=os.getenv("FALKORDB_HOST", "localhost"),
        port=int(os.getenv("FALKORDB_PORT", "6379")),
    )
    return client.select_graph(os.getenv("FALKORDB_GRAPH", "traceshield"))
