import { useEffect, useRef, useState } from "react";
import { GraduationCap } from "lucide-react";
import SectionHeader from "../components/SectionHeader";
import GoalInput from "../components/GoalInput";
import AgentStream from "../components/AgentStream";
import PlanCard from "../components/PlanCard";
import IntentBadge from "../components/IntentBadge";
import SubtaskFlow from "../components/SubtaskFlow";
import { useAgentStream } from "../hooks/useAgentStream";
import { useSession } from "../hooks/useSession";

const EDUCATION_PROMPTS = [
  "Find me scholarships for an MBA in Finance, I'm from OBC category with 70% in graduation",
  "I want to study Computer Science abroad. What scholarships are available for Indian women?",
  "Help me find free skill development programs for rural women in Tamil Nadu",
  "I dropped out of college. What alternative education paths exist for women re-entering education?",
];

export default function EducationPage() {
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
    startStream({ goal, domain: "education", session_id: sessionId });
  };

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <SectionHeader
        title="Education & Scholarships"
        subtitle="Scholarships, fellowships, free skill programs, and education pathways for women at every stage"
        icon={GraduationCap}
        color="text-yellow-400"
      />

      <div className="glass rounded-2xl p-6 mb-6">
        <GoalInput onSubmit={handleSubmit} isLoading={isStreaming} defaultDomain="education" hideDomainSelector prefillValue={prefillValue} />
      </div>

      <div className="mb-6">
        <p className="text-xs text-gray-500 font-medium uppercase tracking-wide mb-2">Education Quick Prompts</p>
        <div className="flex flex-col gap-2">
          {EDUCATION_PROMPTS.map((p, i) => (
            <button
              key={i}
              onClick={() => setPrefillValue(p)}
              className="text-left text-sm text-gray-400 hover:text-yellow-300 bg-white/3 hover:bg-yellow-900/20 border border-white/5 hover:border-yellow-700/30 px-4 py-2.5 rounded-xl transition-all"
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
        </div>
      )}
    </div>
  );
}
