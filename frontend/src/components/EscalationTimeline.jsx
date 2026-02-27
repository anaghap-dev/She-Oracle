import { motion } from "framer-motion";
import { ArrowRight, CheckCircle } from "lucide-react";

/**
 * EscalationTimeline — visual stepped timeline of legal escalation steps.
 *
 * Props:
 *   steps: Array of { step, action, authority, timeline, expected_outcome }
 *          (matches escalation_strategy from legal_rights_checker output)
 */
export default function EscalationTimeline({ steps }) {
  if (!steps || steps.length === 0) return null;

  return (
    <div className="space-y-1 relative">
      {steps.map((step, i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0, x: -12 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: i * 0.08 }}
          className="flex gap-4"
        >
          {/* Timeline spine */}
          <div className="flex flex-col items-center">
            <div className="w-7 h-7 rounded-full bg-oracle-900/60 border border-oracle-700/50 flex items-center justify-center flex-shrink-0">
              <span className="text-xs font-bold text-oracle-300">{step.step || i + 1}</span>
            </div>
            {i < steps.length - 1 && (
              <div className="w-px flex-1 bg-oracle-800/30 mt-1 mb-1" />
            )}
          </div>

          {/* Step content */}
          <div className="pb-4 flex-1 min-w-0">
            <div className="flex items-start justify-between gap-2 mb-1">
              <p className="text-sm font-semibold text-white">{step.action}</p>
              {step.timeline && (
                <span className="text-xs text-oracle-400 flex-shrink-0 flex items-center gap-1">
                  <ArrowRight size={10} />
                  {step.timeline}
                </span>
              )}
            </div>
            {step.authority && (
              <p className="text-xs text-gray-400">Authority: {step.authority}</p>
            )}
            {step.expected_outcome && (
              <p className="text-xs text-green-400 mt-1 flex items-center gap-1">
                <CheckCircle size={10} />
                {step.expected_outcome}
              </p>
            )}
          </div>
        </motion.div>
      ))}
    </div>
  );
}
