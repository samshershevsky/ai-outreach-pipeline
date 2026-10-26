# gtm-pipeline-mcp (demo MCP server)

A sanitized demo MCP server, written in Python with the standard library
only. It exposes the outreach pipeline in `../demo` as MCP tools, running on
the same 25 synthetic leads. No API keys, no network calls, no real data.

Server name: **gtm-pipeline-mcp**

## Tools

| Tool | Input | What it returns |
| --- | --- | --- |
| `enrich_lead` | `lead_id` (L001 to L025) | Simulated enrichment: headcount, tech stack, hiring signals, intent topics |
| `score_lead` | `lead_id` | Rubric score from 0 to 100, tier, and a reason string for every point |
| `draft_outreach` | `lead_id` | A grounded first touch draft for that lead. Draft only, it never sends |
| `get_report` | none | Tier distribution and the top 10 leads with scores and reasons |

## Run it

```bash
python3 mcp-server/server.py
```

The server speaks MCP over stdio (JSON RPC 2.0, one message per line). It
stays quiet until a client connects, which is normal for stdio servers.

Quick smoke test without a client:

```bash
printf '%s\n' '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}' | python3 mcp-server/server.py
```

## Connect it to Claude

Add the server to your MCP client configuration. For Claude Code, run:

```bash
claude mcp add gtm-pipeline-mcp python3 /path/to/ai-outreach-pipeline/mcp-server/server.py
```

For a JSON based MCP configuration (for example Claude Desktop), add:

```json
{
  "mcpServers": {
    "gtm-pipeline-mcp": {
      "command": "python3",
      "args": ["/path/to/ai-outreach-pipeline/mcp-server/server.py"]
    }
  }
}
```

Restart the client, then ask Claude to score lead L005 or draft outreach
for L002. Claude will call the tools above and work from the synthetic
data, exactly like the pipeline demo.

## How it maps to production

In production the same shape holds: an orchestrator agent on Claude calls
specialized agents, the agents call a custom MCP server, and the MCP server
is the only layer that touches tools such as Clay, Apollo, HubSpot, and
Google Workspace. Drafts stop at a human approval step before anything is
sent, and an evals and monitoring layer watches every run. This demo keeps
that architecture and swaps the live tools for synthetic data.
