import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Link } from "react-router-dom";
import {
  Shield,
  AlertTriangle,
  FileText,
  ChevronDown,
  ChevronUp,
  Download,
  Copy,
  Check,
  Loader2,
  Upload,
  Info,
  ExternalLink,
  Car,
} from "lucide-react";
import { analyzeEvidence, generateDocuments } from "../utils/api";
import SeverityMeter, { severityConfig } from "../components/SeverityMeter";
import EscalationTimeline from "../components/EscalationTimeline";

function CollapsibleSection({ title, icon: Icon, iconColor, children, defaultOpen = false }) {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <div className="glass rounded-xl overflow-hidden">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-5 py-4 text-left hover:bg-white/5 transition-colors"
      >
        <div className="flex items-center gap-3">
          <Icon size={16} className={iconColor} />
          <span className="text-sm font-semibold text-white">{title}</span>
        </div>
        {open ? <ChevronUp size={16} className="text-gray-500" /> : <ChevronDown size={16} className="text-gray-500" />}
      </button>
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25 }}
            className="overflow-hidden"
          >
            <div className="px-5 pb-5">{children}</div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

function CopyButton({ text }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <button
      onClick={handleCopy}
      className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-gray-400 hover:text-white text-xs transition-all"
    >
      {copied ? <Check size={12} className="text-green-400" /> : <Copy size={12} />}
      {copied ? "Copied" : "Copy"}
    </button>
  );
}

function DocumentCard({ title, content }) {
  const handleDownload = () => {
    const blob = new Blob([content], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${title.replace(/[^a-z0-9]/gi, "_").toLowerCase()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="bg-gray-900/60 rounded-xl border border-white/10 overflow-hidden">
      <div className="flex items-center justify-between px-4 py-3 border-b border-white/10">
        <span className="text-xs font-semibold text-gray-300">{title}</span>
        <div className="flex items-center gap-2">
          <CopyButton text={content} />
          <button
            onClick={handleDownload}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-oracle-900/40 hover:bg-oracle-800/40 text-oracle-300 hover:text-oracle-200 text-xs transition-all border border-oracle-700/30"
          >
            <Download size={12} />
            Download
          </button>
        </div>
      </div>
      <pre className="px-4 py-4 text-xs text-gray-300 whitespace-pre-wrap font-mono leading-relaxed max-h-64 overflow-y-auto scrollbar-thin">
        {content}
      </pre>
    </div>
  );
}

// ── Main Page ────────────────────────────────────────────────────────────────

export default function ProtectionPage() {
  const [evidenceText, setEvidenceText] = useState("");
  const [contextText, setContextText] = useState("");
  const [victimName, setVictimName] = useState("");
  const [analysisResult, setAnalysisResult] = useState(null);
  const [documents, setDocuments] = useState(null);

  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [analysisError, setAnalysisError] = useState(null);
  const [docError, setDocError] = useState(null);

  const handleAnalyze = async () => {
    if (!evidenceText.trim()) return;
    setIsAnalyzing(true);
    setAnalysisError(null);
    setAnalysisResult(null);
    setDocuments(null);

    try {
      const result = await analyzeEvidence({ evidence_text: evidenceText, context: contextText });
      setAnalysisResult(result);
    } catch (err) {
      setAnalysisError(err.message || "Analysis failed. Please try again.");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleGenerateDocs = async () => {
    if (!analysisResult) return;
    setIsGenerating(true);
    setDocError(null);

    try {
      const result = await generateDocuments({
        victim_name: victimName || "Complainant",
        incident_description: evidenceText,
        evidence_summary: contextText || "Evidence as described above",
        threat_analysis: analysisResult,
      });
      setDocuments(result);
    } catch (err) {
      setDocError(err.message || "Document generation failed.");
    } finally {
      setIsGenerating(false);
    }
  };

  const severity = analysisResult?.severity || {};
  const classification = analysisResult?.threat_classification || {};
  const escalation = analysisResult?.escalation_prediction || {};
  const legalMapping = analysisResult?.legal_mapping || {};
  const cfg = severityConfig[severity.level] || severityConfig.MODERATE;

  return (
    <div className="p-8 max-w-4xl mx-auto">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-8"
      >
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-red-900/30 border border-red-700/30 text-red-300 text-sm font-medium mb-4">
          <Shield size={14} />
          Digital Safety Intelligence Engine
        </div>
        <h1 className="text-4xl font-extrabold text-white mb-3 leading-tight">
          Protection{" "}
          <span className="gradient-text">Intelligence Layer</span>
        </h1>
        <p className="text-gray-400 max-w-xl mx-auto text-sm leading-relaxed">
          Paste your evidence (messages, threats, screenshots as text) and SHE-ORACLE will
          classify the threat, assess severity, map applicable Indian laws, and generate
          formal FIR drafts, complaint letters, and takedown requests.
        </p>
      </motion.div>

      {/* Cab Safety Entry Card */}
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.05 }}
        className="glass rounded-xl p-5 mb-6 border border-red-800/30"
      >
        <div className="flex items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <Car size={15} className="text-red-400" />
              <span className="text-sm font-semibold text-white">Cab Safety Assessment</span>
              <span className="text-xs px-2 py-0.5 rounded-full bg-red-900/40 border border-red-700/40 text-red-400 font-medium">New</span>
            </div>
            <p className="text-xs text-gray-400">
              Real-time risk scoring for rides — get an emergency message, safety card, and complaint draft instantly
            </p>
          </div>
          <Link
            to="/protection/cab-safety"
            className="flex-shrink-0 px-4 py-2 rounded-lg bg-red-700/30 hover:bg-red-700/50 text-red-300 hover:text-red-200 text-sm font-medium transition-all border border-red-700/40"
          >
            Open →
          </Link>
        </div>
      </motion.div>

      {/* Privacy Notice */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.1 }}
        className="flex items-start gap-3 p-4 rounded-xl bg-blue-900/20 border border-blue-700/30 mb-6 text-sm text-blue-300"
      >
        <Info size={16} className="mt-0.5 flex-shrink-0" />
        <span>Your evidence is processed only for analysis and is never stored. All AI processing happens via Gemini API with no persistent logging of sensitive content.</span>
      </motion.div>

      {/* Input Section */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="glass rounded-2xl p-6 mb-6"
      >
        <h2 className="text-sm font-semibold text-gray-300 mb-4 flex items-center gap-2">
          <Upload size={14} className="text-red-400" />
          Submit Evidence for Analysis
        </h2>

        <div className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-gray-400 mb-2">
              Evidence Text * <span className="text-gray-600">(paste screenshots, messages, posts, threats)</span>
            </label>
            <textarea
              value={evidenceText}
              onChange={(e) => setEvidenceText(e.target.value)}
              placeholder="Paste the harassing message, threat, post content, or describe what happened here...&#10;&#10;Example: 'I received this message from @username123: &quot;I know where you live, you will regret ignoring me. I have your photos and I will send them to everyone you know unless you meet me.&quot;'"
              rows={6}
              className="w-full bg-gray-900/60 border border-white/10 rounded-xl px-4 py-3 text-sm text-white placeholder-gray-600 resize-none focus:outline-none focus:ring-1 focus:ring-red-500/50 focus:border-red-500/30 transition-colors"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-400 mb-2">
              Additional Context <span className="text-gray-600">(optional: platform, relationship, history)</span>
            </label>
            <textarea
              value={contextText}
              onChange={(e) => setContextText(e.target.value)}
              placeholder="Example: This is from Instagram DMs. We met once at a networking event 6 months ago. This has been happening for 3 weeks despite blocking on WhatsApp..."
              rows={3}
              className="w-full bg-gray-900/60 border border-white/10 rounded-xl px-4 py-3 text-sm text-white placeholder-gray-600 resize-none focus:outline-none focus:ring-1 focus:ring-oracle-500/50 focus:border-oracle-500/30 transition-colors"
            />
          </div>

          <button
            onClick={handleAnalyze}
            disabled={isAnalyzing || !evidenceText.trim()}
            className="w-full flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-500 hover:to-rose-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold text-sm transition-all"
          >
            {isAnalyzing ? (
              <>
                <Loader2 size={16} className="animate-spin" />
                Analyzing Threat...
              </>
            ) : (
              <>
                <Shield size={16} />
                Analyze & Classify Threat
              </>
            )}
          </button>

          {analysisError && (
            <div className="p-3 rounded-lg bg-red-900/30 border border-red-700/40 text-red-400 text-xs">
              {analysisError}
            </div>
          )}
        </div>
      </motion.div>

      {/* Analysis Results */}
      <AnimatePresence>
        {analysisResult && (
          <motion.div
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-4 mb-6"
          >
            {/* Safety Warning Banner */}
            {analysisResult.safety_warning && (
              <motion.div
                initial={{ scale: 0.97 }}
                animate={{ scale: 1 }}
                className="flex items-start gap-3 p-4 rounded-xl bg-red-900/50 border border-red-500/50 text-red-200"
              >
                <AlertTriangle size={18} className="text-red-400 flex-shrink-0 mt-0.5" />
                <div>
                  <div className="text-xs font-bold text-red-400 uppercase tracking-wider mb-1">Immediate Safety Alert</div>
                  <div className="text-sm">{analysisResult.safety_warning}</div>
                </div>
              </motion.div>
            )}

            {/* Threat Overview */}
            <div className={`glass rounded-xl p-5 border ${cfg.border}`}>
              <div className="flex flex-wrap items-start justify-between gap-4 mb-4">
                <div>
                  <div className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Threat Classification</div>
                  <div className="text-lg font-bold text-white capitalize">
                    {classification.primary_type?.replace(/_/g, " ")}
                  </div>
                  <div className="text-xs text-gray-400 mt-1">{classification.description}</div>
                  {classification.secondary_types?.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 mt-2">
                      {classification.secondary_types.map((t) => (
                        <span key={t} className="text-xs px-2 py-0.5 rounded-full bg-gray-800 text-gray-400 border border-white/10 capitalize">
                          {t.replace(/_/g, " ")}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
                <SeverityMeter score={severity.score} level={severity.level} />
              </div>
              <div className="text-xs text-gray-400 border-t border-white/10 pt-3">
                <span className="font-medium text-gray-300">Severity Justification: </span>
                {severity.justification}
              </div>
            </div>

            {/* Escalation Risk */}
            <CollapsibleSection title="Escalation Risk Prediction" icon={AlertTriangle} iconColor="text-orange-400" defaultOpen={true}>
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <span className="text-xs text-gray-400">Likelihood to Escalate:</span>
                  <span className={`text-xs font-bold px-2.5 py-1 rounded-full ${
                    escalation.likelihood_to_escalate === "HIGH" || escalation.likelihood_to_escalate === "CRITICAL"
                      ? "bg-red-900/40 text-red-400 border border-red-700/40"
                      : escalation.likelihood_to_escalate === "MEDIUM"
                      ? "bg-yellow-900/40 text-yellow-400 border border-yellow-700/40"
                      : "bg-green-900/40 text-green-400 border border-green-700/40"
                  }`}>
                    {escalation.likelihood_to_escalate}
                  </span>
                </div>
                {escalation.timeline && (
                  <div className="text-xs text-gray-400">
                    <span className="text-gray-300 font-medium">Timeline: </span>{escalation.timeline}
                  </div>
                )}
                {escalation.risk_factors?.length > 0 && (
                  <ul className="space-y-1.5">
                    {escalation.risk_factors.map((f, i) => (
                      <li key={i} className="flex items-start gap-2 text-xs text-gray-300">
                        <span className="text-orange-400 mt-0.5">•</span>
                        {f}
                      </li>
                    ))}
                  </ul>
                )}
                {analysisResult.escalation_steps?.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-white/10">
                    <p className="text-xs font-semibold text-gray-400 mb-3">Recommended Escalation Steps:</p>
                    <EscalationTimeline steps={analysisResult.escalation_steps} />
                  </div>
                )}
              </div>
            </CollapsibleSection>

            {/* Legal Mapping */}
            <CollapsibleSection title="Applicable Indian Laws" icon={FileText} iconColor="text-oracle-400" defaultOpen={true}>
              <div className="space-y-3">
                <div className="flex flex-wrap gap-3 mb-3">
                  <div className="text-xs px-3 py-1.5 rounded-lg bg-gray-800 border border-white/10">
                    <span className="text-gray-500">Cognizable Offence: </span>
                    <span className={legalMapping.cognizable_offence ? "text-green-400" : "text-gray-400"}>
                      {legalMapping.cognizable_offence ? "Yes, FIR can be filed directly" : "No, Complaint required"}
                    </span>
                  </div>
                  <div className="text-xs px-3 py-1.5 rounded-lg bg-gray-800 border border-white/10">
                    <span className="text-gray-500">Bailable: </span>
                    <span className={legalMapping.bailable ? "text-yellow-400" : "text-red-400"}>
                      {legalMapping.bailable ? "Yes" : "No (Non-bailable)"}
                    </span>
                  </div>
                  {legalMapping.jurisdiction && (
                    <div className="text-xs px-3 py-1.5 rounded-lg bg-gray-800 border border-white/10">
                      <span className="text-gray-500">File at: </span>
                      <span className="text-white">{legalMapping.jurisdiction}</span>
                    </div>
                  )}
                </div>
                {legalMapping.primary_sections?.map((sec, i) => (
                  <div key={i} className="p-3 rounded-lg bg-gray-900/60 border border-white/10 space-y-1">
                    <div className="flex items-start justify-between gap-2">
                      <span className="text-xs font-bold text-oracle-300">{sec.act}: {sec.section}</span>
                      <span className="text-xs text-gray-500 shrink-0">{sec.description}</span>
                    </div>
                    <div className="text-xs text-gray-400">
                      <span className="text-gray-500">Punishment: </span>{sec.punishment}
                    </div>
                    <div className="text-xs text-gray-400 italic">{sec.applicability}</div>
                  </div>
                ))}
              </div>
            </CollapsibleSection>

            {/* Immediate Actions */}
            <CollapsibleSection title="Immediate Actions Required" icon={Shield} iconColor="text-red-400" defaultOpen={true}>
              <ol className="space-y-2">
                {analysisResult.immediate_actions?.map((action, i) => (
                  <li key={i} className="flex items-start gap-3 text-sm text-gray-300">
                    <span className="flex-shrink-0 w-5 h-5 rounded-full bg-red-900/40 border border-red-700/40 text-red-400 text-xs flex items-center justify-center font-bold">
                      {i + 1}
                    </span>
                    {action}
                  </li>
                ))}
              </ol>
            </CollapsibleSection>

            {/* Platform Actions */}
            {analysisResult.platform_actions?.length > 0 && (
              <CollapsibleSection title="Platform Reporting Steps" icon={ExternalLink} iconColor="text-blue-400">
                <div className="space-y-3">
                  {analysisResult.platform_actions.map((p, i) => (
                    <div key={i} className="p-3 rounded-lg bg-gray-900/60 border border-white/10">
                      <div className="text-xs font-bold text-white mb-1">{p.platform}</div>
                      <div className="text-xs text-gray-400 mb-1">{p.action}</div>
                      {p.reference_law && (
                        <div className="text-xs text-oracle-400 italic">Cite: {p.reference_law}</div>
                      )}
                    </div>
                  ))}
                </div>
              </CollapsibleSection>
            )}

            {/* Evidence Checklist */}
            {analysisResult.evidence_checklist?.length > 0 && (
              <CollapsibleSection title="Evidence Collection Checklist" icon={Check} iconColor="text-green-400">
                <div className="space-y-2">
                  {analysisResult.evidence_checklist.map((item, i) => (
                    <div key={i} className="flex items-center justify-between py-2 border-b border-white/5 last:border-0">
                      <span className="text-xs text-gray-300">{item.item}</span>
                      <span className={`text-xs px-2 py-0.5 rounded-full ${
                        item.priority === "HIGH"
                          ? "bg-red-900/30 text-red-400"
                          : item.priority === "MEDIUM"
                          ? "bg-yellow-900/30 text-yellow-400"
                          : "bg-gray-800 text-gray-500"
                      }`}>
                        {item.priority}
                      </span>
                    </div>
                  ))}
                </div>
              </CollapsibleSection>
            )}

            {/* Support Resources */}
            {analysisResult.support_resources?.length > 0 && (
              <CollapsibleSection title="Support & Helplines" icon={Info} iconColor="text-purple-400">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {analysisResult.support_resources.map((r, i) => (
                    <div key={i} className="p-3 rounded-lg bg-gray-900/60 border border-white/10">
                      <div className="text-xs font-bold text-white">{r.name}</div>
                      <div className="text-xs font-mono text-oracle-300 my-1">{r.contact}</div>
                      <div className="text-xs text-gray-500">{r.purpose}</div>
                    </div>
                  ))}
                </div>
              </CollapsibleSection>
            )}

            {/* Generate Documents Section */}
            <div className="glass rounded-xl p-5">
              <h3 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
                <FileText size={14} className="text-oracle-400" />
                Generate Legal Documents
              </h3>
              <div className="mb-4">
                <label className="block text-xs font-medium text-gray-400 mb-2">
                  Your Name (for documents) <span className="text-gray-600">leave blank to use "Complainant"</span>
                </label>
                <input
                  type="text"
                  value={victimName}
                  onChange={(e) => setVictimName(e.target.value)}
                  placeholder="Your name or leave blank for anonymity"
                  className="w-full bg-gray-900/60 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white placeholder-gray-600 focus:outline-none focus:ring-1 focus:ring-oracle-500/50 focus:border-oracle-500/30 transition-colors"
                />
              </div>
              <button
                onClick={handleGenerateDocs}
                disabled={isGenerating}
                className="w-full flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-oracle-700 to-rose-700 hover:from-oracle-600 hover:to-rose-600 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold text-sm transition-all"
              >
                {isGenerating ? (
                  <>
                    <Loader2 size={16} className="animate-spin" />
                    Drafting Documents...
                  </>
                ) : (
                  <>
                    <FileText size={16} />
                    Generate FIR Draft, Complaint Letter & Takedown Request
                  </>
                )}
              </button>
              {docError && (
                <div className="mt-3 p-3 rounded-lg bg-red-900/30 border border-red-700/40 text-red-400 text-xs">
                  {docError}
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Documents Output */}
      <AnimatePresence>
        {documents && (
          <motion.div
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-4"
          >
            <div className="flex items-center gap-2 px-2">
              <FileText size={16} className="text-oracle-400" />
              <h2 className="text-base font-bold text-white">Generated Legal Documents</h2>
            </div>

            {documents.fir_draft && (
              <DocumentCard title={documents.fir_draft.title} content={documents.fir_draft.content} />
            )}
            {documents.complaint_letter && (
              <DocumentCard title={documents.complaint_letter.title} content={documents.complaint_letter.content} />
            )}
            {documents.takedown_request && (
              <DocumentCard title={documents.takedown_request.title} content={documents.takedown_request.content} />
            )}
            {documents.legal_notice && (
              <DocumentCard title={documents.legal_notice.title} content={documents.legal_notice.content} />
            )}

            {documents.document_tips?.length > 0 && (
              <div className="p-4 rounded-xl bg-blue-900/20 border border-blue-700/30 space-y-2">
                <div className="text-xs font-semibold text-blue-300 uppercase tracking-wider">Tips for Using These Documents</div>
                {documents.document_tips.map((tip, i) => (
                  <div key={i} className="flex items-start gap-2 text-xs text-blue-200">
                    <span className="text-blue-400">•</span>{tip}
                  </div>
                ))}
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
