const express = require("express");
const router = express.Router();

const ORCHESTRATOR_URL = process.env.PYTHON_ORCHESTRATOR_URL || "http://localhost:8000";

// GET /api/session/:id
router.get("/:id", async (req, res) => {
  try {
    const upstream = await fetch(`${ORCHESTRATOR_URL}/session/${req.params.id}`);
    const data = await upstream.json();
    res.json(data);
  } catch (err) {
    res.status(500).json({ error: "Could not fetch session." });
  }
});

// POST /api/session/profile
router.post("/profile", async (req, res) => {
  try {
    const upstream = await fetch(`${ORCHESTRATOR_URL}/session/profile`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(req.body),
    });
    const data = await upstream.json();
    res.json(data);
  } catch (err) {
    res.status(500).json({ error: "Could not update profile." });
  }
});

// POST /api/session/step-complete
router.post("/step-complete", async (req, res) => {
  try {
    const upstream = await fetch(`${ORCHESTRATOR_URL}/session/step-complete`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(req.body),
    });
    const data = await upstream.json();
    res.json(data);
  } catch (err) {
    res.status(500).json({ error: "Could not mark step complete." });
  }
});

// GET /api/session/:id/artifacts
router.get("/:id/artifacts", async (req, res) => {
  try {
    const upstream = await fetch(`${ORCHESTRATOR_URL}/artifacts/${req.params.id}`);
    if (!upstream.ok) {
      return res.status(upstream.status).json({ error: "Could not fetch artifacts." });
    }
    const data = await upstream.json();
    res.json(data);
  } catch (err) {
    res.status(500).json({ error: "Could not fetch artifacts." });
  }
});

module.exports = router;
