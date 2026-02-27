import { motion } from "framer-motion";
import { Target, AlertTriangle, Layers } from "lucide-react";

const URGENCY_CONFIG = {
  low:      { color: "text-green-400",  bg: "bg-green-900/30",  border: "border-green-700/30"  },
  medium:   { color: "text-yellow-400", bg: "bg-yellow-900/30", border: "border-yellow-700/30" },
  high:     { color: "text-orange-400", bg: "bg-orange-900/30", border: "border-orange-700/30" },
  critical: { color: "text-red-400",    bg: "bg-red-900/40",    border: "border-red-700/40"    },
};

const PLAN_TYPE_LABELS = {
  advisory:            "Strategic Advisory",
  legal_action:        "Legal Action",
  financial_analysis:  "Financial Analysis",
  document_generation: "Document Generation",
  threat_response:     "Threat Response",
};

/**
 * IntentBadge — displays the analyzed intent profile.
 * Shows: plan_type chip, urgency badge, sub-intents as pill tags.
 *
 * Props:
 *   intent: IntentProfile object from useAgentStream().intentProfile
 */
export default function IntentBadge({ intent }) {
  if (!intent) return null;

  const urgencyCfg = URGENCY_CONFIG[intent.urgency] || URGENCY_CONFIG.medium;

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass rounded-xl p-4 mb-4"
    >
      <div className="flex items-center gap-2 mb-3">
        <Target size={14} className="text-oracle-400" />
        <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
          Intent Analysis
        </span>
      </div>

      <div className="flex flex-wrap items-center gap-2 mb-3">
        {/* Plan type chip */}
        <span className="text-xs font-bold px-3 py-1 rounded-full bg-oracle-900/50 border border-oracle-700/40 text-oracle-300">
          {PLAN_TYPE_LABELS[intent.plan_type] || intent.plan_type}
        </span>

        {/* Urgency badge */}
        <span
          className={`text-xs font-bold px-3 py-1 rounded-full border flex items-center gap-1.5 ${urgencyCfg.bg} ${urgencyCfg.border} ${urgencyCfg.color}`}
        >
          <AlertTriangle size={10} />
          {intent.urgency?.toUpperCase()} URGENCY
        </span>
      </div>

      {/* Sub-intents */}
      {intent.sub_intents?.length > 0 && (
        <div>
          <div className="flex items-center gap-1.5 mb-2">
            <Layers size={12} className="text-gray-500" />
            <span className="text-xs text-gray-500">
              Decomposed into {intent.sub_intents.length} sub-intents:
            </span>
          </div>
          <div className="flex flex-wrap gap-1.5">
            {intent.sub_intents.map((si, i) => (
              <span
                key={i}
                className="text-xs px-2 py-0.5 rounded-full bg-white/5 border border-white/10 text-gray-400"
              >
                {si}
              </span>
            ))}
          </div>
        </div>
      )}
    </motion.div>
  );
}
