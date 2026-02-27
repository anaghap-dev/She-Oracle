import { useState, useRef, useCallback } from "react";
import { createAgentStream } from "../utils/api";

export function useAgentStream() {
  const [events, setEvents] = useState([]);
  const [plan, setPlan] = useState(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState(null);
  const [criticResult, setCriticResult] = useState(null);
  const [intentProfile, setIntentProfile] = useState(null);
  const [subtasks, setSubtasks] = useState([]);
  const [artifacts, setArtifacts] = useState([]);
  const cancelRef = useRef(null);

  const startStream = useCallback(({ goal, domain, session_id, extra_context }) => {
    // Cancel any running stream
    if (cancelRef.current) cancelRef.current();

    setEvents([]);
    setPlan(null);
    setError(null);
    setCriticResult(null);
    setIntentProfile(null);
    setSubtasks([]);
    setArtifacts([]);
    setIsStreaming(true);

    cancelRef.current = createAgentStream({
      goal,
      domain,
      session_id,
      extra_context,
      onEvent: (event) => {
        if (event.type === "result") {
          setPlan(event.plan);
          // Artifacts are embedded in the plan — sync state (idempotent with streaming)
          if (event.plan?.artifacts?.length > 0) {
            setArtifacts(event.plan.artifacts);
          }
        } else if (event.type === "critic") {
          setCriticResult(event);
          setEvents((prev) => [...prev, { ...event, id: Date.now() + Math.random() }]);
        } else if (event.type === "intent_analyzed") {
          setIntentProfile(event.intent);
          setEvents((prev) => [...prev, { ...event, id: Date.now() + Math.random() }]);
        } else if (event.type === "plan_decomposed") {
          setSubtasks(event.subtasks || []);
          setEvents((prev) => [...prev, { ...event, id: Date.now() + Math.random() }]);
        } else if (event.type === "subtask_start") {
          setSubtasks((prev) =>
            prev.map((st) =>
              st.id === event.subtask_id ? { ...st, status: "active" } : st
            )
          );
        } else if (event.type === "subtask_complete") {
          setSubtasks((prev) =>
            prev.map((st) =>
              st.id === event.subtask_id ? { ...st, status: "complete" } : st
            )
          );
        } else if (event.type === "artifact_ready") {
          setArtifacts((prev) => [...prev, event.artifact]);
          setEvents((prev) => [...prev, { ...event, id: Date.now() + Math.random() }]);
        } else {
          setEvents((prev) => [...prev, { ...event, id: Date.now() + Math.random() }]);
        }
      },
      onDone: () => {
        setIsStreaming(false);
      },
      onError: (msg) => {
        setError(msg);
        setIsStreaming(false);
      },
    });
  }, []);

  const cancel = useCallback(() => {
    if (cancelRef.current) {
      cancelRef.current();
      setIsStreaming(false);
    }
  }, []);

  const reset = useCallback(() => {
    cancel();
    setEvents([]);
    setPlan(null);
    setError(null);
    setCriticResult(null);
    setIntentProfile(null);
    setSubtasks([]);
    setArtifacts([]);
  }, [cancel]);

  return {
    events,
    plan,
    isStreaming,
    error,
    criticResult,
    intentProfile,
    subtasks,
    artifacts,
    startStream,
    cancel,
    reset,
  };
}
