import { useState } from "react";

const SESSION_KEY = "she_oracle_session_id";

// Simple UUID without library dependency
function generateId() {
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    return (c === "x" ? r : (r & 0x3) | 0x8).toString(16);
  });
}

export function useSession() {
  const [sessionId, setSessionId] = useState(() => {
    const stored = localStorage.getItem(SESSION_KEY);
    if (stored) return stored;
    const newId = generateId();
    localStorage.setItem(SESSION_KEY, newId);
    return newId;
  });

  const resetSession = () => {
    const newId = generateId();
    localStorage.setItem(SESSION_KEY, newId);
    setSessionId(newId);
  };

  return { sessionId, resetSession };
}
