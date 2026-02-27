import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown, CheckCircle, ArrowRight, Shield, Target, Map, Lightbulb, ExternalLink, Package } from "lucide-react";
import { markStepComplete } from "../utils/api";
import ArtifactPanel from "./ArtifactPanel";

function Section({ title, icon: Icon, children, defaultOpen = false, color = "text-oracle-400" }) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="border border-white/10 rounded-xl overflow-hidden">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-4 py-3 bg-white/3 hover:bg-white/5 transition-colors"
      >
        <div className="flex items-center gap-2">
          <Icon size={15} className={color} />
          <span className="text-sm font-semibold text-white">{title}</span>
        </div>
        <ChevronDown size={15} className={`text-gray-400 transition-transform ${open ? "rotate-180" : ""}`} />
      </button>
      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="px-4 pb-4 pt-2">{children}</div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

function ImmediateAction({ action, sessionId, index }) {
  const [done, setDone] = useState(false);

  const handleComplete = async () => {
    setDone(true);
    if (sessionId) {
      try {
        await markStepComplete(sessionId, action.action);
      } catch {}
    }
  };

  return (
    <div className={`flex items-start gap-3 p-3 rounded-lg border transition-all ${done ? "border-green-700/30 bg-green-900/10 opacity-60" : "border-white/10 bg-white/3"}`}>
      <button
        onClick={handleComplete}
        disabled={done}
        className={`mt-0.5 w-4 h-4 rounded-full border-2 flex-shrink-0 flex items-center justify-center transition-all ${
          done ? "border-green-500 bg-green-500" : "border-gray-500 hover:border-oracle-400"
        }`}
      >
        {done && <CheckCircle size={10} className="text-white" />}
      </button>
      <div className="min-w-0">
        <p className={`text-sm ${done ? "line-through text-gray-500" : "text-white"}`}>{action.action}</p>
        {action.resource && (
          <p className="text-xs text-gray-400 mt-1 flex items-center gap-1">
            <ArrowRight size={11} />
            {action.resource}
          </p>
        )}
        {action.expected_outcome && (
          <p className="text-xs text-oracle-400 mt-1">{action.expected_outcome}</p>
        )}
      </div>
    </div>
  );
}

export default function PlanCard({ plan, sessionId }) {
  if (!plan) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-4"
    >
      {/* Header */}
      <div className="glass rounded-xl p-5">
        <div className="flex items-start justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-oracle-900/50 border border-oracle-700/40 text-oracle-400 text-xs font-medium mb-2">
              <span className="w-1.5 h-1.5 rounded-full bg-oracle-400" />
              Strategic Plan Generated
            </div>
            <h2 className="text-xl font-bold text-white leading-tight">{plan.goal}</h2>
            <span className="text-xs text-gray-500 capitalize mt-1 inline-block">Domain: {plan.domain}</span>
          </div>
        </div>
        {plan.executive_summary && (
          <p className="text-sm text-gray-300 mt-3 leading-relaxed border-t border-white/10 pt-3">
            {plan.executive_summary}
          </p>
        )}
        {plan.situation_analysis && (
          <p className="text-xs text-gray-400 mt-2 leading-relaxed">{plan.situation_analysis}</p>
        )}
      </div>

      {/* Subgoals */}
      {plan.subgoals?.length > 0 && (
        <Section title="Goal Decomposition" icon={Target} color="text-oracle-400" defaultOpen={true}>
          <div className="space-y-2">
            {plan.subgoals.map((sg, i) => (
              <div key={i} className="flex items-start gap-3 p-3 bg-white/3 rounded-lg border border-white/5">
                <span className="w-6 h-6 rounded-full bg-oracle-800 text-oracle-300 text-xs font-bold flex items-center justify-center flex-shrink-0 mt-0.5">
                  {sg.id || i + 1}
                </span>
                <div>
                  <p className="text-sm font-medium text-white">{sg.subgoal}</p>
                  {sg.why && <p className="text-xs text-gray-400 mt-0.5">{sg.why}</p>}
                  {sg.timeline && <p className="text-xs text-oracle-400 mt-1">⏱ {sg.timeline}</p>}
                </div>
              </div>
            ))}
          </div>
        </Section>
      )}

      {/* Immediate Actions */}
      {plan.immediate_actions?.length > 0 && (
        <Section title="Immediate Actions: This Week" icon={Lightbulb} color="text-yellow-400" defaultOpen={true}>
          <div className="space-y-2">
            {plan.immediate_actions.map((action, i) => (
              <ImmediateAction key={i} action={action} sessionId={sessionId} index={i} />
            ))}
          </div>
        </Section>
      )}

      {/* 30-60-90 Roadmap */}
      {plan.roadmap?.length > 0 && (
        <Section title="30-60-90 Day Roadmap" icon={Map} color="text-blue-400" defaultOpen={true}>
          <div className="grid gap-3 md:grid-cols-3">
            {plan.roadmap.map((phase, i) => (
              <div key={i} className="p-3 bg-white/3 border border-white/5 rounded-xl">
                <div className="text-xs font-bold text-blue-400 mb-1">{phase.phase}</div>
                <p className="text-sm font-medium text-white mb-2">{phase.focus}</p>
                {phase.milestones?.map((m, j) => (
                  <div key={j} className="flex items-start gap-1.5 text-xs text-gray-400 mb-1">
                    <span className="text-blue-500 mt-0.5">▸</span> {m}
                  </div>
                ))}
              </div>
            ))}
          </div>
        </Section>
      )}

      {/* Resources */}
      {plan.key_resources?.length > 0 && (
        <Section title="Key Resources & Support" icon={ExternalLink} color="text-green-400">
          <div className="grid gap-2 sm:grid-cols-2">
            {plan.key_resources.map((r, i) => (
              <div key={i} className="p-3 bg-white/3 border border-white/5 rounded-lg">
                <div className="flex items-start justify-between gap-2">
                  <p className="text-sm font-medium text-white">{r.name}</p>
                  <span className="text-xs bg-green-900/40 text-green-400 px-2 py-0.5 rounded-full flex-shrink-0">
                    {r.type}
                  </span>
                </div>
                {r.how_it_helps && <p className="text-xs text-gray-400 mt-1">{r.how_it_helps}</p>}
                {r.url_or_contact && (
                  <p className="text-xs text-green-400 mt-1 font-mono">{r.url_or_contact}</p>
                )}
              </div>
            ))}
          </div>
        </Section>
      )}

      {/* Risk Mitigation */}
      {plan.risk_mitigation?.length > 0 && (
        <Section title="Risk Mitigation" icon={Shield} color="text-red-400">
          <div className="space-y-2">
            {plan.risk_mitigation.map((r, i) => (
              <div key={i} className="p-3 bg-red-900/10 border border-red-700/20 rounded-lg">
                <p className="text-sm font-medium text-red-300">{r.risk}</p>
                <p className="text-xs text-gray-400 mt-1">{r.mitigation}</p>
              </div>
            ))}
          </div>
        </Section>
      )}

      {/* Success Metrics */}
      {plan.success_metrics?.length > 0 && (
        <Section title="Success Metrics" icon={CheckCircle} color="text-oracle-400">
          <ul className="space-y-1.5">
            {plan.success_metrics.map((m, i) => (
              <li key={i} className="flex items-center gap-2 text-sm text-gray-300">
                <span className="text-oracle-500">◆</span> {m}
              </li>
            ))}
          </ul>
        </Section>
      )}

      {/* Generated Artifacts */}
      {plan.artifacts?.length > 0 && (
        <Section
          title={`Generated Artifacts (${plan.artifacts.length})`}
          icon={Package}
          color="text-blue-400"
          defaultOpen={true}
        >
          <div className="space-y-3">
            {plan.artifacts.map((artifact) => (
              <ArtifactPanel key={artifact.id} artifact={artifact} sessionId={sessionId} />
            ))}
          </div>
        </Section>
      )}
    </motion.div>
  );
}
