import { useEffect, useRef, useState } from "react";
import { TrendingUp } from "lucide-react";
import SectionHeader from "../components/SectionHeader";
import GoalInput from "../components/GoalInput";
import AgentStream from "../components/AgentStream";
import PlanCard from "../components/PlanCard";
import IntentBadge from "../components/IntentBadge";
import SubtaskFlow from "../components/SubtaskFlow";
import { useAgentStream } from "../hooks/useAgentStream";
import { useSession } from "../hooks/useSession";

const FINANCIAL_PROMPTS = [
  "I earn Rs. 25,000/month as a nurse, help me achieve financial independence in 5 years",
  "I'm a homemaker wanting to start earning, build me a realistic income roadmap",
  "Help me build multiple income streams as a part-time graphic designer",
  "I want to invest my savings wisely. What financial plan suits a woman in her 30s?",
];

export default function FinancialPage() {
  const { events, plan, isStreaming, error, intentProfile, subtasks, startStream, reset } = useAgentStream();
  const { sessionId } = useSession();
  const [profile, setProfile] = useState({ skills: "", income: "", location: "India" });
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
      domain: "financial",
      session_id: sessionId,
      extra_context: {
        current_skills: profile.skills || goal,
        current_income: profile.income,
        location: profile.location,
      },
    });
  };

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <SectionHeader
        title="Financial Independence"
        subtitle="Income projections, multiple income streams, investment guidance, and financial independence roadmaps"
        icon={TrendingUp}
        color="text-green-400"
      />

      {/* Quick profile */}
      <div className="glass rounded-xl p-5 mb-6">
        <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-3">Your Financial Profile (optional, improves projections)</p>
        <div className="grid sm:grid-cols-3 gap-3">
          <div>
            <label className="text-xs text-gray-500 block mb-1">Current Skills</label>
            <input
              type="text"
              value={profile.skills}
              onChange={(e) => setProfile({ ...profile, skills: e.target.value })}
              placeholder="e.g. Excel, stitching, teaching"
              className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-green-500"
            />
          </div>
          <div>
            <label className="text-xs text-gray-500 block mb-1">Current Income (monthly)</label>
            <input
              type="text"
              value={profile.income}
              onChange={(e) => setProfile({ ...profile, income: e.target.value })}
              placeholder="e.g. Rs. 20,000 or 0"
              className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-green-500"
            />
          </div>
          <div>
            <label className="text-xs text-gray-500 block mb-1">Location</label>
            <input
              type="text"
              value={profile.location}
              onChange={(e) => setProfile({ ...profile, location: e.target.value })}
              placeholder="e.g. Mumbai, Chennai"
              className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-green-500"
            />
          </div>
        </div>
      </div>

      <div className="glass rounded-2xl p-6 mb-6">
        <GoalInput onSubmit={handleSubmit} isLoading={isStreaming} defaultDomain="financial" hideDomainSelector prefillValue={prefillValue} />
      </div>

      <div className="mb-6">
        <p className="text-xs text-gray-500 font-medium uppercase tracking-wide mb-2">Financial Quick Prompts</p>
        <div className="flex flex-col gap-2">
          {FINANCIAL_PROMPTS.map((p, i) => (
            <button
              key={i}
              onClick={() => setPrefillValue(p)}
              className="text-left text-sm text-gray-400 hover:text-green-300 bg-white/3 hover:bg-green-900/20 border border-white/5 hover:border-green-700/30 px-4 py-2.5 rounded-xl transition-all"
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
