# Loom Walkthrough — 5-Minute Script

**Goal:** a hiring manager watches this and thinks "this guy actually builds."
Record at 1080p, terminal font bumped up (16pt+), and keep the energy conversational —
you're showing a thing you built, not presenting slides.

## 0:00–0:30 — Intro (webcam on)

**On screen:** your face.
**Say:** "Hey, I'm Sam. I build AI systems that take the manual busywork out of
go-to-market work. I can't show you my production systems — they're on company
software — so I rebuilt the core of one with fake data. Let me run it for you
live."

## 0:30–1:30 — The problem + the input (screen share)

**On screen:** `demo/data/leads.csv` open in an editor. Scroll through a few rows.
**Say:** "Here's the starting point: 25 completely fictional leads — fake people,
fake companies, labeled as synthetic right in the file. In the real world this
would be your ICP list from Apollo. The question the pipeline answers is: which
of these are worth a rep's time, and what do you say to them?"

## 1:30–2:30 — Run it live (screen share)

**On screen:** terminal. Type `bash demo/run.sh` and let it run.
**Say (while it runs):** "Five stages. Ingest and validate — then enrichment:
headcount estimates, tech stack, hiring signals. In production that's real API
calls; here it's a deterministic simulation so the demo is reproducible. Then
scoring — zero to a hundred, tiered A, B, C — and every point is explainable.
Then it drafts a personalized email per lead. And finally a report. Nothing gets
sent — the pipeline ends at drafts for a human to approve. That approve-and-send
gate is deliberate."

## 2:30–3:30 — The report (screen share)

**On screen:** `demo/output/report.md`. Show the tier distribution, then scroll
to the per-lead scoring reasons.
**Say:** "Here's what came out — 4 Tier A, 14 B, 7 C. And this is the part I'm
proudest of: every score shows its work. 'Title seniority plus 30, sweet-spot
company size plus 25, hiring signal plus 7.' A sales leader can audit this. Black
box scores don't survive contact with a real sales team."

## 3:30–4:30 — The drafts + the prompts (screen share)

**On screen:** `demo/output/outreach_emails.md` — open two drafts: Robert Hayes
(the "no CRM" pain-signal one) and David Okafor (the HubSpot migration one).
Then flip to `demo/prompts.py` for 10 seconds.
**Say:** "And the drafts pick up the actual signal — the no-CRM guy gets a
different opener than the guy mid-HubSpot-migration. The prompts driving this
live in their own file, versioned and reviewable — and if you plug in an API
key, these exact prompts run live against Claude instead of the built-in
template engine."

## 4:30–5:00 — Close (webcam on)

**On screen:** your face.
**Say:** "So that's the demo — the same staged, explainable, human-in-the-loop
design I used in production, where it cut manual prospecting work about in half.
Happy to rebuild it on real data and walk through the architecture decisions.
Thanks for watching."

## Recording tips

- Do one practice run of `bash demo/run.sh` first so there are no surprises.
- If a draft reads awkwardly live, laugh it off: "template engine, not Claude —
  with an API key these get sharper." Honesty lands well.
- Keep the `output/` folder fresh — re-run right before recording so the report
  date matches.
- End card: put your LinkedIn URL in the Loom description, not in the video.
