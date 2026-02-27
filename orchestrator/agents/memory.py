"""
Memory Agent — persists and retrieves user session context as JSON files.
"""
import os
import json
import time
from typing import Any

MEMORY_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "memory_store")


def _get_path(session_id: str) -> str:
    os.makedirs(MEMORY_DIR, exist_ok=True)
    return os.path.join(MEMORY_DIR, f"{session_id}.json")


def load(session_id: str) -> dict:
    """Load memory for a session. Returns empty structure if not found."""
    path = _get_path(session_id)
    if not os.path.exists(path):
        return {
            "session_id": session_id,
            "created_at": time.time(),
            "user_profile": {},
            "goal_history": [],
            "plan_history": [],
            "completed_steps": [],
            "preferences": {},
            "artifacts": [],
        }
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save(session_id: str, memory: dict) -> None:
    """Save memory for a session."""
    path = _get_path(session_id)
    memory["updated_at"] = time.time()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2, ensure_ascii=False)


def update_profile(session_id: str, profile_data: dict) -> dict:
    """Update user profile fields."""
    memory = load(session_id)
    memory["user_profile"].update(profile_data)
    save(session_id, memory)
    return memory


def add_goal(session_id: str, goal: str, domain: str) -> dict:
    """Record a new user goal."""
    memory = load(session_id)
    memory["goal_history"].append({
        "goal": goal,
        "domain": domain,
        "timestamp": time.time(),
    })
    save(session_id, memory)
    return memory


def add_plan(session_id: str, plan: dict) -> dict:
    """Record a generated plan."""
    memory = load(session_id)
    memory["plan_history"].append({
        "plan": plan,
        "timestamp": time.time(),
    })
    # Keep last 10 plans only
    if len(memory["plan_history"]) > 10:
        memory["plan_history"] = memory["plan_history"][-10:]
    save(session_id, memory)
    return memory


def add_completed_step(session_id: str, step: str) -> dict:
    """Mark a step as completed."""
    memory = load(session_id)
    memory["completed_steps"].append({
        "step": step,
        "completed_at": time.time(),
    })
    save(session_id, memory)
    return memory


def add_artifact(session_id: str, artifact: dict) -> dict:
    """Persist a generated artifact to the session. Capped at 20 artifacts."""
    memory = load(session_id)
    if "artifacts" not in memory:
        memory["artifacts"] = []
    memory["artifacts"].append(artifact)
    # Cap at 20 artifacts — drop oldest 5 when exceeded
    if len(memory["artifacts"]) > 20:
        memory["artifacts"] = memory["artifacts"][-15:]
    save(session_id, memory)
    return memory


def get_artifacts(session_id: str) -> list:
    """Retrieve all artifacts for a session."""
    memory = load(session_id)
    return memory.get("artifacts", [])


def get_context_summary(session_id: str) -> str:
    """Return a compact summary of user context for LLM prompts."""
    memory = load(session_id)
    profile = memory.get("user_profile", {})
    goals = memory.get("goal_history", [])
    completed = memory.get("completed_steps", [])

    lines = []
    if profile:
        lines.append(f"User Profile: {json.dumps(profile)}")
    if goals:
        recent_goals = goals[-3:]
        lines.append(f"Recent Goals: {[g['goal'] for g in recent_goals]}")
    if completed:
        recent_steps = completed[-5:]
        lines.append(f"Completed Steps: {[s['step'] for s in recent_steps]}")

    return "\n".join(lines) if lines else "New user — no prior context."
