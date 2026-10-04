# Hermes OTA

An AI research agent that tracks the global online-travel-agency (OTA) market —
Booking Holdings, Expedia Group, Trip.com Group, and MakeMyTrip, with Airbnb as a
comparator — covering financial performance, strategy, distribution, product
developments, and AI usage. See [IDEA.md](IDEA.md) for the mission and
[AGENTS.md](AGENTS.md) for the full research methodology (sourcing priorities,
claim-level provenance, financial fidelity rules, AI lifecycle evidence standards,
and workspace layout).

## Repository layout

| Path | Contents |
| --- | --- |
| `sources/` | Saved evidence (HTML/text) and source metadata for every claim |
| `data/` | Structured claim records, financial inputs, calculation code and outputs |
| `state/` | Deduplication index (`developments.json`) and dated coverage checkpoints |
| `reports/daily/` | One dated report per run, e.g. `reports/daily/2026-10-05.md` |
| `.claude/loop.md` | The prompt run by the daily cloud routine (see below) |

Each run is additive: it reads `state/` to see what's already covered, extends
coverage by one day, and commits the result. Nothing is overwritten.

## How the daily run works

Research runs automatically once a day via a **Claude cloud routine** — not a
local cron job. A routine is a scheduled, isolated Claude Code session hosted by
Anthropic that clones this repo, executes the prompt in
[.claude/loop.md](.claude/loop.md), and pushes its results (new files under
`sources/`, `data/`, `state/`, `reports/daily/`) straight back to this repo.

- **Schedule**: daily at `30 17 * * *` UTC (23:00 IST)
- **Routine**: [Hermes OTA — Daily Research](https://claude.ai/code/routines/trig_01Cjd6QBbNt2WhLC8UUGEspY)
- **Model**: `claude-sonnet-5`
- **Repo source**: this repository, checked out fresh on every fire
- **Tools available to the run**: `Bash`, `Read`, `Write`, `Edit`, `Glob`, `Grep`, `WebFetch`, `WebSearch`

Because each fire is a brand-new session with no memory of previous runs, all
continuity lives in the committed files — that's why `state/` and dated reports
matter: they're how tomorrow's run knows what today's run already found.

### Viewing and managing the routine

All routine management happens at **https://claude.ai/code/routines**:

- **See run history / logs**: open the routine link above, or from Claude Code ask
  to list its recent runs — each run links to its own session transcript.
- **Run it immediately** (don't wait for the schedule): open the routine and choose
  "Run now", or ask Claude Code to trigger it.
- **Pause / re-enable**: toggle the routine's enabled state on the routines page.
- **Change the schedule, model, or prompt**: edit the routine's configuration on
  the routines page, or ask Claude Code to update it — but keep `.claude/loop.md`
  in sync with whatever prompt the routine actually runs, since that file is the
  checked-in record of what the routine does.
- **Delete the routine**: routines can only be deleted from
  https://claude.ai/code/routines (not via the API).

### Running a research cycle manually

To run the same workflow outside the schedule (e.g. locally in Claude Code), open
this repo and ask Claude to follow [.claude/loop.md](.claude/loop.md) — it is a
self-contained prompt that works the same way whether triggered by the routine or
read manually. A manual run follows the same AGENTS.md workflow and can be
committed the same way:

```bash
git add sources/ data/ state/ reports/
git commit -m "Daily OTA research: YYYY-MM-DD"
git push
```

## Notes on visibility

This repository is currently **public**, so scraped sources, financial data, and
daily reports are visible to anyone. Switch it to private with
`gh repo edit Ryosuke-Kawashima-Career/HermesOTA --visibility private` if that
content shouldn't be public.
