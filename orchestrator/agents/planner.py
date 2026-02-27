"""
Strategic Planner Agent — True ReAct (Reasoning + Acting) loop.

The LLM drives every decision: which tools to call, in what order, and when
to stop gathering data and synthesize the final plan.  This is genuine ReAct,
not a scripted pipeline.

Loop:
  1. Load memory + RAG context.
  2. LLM THINKS: given the goal and what we know so far, what is the best next
     action? It returns a structured JSON decision.
  3. If the decision is CALL_TOOL, we invoke that tool, feed the result back to
     the LLM as an observation, and repeat.
  4. If the decision is SYNTHESIZE, we have enough data to build the plan.
  5. The critic evaluates the plan; on failure we replan with feedback.
"""
import json
import asyncio
import re
from typing import AsyncGenerator
from gemini_client import generate, is_gemini_response_ok
from fallback_responses import get_fallback_plan

from agents import retriever, memory as mem_agent, critic as critic_agent
from agents.intent_analyzer import analyze_intent
from agents.strategy_planner import build_execution_plan, get_subtask_guidance
from tools.grant_finder import grant_finder
from tools.legal_rights_checker import legal_rights_checker
from tools.resume_analyzer import resume_analyzer
from tools.income_projection import income_projection
from tools.risk_assessment import risk_assessment
from tools.career_artifact_generator import generate_career_artifacts
from tools.legal_artifact_generator import generate_legal_artifacts
from tools.financial_artifact_generator import generate_financial_artifacts
from tools.grant_artifact_generator import generate_grant_artifacts
from tools.education_artifact_generator import generate_education_artifacts

MAX_REACT_STEPS = 8          # Safety cap — prevents infinite loops
MAX_REPLAN_ATTEMPTS = 2

# ---------------------------------------------------------------------------
# Artifact generator dispatch — domain -> generator function
# protection uses existing /generate-documents endpoint, not this path
# ---------------------------------------------------------------------------
_ARTIFACT_GENERATORS = {
    "career":    generate_career_artifacts,
    "legal":     generate_legal_artifacts,
    "financial": generate_financial_artifacts,
    "grants":    generate_grant_artifacts,
    "education": generate_education_artifacts,
}

# ---------------------------------------------------------------------------
# Tool registry — the LLM sees these descriptions to decide what to call
# ---------------------------------------------------------------------------
TOOL_REGISTRY = {
    "grant_finder": {
        "description": (
            "Searches government grants, schemes, and funding programs available for women "
            "in India. Returns matching schemes with eligibility criteria, amounts, and "
            "application links. Use when the goal involves funding, loans, subsidies, "
            "startup capital, or government welfare programs."
        ),
    },
    "legal_rights_checker": {
        "description": (
            "Looks up Indian labor laws, workplace rights, legal protections, and remedies "
            "available to women. Returns violated rights, legal provisions, escalation steps, "
            "and protection mechanisms. Use when the goal involves workplace issues, "
            "harassment, legal disputes, or rights violations."
        ),
    },
    "resume_analyzer": {
        "description": (
            "Analyzes a career profile, identifies skill gaps, and recommends upskilling "
            "paths and job targets. Returns gap analysis, certifications to pursue, salary "
            "benchmarks, and target job titles. Use when the goal involves career growth, "
            "job switching, skill development, or professional advancement."
        ),
    },
    "income_projection": {
        "description": (
            "Projects realistic income growth over 6, 12, and 24 months based on current "
            "skills, domain, and location. Returns income forecasts by skill path with "
            "actionable steps. Use when the goal involves financial planning, income growth, "
            "salary negotiation, or understanding earning potential."
        ),
    },
    "risk_assessment": {
        "description": (
            "Builds a risk matrix for a plan or business idea: financial, legal, market, "
            "and personal risks with specific mitigation strategies. Use when the goal "
            "involves starting a business, making a major career move, or any situation "
            "where failure scenarios need to be mapped."
        ),
    },
}

SYSTEM_PROMPT = """You are SHE-ORACLE — an elite autonomous AI strategist dedicated to empowering women in India.

Your mission: Transform women's goals into structured, legally grounded, and realistically executable strategic plans.

Your persona: Authoritative yet empathetic. Data-driven yet human. You combine the precision of a management consultant, the expertise of a labor lawyer, and the empathy of a mentor.

You operate with RAG-retrieved knowledge of:
- Indian labor laws and women's rights
- Government schemes and grants for women
- Scholarship programs
- Financial independence strategies

You DO NOT give generic advice. You give SPECIFIC, ACTIONABLE, GROUNDED intelligence.

Always structure your plans with:
1. Situation Analysis
2. Goal Decomposition (subgoals)
3. Immediate Actions (this week)
4. 30-60-90 Day Roadmap
5. Resources and Support Systems
6. Risk Mitigation
7. Success Metrics"""


# ---------------------------------------------------------------------------
# Tool execution
# ---------------------------------------------------------------------------

def _call_tool(tool_name: str, goal: str, domain: str, extra: dict = None) -> dict:
    """Dispatch a tool call and return its result dict."""
    extra = extra or {}
    if tool_name == "grant_finder":
        return grant_finder(goal, domain)
    elif tool_name == "legal_rights_checker":
        return legal_rights_checker(goal, extra.get("situation_type", "workplace"))
    elif tool_name == "resume_analyzer":
        return resume_analyzer(
            extra.get("resume_text", goal),
            extra.get("target_role", ""),
            extra.get("location", "India"),
        )
    elif tool_name == "income_projection":
        return income_projection(
            extra.get("current_skills", goal),
            extra.get("current_income", "0"),
            extra.get("target_domain", domain),
            extra.get("location", "India"),
        )
    elif tool_name == "risk_assessment":
        return risk_assessment(goal, extra.get("plan_type", domain), extra.get("budget", ""))
    return {}


# ---------------------------------------------------------------------------
# ReAct decision prompt
# ---------------------------------------------------------------------------

def _build_react_prompt(
    goal: str,
    domain: str,
    context_summary: str,
    rag_context: str,
    tool_results: dict,
    step: int,
    subtask_guidance: str = "",
) -> str:
    tools_desc = "\n".join(
        f"- {name}: {info['description']}"
        for name, info in TOOL_REGISTRY.items()
    )
    already_called = list(tool_results.keys()) or ["none yet"]
    observations = ""
    if tool_results:
        observations = "\n\nOBSERVATIONS FROM TOOLS CALLED SO FAR:\n"
        for tool, result in tool_results.items():
            # Truncate large results to keep the prompt manageable
            result_str = json.dumps(result, indent=2)
            if len(result_str) > 800:
                result_str = result_str[:800] + "\n... (truncated)"
            observations += f"\n[{tool}]:\n{result_str}\n"

    guidance_section = ""
    if subtask_guidance:
        guidance_section = f"\nINTENT-BASED GUIDANCE (soft recommendation — you decide):\n{subtask_guidance}\n"

    return f"""{SYSTEM_PROMPT}

You are in the REASONING phase of a ReAct loop. Your job is to decide the SINGLE BEST next action.

USER GOAL: {goal}
DOMAIN: {domain}
REACT STEP: {step} of {MAX_REACT_STEPS}

USER CONTEXT (memory):
{context_summary}

RETRIEVED KNOWLEDGE BASE:
{rag_context}
{observations}{guidance_section}
AVAILABLE TOOLS:
{tools_desc}

TOOLS ALREADY CALLED: {', '.join(already_called)}

DECISION RULES:
- If you need more data to build a high-quality plan, call a relevant tool.
- Do NOT call a tool that has already been called.
- Once you have enough intelligence (usually 2-4 tools), or you are at step {MAX_REACT_STEPS}, choose SYNTHESIZE.
- Choose SYNTHESIZE if the goal is informational and doesn't need all tools.
- Always explain your reasoning before deciding.

Return ONLY valid JSON — no markdown, no extra text:
{{
  "thought": "Your reasoning: what you know, what is missing, and why you are making this decision",
  "action": "CALL_TOOL or SYNTHESIZE",
  "tool": "tool_name if action is CALL_TOOL, else null",
  "reason": "One sentence explaining why this tool or why synthesizing now"
}}"""


# ---------------------------------------------------------------------------
# Plan synthesis prompt
# ---------------------------------------------------------------------------

def _build_synthesis_prompt(
    goal: str,
    domain: str,
    context_summary: str,
    rag_context: str,
    tool_results: dict,
) -> str:
    tool_results_str = json.dumps(tool_results, indent=2)
    return f"""{SYSTEM_PROMPT}

USER GOAL: {goal}
DOMAIN: {domain}

USER CONTEXT (from memory):
{context_summary}

RETRIEVED KNOWLEDGE BASE:
{rag_context}

TOOL INTELLIGENCE GATHERED:
{tool_results_str}

Now synthesize ALL of the above into a comprehensive, structured strategic plan.

Return ONLY valid JSON:
{{
  "goal": "{goal}",
  "domain": "{domain}",
  "executive_summary": "2-3 sentence overview of the strategy",
  "situation_analysis": "Current situation assessment in 3-4 sentences",
  "subgoals": [
    {{
      "id": 1,
      "subgoal": "Specific subgoal",
      "why": "Why this matters",
      "timeline": "When to achieve this"
    }}
  ],
  "immediate_actions": [
    {{
      "action": "Specific action to take this week",
      "resource": "Tool/link/contact needed",
      "expected_outcome": "What this achieves"
    }}
  ],
  "roadmap": [
    {{
      "phase": "30 Days",
      "focus": "Primary focus",
      "milestones": ["Milestone 1", "Milestone 2"],
      "resources_needed": ["Resource 1"]
    }},
    {{
      "phase": "60 Days",
      "focus": "Primary focus",
      "milestones": ["Milestone 1"],
      "resources_needed": []
    }},
    {{
      "phase": "90 Days",
      "focus": "Primary focus",
      "milestones": ["Milestone 1"],
      "resources_needed": []
    }}
  ],
  "key_resources": [
    {{
      "name": "Resource name",
      "type": "Scheme/Platform/Tool/Contact",
      "url_or_contact": "Link or number",
      "how_it_helps": "Specific benefit"
    }}
  ],
  "risk_mitigation": [
    {{
      "risk": "Risk description",
      "mitigation": "How to handle it"
    }}
  ],
  "success_metrics": [
    "Measurable success indicator"
  ],
  "tool_insights": {tool_results_str}
}}"""


# ---------------------------------------------------------------------------
# JSON extraction helper  (defined before _analyze_goal which calls it)
# ---------------------------------------------------------------------------

def _extract_json(text: str) -> dict:
    """Strip markdown fences and parse JSON. Raises on failure."""
    text = text.strip()
    if text.startswith("```"):
        # Remove opening fence
        text = re.sub(r"^```[a-z]*\n?", "", text)
        # Remove closing fence
        text = re.sub(r"\n?```$", "", text.strip())
    return json.loads(text.strip())


# ---------------------------------------------------------------------------
# Goal analysis — LLM extracts structured context from free-text goal
# ---------------------------------------------------------------------------

def _analyze_goal(goal: str, domain: str, context_summary: str) -> dict:
    """
    Ask the LLM to extract structured context from the user's goal.
    Returns a dict that enriches the `extra` dict for all tool calls.
    Falls back to empty dict on any failure.
    """
    prompt = f"""You are an expert intake analyst for SHE-ORACLE, an AI strategist for women in India.

Analyze the user's goal and extract structured information to help specialist tools serve them better.

USER GOAL: {goal}
DOMAIN: {domain}
PRIOR CONTEXT: {context_summary}

Extract what you can infer. If a field is not mentioned or cannot be reasonably inferred, use null.

Return ONLY valid JSON — no markdown, no extra text:
{{
  "target_role": "The job title or career target mentioned, or null",
  "current_skills": "Comma-separated list of skills mentioned or implied, or the goal itself if unclear",
  "current_income": "Current salary/income mentioned (as string with currency), or '0' if not mentioned",
  "target_domain": "The specific industry or domain (e.g. 'tech', 'healthcare', 'retail', 'agriculture'), or the domain param",
  "location": "City or state mentioned, or 'India' if not specified",
  "situation_type": "One of: workplace, harassment, maternity, equal_pay, termination, startup, general",
  "budget": "Investment budget or capital mentioned, or empty string if not mentioned",
  "resume_text": "A 2-3 sentence career summary inferred from the goal, for resume analysis",
  "plan_type": "One of: career, legal, financial, startup, education, general"
}}"""

    try:
        text = generate(prompt)
        result = _extract_json(text)
        # Ensure required fields have defaults
        result.setdefault("location", "India")
        result.setdefault("current_income", "0")
        result.setdefault("plan_type", domain)
        result.setdefault("target_domain", domain)
        result.setdefault("current_skills", goal)
        result.setdefault("resume_text", goal)
        return result
    except Exception:
        return {
            "location": "India",
            "current_income": "0",
            "plan_type": domain,
            "target_domain": domain,
            "current_skills": goal,
            "resume_text": goal,
        }


# ---------------------------------------------------------------------------
# Main ReAct planning loop
# ---------------------------------------------------------------------------

async def run_plan(
    goal: str,
    domain: str,
    session_id: str,
    extra_context: dict = None,
) -> AsyncGenerator[dict, None]:
    """
    True ReAct planning loop. The LLM drives every tool-selection decision.

    Yields SSE-style event dicts:
        {"type": "thinking",    "content": "..."}
        {"type": "acting",      "content": "...", "tool": "tool_name"}
        {"type": "tool_result", "tool": "...", "data": {...}}
        {"type": "critic",      "content": "...", "scores": {...}}
        {"type": "result",      "plan": {...}}
        {"type": "error",       "content": "..."}
    """
    extra = extra_context or {}

    # ------------------------------------------------------------------
    # PHASE 0: Memory + RAG — gather background context
    # ------------------------------------------------------------------
    yield {"type": "thinking", "content": "Loading session context and prior history..."}
    await asyncio.sleep(0)
    context_summary = mem_agent.get_context_summary(session_id)
    mem_agent.add_goal(session_id, goal, domain)

    yield {"type": "thinking", "content": f"Retrieving relevant knowledge for domain: {domain}..."}
    await asyncio.sleep(0)
    rag_context = retriever.retrieve_formatted(goal, domain, n_results=5)

    # ------------------------------------------------------------------
    # PHASE 0b: Goal Analysis — LLM extracts structured context
    # This enriches every subsequent tool call with precise inputs
    # instead of just passing raw goal text.
    # ------------------------------------------------------------------
    yield {"type": "thinking", "content": "Analysing your goal to extract context for specialist tools..."}
    await asyncio.sleep(0)
    inferred_context = _analyze_goal(goal, domain, context_summary)

    # _analyze_goal already handles Gemini failures internally (returns safe
    # defaults), but if it detected the sentinel it sets a flag we can check.
    # Do a lightweight probe: if the sentinel came back from _analyze_goal's
    # inner generate call the inferred_context will just have defaults — that
    # is fine; we proceed. We only bail to the full fallback path if synthesis
    # also fails (checked below).

    # Merge inferred context with any explicit extra_context (explicit wins)
    merged_extra = {**inferred_context, **extra}

    # Update memory profile with newly inferred context
    profile_update = {
        k: v for k, v in inferred_context.items()
        if k in ("location", "target_role", "target_domain") and v and v != "null"
    }
    if profile_update:
        mem_agent.update_profile(session_id, profile_update)

    # ------------------------------------------------------------------
    # PHASE 0c: Intent Analysis — classify goal type and urgency
    # ------------------------------------------------------------------
    yield {"type": "thinking", "content": "Analyzing intent and classifying goal type..."}
    await asyncio.sleep(0)

    intent_profile = analyze_intent(goal, domain, context_summary)
    yield {
        "type": "intent_analyzed",
        "intent": intent_profile.model_dump(),
    }
    await asyncio.sleep(0)

    # ------------------------------------------------------------------
    # PHASE 0d: Strategy Planning — decompose into ordered subtasks
    # ------------------------------------------------------------------
    yield {"type": "thinking", "content": "Decomposing goal into executable subtasks..."}
    await asyncio.sleep(0)

    execution_plan = build_execution_plan(intent_profile, session_id, merged_extra)
    subtasks_list = [st.model_dump() for st in execution_plan.subtasks]
    subtask_guidance = get_subtask_guidance(execution_plan)

    yield {
        "type": "plan_decomposed",
        "subtasks": subtasks_list,
    }
    await asyncio.sleep(0)

    # ------------------------------------------------------------------
    # PHASE 1: True ReAct loop — LLM decides what to do at each step
    # ------------------------------------------------------------------
    tool_results: dict = {}
    _gemini_failed_in_react = False

    for step in range(1, MAX_REACT_STEPS + 1):
        # THINK: ask the LLM what the best next action is
        react_prompt = _build_react_prompt(
            goal, domain, context_summary, rag_context, tool_results, step,
            subtask_guidance=subtask_guidance,
        )

        yield {"type": "thinking", "content": f"Reasoning about next action (step {step})..."}
        await asyncio.sleep(0)

        try:
            decision_text = generate(react_prompt)
            if not is_gemini_response_ok(decision_text):
                # Gemini is completely down — no point continuing the loop
                _gemini_failed_in_react = True
                yield {"type": "thinking", "content": "AI service is temporarily unavailable. Loading curated guidance from knowledge base..."}
                await asyncio.sleep(0)
                break
            decision = _extract_json(decision_text)
        except Exception as e:
            yield {"type": "thinking", "content": f"Reasoning parse issue at step {step}, continuing to synthesis: {str(e)[:80]}"}
            break

        thought = decision.get("thought", "")
        action = decision.get("action", "SYNTHESIZE").upper()
        tool_name = decision.get("tool")
        reason = decision.get("reason", "")

        # Surface the LLM's reasoning as a thinking event
        if thought:
            yield {"type": "thinking", "content": thought}
            await asyncio.sleep(0)

        if action == "SYNTHESIZE" or not tool_name:
            yield {"type": "thinking", "content": f"Sufficient intelligence gathered. Proceeding to synthesis. ({reason})"}
            await asyncio.sleep(0)
            break

        # ACT: call the chosen tool
        if tool_name not in TOOL_REGISTRY:
            yield {"type": "thinking", "content": f"Unknown tool '{tool_name}' selected, moving to synthesis."}
            break

        if tool_name in tool_results:
            # LLM tried to re-call a tool — just synthesize
            yield {"type": "thinking", "content": f"Tool '{tool_name}' already called, proceeding to synthesis."}
            break

        # Find matching subtask to track its status
        matching_subtask = next(
            (st for st in execution_plan.subtasks
             if st.agent_type == tool_name and st.status == "pending"),
            None,
        )
        if matching_subtask:
            matching_subtask.status = "active"
            yield {
                "type": "subtask_start",
                "subtask_id": matching_subtask.id,
                "description": matching_subtask.description,
            }
            await asyncio.sleep(0)

        yield {
            "type": "acting",
            "content": f"Invoking {tool_name.replace('_', ' ').title()}... ({reason})",
            "tool": tool_name,
        }
        await asyncio.sleep(0)

        try:
            result = _call_tool(tool_name, goal, domain, merged_extra)
            tool_results[tool_name] = result
            yield {"type": "tool_result", "tool": tool_name, "data": result}
        except Exception as e:
            yield {
                "type": "acting",
                "content": f"Tool {tool_name} encountered an issue: {str(e)}",
                "tool": tool_name,
            }
            tool_results[tool_name] = {"error": str(e)}

        if matching_subtask:
            matching_subtask.status = "complete"
            yield {
                "type": "subtask_complete",
                "subtask_id": matching_subtask.id,
                "artifact_type": None,
            }
        await asyncio.sleep(0)

    # ------------------------------------------------------------------
    # PHASE 2: Synthesize plan with Gemini
    # ------------------------------------------------------------------
    yield {"type": "thinking", "content": "Synthesizing strategic plan from all intelligence gathered..."}
    await asyncio.sleep(0)

    # If Gemini already failed in the ReAct loop, skip straight to fallback
    if _gemini_failed_in_react:
        fallback_plan = get_fallback_plan(domain, goal)
        fallback_plan["artifacts"] = []
        fallback_plan["intent"] = intent_profile.model_dump()
        mem_agent.add_plan(session_id, fallback_plan)
        yield {"type": "result", "plan": fallback_plan}
        return

    synthesis_prompt = _build_synthesis_prompt(
        goal, domain, context_summary, rag_context, tool_results
    )

    plan = None
    attempt = 0

    while attempt <= MAX_REPLAN_ATTEMPTS:
        try:
            text = generate(synthesis_prompt)
            if not is_gemini_response_ok(text):
                # Gemini down during synthesis — use curated fallback
                yield {"type": "thinking", "content": "AI synthesis unavailable. Serving curated guidance from knowledge base..."}
                await asyncio.sleep(0)
                fallback_plan = get_fallback_plan(domain, goal)
                fallback_plan["artifacts"] = []
                fallback_plan["intent"] = intent_profile.model_dump()
                mem_agent.add_plan(session_id, fallback_plan)
                yield {"type": "result", "plan": fallback_plan}
                return
            plan = _extract_json(text)
        except Exception as e:
            # JSON parse failed (truncated/malformed response) — use fallback instead of erroring
            logger.warning("[PLANNER] Plan synthesis JSON parse failed (attempt %d): %s", attempt, str(e)[:120])
            if attempt < MAX_REPLAN_ATTEMPTS:
                attempt += 1
                continue
            # All attempts exhausted — serve curated fallback
            yield {"type": "thinking", "content": "Using curated guidance from knowledge base..."}
            await asyncio.sleep(0)
            fallback_plan = get_fallback_plan(domain, goal)
            fallback_plan["artifacts"] = []
            fallback_plan["intent"] = intent_profile.model_dump()
            mem_agent.add_plan(session_id, fallback_plan)
            yield {"type": "result", "plan": fallback_plan}
            return

        # ------------------------------------------------------------------
        # PHASE 3: Critic evaluation
        # ------------------------------------------------------------------
        yield {"type": "thinking", "content": "Running self-critic evaluation on the plan..."}
        await asyncio.sleep(0)

        try:
            critique = critic_agent.evaluate_plan(plan, goal, domain)
            # critic uses generate() internally — it may return a default
            # approval dict if Gemini was down (critic handles this gracefully)
            yield {
                "type": "critic",
                "content": critique.get("verdict_reasoning", ""),
                "scores": critique.get("scores", {}),
                "passed": critique.get("passed", True),
                "verdict": critique.get("verdict", "APPROVED"),
            }
        except Exception:
            critique = {"passed": True}

        if critique.get("passed", True):
            break

        # Replan with critic feedback
        attempt += 1
        if attempt <= MAX_REPLAN_ATTEMPTS:
            hints = critique.get("improvement_hints", [])
            yield {
                "type": "thinking",
                "content": f"Replanning (attempt {attempt}) based on critic feedback: {'; '.join(hints[:2])}",
            }
            await asyncio.sleep(0)
            synthesis_prompt += (
                "\n\nCRITIC FEEDBACK (address these in revision):\n"
                + "\n".join(f"- {h}" for h in hints)
            )

    # ------------------------------------------------------------------
    # PHASE 4: Artifact Generation (after synthesis, before memory save)
    # ------------------------------------------------------------------
    artifacts = []
    if plan:
        artifact_generator = _ARTIFACT_GENERATORS.get(domain)
        if artifact_generator:
            yield {"type": "thinking", "content": f"Generating structured artifacts for {domain} domain..."}
            await asyncio.sleep(0)
            try:
                generated = artifact_generator(plan, tool_results, merged_extra)
                for artifact in generated:
                    artifacts.append(artifact)
                    # Mark matching subtask as complete
                    for st in execution_plan.subtasks:
                        if (st.expected_artifact_type == artifact.get("type")
                                and st.status == "pending"):
                            st.status = "complete"
                            break
                    yield {"type": "artifact_ready", "artifact": artifact}
                    await asyncio.sleep(0)
                    mem_agent.add_artifact(session_id, artifact)
            except Exception as e:
                yield {"type": "thinking", "content": f"Artifact generation issue: {str(e)[:80]}"}

    # ------------------------------------------------------------------
    # PHASE 5: Save enriched plan to memory and return
    # ------------------------------------------------------------------
    if plan:
        plan["artifacts"] = artifacts
        plan["intent"] = intent_profile.model_dump()
        mem_agent.add_plan(session_id, plan)
        yield {"type": "result", "plan": plan}
    else:
        yield {"type": "error", "content": "Failed to generate a valid plan after multiple attempts."}
