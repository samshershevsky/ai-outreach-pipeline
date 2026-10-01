# Case Study: How I Cut Manual Prospecting Work 50% with a 12-Agent AI System

*Sanitized from production work. Company name withheld; no proprietary code shown.
The architecture, tools, and results below are real. A runnable mini-version of
the core pipeline is in `demo/`.*

## The problem

Prospecting was eating the week. Reps were manually researching accounts, copying
data between Apollo and HubSpot, scoring leads by gut feel, and writing every
first-touch email from scratch. CRM hygiene was decaying — dupes, dead emails,
stale titles — which made every downstream number untrustworthy. The team didn't
need "AI magic." It needed the busywork gone.

## The system: 12 agents, one pipeline

Built on Claude Enterprise, wired to our stack through MCP connectors (Apollo,
HubSpot, Gmail, Google Calendar). Each agent does one job and hands off cleanly:

1. **Lead discovery** — pulls target accounts from Apollo against ICP filters.
2. **Enrichment** — firmographics, tech stack, hiring signals per account.
3. **Dedupe & validation** — checks every record against HubSpot; kills dupes
   and dead data before anything else touches it. (CRM hygiene first — garbage
   in, garbage out.)
4. **ICP scoring** — transparent 0–100 fit score with reasons, not a black box.
5. **Signal watcher** — job posts, leadership changes, tech migrations; re-scores
   when something meaningful happens.
6. **Outreach drafter** — writes the first touch from the lead's actual signals.
7. **Personalization reviewer** — a second agent critiques every draft: no
   invented facts, one observation max, plain language. Drafts that fail get
   rewritten, not shipped.
8. **Approve-and-send gate** — a human approves every send. Nothing goes out
   autonomously. Non-negotiable.
9. **Reply classifier** — sorts inbound: interested / not now / opt-out, and
   routes each correctly (opt-outs suppressed immediately).
10. **CRM sync** — HubSpot updated automatically; activity logged where it happened.
11. **Meeting scheduler** — books time via the Calendar connector when a lead
    says yes.
12. **Reporting** — weekly digest: what got sent, what converted, what to change.

## The tools

Claude Enterprise + MCP connectors (Apollo, HubSpot, Gmail, Google Calendar),
plus the unglamorous parts that made adoption stick: a shared prompt library,
approve-and-send review workflows, and plain-language AI usage guidelines I wrote
so the team actually used the thing instead of routing around it. I also trained
coworkers on agentic workflows directly — enablement was half the job.

## The outcome

**Manual prospecting workload dropped ~50%.** Reps spent their time on
conversations instead of research and data entry. I ran the same AI-augmented
workflow end-to-end myself and hit 150% of monthly target after a 30-day ramp —
which is what convinced the skeptics faster than any slide deck.

## What I'd do again (and what I'd skip)

- **Do again:** start with CRM hygiene (agent 3). Clean data made every other
  agent 10x more trustworthy.
- **Do again:** the reviewer agent (7). Two cheap agents beat one clever one —
  the critic catches hallucinations the drafter can't see in its own work.
- **Do again:** human-in-the-loop from day one. "Approve-and-send" got us trust
  from legal and leadership in weeks instead of quarters.
- **Skip:** over-automating edge cases early. The first version tried to handle
  every weird reply; the 80/20 version shipped in half the time and the edge
  cases got a human queue.

---
*Want to see the core of this running? `bash demo/run.sh` — same staged design,
synthetic data, zero setup.*
