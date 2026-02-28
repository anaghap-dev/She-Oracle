# SHE-ORACLE — API Reference

Base URL (production): `https://she-oracle-backend.onrender.com`

---

## Health

### `GET /api/health`
Check backend and orchestrator status.

**Response**
```json
{
  "backend": "ok",
  "orchestrator": {
    "status": "ok",
    "knowledge_chunks": 51,
    "ai": { "healthy": true, "last_failure": null, "fallback_mode": false }
  }
}
```

---

## Agent

### `POST /api/agent/stream`
Stream agent responses via Server-Sent Events (SSE).

**Request Body**
```json
{
  "goal": "I want to find scholarships for women in engineering",
  "domain": "education",
  "session_id": "optional-uuid",
  "extra_context": {}
}
```

**SSE Event Types**
| Type | Description |
|---|---|
| `session` | Session ID assigned |
| `thinking` | Agent reasoning step |
| `tool_call` | Tool being invoked |
| `observation` | Tool result |
| `result` | Final plan object |
| `error` | Error message |
| `done` | Stream complete |

**Domains:** `career` · `legal` · `financial` · `education` · `grants` · `general`

---

### `POST /api/agent/run`
Non-streaming version — returns complete plan in one response.

**Request Body** — same as `/stream`

**Response**
```json
{
  "session_id": "uuid",
  "plan": { ... },
  "events": [ ... ]
}
```

---

## Session Memory

### `GET /api/session/:session_id`
Retrieve session memory and past interactions.

### `POST /api/session/profile`
Update user profile in session.

**Request Body**
```json
{
  "session_id": "uuid",
  "profile_data": { "name": "...", "location": "...", "goal": "..." }
}
```

### `POST /api/session/step-complete`
Mark a plan step as completed.

**Request Body**
```json
{
  "session_id": "uuid",
  "step": "Apply to XYZ scholarship"
}
```

---

## Protection Intelligence

### `POST /api/protection/analyze-threat`
Analyze digital harassment evidence.

**Request Body**
```json
{
  "evidence_text": "Screenshot text / message content describing the incident",
  "context": "optional additional context"
}
```

**Response** — Threat classification, severity score (1–10), legal sections, escalation steps.

---

### `POST /api/protection/generate-documents`
Generate legal documents (FIR draft, complaint letter, takedown request).

**Request Body**
```json
{
  "victim_name": "Jane Doe",
  "incident_description": "...",
  "evidence_summary": "...",
  "threat_analysis": { ... },
  "contact_info": "optional"
}
```

---

### `POST /api/protection/cab-safety`
Real-time cab ride risk assessment.

**Request Body**
```json
{
  "driver_name": "optional",
  "vehicle_plate": "optional",
  "pickup": "MG Road, Bangalore",
  "destination": "Whitefield, Bangalore",
  "time_of_day": "night",
  "area_type": "urban",
  "behaviour_flags": ["route_deviation", "phone_usage"]
}
```

**`time_of_day` values:** `day` · `evening` · `night` · `late_night`
**`area_type` values:** `urban` · `suburban` · `rural` · `highway`

**Response** — Risk score, safety card, emergency message template, helplines.

---

## Artifacts

### `GET /api/agent/artifacts/:session_id`
Retrieve all generated documents/artifacts for a session.

### `POST /api/agent/download-artifact`
Download a specific artifact as a file.

**Request Body**
```json
{
  "artifact_id": "uuid",
  "session_id": "uuid",
  "filename": "optional-filename.md"
}
```
