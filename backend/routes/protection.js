const express = require("express");
const router = express.Router();

const ORCHESTRATOR_URL = process.env.PYTHON_ORCHESTRATOR_URL || "http://localhost:8000";

// POST /api/protection/analyze
// Forwards evidence text to Python threat analyzer
router.post("/analyze", async (req, res) => {
  try {
    const upstream = await fetch(`${ORCHESTRATOR_URL}/analyze-threat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        evidence_text: req.body.evidence_text || "",
        context: req.body.context || "",
      }),
    });

    if (!upstream.ok) {
      const err = await upstream.text();
      return res.status(upstream.status).json({ error: err });
    }

    const data = await upstream.json();
    res.json(data);
  } catch (err) {
    res.status(500).json({ error: "Threat analysis service unavailable: " + err.message });
  }
});

// POST /api/protection/generate-documents
// Forwards document generation request to Python
router.post("/generate-documents", async (req, res) => {
  try {
    const upstream = await fetch(`${ORCHESTRATOR_URL}/generate-documents`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        victim_name: req.body.victim_name || "Complainant",
        incident_description: req.body.incident_description || "",
        evidence_summary: req.body.evidence_summary || "",
        threat_analysis: req.body.threat_analysis || {},
        contact_info: req.body.contact_info || "",
      }),
    });

    if (!upstream.ok) {
      const err = await upstream.text();
      return res.status(upstream.status).json({ error: err });
    }

    const data = await upstream.json();
    res.json(data);
  } catch (err) {
    res.status(500).json({ error: "Document generation service unavailable: " + err.message });
  }
});

module.exports = router;
