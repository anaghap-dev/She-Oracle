import { useEffect, useRef, useState } from "react";
import { Scale, Phone, AlertTriangle } from "lucide-react";
import { motion } from "framer-motion";
import SectionHeader from "../components/SectionHeader";
import GoalInput from "../components/GoalInput";
import AgentStream from "../components/AgentStream";
import PlanCard from "../components/PlanCard";
import IntentBadge from "../components/IntentBadge";
import SubtaskFlow from "../components/SubtaskFlow";
import EscalationTimeline from "../components/EscalationTimeline";
import { useAgentStream } from "../hooks/useAgentStream";
import { useSession } from "../hooks/useSession";

const HELPLINES = [
  { name: "Women Helpline",         number: "181",         desc: "24/7 emergency support" },
  { name: "National Commission for Women", number: "7827-170-170", desc: "File complaints, seek guidance" },
  { name: "Police Emergency",       number: "100",         desc: "Immediate danger" },
  { name: "Cyber Crime",            number: "1930",        desc: "Online harassment, fraud" },
  { name: "Legal Aid (NALSA)",      number: "15100",       desc: "Free legal assistance" },
];

const LEGAL_PROMPTS = [
  "My manager is making sexual comments and threatening my job if I report. What are my rights?",
  "My employer denied my maternity leave. What action can I take?",
  "I'm being paid less than male colleagues for the same work. Is this legal?",
  "I want to understand my rights under the POSH Act",
  "I was fired after complaining about harassment. What legal recourse do I have?",
];

export default function LegalPage() {
  const { events, plan, isStreaming, error, intentProfile, subtasks, startStream, reset } = useAgentStream();
  const { sessionId } = useSession();
  const [prefillValue, setPrefillValue] = useState("");
  const planRef = useRef(null);

  useEffect(() => {
    if (plan && planRef.current) {
      planRef.current.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }, [plan]);

  const handleSubmit = ({ goal }) => {
    reset();
    startStream({ goal, domain: "legal", session_id: sessionId, extra_context: { situation_type: "workplace" } });
  };

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <SectionHeader
        title="Legal Rights & Protection"
        subtitle="Workplace harassment, labor law violations, escalation strategies, and formal complaint drafts"
        icon={Scale}
        color="text-red-400"
      />

      {/* Emergency banner */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="flex items-start gap-3 p-4 bg-red-900/20 border border-red-700/30 rounded-xl mb-6"
      >
        <AlertTriangle size={16} className="text-red-400 flex-shrink-0 mt-0.5" />
        <div>
          <p className="text-sm font-semibold text-red-300">In Immediate Danger?</p>
          <p className="text-xs text-gray-400 mt-0.5">
            Call <span className="text-red-400 font-bold">100</span> (Police) or{" "}
            <span className="text-red-400 font-bold">181</span> (Women Helpline) immediately.
            This AI is for strategic legal guidance, not emergency response.
          </p>
        </div>
      </motion.div>

      {/* Helplines */}
      <div className="glass rounded-xl p-4 mb-6">
        <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-3 flex items-center gap-2">
          <Phone size={12} className="text-red-400" /> Emergency Helplines
        </p>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
          {HELPLINES.map((h) => (
            <div key={h.name} className="bg-white/3 rounded-lg p-3 border border-white/5">
              <div className="text-base font-bold text-red-400">{h.number}</div>
              <div className="text-xs font-medium text-white">{h.name}</div>
              <div className="text-xs text-gray-500">{h.desc}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="glass rounded-2xl p-6 mb-6">
        <GoalInput onSubmit={handleSubmit} isLoading={isStreaming} defaultDomain="legal" hideDomainSelector prefillValue={prefillValue} />
      </div>

      {/* Quick prompts */}
      <div className="mb-6">
        <p className="text-xs text-gray-500 font-medium uppercase tracking-wide mb-2">Common Legal Situations</p>
        <div className="flex flex-col gap-2">
          {LEGAL_PROMPTS.map((p, i) => (
            <button
              key={i}
              onClick={() => setPrefillValue(p)}
              className="text-left text-sm text-gray-400 hover:text-red-300 bg-white/3 hover:bg-red-900/20 border border-white/5 hover:border-red-700/30 px-4 py-2.5 rounded-xl transition-all"
            >
              {p}
            </button>
          ))}
        </div>
      </div>

      {(isStreaming || events.length > 0 || error) && (
        <div className="mb-6">
          <AgentStream events={events} isStreaming={isStreaming} error={error} planReady={!!plan} />
          {intentProfile && <div className="mt-4"><IntentBadge intent={intentProfile} /></div>}
          {subtasks.length > 0 && <SubtaskFlow subtasks={subtasks} />}
        </div>
      )}

      {plan && (
        <div ref={planRef}>
          <PlanCard plan={plan} sessionId={sessionId} />
          {plan.tool_insights?.legal_rights_checker?.escalation_strategy?.length > 0 && (
            <div className="glass rounded-xl p-5 mt-4">
              <h3 className="text-sm font-semibold text-white mb-4">Legal Escalation Timeline</h3>
              <EscalationTimeline steps={plan.tool_insights.legal_rights_checker.escalation_strategy} />
            </div>
          )}
        </div>
      )}
    </div>
  );
}
