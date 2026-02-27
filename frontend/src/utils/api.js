import axios from "axios";

const BASE_URL = "/api";

export const api = axios.create({
  baseURL: BASE_URL,
  timeout: 120000,
  headers: { "Content-Type": "application/json" },
});

export async function runAgent({ goal, domain, session_id, extra_context = {} }) {
  const res = await api.post("/agent/run", { goal, domain, session_id, extra_context });
  return res.data;
}

export async function getSession(session_id) {
  const res = await api.get(`/session/${session_id}`);
  return res.data;
}

export async function updateProfile(session_id, profile_data) {
  const res = await api.post("/session/profile", { session_id, profile_data });
  return res.data;
}

export async function markStepComplete(session_id, step) {
  const res = await api.post("/session/step-complete", { session_id, step });
  return res.data;
}

export async function analyzeEvidence({ evidence_text, context = "" }) {
  const res = await api.post("/protection/analyze", { evidence_text, context });
  return res.data;
}

export async function generateDocuments({ victim_name, incident_description, evidence_summary, threat_analysis, contact_info = "" }) {
  const res = await api.post("/protection/generate-documents", {
    victim_name,
    incident_description,
    evidence_summary,
    threat_analysis,
    contact_info,
  });
  return res.data;
}

export async function getArtifacts(session_id) {
  const res = await api.get(`/session/${session_id}/artifacts`);
  return res.data;
}

export async function downloadArtifact({ artifact_id, session_id, filename }) {
  const res = await fetch("/api/agent/download-artifact", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ artifact_id, session_id, filename: filename || "" }),
  });

  if (!res.ok) {
    throw new Error("Download failed");
  }

  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename || "document.md";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

export async function assessCabSafety(payload) {
  const res = await api.post("/agent/cab-safety-assess", payload);
  return res.data;
}

export function createAgentStream({ goal, domain, session_id, extra_context = {}, onEvent, onDone, onError }) {
  // Use fetch with SSE since EventSource doesn't support POST
  const controller = new AbortController();

  fetch("/api/agent/stream", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ goal, domain, session_id, extra_context }),
    signal: controller.signal,
  })
    .then(async (res) => {
      if (!res.ok) {
        onError?.("Stream connection failed.");
        return;
      }
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });

        const lines = buffer.split("\n");
        buffer = lines.pop(); // keep incomplete line in buffer

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const event = JSON.parse(line.slice(6));
              if (event.type === "done") {
                onDone?.();
              } else {
                onEvent?.(event);
              }
            } catch {
              // ignore parse errors
            }
          }
        }
      }
      onDone?.();
    })
    .catch((err) => {
      if (err.name !== "AbortError") {
        onError?.(err.message || "Connection error.");
      }
    });

  return () => controller.abort(); // returns cancel function
}
