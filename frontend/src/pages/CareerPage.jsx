import { useEffect, useRef } from "react";
import { Briefcase } from "lucide-react";
import { useState } from "react";
import SectionHeader from "../components/SectionHeader";
import GoalInput from "../components/GoalInput";
import AgentStream from "../components/AgentStream";
import PlanCard from "../components/PlanCard";
import IntentBadge from "../components/IntentBadge";
import SubtaskFlow from "../components/SubtaskFlow";
import { useAgentStream } from "../hooks/useAgentStream";
import { useSession } from "../hooks/useSession";

const CAREER_PROMPTS = [
  "Analyze my skills in Python and data analysis, help me transition to a data scientist role",
  "I'm a teacher with 5 years experience. How do I upskill for an EdTech career?",
  "Help me negotiate a 40% salary hike at my current company",
  "I want to become a freelance UX designer, build me a 90-day roadmap",
];

export default function CareerPage() {
  const { events, plan, isStreaming, error, intentProfile, subtasks, startStream, reset } = useAgentStream();
  const { sessionId } = useSession();
  const [resumeText, setResumeText] = useState("");
  const [prefillValue, setPrefillValue] = useState("");
  const planRef = useRef(null);

  useEffect(() => {
    if (plan && planRef.current) {
      planRef.current.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }, [plan]);

  const handleSubmit = ({ goal, domain }) => {
    reset();
    startStream({
      goal,
      domain: "career",
      session_id: sessionId,
      extra_context: { resume_text: resumeText || goal },
    });
  };

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <SectionHeader
        title="Career Growth"
        subtitle="Resume analysis, skill gaps, upskilling roadmaps, and salary negotiation strategies"
        icon={Briefcase}
        color="text-blue-400"
      />

      {/* Optional resume paste */}
      <div className="glass rounded-xl p-5 mb-6">
        <label className="text-xs font-semibold text-gray-400 uppercase tracking-wide block mb-2">
          Paste Your Resume / Skills Profile (optional, improves analysis)
        </label>
        <textarea
          value={resumeText}
          onChange={(e) => setResumeText(e.target.value)}
          placeholder="Paste your resume text or describe your skills and experience..."
          rows={4}
          className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-600 resize-none focus:outline-none focus:border-blue-500 text-sm"
        />
      </div>

      <div className="glass rounded-2xl p-6 mb-6">
        <GoalInput onSubmit={handleSubmit} isLoading={isStreaming} defaultDomain="career" hideDomainSelector prefillValue={prefillValue} />
      </div>

      {/* Quick prompts */}
      <div className="mb-6">
        <p className="text-xs text-gray-500 font-medium uppercase tracking-wide mb-2">Career Quick Prompts</p>
        <div className="flex flex-col gap-2">
          {CAREER_PROMPTS.map((p, i) => (
            <button
              key={i}
              onClick={() => setPrefillValue(p)}
              className="text-left text-sm text-gray-400 hover:text-blue-300 bg-white/3 hover:bg-blue-900/20 border border-white/5 hover:border-blue-700/30 px-4 py-2.5 rounded-xl transition-all"
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
