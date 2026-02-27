"""
Tool: cab_safety_advisor
LLM-powered narrative + action advice for cab safety assessment.
Receives pre-computed risk score from cab_risk_scorer and generates:
  - immediate_actions (ordered steps to take right now)
  - emergency_message (ready-to-send WhatsApp/SMS text)
  - safety_card (screenshot-ready structured summary)
  - escalation_steps (police/app complaint path)
  - complaint_draft (formal markdown complaint)
  - helplines (emergency contacts)
"""
import json
import logging
from datetime import datetime
from gemini_client import generate, is_gemini_response_ok

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Hardcoded fallback by severity (if Gemini is unavailable)
# ---------------------------------------------------------------------------

_FALLBACK_BY_LEVEL = {
    "LOW": {
        "immediate_actions": [
            "Share your live location with a trusted contact via WhatsApp.",
            "Keep your phone charged and volume on.",
            "Note the driver's name and vehicle plate from the app.",
            "Stay alert — trust your instincts if anything feels off.",
        ],
        "emergency_message": (
            "Hi, I'm currently in a cab. Ride details below. Please check in on me.\n"
            "If I don't respond in 20 minutes, please call Police: 100 or Women Helpline: 1091."
        ),
        "safety_card": {
            "ride_details": "See booking app for driver + vehicle details",
            "route": "As booked",
            "time": datetime.now().strftime("%I:%M %p"),
            "risk_level": "LOW",
            "key_concern": "Standard precaution — stay alert",
            "check_in_instruction": "If no reply in 20 mins, call Police: 100",
        },
        "escalation_steps": [
            {"step": 1, "action": "Share location with trusted contact", "authority": "Trusted contact", "timeline": "Now"},
            {"step": 2, "action": "Call Ola/Uber helpline if driver behaviour changes", "authority": "Ola: 1800-xxx / Uber: 1800-xxx", "timeline": "If needed"},
            {"step": 3, "action": "Dial 100 in an emergency", "authority": "Police", "timeline": "Emergency"},
        ],
        "complaint_draft": (
            "# Cab Safety Report\n\n"
            "**Date/Time:** " + datetime.now().strftime("%d %B %Y, %I:%M %p") + "\n\n"
            "**Concern:** General safety precaution raised during cab ride.\n\n"
            "No immediate incident occurred. This report is for record purposes.\n"
        ),
        "helplines": [
            {"name": "Police Emergency", "number": "100", "purpose": "Immediate police assistance"},
            {"name": "Women's Helpline", "number": "1091", "purpose": "Women in distress"},
            {"name": "Emergency Services", "number": "112", "purpose": "All emergency services"},
        ],
    },
    "MODERATE": {
        "immediate_actions": [
            "Immediately share your live location with 2-3 trusted contacts via WhatsApp.",
            "Call a contact and keep the line open — let the driver know you're on a call.",
            "Note the exact cab details (driver name, vehicle plate, cab colour).",
            "Use the SOS button in your Ola/Uber app.",
            "Stay in well-lit, populated areas if the ride stops unexpectedly.",
        ],
        "emergency_message": (
            "🚨 I need someone to track me. I am in a cab and something feels off.\n"
            "Please call me every 10 minutes. If I don't pick up, call Police 100 immediately.\n"
            "I will send cab details shortly."
        ),
        "safety_card": {
            "ride_details": "Check booking app for driver and vehicle details",
            "route": "As booked — monitor for deviations",
            "time": datetime.now().strftime("%I:%M %p"),
            "risk_level": "MODERATE",
            "key_concern": "Situation warrants active monitoring",
            "check_in_instruction": "If no reply in 10 mins, call Police: 100",
        },
        "escalation_steps": [
            {"step": 1, "action": "Share live location immediately", "authority": "Trusted contacts", "timeline": "Now"},
            {"step": 2, "action": "Keep a phone call active", "authority": "Friend/family", "timeline": "Now"},
            {"step": 3, "action": "Use SOS in cab app", "authority": "Ola/Uber emergency", "timeline": "If needed"},
            {"step": 4, "action": "Dial 112 or 100", "authority": "Police", "timeline": "If unsafe"},
        ],
        "complaint_draft": (
            "# Cab Safety Complaint\n\n"
            "**Date/Time:** " + datetime.now().strftime("%d %B %Y, %I:%M %p") + "\n\n"
            "**Concern Level:** MODERATE\n\n"
            "I am writing to report concerning behaviour during a cab ride.\n"
            "Please investigate this ride and take appropriate action.\n"
        ),
        "helplines": [
            {"name": "Police Emergency", "number": "100", "purpose": "Immediate police assistance"},
            {"name": "Women's Helpline", "number": "1091", "purpose": "Women in distress"},
            {"name": "Emergency Services", "number": "112", "purpose": "All emergency services"},
            {"name": "Cybercrime Helpline", "number": "1930", "purpose": "For digital threats or tracking"},
        ],
    },
    "HIGH": {
        "immediate_actions": [
            "🚨 CALL 112 NOW or ask someone nearby to help.",
            "Do NOT show fear — speak loudly and firmly: 'I have shared my location. Police are aware.'",
            "Use the Emergency SOS in your Ola/Uber app immediately.",
            "If the vehicle slows down: unlock doors, prepare to exit safely.",
            "Do NOT hand over your phone or bag.",
        ],
        "emergency_message": (
            "🚨 URGENT — I am in danger in a cab. Please call Police 100 NOW if I don't reply in 5 minutes.\n"
            "I will send ride details. Call 112 if you cannot reach me."
        ),
        "safety_card": {
            "ride_details": "Get from booking app immediately",
            "route": "DEVIATION LIKELY — monitor",
            "time": datetime.now().strftime("%I:%M %p"),
            "risk_level": "HIGH",
            "key_concern": "Multiple high-risk indicators present",
            "check_in_instruction": "If no reply in 5 mins — CALL POLICE: 100",
        },
        "escalation_steps": [
            {"step": 1, "action": "Call 112 immediately", "authority": "Emergency services", "timeline": "NOW"},
            {"step": 2, "action": "Use SOS in cab booking app", "authority": "Ola/Uber", "timeline": "NOW"},
            {"step": 3, "action": "Alert people nearby if vehicle stops", "authority": "Public", "timeline": "If vehicle stops"},
            {"step": 4, "action": "File FIR at nearest police station after reaching safety", "authority": "Police station", "timeline": "After reaching safety"},
        ],
        "complaint_draft": (
            "# HIGH RISK — Cab Safety Incident Report\n\n"
            "**Date/Time:** " + datetime.now().strftime("%d %B %Y, %I:%M %p") + "\n\n"
            "**Risk Level:** HIGH\n\n"
            "This is an urgent complaint regarding unsafe cab ride conditions.\n"
            "Multiple high-risk behavioural indicators were present.\n"
            "Immediate investigation and action required.\n"
        ),
        "helplines": [
            {"name": "Emergency Services", "number": "112", "purpose": "ALL emergencies — call first"},
            {"name": "Police Emergency", "number": "100", "purpose": "Police"},
            {"name": "Women's Helpline", "number": "1091", "purpose": "Women in distress"},
            {"name": "iSafe App", "number": "Available on Play Store", "purpose": "Safety tracking app"},
        ],
    },
    "CRITICAL": {
        "immediate_actions": [
            "🚨 CALL 112 RIGHT NOW. Do not wait.",
            "Scream for help if anyone is nearby.",
            "Unlock doors at the next traffic stop — exit if safe.",
            "Break a window only as last resort.",
            "Keep fighting — do not comply with demands.",
        ],
        "emergency_message": (
            "🚨🚨 EMERGENCY. I am in a dangerous cab. CALL POLICE 100 / 112 NOW.\n"
            "Do not wait for my reply. Send police to trace this number immediately."
        ),
        "safety_card": {
            "ride_details": "Report to police via call tracking",
            "route": "UNKNOWN — possible deviation",
            "time": datetime.now().strftime("%I:%M %p"),
            "risk_level": "CRITICAL",
            "key_concern": "IMMEDIATE DANGER — act now",
            "check_in_instruction": "CALL 112 NOW — do not wait",
        },
        "escalation_steps": [
            {"step": 1, "action": "CALL 112 IMMEDIATELY", "authority": "Emergency services", "timeline": "THIS SECOND"},
            {"step": 2, "action": "Scream, make noise, attract attention", "authority": "Public", "timeline": "NOW"},
            {"step": 3, "action": "Exit at next traffic stop if safe", "authority": "Self", "timeline": "Next opportunity"},
            {"step": 4, "action": "File FIR with full evidence", "authority": "Police station", "timeline": "After safety"},
        ],
        "complaint_draft": (
            "# CRITICAL — Emergency Cab Safety Incident\n\n"
            "**Date/Time:** " + datetime.now().strftime("%d %B %Y, %I:%M %p") + "\n\n"
            "**Risk Level:** CRITICAL — IMMEDIATE DANGER REPORTED\n\n"
            "This complaint requires URGENT police attention.\n"
            "Suspect cab driver showed multiple critical danger indicators.\n"
            "Applicable sections: IPC 354 (Assault/criminal force to woman), IPC 366 (Kidnapping), IT Act Section 67.\n"
        ),
        "helplines": [
            {"name": "Emergency Services", "number": "112", "purpose": "CALL FIRST — ALL emergencies"},
            {"name": "Police Emergency", "number": "100", "purpose": "Police control room"},
            {"name": "Women's Helpline", "number": "1091", "purpose": "Women's emergency line"},
            {"name": "Nirbhaya Fund Helpline", "number": "181", "purpose": "Women in danger"},
        ],
    },
}


def _build_prompt(
    risk_result: dict,
    driver_name: str,
    vehicle_plate: str,
    pickup: str,
    destination: str,
    time_of_day: str,
    area_type: str,
    behaviour_flags: list,
) -> str:
    level = risk_result.get("level", "MODERATE")
    score = risk_result.get("score", 50)
    factors = risk_result.get("triggered_factors", [])
    now = datetime.now().strftime("%d %B %Y, %I:%M %p")

    flags_text = ", ".join(behaviour_flags) if behaviour_flags else "none"
    factors_text = "\n".join(f"  - {f}" for f in factors) if factors else "  - None"

    driver_info = f"{driver_name} / {vehicle_plate}" if (driver_name or vehicle_plate) else "Unknown (not provided)"
    route = f"{pickup} → {destination}" if (pickup or destination) else "Not specified"

    return f"""You are SHE-ORACLE's Cab Safety Intelligence Engine — an expert in women's safety, Indian law enforcement, and emergency response for transport incidents in India.

A woman is using this tool to assess her safety in a cab ride RIGHT NOW or before boarding.

SITUATION:
- Risk Score: {score}/100 — Severity: {level}
- Driver/Vehicle: {driver_info}
- Route: {route}
- Time: {now} ({time_of_day.replace("_", " ")} ride)
- Area type: {area_type}
- Behaviour flags raised: {flags_text}

TRIGGERED RISK FACTORS:
{factors_text}

TASK: Generate an immediate safety response in valid JSON format. This is NOT advisory — it is an urgent safety tool. Be direct, specific, and action-focused. Use Indian context (Ola/Uber SOS, 112/100/1091, IPC sections).

Return ONLY valid JSON with no markdown fences:
{{
  "immediate_actions": [
    "Step 1: ...",
    "Step 2: ...",
    "Step 3: ..."
  ],
  "emergency_message": "The exact ready-to-send WhatsApp/SMS text the user should copy right now. Include cab details placeholders if unknown. End with: 'If no reply in X minutes call Police 100.'",
  "safety_card": {{
    "ride_details": "Cab: {vehicle_plate} | Driver: {driver_name}",
    "route": "{route}",
    "time": "{now}",
    "risk_level": "{level}",
    "key_concern": "Single most important risk in plain English",
    "check_in_instruction": "If no reply in X mins, [what to do]"
  }},
  "escalation_steps": [
    {{"step": 1, "action": "...", "authority": "...", "timeline": "..."}},
    {{"step": 2, "action": "...", "authority": "...", "timeline": "..."}}
  ],
  "complaint_draft": "Full markdown complaint letter for filing with Ola/Uber/Police. Include: incident description, risk factors, requested action, applicable IPC/IT Act sections if relevant.",
  "helplines": [
    {{"name": "...", "number": "...", "purpose": "..."}}
  ]
}}

Guidelines:
- immediate_actions: 3-5 steps, ordered by urgency. Be specific (e.g. "Open WhatsApp, tap [contact name]" not "call someone")
- emergency_message: Must be copy-paste ready. Max 3 sentences. Include check-in instruction.
- escalation_steps: 3-5 steps from immediate to formal complaint. Include police, app helpline, NCW/NHRC if warranted.
- complaint_draft: Formal, includes date/time, driver details, risk factors, requested action. Cite IPC 354 (molestation/force), IPC 366 (abduction) or IT Act 66C/66E as appropriate.
- helplines: Always include 112, 100, 1091. Add Ola/Uber helpline, iGoSafe or Nirbhaya scheme helpline for HIGH/CRITICAL.
- For CRITICAL/HIGH: tone must be urgent, directive, no softening language."""


def generate_cab_safety_response(
    risk_result: dict,
    driver_name: str,
    vehicle_plate: str,
    pickup: str,
    destination: str,
    time_of_day: str,
    area_type: str,
    behaviour_flags: list,
) -> dict:
    """
    Generate LLM-powered safety response for a cab situation.

    Args:
        risk_result: Output from score_cab_risk()
        driver_name, vehicle_plate, pickup, destination: Ride details
        time_of_day: "day"|"evening"|"night"|"late_night"
        area_type: "urban"|"suburban"|"rural"|"highway"
        behaviour_flags: List of flag IDs

    Returns:
        dict with immediate_actions, emergency_message, safety_card,
        escalation_steps, complaint_draft, helplines
    """
    level = risk_result.get("level", "MODERATE")

    prompt = _build_prompt(
        risk_result=risk_result,
        driver_name=driver_name,
        vehicle_plate=vehicle_plate,
        pickup=pickup,
        destination=destination,
        time_of_day=time_of_day,
        area_type=area_type,
        behaviour_flags=behaviour_flags,
    )

    try:
        text = generate(prompt)
        if not is_gemini_response_ok(text):
            logger.warning("Gemini response not OK — using fallback for level=%s", level)
            return _FALLBACK_BY_LEVEL.get(level, _FALLBACK_BY_LEVEL["MODERATE"])

        text = text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])
        text = text.strip()

        result = json.loads(text)

        # Ensure required keys are present, fill from fallback if missing
        fallback = _FALLBACK_BY_LEVEL.get(level, _FALLBACK_BY_LEVEL["MODERATE"])
        for key in ("immediate_actions", "emergency_message", "safety_card",
                    "escalation_steps", "complaint_draft", "helplines"):
            if key not in result or not result[key]:
                result[key] = fallback[key]

        return result

    except Exception as e:
        logger.warning("Cab safety LLM call failed (%s) — using fallback for level=%s", e, level)
        return _FALLBACK_BY_LEVEL.get(level, _FALLBACK_BY_LEVEL["MODERATE"])
