"""
Shared Pydantic models for SHE-ORACLE multi-agent system.
All new agent modules import from here.
"""

from pydantic import BaseModel, Field
from pydantic import ConfigDict
from typing import Optional, List, Dict, Any
import time
import uuid


class IntentProfile(BaseModel):
    model_config = ConfigDict(frozen=False)

    plan_type: str           # advisory|legal_action|financial_analysis|document_generation|threat_response
    urgency: str             # low|medium|high|critical
    sub_intents: List[str]   # e.g. ["identify_skill_gaps", "generate_resume_draft"]
    required_agents: List[str]  # e.g. ["resume_analyzer", "income_projection"]
    required_artifacts: List[str]  # e.g. ["skill_gap_report", "resume_draft"]
    domain: str
    raw_goal: str


class SubTask(BaseModel):
    model_config = ConfigDict(frozen=False)

    id: int
    description: str
    agent_type: str          # maps to TOOL_REGISTRY key or "artifact_generator"
    input_data: Dict[str, Any] = Field(default_factory=dict)
    expected_artifact_type: Optional[str] = None  # None if no artifact produced
    status: str = "pending"  # pending|active|complete|failed


class ExecutionPlan(BaseModel):
    model_config = ConfigDict(frozen=False)

    session_id: str
    intent: IntentProfile
    subtasks: List[SubTask]
    created_at: float = Field(default_factory=time.time)


class Artifact(BaseModel):
    model_config = ConfigDict(frozen=False)

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str   # fir_draft|complaint_letter|escalation_plan|skill_gap_report|
                # resume_draft|projection_report|scheme_checklist|
                # scholarship_list|rights_summary|takedown_request|legal_notice|scheme_match_report|enrollment_checklist
    title: str
    domain: str  # career|legal|financial|grants|education|protection
    content: str  # Full markdown or plain text content
    format: str = "markdown"   # markdown|text|structured
    created_at: float = Field(default_factory=time.time)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EnrichedPlan(BaseModel):
    """The final plan dict augmented with artifacts and intent data."""
    goal: str
    domain: str
    executive_summary: str
    situation_analysis: str
    subgoals: List[Dict]
    immediate_actions: List[Dict]
    roadmap: List[Dict]
    key_resources: List[Dict]
    risk_mitigation: List[Dict]
    success_metrics: List[str]
    tool_insights: Dict
    # New fields
    intent: Optional[Dict] = None
    artifacts: List[Dict] = Field(default_factory=list)
