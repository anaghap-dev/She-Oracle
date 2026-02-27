import { useState } from "react";
import { motion } from "framer-motion";
import { FileText, Download, Copy, Check, ChevronDown, ChevronUp } from "lucide-react";
import { downloadArtifact } from "../utils/api";

const TYPE_LABELS = {
  skill_gap_report:     "Skill Gap Report",
  resume_draft:         "Resume Draft",
  rights_summary:       "Rights Summary",
  escalation_plan:      "Escalation Plan",
  projection_report:    "Income Projection",
  scheme_checklist:     "Scheme Checklist",
  scheme_match_report:  "Scheme Match Report",
  scholarship_list:     "Scholarship List",
  enrollment_checklist: "Enrollment Checklist",
  fir_draft:            "FIR Draft",
  complaint_letter:     "Complaint Letter",
  takedown_request:     "Takedown Request",
  legal_notice:         "Legal Notice",
};

const DOMAIN_COLORS = {
  career:     "text-blue-400 bg-blue-900/30 border-blue-700/30",
  legal:      "text-red-400 bg-red-900/30 border-red-700/30",
  financial:  "text-green-400 bg-green-900/30 border-green-700/30",
  grants:     "text-pink-400 bg-pink-900/30 border-pink-700/30",
  education:  "text-purple-400 bg-purple-900/30 border-purple-700/30",
  protection: "text-orange-400 bg-orange-900/30 border-orange-700/30",
};

/**
 * ArtifactPanel — single artifact card with preview, copy, and download.
 *
 * Props:
 *   artifact: Artifact object
 *   sessionId: string (needed for server-side download)
 */
export default function ArtifactPanel({ artifact, sessionId }) {
  const [expanded, setExpanded] = useState(false);
  const [copied, setCopied] = useState(false);
  const [downloading, setDownloading] = useState(false);

  const domainColor = DOMAIN_COLORS[artifact.domain] || DOMAIN_COLORS.career;
  const typeLabel = TYPE_LABELS[artifact.type] || artifact.type;
  const previewText =
    artifact.content?.slice(0, 240) + (artifact.content?.length > 240 ? "..." : "");

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(artifact.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // clipboard not available — silent fail
    }
  };

  const handleDownload = async () => {
    setDownloading(true);
    const filename = `${artifact.type}_${artifact.id?.slice(0, 8) || "doc"}.md`;
    try {
      if (sessionId) {
        await downloadArtifact({ artifact_id: artifact.id, session_id: sessionId, filename });
      } else {
        throw new Error("No session");
      }
    } catch {
      // Fallback: build blob directly from content
      const blob = new Blob([artifact.content], { type: "text/markdown" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      a.click();
      URL.revokeObjectURL(url);
    } finally {
      setDownloading(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.97 }}
      animate={{ opacity: 1, scale: 1 }}
      className="bg-gray-900/60 rounded-xl border border-white/10 overflow-hidden"
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-3 px-4 py-3 border-b border-white/10">
        <div className="flex items-start gap-2.5 min-w-0">
          <FileText size={14} className="text-gray-400 mt-0.5 flex-shrink-0" />
          <div className="min-w-0">
            <p className="text-sm font-semibold text-white truncate">{artifact.title}</p>
            <span
              className={`text-xs px-2 py-0.5 rounded-full border mt-1 inline-block ${domainColor}`}
            >
              {typeLabel}
            </span>
          </div>
        </div>
        <div className="flex items-center gap-2 flex-shrink-0">
          <button
            onClick={handleCopy}
            className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-gray-400 hover:text-white text-xs transition-all"
          >
            {copied ? <Check size={11} className="text-green-400" /> : <Copy size={11} />}
            {copied ? "Copied" : "Copy"}
          </button>
          <button
            onClick={handleDownload}
            disabled={downloading}
            className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-oracle-900/40 hover:bg-oracle-800/40 text-oracle-300 text-xs transition-all border border-oracle-700/30 disabled:opacity-50"
          >
            <Download size={11} />
            {downloading ? "..." : "Download"}
          </button>
        </div>
      </div>

      {/* Content preview / full */}
      <div className="px-4 py-3">
        <pre className="text-xs text-gray-400 whitespace-pre-wrap font-mono leading-relaxed">
          {expanded ? artifact.content : previewText}
        </pre>
        {artifact.content?.length > 240 && (
          <button
            onClick={() => setExpanded((v) => !v)}
            className="mt-2 flex items-center gap-1 text-xs text-oracle-400 hover:text-oracle-300 transition-colors"
          >
            {expanded ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
            {expanded ? "Show less" : "Show full document"}
          </button>
        )}
      </div>
    </motion.div>
  );
}
