# Claude Loop Configuration

This file is the prompt body for the Hermes OTA daily research routine — a Claude cloud
routine (see [claude.ai/code/routines](https://claude.ai/code/routines)) scheduled via
cron. Each fire is a fresh,
isolated session with this repository checked out; it has no memory of prior runs beyond
what is committed to `state/`, `sources/`, `data/`, and `reports/`.

## Schedule

- Cadence: daily
- Cron (UTC): `30 17 * * *`
- Local equivalent: 23:00 Asia/Kolkata (IST)

## Mission

Hermes OTA tracks the global online-travel-agency market — Booking Holdings, Expedia
Group, Trip.com Group, MakeMyTrip, with Airbnb as a comparator — per [IDEA.md](../IDEA.md).
Each run extends that coverage by one day: new financial disclosures, strategy moves,
distribution changes, product launches, and AI developments since the last run.

## What to do on each fire

1. Read [AGENTS.md](../AGENTS.md) in full — it is the binding methodology for sourcing,
   provenance, classification, financial fidelity, AI lifecycle evidence, workspace layout,
   and the research workflow. Follow it exactly; nothing below overrides it.
2. Read `state/developments.json` and the most recent file(s) in `state/coverage-*.json`
   to see what has already been covered and when it was last checked.
3. Execute the research workflow in [AGENTS.md](../AGENTS.md) §"Research workflow" for
   today's date: discover and open primary sources, save evidence under `sources/`,
   extract claim-level records into `data/`, deduplicate against `state/`, and write a
   dated report to `reports/daily/YYYY-MM-DD.md` (use today's actual date from the system
   clock — do not reuse or guess a prior date).
4. Update `state/developments.json` and write a new `state/coverage-YYYY-MM-DD.json`
   checkpoint, following the existing files' structure.
5. Run the completion checks at the bottom of [AGENTS.md](../AGENTS.md) before finishing.

## Committing results

This routine's only externally visible action is committing to this repository — no
bookings, messages, or other external actions (per AGENTS.md "Safety and external-action
limits"). At the end of a successful run:

```bash
git add sources/ data/ state/ reports/
git commit -m "Daily OTA research: YYYY-MM-DD"
git push
```

Use the actual run date in the commit message. If a step failed or was blocked (a source
unreachable, no new developments found), still commit whatever evidence/state was saved
and say so plainly in the report rather than skipping the commit — per AGENTS.md, record
failures rather than inventing results. If there is truly nothing to commit (identical
state, no new developments, no new evidence files), skip the commit rather than creating
an empty one.
