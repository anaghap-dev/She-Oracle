require("dotenv").config();
const express = require("express");
const cors = require("cors");
const agentRoutes = require("./routes/agent");
const sessionRoutes = require("./routes/session");
const protectionRoutes = require("./routes/protection");

const app = express();
const PORT = process.env.PORT || 3001;

// ── Middleware ─────────────────────────────────────────────────────────────
const ALLOWED_ORIGINS = [
  "http://localhost:5173",
  "http://localhost:3000",
  process.env.FRONTEND_URL,           // e.g. https://she-oracle.vercel.app
].filter(Boolean);

app.use(cors({
  origin: ALLOWED_ORIGINS,
  credentials: true,
}));
app.use(express.json({ limit: "2mb" }));

// ── Routes ─────────────────────────────────────────────────────────────────
app.use("/api/agent", agentRoutes);
app.use("/api/session", sessionRoutes);
app.use("/api/protection", protectionRoutes);

app.get("/api/health", async (req, res) => {
  try {
    const ORCHESTRATOR_URL = process.env.PYTHON_ORCHESTRATOR_URL || "http://localhost:8000";
    const upstream = await fetch(`${ORCHESTRATOR_URL}/health`);
    const data = await upstream.json();
    res.json({ backend: "ok", orchestrator: data });
  } catch {
    res.json({ backend: "ok", orchestrator: "unreachable" });
  }
});

// ── Start ─────────────────────────────────────────────────────────────────
app.listen(PORT, () => {
  console.log(`SHE-ORACLE Backend running on http://localhost:${PORT}`);
  console.log(`Orchestrator URL: ${process.env.PYTHON_ORCHESTRATOR_URL || "http://localhost:8000"}`);

  // Keep-alive: ping both services every 10 min so Render free tier doesn't spin them down
  const ORCHESTRATOR_URL = process.env.PYTHON_ORCHESTRATOR_URL || "http://localhost:8000";
  const BACKEND_URL = process.env.SELF_URL || `http://localhost:${PORT}`;
  setInterval(async () => {
    try {
      await fetch(`${ORCHESTRATOR_URL}/health`);
      console.log("[keep-alive] orchestrator pinged");
    } catch (e) {
      console.warn("[keep-alive] orchestrator unreachable:", e.message);
    }
    try {
      await fetch(`${BACKEND_URL}/api/health`);
    } catch (_) {}
  }, 10 * 60 * 1000); // every 10 minutes
});
