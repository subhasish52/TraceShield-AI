# TraceShield AI

**Graph-powered security investigation, contextual prioritization, and
remediation verification**

TraceShield AI is a **local defensive-security demonstration** combining
**FalkorDB**, a **Gemini-powered LangChain/LangGraph agent**, a
**Streamlit dashboard**, and **authorized HTTP scanners**. Rather than
treating scanner findings as isolated alerts, TraceShield maps each
finding onto an application dependency graph, correlates related issues,
traces potentially affected data, recommends a next step, and records
evidence from repeatable tests.

> **Scope and safety:** The included DemoShop app uses **fake users and
> fake orders** on `127.0.0.1`. The intentionally vulnerable
> configuration is **for local testing only**. Do not expose DemoShop or
> the unauthenticated development database to the public internet. Only
> scan systems you own or have explicit permission to assess.

## What is implemented

| Capability                   | Implementation                                                                                          |
|------------------------------|---------------------------------------------------------------------------------------------------------|
| Application dependency graph | FalkorDB with websites, endpoints, services, databases, data assets, findings, and evidence             |
| Graph investigation          | Multi-hop Cypher traversal: finding → endpoint → service → database → asset                             |
| Contextual scoring           | Deterministic **inherent-impact** heuristic (0–100); not a probability of exploitation                  |
| Correlation                  | Find other findings sharing endpoints, services, or databases                                           |
| What-if analysis             | Simulate a change in linked data classification **without modifying the graph**                         |
| AI security analyst          | Gemini model via LangChain `create_agent` (LangGraph execution), using graph-backed tools               |
| HTTP security-header scanner | Observes whether the local DemoShop homepage returns a CSP header                                       |
| BOLA authorization test      | Uses two synthetic users to check cross-user access to a fake order                                     |
| Verification history         | Saves `TestResult` records and shows before/after authorization checks                                  |
| Audit trail                  | Can store an `Investigation` and **proposed** `Action` in FalkorDB                                      |
| Dashboard                    | Investigation queue, impact graph, graph reasoning, verification timeline, Gemini agent, local scanners |

**Important:** Graph paths show possible dependencies, **not** proven
exploit chains. `F-001`/`F-002` are seeded fixtures; `F-003` is an
observed missing-header configuration issue; `F-004` is a
synthetic-account authorization finding that can be confirmed and
remediated through a local retest. A successful retest is evidence for
the **tested scenario**, not proof that all authorization flaws are
eliminated.

## Architecture

``` mermaid
flowchart TD
    Demo["DemoShop local web app / fake orders"]
    Headers["HTTP-header scanner"]
    BOLA["Synthetic-user BOLA test"]
    Ingest["Normalizer + graph writers"]
    DB[("FalkorDB security knowledge graph")]
    Tools["Graph tools / graph intelligence"]
    Agent["Gemini + LangChain/LangGraph agent"]
    UI["Streamlit security dashboard"]
    Demo --> Headers
    Demo --> BOLA
    Headers --> Ingest
    BOLA --> Ingest
    Ingest --> DB
    DB --> Tools
    Tools --> Agent
    DB --> UI
    Agent --> UI
```

**Representative graph schema**

``` mermaid
flowchart LR
    W[Website] -->|EXPOSES| E[Endpoint]
    F[Finding] -->|AFFECTS| E
    E -->|ROUTES_TO| S[Service]
    S -->|QUERIES| D[Database]
    D -->|STORES| A[DataAsset]
    F -->|SUPPORTED_BY| EV[Evidence]
    F -.->|investigated in| I[Investigation]
    I -.->|proposes| AC[Action]
    F -.->|verified by| T[TestResult]
```

The dashed relationships above are **conceptual**: inspect
`graph_intelligence.py` and `ingestion/bola_writer.py` for the exact
Cypher relationship names used in your installed version. Do not rely on
the diagram as a migration script.

## Technology stack

- **Python:** 3.11 or 3.12 recommended; the project has also been run
  with Python 3.13.
- **FalkorDB:** graph database, running in Docker.
- **LangChain / LangGraph:** tool-calling investigation workflow.
- **Google Gemini:** model selected using `GEMINI_MODEL` (example:
  `gemini-2.5-flash-lite`). A valid Gemini API key is required for the
  AI agent.
- **Streamlit / pandas / Graphviz:** browser-based dashboard, tables,
  and dependency visualization.
- **Python standard library:** local HTTP server, HTTP test requests,
  JSON, timestamps, and subprocesses.

`requirements.txt` contains **version ranges**, not a tested lockfile.
For a fully reproducible submission, test a fresh environment and
optionally export your working dependency versions with
`python -m pip freeze > requirements-lock.txt`.

## Project layout

``` text
traceshield-graph-starter/
├── .env                       # Local secrets; never commit
├── .env.example               # Safe template; see below
├── .gitignore                 # Recommended; see below
├── requirements.txt
├── docker-compose.yml
├── graph_db.py                # FalkorDB connection
├── graph_tools.py             # Finding, impact, evidence, risk-score tools
├── graph_intelligence.py      # Correlation, investigation, what-if, audit
├── agent_graph_tools_v2.py    # Extra tools exposed to Gemini
├── agent.py                   # Gemini-powered graph agent
├── seed_graph.py              # Seed synthetic graph fixtures
├── demo.py                    # CLI graph demo (no LLM)
├── dashboard.py               # Streamlit application
├── demoshop/
│   └── app.py                 # Local DemoShop + synthetic order API
├── scanners/
│   ├── __init__.py
│   ├── http_headers.py        # Local CSP header scan
│   └── bola_check.py          # Two-user authorization test
└── ingestion/
    ├── __init__.py
    ├── normalizer.py          # Normalize HTTP scan observations
    ├── graph_writer.py        # Persist HTTP scan observations
    └── bola_writer.py         # Persist BOLA evidence/test history
```

This layout represents the **combined starter plus the upgrades**. The
original starter ZIP alone does not contain all these files; copy the
previously supplied dashboard, scanner, DemoShop, and graph-intelligence
upgrades into the project root before running the full workflow. Make
sure `scanners/__init__.py` and `ingestion/__init__.py` exist (empty
files are sufficient).

------------------------------------------------------------------------

## Local setup — Windows 10/11 (VS Code + CMD)

### 1. Prerequisites

Install and launch:

1.  **Python 3.11+** (`py --version` or `python --version`); ensure
    Python is on PATH.
2.  **Docker Desktop** with Docker Compose (`docker --version`,
    `docker compose version`). Start Docker Desktop before launching the
    database.
3.  **VS Code** (recommended) and a modern browser.
4.  **Gemini API key** for the optional AI agent; graph tools and
    scanners run without it.

In VS Code, open the **project folder containing `agent.py` and
`docker-compose.yml`**. Open a terminal and select **Command Prompt**
rather than PowerShell for the commands below.

### 2. Create and activate the Python environment

``` cmd
py -3 -m venv .venv
.venv\Scripts\activate
python --version
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

The terminal prompt should start with `(.venv)`. If `py` is unavailable,
use `python -m venv .venv`.

**PowerShell alternative:** `.\.venv\Scripts\Activate.ps1` (PowerShell
may require an execution-policy adjustment). **macOS/Linux:**
`python3 -m venv .venv && source .venv/bin/activate`.

### 3. Configure `.env`

If `.env.example` exists:

``` cmd
copy .env.example .env
```

Use the following contents in `.env` (replace the placeholder with
**your own** API key):

``` dotenv
FALKORDB_HOST=localhost
FALKORDB_PORT=6379
FALKORDB_GRAPH=traceshield
GOOGLE_API_KEY=YOUR_GEMINI_API_KEY_HERE
GEMINI_MODEL=gemini-2.5-flash-lite
```

**Note:** The **original** starter `agent.py` imported
`langchain_openai.ChatOpenAI` and used `OPENAI_API_KEY`. Your **current
working agent** uses `langchain_google_genai.ChatGoogleGenerativeAI`,
`GOOGLE_API_KEY`, and `GEMINI_MODEL`. This README and `requirements.txt`
target the **current Gemini version**. If your local `agent.py` still
imports `langchain_openai`, update it to the Gemini version before
following the agent commands; do **not** install both providers unless
your code actually supports both.

Never publish `.env`, keys, authorization tokens, or private data.
Gemini API access and quota are managed by Google separately from any
ChatGPT subscription.

### 4. Start FalkorDB

From the project root:

``` cmd
docker compose up -d
docker compose ps
```

The starter `docker-compose.yml` maps:

| Service           | Address                 | Purpose                     |
|-------------------|-------------------------|-----------------------------|
| FalkorDB protocol | `127.0.0.1:6379`        | Python graph client         |
| FalkorDB browser  | <http://localhost:3000> | Inspect graph data visually |

**Development-only configuration:** the supplied Compose file does not
configure database authentication or persistent storage. Do not expose
ports publicly. A `docker compose down` command removes the running
container; without a configured persistent volume, **your graph data may
be lost**. Avoid `docker compose down -v` unless you intentionally want
to delete stored data. For a durable installation, add a properly
configured persistent volume and authentication before any non-local
use.

Check the database connection:

``` cmd
python -c "from graph_db import get_graph; print(get_graph().ro_query('RETURN 1').result_set)"
```

Expected: `[[1]]` (or an equivalent single-row result).

### 5. Seed the initial graph

``` cmd
python seed_graph.py
python demo.py F-001
python demo.py F-002
```

`F-001` and `F-002` are **synthetic, unverified examples**. `F-001`
links the Orders endpoint to sensitive customer-order data; `F-002`
represents a missing-CSP scenario. Seeding uses Cypher `MERGE` to avoid
duplicating seeded nodes and edges.

If you already have F-003/F-004 and their history in FalkorDB, **do not
reset the graph just to follow these instructions**.

### 6. Run DemoShop locally

Open a **second CMD terminal**, activate the same `.venv` if needed, and
run:

``` cmd
python demoshop\app.py --secure
```

Visit <http://127.0.0.1:8000/>. The `--secure` flag enforces order
ownership in the fake order API. Keep this terminal open while scanning
or using dashboard scanner buttons.

The deliberately vulnerable test mode is:

``` cmd
python demoshop\app.py
```

**Only use vulnerable mode on localhost with synthetic data.** Stop the
existing DemoShop process with **Ctrl+C** before switching modes; only
one process can listen on port 8000.

### 7. Run the HTTP-header scanner

From another terminal at the project root:

``` cmd
python -m scanners.http_headers
```

The scanner makes an authorized local request and records the observed
missing Content-Security-Policy header as `F-003` with evidence in
FalkorDB. An absent CSP header is a **configuration observation**, not
proof that XSS is exploitable.

### 8. Run the synthetic-user BOLA verification

**To reproduce the full before/after lifecycle:**

1.  Stop DemoShop if running (`Ctrl+C`). Start the deliberately
    vulnerable demo: `python demoshop\app.py`.
2.  In another terminal run `python -m scanners.bola_check`.
3.  Expected: Alice **HTTP 200**, Bob **HTTP 200**; cross-user access is
    observed on **fake order 101**, creating/updating `F-004` and a
    `TestResult`.
4.  Stop DemoShop; restart securely: `python demoshop\app.py --secure`.
5.  Rerun `python -m scanners.bola_check`.
6.  Expected: Alice **HTTP 200**, Bob **HTTP 403**; the test records
    denial of cross-user access. If a prior confirming test exists,
    `F-004` can transition to **REMEDIATED**.
7.  Inspect the saved history:

``` cmd
python -m scanners.bola_check --history
```

**Do not present the secure-mode switch as an AI automatically patching
production code.** It is a controlled developer-operated demonstration.
The scanner uses local fake identities (`demo-alice`, `demo-bob`) and
fake order data; it does not use real accounts.

### 9. Run graph intelligence (no LLM key required)

``` cmd
python graph_intelligence.py investigate F-004
python graph_intelligence.py compare F-003 F-004
python graph_intelligence.py whatif F-004 public
python graph_intelligence.py record F-003
```

- `investigate` returns the finding, graph paths, evidence, score,
  correlated findings, and a proposed next action.
- `compare` ranks by the heuristic score; **always interpret the current
  remediation status separately**.
- `whatif` simulates reclassifying linked data assets **in memory**,
  without writing to FalkorDB.
- `record` creates investigation/proposed-action records. It does
  **not** apply a fix.

The default scoring heuristic uses severity, internet exposure, data
sensitivity, and graph reachability. A risk score of 90 can remain
visible on a **REMEDIATED** finding because it describes **inherent
impact**, not current exploitability or remediation success.

### 10. Run the Gemini graph agent

Make sure `.env` contains a valid `GOOGLE_API_KEY` and your `agent.py`
has the graph-intelligence tools integrated. Examples:

``` cmd
python agent.py "Investigate F-004 and explain the evidence and graph impact"
python agent.py "Compare F-003 and F-004, including current remediation status"
python agent.py "What happens to F-004 risk if linked data were public?"
python agent.py "Record an investigation and proposed next action for F-003"
```

The agent should call graph-backed tools, separate **observed evidence**
from assumptions, and distinguish **historical inherent impact** from
**current remediation status**. Model responses are not a substitute for
the recorded test results.

### 11. Start the Streamlit dashboard

Open a **third CMD terminal** in the project root:

``` cmd
.venv\Scripts\activate
python -m streamlit run dashboard.py
```

Open <http://localhost:8501/>. The upgraded dashboard includes:

| Tab                   | What to demonstrate                                                         |
|-----------------------|-----------------------------------------------------------------------------|
| Investigation Queue   | Findings, sources, statuses, inherent risk, unresolved vs. remediated       |
| Impact Graph          | Finding → endpoint → service → database → data asset                        |
| Graph Reasoning       | Correlated findings and hypothetical asset-classification change            |
| Verification Timeline | Chronological BOLA test evidence: confirmed failure, then successful denial |
| Gemini Agent          | Tool-grounded security investigation and comparison                         |
| Local Scanners        | Run localhost-only CSP and synthetic-account BOLA checks                    |

The dashboard reads FalkorDB directly. If a scan finishes, use the
**Refresh dashboard data** button or rerun the page to see updated
results.

**Normal local run: three terminals**

``` text
Terminal A: docker compose up -d           (Docker service runs in background)
Terminal B: python demoshop\app.py --secure
Terminal C: python -m streamlit run dashboard.py
```

The CLI scans and agent commands can be run in another terminal as
needed.

------------------------------------------------------------------------

## Findings and interpretation

| ID      | Origin                   | Meaning                                                               | Typical state                                                   |
|---------|--------------------------|-----------------------------------------------------------------------|-----------------------------------------------------------------|
| `F-001` | Seeded fixture           | Possible broken order authorization, with sensitive-data graph path   | `UNVERIFIED`                                                    |
| `F-002` | Seeded fixture           | Missing-CSP example                                                   | `UNVERIFIED`                                                    |
| `F-003` | Local HTTP scanner       | Missing CSP header observed at `/`                                    | `UNVERIFIED` for exploitability; header observation is recorded |
| `F-004` | Local two-user HTTP test | Cross-user access to fake order, followed by secure-mode verification | `CONFIRMED` before fix; `REMEDIATED` after successful retest    |

`F-001` and `F-004` can share the Orders API/service/database.
**Correlation is not identity:** a remediated `F-004` does not
automatically prove every possible `F-001` authorization concern is
resolved. Similarly, `F-002` is a fixture, while `F-003` is an actual
observed header response.

### Sample FalkorDB Cypher queries

Open the FalkorDB browser at <http://localhost:3000> and select the
`traceshield` graph (or use `get_graph().ro_query(...)`).

**List findings:**

``` cypher
MATCH (f:Finding)
RETURN f.id, f.title, f.status, f.source
ORDER BY f.id
```

**Trace downstream impact:**

``` cypher
MATCH (f:Finding {id: 'F-004'})-[:AFFECTS]->(e:Endpoint)
OPTIONAL MATCH (e)-[:ROUTES_TO]->(s:Service)
OPTIONAL MATCH (s)-[:QUERIES]->(d:Database)
OPTIONAL MATCH (d)-[:STORES]->(a:DataAsset)
RETURN f.id, e.path, s.name, d.name, a.name, a.classification
```

**Find other findings on the same endpoint:**

``` cypher
MATCH (f:Finding {id: 'F-004'})-[:AFFECTS]->(e:Endpoint)<-[:AFFECTS]-(other:Finding)
WHERE other.id <> f.id
RETURN DISTINCT other.id, other.title
```

**Inspect BOLA test records:**

``` cypher
MATCH (t:TestResult)
RETURN t.id, t.outcome, t.owner_http, t.other_http, t.checked_at
ORDER BY t.checked_at
```

**Inspect evidence:**

``` cypher
MATCH (f:Finding {id: 'F-004'})-[:SUPPORTED_BY]->(e:Evidence)
RETURN f.id, e.id, e.summary, e.confirmed
```

Use parameterized Cypher in application code; avoid concatenating
user-provided strings into graph queries.

## Suggested demo (3–4 minutes)

1.  **Problem (20s):** Conventional security scanners report isolated
    issues; application context is missing.
2.  **Detection (45s):** Run the synthetic-user BOLA test against
    deliberately vulnerable local DemoShop; show Alice/Bob HTTP 200 and
    a stored test result.
3.  **Graph impact (45s):** Show F-004 linked to the Orders Service,
    Shop Database, and sensitive Customer Orders.
4.  **Agent reasoning (45s):** Ask Gemini to compare F-003 and F-004,
    including evidence and current verification status. Demonstrate
    graph correlation and the what-if score change.
5.  **Verification (45s):** Restart DemoShop with `--secure`; rerun the
    test; show Bob HTTP 403 and the verification timeline.
6.  **Conclusion (20s):** Explain why the graph is central to impact
    tracing, correlation, and auditable evidence.

Record a backup demo video and screenshots before the submission
deadline. Only claim capabilities you can reproduce on a fresh local
installation.

## Troubleshooting

| Problem                                                    | What to check                                                                                                      |
|------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------|
| `ModuleNotFoundError`                                      | Activate `.venv`; run `python -m pip install -r requirements.txt`; confirm the correct VS Code interpreter         |
| Docker connection refused on `6379`                        | Start Docker Desktop; run `docker compose up -d`; inspect `docker compose ps` and `docker compose logs falkordb`   |
| FalkorDB browser unavailable on `3000`                     | Check container health and port conflicts; `docker compose ps`                                                     |
| No findings in dashboard                                   | Run `python seed_graph.py` and scanners; confirm `FALKORDB_GRAPH=traceshield`                                      |
| DemoShop connection refused                                | Start `python demoshop\app.py --secure` in another terminal; check port `8000`                                     |
| Port `8000` already in use                                 | Stop the existing DemoShop process with `Ctrl+C` before starting another mode                                      |
| BOLA scanner reports HTTP 200 for Bob                      | You are probably running **vulnerable mode**; use `--secure` to demonstrate remediation                            |
| BOLA scanner reports HTTP 403 for Bob                      | Ownership enforcement is active for the tested synthetic order                                                     |
| Gemini authentication or quota error                       | Verify `GOOGLE_API_KEY`, model access, quota, and network connectivity; graph/scanner tools can run without Gemini |
| Blank Streamlit page                                       | Check Streamlit terminal traceback; `python -m py_compile dashboard.py`; hard-refresh browser; restart Streamlit   |
| Graph diagram fails                                        | Install `graphviz` Python package; verify `st.graphviz_chart` support and browser connectivity                     |
| Missing Graph Reasoning tab                                | You are running an older `dashboard.py`; install the revised dashboard                                             |
| Agent claims remediated F-004 is still highest active risk | Instruct it to consider current status; keep inherent impact separate from current investigation priority          |
| Data disappeared after container removal                   | Original Compose setup has no guaranteed persistent volume; reseed and rerun scanners                              |

Quick checks:

``` cmd
python -m py_compile agent.py dashboard.py graph_intelligence.py
python -c "from graph_db import get_graph; print(get_graph().ro_query('MATCH (f:Finding) RETURN count(f)').result_set)"
python -m scanners.bola_check --history
```

## Privacy, security, and limitations

- Only perform scans on **authorized** targets. Current scanner modules
  intentionally target the local DemoShop environment.
- The default DemoShop application is deliberately vulnerable; it must
  **never** be hosted as a public production service.
- FalkorDB's starter Compose file is **unauthenticated development
  configuration**; keep it on loopback and add authentication,
  persistence, and hardening before any deployment.
- No production credentials, real user data, or personal order
  information should be ingested into the graph.
- The synthetic-account BOLA check covers a **single fake order and two
  fake users**. A 403 response does not prove all authorization paths
  are secure.
- A missing CSP header does not independently demonstrate XSS; an
  implemented CSP must also be reviewed for policy quality.
- The graph-based priority score is a **heuristic**; it is not a
  calibrated probability, CVSS replacement, or proof of compromise.
- Correlation means findings share a graph component, not necessarily a
  root cause.
- What-if classification simulates a scoring-input change, not a real
  remediation or causal intervention.
- `record_investigation` creates a proposed action; **a human must
  approve actual changes**. The demo's `--secure` flag is an
  operator-controlled configuration switch.
- AI explanations can be incorrect. Review them against FalkorDB nodes,
  scan outputs, and test history.

## GitHub hygiene

Create a `.gitignore` containing at least:

``` gitignore
.venv/
.env
__pycache__/
*.py[cod]
.pytest_cache/
.streamlit/secrets.toml
*.log
.DS_Store
.vscode/
```

Commit a **safe** `.env.example` containing the variable names with an
empty API-key value. Do not commit your real `.env`, API keys, access
tokens, or exported graph data containing secrets.

### Recommended validation before publishing

``` cmd
python -m pip check
python -m py_compile agent.py dashboard.py graph_intelligence.py
python demo.py F-001
python -m scanners.http_headers
python -m scanners.bola_check
python -m scanners.bola_check --history
```

For a clean-install check, create a new virtual environment and install
only from `requirements.txt`. Do not claim a clean install has been
verified until you've run it yourself.

## Project status and future work

This is a **local hackathon prototype**, not a production vulnerability
management platform. Potential future extensions include scanner
adapters, authenticated multi-tenant deployments, automated regression
suites, secure remediation approval workflows, richer graph analytics,
and persistent database backups.

## Acknowledgments and AI assistance

Built with FalkorDB, LangChain/LangGraph, Google Gemini, Streamlit, and
Python. AI assistance was used in the design, implementation, and
documentation workflow; all security claims should be validated against
reproducible tests. Add your **team name, repository URL, demo video,
and hackathon submission link** before publishing.

## License

No license is implied by this README. Add a `LICENSE` file only after
choosing the terms under which you want others to use the code.
