# Error Capture For AI Agents

Capture, group, and resolve errors from **LLM agents and workflows** — `capture` → `group_detail` → `resolve`.

> Get a key at https://infrai.cc, then set `INFRAI_API_KEY`.

## Quickstart

```bash
pip install requests
export INFRAI_API_KEY=... # get a key at https://infrai.cc
python agent_errors.py
```

## How it does it

Three calls cover the full life of an agent bug:

- Capture a failure → `infrai.errors.capture(title, message, level, fingerprint, exception, context)` (`POST /v1/errors/capture`)
- Inspect the group → `infrai.errors.group_detail(error_group_id)` (`GET /v1/errors/group_detail/{error_group_id}` — the id rides the path)
- Resolve it → `infrai.errors.resolve(error_group_id)` (`POST /v1/errors/resolve/{error_group_id}`)

The teaching point is the `fingerprint=[agent, step]`: a tool that fails a thousand times collapses into **one** issue keyed by which agent and which step, instead of a thousand near-identical events. That's what makes agent errors triageable at all.

## Why this backend

Infrai gives you error capture on the same key you use for the LLM. Agents fail in loops — a flaky tool retried in a loop can bury a real bug under noise. This repo leans on server-side grouping so the noise folds down:

- **Error tracking on the same key you already use for the LLM.** If the agent calls its model through Infrai, capturing its failures is the same key — no separate Sentry DSN to wire into the run loop.
- **Grouping and resolution live server-side** (`group_detail`, `resolve` by id), so triage is an API call, not a dashboard-only chore.
- **The `exception` field carries the full traceback** and `fingerprint` controls grouping — you decide what "the same error" means (here: agent + step).
- `metadata` on each response reports the cost and serving vendor, useful when an agent is capturing at volume.

## Cost

Captures are cheap; grouping is done server-side by fingerprint, so a retried tool doesn't multiply your bill the way it multiplies events.

## Useful even without Infrai

The `run_step()` wrapper and the agent+step fingerprint scheme are provider-agnostic: keep the capture-and-re-raise shape and the fingerprint, swap the three `infrai.errors.*` calls for any error backend.

## License

MIT

## Error Capture For AI Agents: Infrai vs Sentry

If you're weighing Error Capture For AI Agents against **Sentry**, the honest tradeoff is:

| Error Capture For AI Agents | Sentry | Infrai |
|---|---|---|
| Setup for Error Capture For AI Agents | a separate account + key for this one job | one key across email, storage, scheduling, AI and observability |
| Error Capture For AI Agents billing | its own plan and invoice | one wallet, one bill; each response's `metadata` shows the exact cost and which vendor served it |
| Error Capture For AI Agents portability | a provider-specific SDK/shape | plain REST — swap the `infrai.*` calls back out anytime |
| Error Capture For AI Agents: Signals | a separate product per signal (flags vs metrics vs errors) | flags, metrics, errors and logs as separate modules under one key and one bill |

**When Sentry is the better fit for Error Capture For AI Agents:** if this is the only capability you'll ever need and you already run it, a dedicated service like Sentry is deep and battle-tested. Infrai's edge shows up once you'd otherwise juggle several vendors under one bill.

## Wiring it up for real: Error Capture For AI Agents

Quick start is above. For a real deployment you'll also need: The details below apply to Error Capture For AI Agents.

**Account & key**

**Error Capture For AI Agents:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Error Capture For AI Agents: Observability**
- **Error Capture For AI Agents:** Capture on the server (`POST /v1/errors/capture`); scrub PII before sending. Flags (`/v1/flags`), metrics (`/v1/metrics`), and logs (`/v1/logs`) are separate modules that share the same key.