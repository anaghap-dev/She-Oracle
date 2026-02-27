import { motion } from "framer-motion";
import { ArrowRight } from "lucide-react";

/**
 * ActionFlow — ordered list of immediate actions with priority indicators.
 * Used on domain pages to display plan.immediate_actions in a visual flow.
 *
 * Props:
 *   actions: Array of { action, resource, expected_outcome }
 */
export default function ActionFlow({ actions }) {
  if (!actions || actions.length === 0) return null;

  return (
    <div className="space-y-2">
      {actions.map((action, i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0, y: 6 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.06 }}
          className="flex items-start gap-3 p-3 rounded-xl border border-white/10 bg-white/[0.02]"
        >
          <div className="w-6 h-6 rounded-full bg-oracle-900/60 border border-oracle-700/40 flex items-center justify-center flex-shrink-0 mt-0.5">
            <span className="text-xs font-bold text-oracle-300">{i + 1}</span>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm text-white">{action.action}</p>
            {action.resource && (
              <p className="text-xs text-gray-500 mt-1 flex items-center gap-1">
                <ArrowRight size={10} />
                {action.resource}
              </p>
            )}
            {action.expected_outcome && (
              <p className="text-xs text-oracle-400 mt-1">{action.expected_outcome}</p>
            )}
          </div>
        </motion.div>
      ))}
    </div>
  );
}
