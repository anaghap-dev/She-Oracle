import { useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Brain, Zap, CheckCircle, AlertCircle, Database,
  Target, Layers, FileText,
} from "lucide-react";

const EVENT_CONFIG = {
  thinking:        { icon: Brain,       color: "text-oracle-400", bg: "bg-oracle-900/30 border-oracle-700/30",   label: "Thinking"  },
  acting:          { icon: Zap,         color: "text-yellow-400", bg: "bg-yellow-900/20 border-yellow-700/30",   label: "Acting"    },
  tool_result:     { icon: Database,    color: "text-blue-400",   bg: "bg-blue-900/20 border-blue-700/30",       label: "Data"      },
  critic:          { icon: CheckCircle, color: "text-green-400",  bg: "bg-green-900/20 border-green-700/30",     label: "Critic"    },
  error:           { icon: AlertCircle, color: "text-red-400",    bg: "bg-red-900/20 border-red-700/30",         label: "Error"     },
  session:         { icon: CheckCircle, color: "text-gray-400",   bg: "bg-gray-800/30 border-gray-700/30",       label: "Session"   },
  intent_analyzed: { icon: Target,      color: "text-oracle-300", bg: "bg-oracle-900/20 border-oracle-700/20",   label: "Intent"    },
  plan_decomposed: { icon: Layers,      color: "text-purple-400", bg: "bg-purple-900/20 border-purple-700/20",   label: "Plan"      },
  artifact_ready:  { icon: FileText,    color: "text-blue-300",   bg: "bg-blue-900/10 border-blue-700/20",       label: "Artifact"  },
};

function EventItem({ event }) {
  const config = EVENT_CONFIG[event.type] || EVENT_CONFIG.thinking;
  const Icon = config.icon;

  const getContent = () => {
    if (event.type === "tool_result") {
      const tool = event.tool?.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
      return `${tool} returned ${Object.keys(event.data || {}).length} data fields`;
    }
    if (event.type === "critic") {
      const scores = event.scores || {};
      return `${event.content || ""} | Feasibility: ${scores.feasibility}/10 | Risk: ${scores.risk_coverage}/10 | Timeline: ${scores.timeline_realism}/10`;
    }
    if (event.type === "intent_analyzed") {
      const intent = event.intent || {};
      return `Goal classified as: ${intent.plan_type || "advisory"} | Urgency: ${intent.urgency || "medium"} | ${intent.sub_intents?.length || 0} sub-intents identified`;
    }
    if (event.type === "plan_decomposed") {
      const subtasks = event.subtasks || [];
      const toolTasks = subtasks.filter((s) => s.agent_type !== "artifact_generator").length;
      const artifactTasks = subtasks.filter((s) => s.agent_type === "artifact_generator").length;
      return `${subtasks.length} subtasks: ${toolTasks} tool call${toolTasks !== 1 ? "s" : ""} + ${artifactTasks} artifact generation${artifactTasks !== 1 ? "s" : ""}`;
    }
    if (event.type === "artifact_ready") {
      return `Generated: ${event.artifact?.title || event.artifact?.type || "document"}`;
    }
    return event.content || JSON.stringify(event).slice(0, 120);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      className={`flex items-start gap-3 p-3 rounded-lg border stream-item ${config.bg}`}
    >
      <Icon size={15} className={`mt-0.5 flex-shrink-0 ${config.color}`} />
      <div className="min-w-0">
        <span className={`text-xs font-semibold uppercase tracking-wide ${config.color}`}>
          {config.label}
          {event.tool && (
            <span className="ml-1 normal-case font-normal text-gray-400">, {event.tool}</span>
          )}
        </span>
        <p className="text-xs text-gray-300 mt-0.5 leading-relaxed">{getContent()}</p>
      </div>
    </motion.div>
  );
}

// Ordered steps the agent goes through — used to derive progress %
const AGENT_STEPS = [
  { key: "session",          label: "Initialising session"          },
  { key: "intent_analyzed",  label: "Analyzing intent"              },
  { key: "plan_decomposed",  label: "Building execution plan"       },
  { key: "thinking",         label: "Reasoning through the problem" },
  { key: "acting",           label: "Running specialist tools"      },
  { key: "tool_result",      label: "Processing intelligence"       },
  { key: "artifact_ready",   label: "Generating documents"          },
  { key: "critic",           label: "Quality checking plan"         },
  { key: "result",           label: "Plan ready"                    },
];

function ProgressBar({ events, isStreaming, planReady }) {
  if (planReady) {
    return (
      <div className="mb-3">
        <div className="flex items-center justify-between mb-1.5">
          <span className="text-xs text-green-400 font-medium">Plan ready</span>
          <span className="text-xs font-semibold text-green-400">Complete</span>
        </div>
        <div className="w-full h-1.5 bg-gray-800 rounded-full overflow-hidden">
          <motion.div
            className="h-full rounded-full bg-gradient-to-r from-green-500 to-emerald-400"
            initial={{ width: "80%" }}
            animate={{ width: "100%" }}
            transition={{ duration: 0.6, ease: "easeOut" }}
          />
        </div>
      </div>
    );
  }

  const seenTypes = new Set(events.map((e) => e.type));
  let currentStep = 0;
  AGENT_STEPS.forEach((s, i) => {
    if (seenTypes.has(s.key)) currentStep = i;
  });
  const total = AGENT_STEPS.length - 1;
  const pct = Math.round((currentStep / total) * 100);
  const label = isStreaming ? AGENT_STEPS[currentStep]?.label : "Complete";

  return (
    <div className="mb-3">
      <div className="flex items-center justify-between mb-1.5">
        <span className="text-xs text-gray-400">{label}</span>
        <span className="text-xs font-semibold text-oracle-400">
          Step {currentStep + 1} / {total + 1}
        </span>
      </div>
      <div className="w-full h-1.5 bg-gray-800 rounded-full overflow-hidden">
        <motion.div
          className="h-full rounded-full bg-gradient-to-r from-oracle-500 to-rose-500"
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.5, ease: "easeOut" }}
        />
      </div>
    </div>
  );
}

export default function AgentStream({ events, isStreaming, error, planReady }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [events.length]);

  if (!isStreaming && events.length === 0 && !error) return null;

  return (
    <div className="glass rounded-xl overflow-hidden">
      {/* Sticky header + progress bar */}
      <div className="sticky top-0 z-10 bg-gray-900/90 backdrop-blur-sm px-4 pt-4 pb-3 border-b border-white/10">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
            Agent Activity
          </h3>
          {isStreaming && !planReady && (
            <span className="flex items-center gap-1.5 text-xs text-oracle-400">
              <span className="w-1.5 h-1.5 rounded-full bg-oracle-400 animate-pulse" />
              Running...
            </span>
          )}
          {planReady && (
            <span className="flex items-center gap-1.5 text-xs text-green-400">
              <CheckCircle size={12} />
              Done
            </span>
          )}
        </div>
        {events.length > 0 && (
          <ProgressBar events={events} isStreaming={isStreaming} planReady={planReady} />
        )}
      </div>

      {/* Scrollable event log */}
      <div className="p-4 space-y-2 max-h-56 overflow-y-auto scrollbar-thin">
        <AnimatePresence initial={false}>
          {events.map((event) => (
            <EventItem key={event.id} event={event} />
          ))}
        </AnimatePresence>

        {error && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex items-center gap-2 p-3 bg-red-900/20 border border-red-700/30 rounded-lg"
          >
            <AlertCircle size={15} className="text-red-400 flex-shrink-0" />
            <p className="text-xs text-red-300">{error}</p>
          </motion.div>
        )}

        <div ref={bottomRef} />
      </div>
    </div>
  );
}
