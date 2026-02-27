"""
Intent Analyzer Agent.

Takes a raw user goal + domain, asks Gemini to classify into a structured
IntentProfile, then returns the profile for SSE emission and strategy planning.

Runs BEFORE the ReAct loop so the planner can use the intent to guide
which tools to call.
"""
import json
import logging
from gemini_client import generate, is_gemini_response_ok
from models.schemas import IntentProfile

logger = logging.getLogger(__name__)

VALID_PLAN_TYPES = [
    "advisory",
    "legal_action",
    "financial_analysis",
    "document_generation",
    "threat_response",
]

VALID_URGENCY = ["low", "medium", "high", "critical"]

VALID_AGENTS = [
    "resume_analyzer",
    "legal_rights_checker",
    "grant_finder",
    "income_projection",
    "risk_assessment",
]

VALID_ARTIFACT_TYPES = [
    "resume_draft",
    "skill_gap_report",
    "rights_summary",
    "escalation_plan",
    "projection_report",
    "scheme_checklist",
    "scheme_match_report",
    "scholarship_list",
    "enrollment_checklist",
    "fir_draft",
    "complaint_letter",
    "takedown_request",
    "legal_notice",
]

_FALLBACK_INTENTS = {
    "career": {
        "plan_type": "advisory",
        "urgency": "medium",
        "sub_intents": ["analyze career profile", "identify skill gaps", "plan upskilling path"],
        "required_agents": ["resume_analyzer", "income_projection"],
        "required_artifacts": ["skill_gap_report"],
    },
    "legal": {
        "plan_type": "legal_action",
        "urgency": "high",
        "sub_intents": ["identify rights violations", "map applicable laws", "plan escalation"],
        "required_agents": ["legal_rights_checker"],
        "required_artifacts": ["rights_summary", "escalation_plan"],
    },
    "financial": {
        "plan_type": "financial_analysis",
        "urgency": "medium",
        "sub_intents": ["project income growth", "identify government schemes", "build financial plan"],
        "required_agents": ["income_projection", "grant_finder"],
        "required_artifacts": ["projection_report", "scheme_checklist"],
    },
    "grants": {
        "plan_type": "advisory",
        "urgency": "medium",
        "sub_intents": ["find matching schemes", "assess eligibility", "build application checklist"],
        "required_agents": ["grant_finder"],
        "required_artifacts": ["scheme_match_report", "scheme_checklist"],
    },
    "education": {
        "plan_type": "advisory",
        "urgency": "medium",
        "sub_intents": ["find scholarships", "plan enrollment", "identify skill programs"],
        "required_agents": ["grant_finder"],
        "required_artifacts": ["scholarship_list", "enrollment_checklist"],
    },
    "protection": {
        "plan_type": "threat_response",
        "urgency": "critical",
        "sub_intents": ["classify threat", "map legal sections", "generate legal documents"],
        "required_agents": ["legal_rights_checker"],
        "required_artifacts": ["rights_summary", "escalation_plan"],
    },
    "general": {
        "plan_type": "advisory",
        "urgency": "medium",
        "sub_intents": ["understand goal", "identify domain", "build strategic plan"],
        "required_agents": ["grant_finder", "income_projection"],
        "required_artifacts": ["scheme_checklist"],
    },
}


def _build_prompt(goal: str, domain: str, context_summary: str) -> str:
    return f"""You are SHE-ORACLE's Intent Classification Engine for women empowerment in India.

Analyze this user goal and classify it into a structured intent profile.

USER GOAL: {goal}
DOMAIN: {domain}
PRIOR SESSION CONTEXT: {context_summary}

VALID plan_type values (pick exactly one): {VALID_PLAN_TYPES}
VALID urgency values (pick exactly one): {VALID_URGENCY}
VALID required_agents (only pick from this list): {VALID_AGENTS}
VALID required_artifact_types (only pick from this list): {VALID_ARTIFACT_TYPES}

Guidelines:
- urgency=critical for harassment, legal threats, job loss, safety issues
- urgency=high for urgent legal matters, financial distress
- urgency=medium for career planning, business development
- urgency=low for long-term education/skill building
- sub_intents should be 2-4 specific actionable tasks derived from the goal
- required_agents should be 1-3 tools most relevant to the goal
- required_artifacts should match the domain and be 1-3 items

Return ONLY valid JSON with no markdown fences:
{{
  "plan_type": "advisory",
  "urgency": "medium",
  "sub_intents": ["analyze current career skills", "identify in-demand roles", "build upskilling roadmap"],
  "required_agents": ["resume_analyzer", "income_projection"],
  "required_artifacts": ["skill_gap_report", "resume_draft"]
}}"""


def analyze_intent(goal: str, domain: str, context_summary: str) -> IntentProfile:
    """
    Classify user intent. Returns an IntentProfile.
    Falls back to a safe domain-specific default if Gemini fails.

    Args:
        goal: Raw user goal text
        domain: Domain string (career|legal|financial|grants|education|protection|general)
        context_summary: From memory.get_context_summary()

    Returns:
        IntentProfile (Pydantic model, mutable)
    """
    prompt = _build_prompt(goal, domain, context_summary)

    try:
        text = generate(prompt)
        if not is_gemini_response_ok(text):
            return _fallback_intent(goal, domain)

        # Strip markdown fences if present
        text = text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])
        text = text.strip()

        raw = json.loads(text)

        # Sanitize to prevent hallucinated tool/artifact names
        plan_type = raw.get("plan_type", "advisory")
        if plan_type not in VALID_PLAN_TYPES:
            plan_type = "advisory"

        urgency = raw.get("urgency", "medium")
        if urgency not in VALID_URGENCY:
            urgency = "medium"

        valid_agents = [a for a in raw.get("required_agents", []) if a in VALID_AGENTS]
        valid_artifacts = [a for a in raw.get("required_artifacts", []) if a in VALID_ARTIFACT_TYPES]

        # Ensure at least one agent and artifact based on domain if LLM gave empty lists
        if not valid_agents or not valid_artifacts:
            fb = _FALLBACK_INTENTS.get(domain, _FALLBACK_INTENTS["general"])
            if not valid_agents:
                valid_agents = fb["required_agents"]
            if not valid_artifacts:
                valid_artifacts = fb["required_artifacts"]

        return IntentProfile(
            plan_type=plan_type,
            urgency=urgency,
            sub_intents=raw.get("sub_intents", []),
            required_agents=valid_agents,
            required_artifacts=valid_artifacts,
            domain=domain,
            raw_goal=goal,
        )

    except Exception as e:
        logger.warning(f"Intent analysis failed ({e}), using fallback for domain={domain}")
        return _fallback_intent(goal, domain)


def _fallback_intent(goal: str, domain: str) -> IntentProfile:
    """Safe default when Gemini is unavailable."""
    fb = _FALLBACK_INTENTS.get(domain, _FALLBACK_INTENTS["general"])
    return IntentProfile(
        plan_type=fb["plan_type"],
        urgency=fb["urgency"],
        sub_intents=fb["sub_intents"],
        required_agents=fb["required_agents"],
        required_artifacts=fb["required_artifacts"],
        domain=domain,
        raw_goal=goal,
    )
