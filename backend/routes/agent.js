const express = require("express");
const router = express.Router();

const ORCHESTRATOR_URL = process.env.PYTHON_ORCHESTRATOR_URL || "http://localhost:8000";

// POST /api/agent/run — non-streaming plan generation
router.post("/run", async (req, res) => {
  try {
    const { goal, domain, session_id, extra_context } = req.body;

    if (!goal || !goal.trim()) {
      return res.status(400).json({ error: "Goal is required." });
    }

    const upstream = await fetch(`${ORCHESTRATOR_URL}/run`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        goal,
        domain: domain || "general",
        session_id: session_id || "",
        extra_context: extra_context || {},
      }),
    });

    if (!upstream.ok) {
      const errText = await upstream.text();
      return res.status(upstream.status).json({ error: errText });
    }

    const data = await upstream.json();
    res.json(data);
  } catch (err) {
    console.error("Agent run error:", err.message);
    res.status(500).json({ error: "Orchestrator unreachable. Is the Python server running?" });
  }
});

// POST /api/agent/stream — SSE proxy to Python /stream
router.post("/stream", async (req, res) => {
  const { goal, domain, session_id, extra_context } = req.body;

  if (!goal || !goal.trim()) {
    return res.status(400).json({ error: "Goal is required." });
  }

  // Set SSE headers immediately
  res.setHeader("Content-Type", "text/event-stream");
  res.setHeader("Cache-Control", "no-cache");
  res.setHeader("Connection", "keep-alive");
  res.setHeader("X-Accel-Buffering", "no");
  res.flushHeaders();

  try {
    const upstream = await fetch(`${ORCHESTRATOR_URL}/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        goal,
        domain: domain || "general",
        session_id: session_id || "",
        extra_context: extra_context || {},
      }),
    });

    if (!upstream.ok) {
      const errText = await upstream.text();
      res.write(`data: ${JSON.stringify({ type: "error", content: errText })}\n\n`);
      res.end();
      return;
    }

    // Pipe SSE stream from Python → client using Web Streams API (Node 18+)
    const reader = upstream.body.getReader();
    const decoder = new TextDecoder();

    const pump = async () => {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        res.write(decoder.decode(value, { stream: true }));
      }
      res.end();
    };

    pump().catch((err) => {
      res.write(`data: ${JSON.stringify({ type: "error", content: err.message })}\n\n`);
      res.end();
    });

    // Handle client disconnect
    req.on("close", () => {
      reader.cancel();
    });
  } catch (err) {
    console.error("SSE proxy error:", err.message);
    res.write(`data: ${JSON.stringify({ type: "error", content: "Orchestrator unreachable. Is the Python server running on port 8000?" })}\n\n`);
    res.end();
  }
});

// POST /api/agent/download-artifact — forward artifact download from Python
router.post("/download-artifact", async (req, res) => {
  try {
    const { artifact_id, session_id, filename } = req.body;

    const upstream = await fetch(`${ORCHESTRATOR_URL}/download-artifact`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ artifact_id, session_id, filename: filename || "" }),
    });

    if (!upstream.ok) {
      const err = await upstream.text();
      return res.status(upstream.status).json({ error: err });
    }

    const contentType = upstream.headers.get("content-type") || "text/plain";
    const contentDisposition = upstream.headers.get("content-disposition") || "attachment";
    res.setHeader("Content-Type", contentType);
    res.setHeader("Content-Disposition", contentDisposition);

    const buffer = await upstream.arrayBuffer();
    res.send(Buffer.from(buffer));
  } catch (err) {
    console.error("Artifact download error:", err.message);
    res.status(500).json({ error: "Could not download artifact." });
  }
});

// POST /api/agent/cab-safety-assess — forward cab safety assessment to Python
router.post("/cab-safety-assess", async (req, res) => {
  try {
    const upstream = await fetch(`${ORCHESTRATOR_URL}/cab-safety/assess`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(req.body),
    });
    if (!upstream.ok) {
      const err = await upstream.text();
      return res.status(upstream.status).json({ error: err });
    }
    const data = await upstream.json();
    res.json(data);
  } catch (err) {
    console.error("Cab safety assess error:", err.message);
    res.status(500).json({ error: "Cab safety assessment failed. Is the Python server running?" });
  }
});

module.exports = router;
