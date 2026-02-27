import { useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { Sparkles } from "lucide-react";
import GoalInput from "../components/GoalInput";
import AgentStream from "../components/AgentStream";
import PlanCard from "../components/PlanCard";
import IntentBadge from "../components/IntentBadge";
import SubtaskFlow from "../components/SubtaskFlow";
import { useAgentStream } from "../hooks/useAgentStream";
import { useSession } from "../hooks/useSession";


export default function Dashboard() {
  const { events, plan, isStreaming, error, criticResult, intentProfile, subtasks, startStream, reset } = useAgentStream();
  const { sessionId } = useSession();
  const planRef = useRef(null);

  useEffect(() => {
    if (plan && planRef.current) {
      planRef.current.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }, [plan]);

  const handleSubmit = ({ goal, domain }) => {
    reset();
    startStream({ goal, domain, session_id: sessionId });
  };

  return (
    <div className="p-8 max-w-4xl mx-auto">
      {/* Hero */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-8"
      >
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-oracle-900/40 border border-oracle-700/30 text-oracle-300 text-sm font-medium mb-4">
          <Sparkles size={14} />
          Autonomous AI Strategist for Women
        </div>
        <h1 className="text-4xl font-extrabold text-white mb-3 leading-tight">
          Your Goals.{" "}
          <span className="gradient-text">Our Intelligence.</span>
          <br />
          Unstoppable Outcomes.
        </h1>
        <p className="text-gray-400 max-w-xl mx-auto text-sm leading-relaxed">
          SHE-ORACLE decomposes your career, legal, financial, and entrepreneurship goals into legally grounded,
          realistically executable strategic plans, powered by Indian law, government schemes, and multi-agent AI.
        </p>
      </motion.div>

      {/* Goal Input */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="glass rounded-2xl p-6 mb-6"
      >
        <h2 className="text-sm font-semibold text-gray-300 mb-4 flex items-center gap-2">
          <Sparkles size={14} className="text-oracle-400" />
          Set Your Goal
        </h2>
        <GoalInput onSubmit={handleSubmit} isLoading={isStreaming} />
      </motion.div>

      {/* Agent Stream */}
      {(isStreaming || events.length > 0 || error) && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="mb-6"
        >
          <AgentStream events={events} isStreaming={isStreaming} error={error} planReady={!!plan} />
          {intentProfile && <div className="mt-4"><IntentBadge intent={intentProfile} /></div>}
          {subtasks.length > 0 && <SubtaskFlow subtasks={subtasks} />}
        </motion.div>
      )}

      {/* Critic badge */}
      {criticResult && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="mb-4 p-4 glass rounded-xl"
        >
          <div className="flex items-center justify-between flex-wrap gap-2">
            <span className="text-xs font-semibold text-gray-400 uppercase tracking-wide">Critic Evaluation</span>
            <span className={`text-xs font-bold px-3 py-1 rounded-full ${criticResult.passed ? "bg-green-900/40 text-green-400" : "bg-yellow-900/40 text-yellow-400"}`}>
              {criticResult.verdict || (criticResult.passed ? "APPROVED" : "REVISED")}
            </span>
          </div>
          <div className="flex gap-4 mt-2">
            {criticResult.scores && Object.entries(criticResult.scores).map(([key, val]) => (
              <div key={key} className="text-center">
                <div className="text-lg font-bold text-white">{val}<span className="text-xs text-gray-500">/10</span></div>
                <div className="text-xs text-gray-500 capitalize">{key.replace(/_/g, " ")}</div>
              </div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Plan */}
      {plan && (
        <div ref={planRef}>
          <PlanCard plan={plan} sessionId={sessionId} />
        </div>
      )}
    </div>
  );
}
