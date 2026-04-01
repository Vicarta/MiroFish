# MiroFish MCP Development Plan

## Goal

Створити окремий MCP server як thin wrapper над MiroFish backend API, щоб агенти могли запускати весь workflow без UI.

## Product Shape

- MiroFish frontend/backend залишається окремим продуктом для людей.
- MCP server додається як окремий сервісний шар для агентів.
- MCP server викликає backend API напряму.
- Human users work via UI, AI agents work via MCP.

## MVP Tools

- `generate_ontology`
- `build_graph`
- `get_graph_task`
- `create_simulation`
- `prepare_simulation`
- `get_prepare_status`
- `start_simulation`
- `get_run_status`
- `generate_report`
- `get_report_status`
- `get_report`
- `chat_with_report_agent`
- `search_graph`
- `get_graph_statistics`

## MVP Resources

- `mirofish://projects/{project_id}`
- `mirofish://graphs/{graph_id}`
- `mirofish://simulations/{simulation_id}`
- `mirofish://simulations/{simulation_id}/profiles`
- `mirofish://simulations/{simulation_id}/config`
- `mirofish://reports/{report_id}`

## File Ingestion

Recommended first implementation:

- accept uploaded files as `content_base64` in the MCP tool input;
- write them to a temp directory;
- submit them to MiroFish `multipart/form-data` endpoint;
- return `project_id` plus ontology output.

Alternative for later:

- separate `upload_file` tool returning `file_id`.

## Async Job Model

Long-running stages must be modeled as async jobs:

- graph build
- simulation prepare
- simulation run
- report generation

Standard response shape:

```json
{
  "id": "task_xxx",
  "kind": "graph_build",
  "status": "queued|processing|completed|failed",
  "progress": 0,
  "message": "human readable status",
  "result": null,
  "error": null
}
```

Expected agent loop:

1. call start tool
2. receive `task_id`
3. poll status tool
4. continue when status becomes `completed`

## Suggested Python Stack

- Python 3.11+
- `fastmcp` or official Python MCP SDK
- `httpx`
- `pydantic`

Suggested modules:

- `client.py`
- `schemas.py`
- `tools/graph.py`
- `tools/simulation.py`
- `tools/report.py`
- `resources.py`
- `server.py`

## Security

- MCP should call private backend URL, for example `http://127.0.0.1:15001`
- no public exposure needed for MCP
- temporary files should be deleted after upload handoff
- request/response logs must redact secrets and file contents

## Delivery Milestones

1. server scaffolding and health check
2. graph tools
3. simulation tools
4. report tools
5. resources
6. auth, logging and cleanup
7. integration tests

## Done Definition

- an agent can upload source files and create a project through MCP
- an agent can build a graph and poll until completion
- an agent can prepare and run a simulation
- an agent can generate a report and ask follow-up questions
- docs clearly describe upload, polling and result retrieval flow
