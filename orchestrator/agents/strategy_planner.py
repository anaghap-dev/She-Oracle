"""
Strategy Planner Agent.

Takes an IntentProfile and decomposes it into an ordered ExecutionPlan of SubTasks.
Phase 1 subtasks are tool-calling (map to TOOL_REGISTRY keys in planner.py).
Phase 2 subtasks are artifact generators (run after synthesis, agent_type="artifact_generator").

The planner.py ReAct loop receives the subtask list as soft guidance injected into
the system prompt — the LLM still decides freely what to call.
"""
import time
from models.schemas import IntentProfile, SubTask, ExecutionPlan


def build_execution_plan(
    intent: IntentProfile,
    session_id: str,
    inferred_context: dict,
) -> ExecutionPlan:
    """
    Decompose an IntentProfile into an ordered list of SubTasks.

    Args:
        intent: The IntentProfile from intent_analyzer.analyze_intent()
        session_id: Current session ID
        inferred_context: The merged extra_context dict from planner (after _analyze_goal)

    Returns:
        ExecutionPlan with tool subtasks first, artifact subtasks last
    """
    subtasks = []
    task_id = 1

    # Phase 1: Tool-calling subtasks (run inside existing ReAct loop)
    for agent_name in intent.required_agents:
        input_data = _build_tool_input(agent_name, intent, inferred_context)
        subtasks.append(SubTask(
            id=task_id,
            description=_tool_description(agent_name),
            agent_type=agent_name,
            input_data=input_data,
            expected_artifact_type=None,
            status="pending",
        ))
        task_id += 1

    # Phase 2: Artifact generation subtasks (run after synthesis)
    for artifact_type in intent.required_artifacts:
        subtasks.append(SubTask(
            id=task_id,
            description=f"Generate {artifact_type.replace('_', ' ')} document",
            agent_type="artifact_generator",
            input_data={"artifact_type": artifact_type, "domain": intent.domain},
            expected_artifact_type=artifact_type,
            status="pending",
        ))
        task_id += 1

    return ExecutionPlan(
        session_id=session_id,
        intent=intent,
        subtasks=subtasks,
        created_at=time.time(),
    )


def _tool_description(agent_name: str) -> str:
    descriptions = {
        "resume_analyzer":       "Analyze resume and identify skill gaps vs target role",
        "legal_rights_checker":  "Retrieve applicable labor laws and map violations",
        "grant_finder":          "Search government schemes and grants matching your profile",
        "income_projection":     "Project income growth over 6, 12, and 24 months",
        "risk_assessment":       "Assess risks and build mitigation strategy for your plan",
    }
    return descriptions.get(agent_name, f"Run {agent_name.replace('_', ' ')}")


def _build_tool_input(agent_name: str, intent: IntentProfile, ctx: dict) -> dict:
    """Build tool-specific input_data from intent and inferred context."""
    base = {
        "goal": intent.raw_goal,
        "domain": intent.domain,
    }

    if agent_name == "resume_analyzer":
        base["resume_text"] = ctx.get("resume_text", intent.raw_goal)
        base["target_role"] = ctx.get("target_role", "")
        base["location"] = ctx.get("location", "India")

    elif agent_name == "legal_rights_checker":
        base["situation"] = intent.raw_goal
        base["situation_type"] = ctx.get("situation_type", "workplace")

    elif agent_name == "income_projection":
        base["current_skills"] = ctx.get("current_skills", intent.raw_goal)
        base["current_income"] = ctx.get("current_income", "0")
        base["target_domain"] = ctx.get("target_domain", intent.domain)
        base["location"] = ctx.get("location", "India")

    elif agent_name == "risk_assessment":
        base["plan"] = intent.raw_goal
        base["plan_type"] = ctx.get("plan_type", intent.domain)
        base["budget"] = ctx.get("budget", "")

    elif agent_name == "grant_finder":
        base["location"] = ctx.get("location", "India")
        base["category"] = intent.domain

    return base


def get_subtask_guidance(execution_plan: ExecutionPlan) -> str:
    """
    Build a guidance string to inject into the ReAct system prompt.
    This nudges the LLM toward the expected tool sequence without forcing it.
    """
    tool_subtasks = [st for st in execution_plan.subtasks if st.agent_type != "artifact_generator"]
    if not tool_subtasks:
        return ""

    lines = ["Recommended tool sequence based on intent analysis:"]
    for i, st in enumerate(tool_subtasks):
        lines.append(f"  {i + 1}. {st.description} (tool: {st.agent_type})")
    lines.append("You may call tools in a different order if your reasoning justifies it.")
    return "\n".join(lines)
