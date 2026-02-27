import { useEffect, useRef, useState } from "react";
import { Landmark } from "lucide-react";
import SectionHeader from "../components/SectionHeader";
import GoalInput from "../components/GoalInput";
import AgentStream from "../components/AgentStream";
import PlanCard from "../components/PlanCard";
import IntentBadge from "../components/IntentBadge";
import SubtaskFlow from "../components/SubtaskFlow";
import { useAgentStream } from "../hooks/useAgentStream";
import { useSession } from "../hooks/useSession";

const GRANTS_PROMPTS = [
  "I want to start a home bakery, find me grants and loans under Rs. 5 lakh",
  "I'm launching a women's safety tech startup. What funding is available?",
  "Help me apply for PM Mudra Yojana for my tailoring business",
  "I'm a first-generation entrepreneur in rural Maharashtra. What schemes can I access?",
  "Find me incubators and accelerators for women-led social enterprises in India",
];

export default function GrantsPage() {
  const { events, plan, isStreaming, error, intentProfile, subtasks, startStream, reset } = useAgentStream();
  const { sessionId } = useSession();
  const [budget, setBudget] = useState("");
  const [prefillValue, setPrefillValue] = useState("");
  const planRef = useRef(null);

  useEffect(() => {
    if (plan && planRef.current) {
      planRef.current.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }, [plan]);

  const handleSubmit = ({ goal }) => {
    reset();
    startStream({
      goal,
      domain: "grants",
      session_id: sessionId,
      extra_context: { budget, plan_type: "startup" },
    });
  };

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <SectionHeader
        title="Grants & Government Schemes"
        subtitle="Government grants, startup funding, incubators, and scheme eligibility for women entrepreneurs"
        icon={Landmark}
        color="text-pink-400"
      />

      <div className="glass rounded-xl p-5 mb-6">
        <label className="text-xs font-semibold text-gray-400 uppercase tracking-wide block mb-2">
          Available Budget / Investment Capacity (optional)
        </label>
        <input
          type="text"
          value={budget}
          onChange={(e) => setBudget(e.target.value)}
          placeholder="e.g. Rs. 50,000 or No capital, looking for grants"
          className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-pink-500"
        />
      </div>

      <div className="glass rounded-2xl p-6 mb-6">
        <GoalInput onSubmit={handleSubmit} isLoading={isStreaming} defaultDomain="grants" hideDomainSelector prefillValue={prefillValue} />
      </div>

      <div className="mb-6">
        <p className="text-xs text-gray-500 font-medium uppercase tracking-wide mb-2">Grants Quick Prompts</p>
        <div className="flex flex-col gap-2">
          {GRANTS_PROMPTS.map((p, i) => (
            <button
              key={i}
              onClick={() => setPrefillValue(p)}
              className="text-left text-sm text-gray-400 hover:text-pink-300 bg-white/3 hover:bg-pink-900/20 border border-white/5 hover:border-pink-700/30 px-4 py-2.5 rounded-xl transition-all"
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
