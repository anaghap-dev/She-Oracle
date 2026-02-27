import { motion } from "framer-motion";

export const severityConfig = {
  LOW:      { bg: "bg-green-900/30",  border: "border-green-700/40",  text: "text-green-400",  bar: "bg-green-500"  },
  MODERATE: { bg: "bg-yellow-900/30", border: "border-yellow-700/40", text: "text-yellow-400", bar: "bg-yellow-500" },
  HIGH:     { bg: "bg-orange-900/30", border: "border-orange-700/40", text: "text-orange-400", bar: "bg-orange-500" },
  CRITICAL: { bg: "bg-red-900/40",    border: "border-red-700/50",    text: "text-red-400",    bar: "bg-red-500"    },
};

/**
 * SeverityMeter — animated severity score display.
 *
 * Props:
 *   score: number (1-10)
 *   level: "LOW" | "MODERATE" | "HIGH" | "CRITICAL"
 */
export default function SeverityMeter({ score, level }) {
  const cfg = severityConfig[level] || severityConfig.MODERATE;
  const pct = (score / 10) * 100;

  return (
    <div className={`rounded-xl p-4 border ${cfg.bg} ${cfg.border}`}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
          Severity Score
        </span>
        <span className={`text-2xl font-extrabold ${cfg.text}`}>
          {score}
          <span className="text-sm text-gray-500">/10</span>
        </span>
      </div>
      <div className="w-full h-2.5 bg-gray-800 rounded-full overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 1, ease: "easeOut" }}
          className={`h-full rounded-full ${cfg.bar}`}
        />
      </div>
      <div className="flex items-center justify-between mt-2">
        <span className="text-xs text-gray-500">Low</span>
        <span
          className={`text-xs font-bold px-2 py-0.5 rounded-full ${cfg.bg} ${cfg.text} border ${cfg.border}`}
        >
          {level}
        </span>
        <span className="text-xs text-gray-500">Critical</span>
      </div>
    </div>
  );
}
