"""Capture, inspect, and resolve errors from an LLM agent / workflow.

When a tool call or step throws, capture it with context (which agent, which
step, the inputs) and a stable fingerprint so repeated failures group into one
issue. Then pull the group for triage and resolve it once fixed. Each call is a
single Infrai REST call (see infrai.py).
"""
import traceback
import infrai


def run_step(agent: str, step: str, fn, **inputs):
    """Run one agent step; capture and re-raise on failure."""
    try:
        return fn(**inputs)
    except Exception as exc:
        infrai.errors.capture(
            title=f"{agent}/{step} failed",
            message=f"{type(exc).__name__}: {exc}",
            level="error",
            fingerprint=[agent, step],          # group by agent + step
            exception=traceback.format_exc(),   # full traceback string
            context={"agent": agent, "step": step, "inputs": inputs},
        )
        raise


def inspect_group(error_group_id: str) -> dict:
    """Pull the grouped occurrences for triage (id on the path)."""
    return infrai.errors.group_detail(error_group_id)


def mark_fixed(error_group_id: str) -> None:
    """Resolve a group once the underlying bug is shipped (id on the path)."""
    infrai.errors.resolve(error_group_id)


if __name__ == "__main__":
    def flaky(**_):
        raise ValueError("tool 'search' returned no results")

    try:
        run_step("research-agent", "web-search", flaky, query="infrai")
    except ValueError:
        print("captured agent error (grouped by agent + step)")
