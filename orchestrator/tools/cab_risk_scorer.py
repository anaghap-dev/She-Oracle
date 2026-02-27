"""
Tool: cab_risk_scorer
Deterministic weighted risk scorer for cab safety assessment.
No LLM dependency — pure rule engine for consistent, instant scoring.

Score range: 0-100
Severity levels: LOW (0-25) | MODERATE (26-50) | HIGH (51-75) | CRITICAL (76-100)
"""

# ---------------------------------------------------------------------------
# Weight tables
# ---------------------------------------------------------------------------

_TIME_WEIGHTS = {
    "day":        0,
    "evening":    8,
    "night":      15,
    "late_night": 20,
}

_AREA_WEIGHTS = {
    "urban":     0,
    "suburban":  5,
    "rural":     10,
    "highway":   15,
}

# Behaviour flag IDs → score contribution
FLAG_WEIGHTS = {
    "route_deviation":    20,
    "doors_locked":       15,
    "cancel_app":         15,
    "aggressive":         15,
    "personal_questions": 10,
    "phone_distracted":    5,
    "speeding":            5,
    "uncomfortable":       3,
}

# Human-readable labels for triggered factors
FLAG_LABELS = {
    "route_deviation":    "Driver taking wrong/unfamiliar route",
    "doors_locked":       "Doors locked / central locking activated",
    "cancel_app":         "Driver asked to cancel app or go offline",
    "aggressive":         "Driver aggressive or intoxicated",
    "personal_questions": "Driver asking personal questions",
    "phone_distracted":   "Driver distracted / on phone",
    "speeding":           "Driving erratically / speeding",
    "uncomfortable":      "General discomfort / gut feeling",
}

_TIME_LABELS = {
    "day":        "Daytime ride (low baseline risk)",
    "evening":    "Evening ride (moderate baseline risk)",
    "night":      "Night ride (elevated baseline risk)",
    "late_night": "Late-night ride (high baseline risk)",
}

_AREA_LABELS = {
    "urban":    None,          # 0 pts — not shown in breakdown
    "suburban": "Suburban area (limited escape routes)",
    "rural":    "Rural area (isolated, far from help)",
    "highway":  "Highway (high-speed, difficult to exit)",
}


# ---------------------------------------------------------------------------
# Safe exit lookup (deterministic by area_type × level)
# ---------------------------------------------------------------------------

_SAFE_EXIT_SPOTS = {
    "urban": [
        "Petrol station or CNG pump (24-hr staff, CCTV, lit)",
        "Hospital gate or emergency entrance",
        "Police chowki or PCR van stop",
        "Shopping mall or metro station entrance",
        "Busy restaurant or dhaba with visible customers",
    ],
    "suburban": [
        "Petrol station on the main road",
        "Pharmacy (open late, lit, has staff)",
        "Auto stand or local taxi rank (other drivers present)",
        "Bank ATM with security guard",
        "Colony gate with guard post",
    ],
    "rural": [
        "Government health centre (PHC) — has staff on duty",
        "Bus stand or truck stop (other people present)",
        "Any pucca shop with visible activity",
        "School or government building gate",
        "Group of people on the roadside — board any vehicle",
    ],
    "highway": [
        "Highway toll booth (CCTV, 24-hr staff, police patrol)",
        "Dhaba / highway restaurant with trucks parked outside",
        "CNG / petrol pump with attendants",
        "Any service area or rest stop on expressway",
        "Toll plaza emergency lane — wave down highway patrol",
    ],
}

_SAFE_EXIT_AVOID = {
    "urban":    "Avoid dark lanes, construction sites, or isolated parking lots.",
    "suburban": "Avoid empty plots, unlit roads, or areas with no street lights.",
    "rural":    "Avoid forested stretches, open fields, or any area with no buildings.",
    "highway":  "Never exit on the highway carriageway itself — only at lit rest areas or toll plazas.",
}

_SAFE_EXIT_TIMING = {
    "LOW":      "When convenient — no immediate need to exit.",
    "MODERATE": "At the next well-lit stop or traffic signal with activity.",
    "HIGH":     "At the very next opportunity — petrol pump, traffic signal, or crowded area.",
    "CRITICAL": "Exit at the next traffic light or any stop where people are present. Do not wait.",
}


def _build_safe_exit(area_type: str, level: str) -> dict:
    """Build a context-aware safe exit recommendation block."""
    spots = _SAFE_EXIT_SPOTS.get(area_type, _SAFE_EXIT_SPOTS["urban"])
    avoid = _SAFE_EXIT_AVOID.get(area_type, "")
    timing = _SAFE_EXIT_TIMING.get(level, _SAFE_EXIT_TIMING["MODERATE"])

    return {
        "recommended_spots": spots,
        "avoid_note": avoid,
        "timing_advice": timing,
        "exit_signal": (
            "At a traffic stop: unlock door, step out, walk toward lit area. "
            "Do not run — walk firmly toward people."
        ),
    }


def _severity_level(score: int) -> str:
    if score <= 25:
        return "LOW"
    elif score <= 50:
        return "MODERATE"
    elif score <= 75:
        return "HIGH"
    else:
        return "CRITICAL"


def score_cab_risk(
    driver_name: str,
    vehicle_plate: str,
    time_of_day: str,
    area_type: str,
    behaviour_flags: list,
) -> dict:
    """
    Compute a deterministic 0-100 risk score for a cab ride.

    Args:
        driver_name:     Driver name from booking (empty = unknown)
        vehicle_plate:   Vehicle registration plate (empty = unknown)
        time_of_day:     "day" | "evening" | "night" | "late_night"
        area_type:       "urban" | "suburban" | "rural" | "highway"
        behaviour_flags: List of flag IDs from FLAG_WEIGHTS keys

    Returns:
        dict with score, level, triggered_factors, weight_breakdown
    """
    weight_breakdown = {}
    triggered_factors = []

    # --- Time of day ---
    time_pts = _TIME_WEIGHTS.get(time_of_day, 0)
    if time_pts > 0:
        weight_breakdown["time_of_day"] = time_pts
        triggered_factors.append(_TIME_LABELS.get(time_of_day, ""))

    # --- Area type ---
    area_pts = _AREA_WEIGHTS.get(area_type, 0)
    if area_pts > 0:
        weight_breakdown["area_type"] = area_pts
        label = _AREA_LABELS.get(area_type)
        if label:
            triggered_factors.append(label)

    # --- Driver info missing ---
    missing_pts = 0
    name_missing = not driver_name.strip()
    plate_missing = not vehicle_plate.strip()
    if name_missing and plate_missing:
        missing_pts = 10
        triggered_factors.append("Driver name and plate number unknown (cannot report)")
    elif name_missing or plate_missing:
        missing_pts = 5
        triggered_factors.append("Driver name or plate number unknown (partial info)")
    if missing_pts > 0:
        weight_breakdown["missing_driver_info"] = missing_pts

    # --- Behaviour flags ---
    for flag in behaviour_flags:
        pts = FLAG_WEIGHTS.get(flag, 0)
        if pts > 0:
            weight_breakdown[flag] = pts
            triggered_factors.append(FLAG_LABELS.get(flag, flag))

    # --- Total score (capped at 100) ---
    raw_score = time_pts + area_pts + missing_pts + sum(
        FLAG_WEIGHTS.get(f, 0) for f in behaviour_flags
    )
    score = min(100, raw_score)
    level = _severity_level(score)

    safe_exit = _build_safe_exit(area_type, level)

    return {
        "score": score,
        "level": level,
        "triggered_factors": [f for f in triggered_factors if f],
        "weight_breakdown": weight_breakdown,
        "safe_exit_strategy": safe_exit,
    }
