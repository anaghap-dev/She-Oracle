import { motion } from "framer-motion";
import { CheckCircle, Circle, Loader2, FileText, Wrench } from "lucide-react";

const STATUS_CONFIG = {
  pending:  { icon: Circle,      color: "text-gray-600",   bg: ""                        },
  active:   { icon: Loader2,     color: "text-oracle-400", bg: "bg-oracle-900/20"        },
  complete: { icon: CheckCircle, color: "text-green-400",  bg: "bg-green-900/10"         },
  failed:   { icon: Circle,      color: "text-red-400",    bg: "bg-red-900/10"           },
};

/**
 * SubtaskFlow — ordered list of subtasks with live status indicators.
 *
 * Props:
 *   subtasks: SubTask[] from useAgentStream().subtasks
 */
export default function SubtaskFlow({ subtasks }) {
  if (!subtasks || subtasks.length === 0) return null;

  return (
    <div className="glass rounded-xl p-4 mb-4">
      <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">
        Execution Plan
      </h3>
      <div className="space-y-2">
        {subtasks.map((task, i) => {
          const cfg = STATUS_CONFIG[task.status] || STATUS_CONFIG.pending;
          const Icon = cfg.icon;
          const isArtifact = task.agent_type === "artifact_generator";

          return (
            <motion.div
              key={task.id}
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.04 }}
              className={`flex items-center gap-3 px-3 py-2 rounded-lg border border-white/5 ${cfg.bg}`}
            >
              <Icon
                size={13}
                className={`flex-shrink-0 ${cfg.color} ${task.status === "active" ? "animate-spin" : ""}`}
              />
              <div className="flex-1 min-w-0">
                <p className="text-xs text-gray-300 truncate">{task.description}</p>
              </div>
              <span className="text-xs text-gray-600 flex items-center gap-1 flex-shrink-0">
                {isArtifact ? <FileText size={10} /> : <Wrench size={10} />}
                {isArtifact ? "artifact" : "tool"}
              </span>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
