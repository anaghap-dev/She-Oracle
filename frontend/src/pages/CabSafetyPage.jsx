import { useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Car, Shield, AlertTriangle, Info, Loader2, ChevronLeft,
  RefreshCw, CheckCircle2, Download, Trash2, TrendingDown,
} from "lucide-react";
import { Link } from "react-router-dom";
import { assessCabSafety } from "../utils/api";
import SeverityMeter, { severityConfig } from "../components/SeverityMeter";
import EscalationTimeline from "../components/EscalationTimeline";
import ArtifactPanel from "../components/ArtifactPanel";
import BehaviourFlags from "../components/cab/BehaviourFlags";
import EmergencySharePanel from "../components/cab/EmergencySharePanel";
import RiskBreakdown from "../components/cab/RiskBreakdown";
import SafeExitPanel from "../components/cab/SafeExitPanel";

// ── Constants ──────────────────────────────────────────────────────────────────

const TIME_OPTIONS = [
  { value: "day",        label: "Daytime",    sub: "6 AM – 6 PM" },
  { value: "evening",    label: "Evening",    sub: "6 PM – 10 PM" },
  { value: "night",      label: "Night",      sub: "10 PM – 1 AM" },
  { value: "late_night", label: "Late Night", sub: "1 AM – 6 AM" },
];

const AREA_OPTIONS = [
  { value: "urban",    label: "Urban",    sub: "City centre" },
  { value: "suburban", label: "Suburban", sub: "Outskirts / colonies" },
  { value: "rural",    label: "Rural",    sub: "Village / remote" },
  { value: "highway",  label: "Highway",  sub: "Expressway / NH" },
];

const levelBannerConfig = {
  LOW:      { bg: "bg-green-900/30 border-green-700/40",   text: "text-green-300",  icon: Shield,        msg: "Risk is low. Stay alert and share your location as a precaution." },
  MODERATE: { bg: "bg-yellow-900/30 border-yellow-700/40", text: "text-yellow-300", icon: AlertTriangle, msg: "Some risk indicators present. Take precautions and share your location now." },
  HIGH:     { bg: "bg-orange-900/40 border-orange-600/50", text: "text-orange-300", icon: AlertTriangle, msg: "Multiple risk factors detected. Activate your emergency contacts immediately." },
  CRITICAL: { bg: "bg-red-900/50 border-red-500/60",       text: "text-red-300",    icon: AlertTriangle, msg: "CRITICAL RISK. Call 112 or 100 right now. Do not wait." },
};

// Situation updates user can select in de-escalation mode
const SITUATION_UPDATES = [
  { id: "route_corrected",    label: "Driver corrected the route",          removes: ["route_deviation"] },
  { id: "entered_busy_area",  label: "Entered a busy / populated area",     reduces_area: "urban" },
  { id: "doors_unlocked",     label: "Doors are now unlocked",              removes: ["doors_locked"] },
  { id: "calm_behaviour",     label: "Driver behaviour has calmed down",    removes: ["aggressive", "personal_questions"] },
  { id: "back_on_app",        label: "Driver is back on the app",           removes: ["cancel_app"] },
];

// ── Helper ─────────────────────────────────────────────────────────────────────

function deltaLabel(prev, curr) {
  const diff = curr - prev;
  if (diff === 0) return null;
  return { value: Math.abs(diff), direction: diff < 0 ? "down" : "up" };
}

// ── Sub-components ─────────────────────────────────────────────────────────────

function ModeHeader({ mode, riskLevel, peakScore, onEndRide }) {
  if (mode === "assessing") return null;

  const isMonitoring = mode === "monitoring";
  return (
    <div className={`flex items-center justify-between px-4 py-2.5 rounded-xl mb-4 text-xs font-medium border ${
      isMonitoring
        ? "bg-blue-900/20 border-blue-700/30 text-blue-300"
        : "bg-green-900/20 border-green-700/30 text-green-300"
    }`}>
      <div className="flex items-center gap-2">
        <div className={`w-2 h-2 rounded-full animate-pulse ${isMonitoring ? "bg-blue-400" : "bg-green-400"}`} />
        {isMonitoring ? "Monitoring mode — situation updated" : "Ride ended safely"}
      </div>
      {isMonitoring && (
        <button
          onClick={onEndRide}
          className="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-green-900/30 hover:bg-green-900/50 text-green-400 hover:text-green-300 border border-green-700/30 transition-all"
        >
          <CheckCircle2 size={12} />
          End Ride Safely
        </button>
      )}
    </div>
  );
}

function DeescalationPanel({ form, flags, onReassess, isReassessing }) {
  const [applied, setApplied] = useState([]);

  const toggle = (updateId) => {
    setApplied((prev) =>
      prev.includes(updateId) ? prev.filter((u) => u !== updateId) : [...prev, updateId]
    );
  };

  const handleReassess = () => {
    // Compute updated flags by applying removals
    let updatedFlags = [...flags];
    let updatedArea = form.area_type;

    for (const updateId of applied) {
      const update = SITUATION_UPDATES.find((u) => u.id === updateId);
      if (!update) continue;
      if (update.removes) {
        updatedFlags = updatedFlags.filter((f) => !update.removes.includes(f));
      }
      if (update.reduces_area) {
        updatedArea = update.reduces_area;
      }
    }

    onReassess({ updatedFlags, updatedArea });
  };

  return (
    <div className="glass rounded-xl p-5 border border-blue-700/30">
      <div className="flex items-center gap-2 mb-4">
        <TrendingDown size={14} className="text-blue-400" />
        <h3 className="text-sm font-semibold text-white">Situation Update</h3>
        <span className="text-xs text-gray-500">— what has changed?</span>
      </div>

      <div className="space-y-2 mb-4">
        {SITUATION_UPDATES.map((update) => (
          <button
            key={update.id}
            onClick={() => toggle(update.id)}
            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg border text-left text-sm transition-all ${
              applied.includes(update.id)
                ? "bg-blue-900/30 border-blue-600/50 text-blue-200"
                : "bg-white/3 border-white/8 text-gray-400 hover:bg-white/6 hover:text-gray-300"
            }`}
          >
            <div className={`flex-shrink-0 w-4 h-4 rounded border-2 flex items-center justify-center transition-all ${
              applied.includes(update.id) ? "bg-blue-500 border-blue-400" : "border-gray-600"
            }`}>
              {applied.includes(update.id) && (
                <svg width="8" height="6" viewBox="0 0 8 6" fill="none">
                  <path d="M1 3L3 5L7 1" stroke="white" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              )}
            </div>
            {update.label}
          </button>
        ))}
      </div>

      <button
        onClick={handleReassess}
        disabled={applied.length === 0 || isReassessing}
        className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-blue-700/40 hover:bg-blue-700/60 disabled:opacity-40 disabled:cursor-not-allowed text-blue-200 text-sm font-medium border border-blue-600/40 transition-all"
      >
        {isReassessing ? (
          <><Loader2 size={14} className="animate-spin" /> Recalculating...</>
        ) : (
          <><RefreshCw size={14} /> Reassess Risk</>
        )}
      </button>
    </div>
  );
}

function RideClosure({ summary, form, advice, onStartNew }) {
  const safeArtifact = advice?.complaint_draft
    ? {
        id: "cab-complaint-final",
        type: "complaint_letter",
        title: "Cab Safety Incident Report",
        domain: "protection",
        content: advice.complaint_draft,
        format: "markdown",
        created_at: Date.now() / 1000,
        metadata: { source: "cab_safety_mode" },
      }
    : null;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.97 }}
      animate={{ opacity: 1, scale: 1 }}
      className="space-y-5"
    >
      {/* Safe arrival banner */}
      <div className="flex flex-col items-center text-center py-8 px-6 glass rounded-2xl border border-green-700/30">
        <div className="w-16 h-16 rounded-full bg-green-900/40 border border-green-600/50 flex items-center justify-center mb-4">
          <CheckCircle2 size={32} className="text-green-400" />
        </div>
        <h2 className="text-2xl font-bold text-white mb-1">You arrived safely.</h2>
        <p className="text-sm text-gray-400">SHE-ORACLE monitored your ride. Here's a summary.</p>
      </div>

      {/* Session summary */}
      <div className="glass rounded-xl p-5 space-y-3">
        <h3 className="text-sm font-semibold text-gray-300 mb-3">Ride Session Summary</h3>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div className="bg-white/4 rounded-lg p-3 text-center">
            <div className="text-xs text-gray-500 mb-1">Initial Risk</div>
            <div className={`text-lg font-bold ${
              summary.initialLevel === "LOW" ? "text-green-400" :
              summary.initialLevel === "MODERATE" ? "text-yellow-400" :
              summary.initialLevel === "HIGH" ? "text-orange-400" : "text-red-400"
            }`}>{summary.initialScore}</div>
            <div className="text-xs text-gray-500">{summary.initialLevel}</div>
          </div>
          <div className="bg-white/4 rounded-lg p-3 text-center">
            <div className="text-xs text-gray-500 mb-1">Peak Risk</div>
            <div className={`text-lg font-bold ${
              summary.peakLevel === "LOW" ? "text-green-400" :
              summary.peakLevel === "MODERATE" ? "text-yellow-400" :
              summary.peakLevel === "HIGH" ? "text-orange-400" : "text-red-400"
            }`}>{summary.peakScore}</div>
            <div className="text-xs text-gray-500">{summary.peakLevel}</div>
          </div>
          <div className="bg-white/4 rounded-lg p-3 text-center">
            <div className="text-xs text-gray-500 mb-1">Final Risk</div>
            <div className="text-lg font-bold text-green-400">{summary.finalScore}</div>
            <div className="text-xs text-gray-500">{summary.finalLevel}</div>
          </div>
          <div className="bg-white/4 rounded-lg p-3 text-center">
            <div className="text-xs text-gray-500 mb-1">Reassessments</div>
            <div className="text-lg font-bold text-blue-400">{summary.reassessCount}</div>
            <div className="text-xs text-gray-500">updates</div>
          </div>
        </div>

        {form.driver_name || form.vehicle_plate ? (
          <div className="pt-2 border-t border-white/8 text-xs text-gray-400">
            <span className="text-gray-500">Ride: </span>
            {[form.driver_name, form.vehicle_plate, form.pickup && form.destination ? `${form.pickup} → ${form.destination}` : ""].filter(Boolean).join(" · ")}
          </div>
        ) : null}
      </div>

      {/* Options */}
      <div className="grid sm:grid-cols-3 gap-3">
        {safeArtifact && (
          <div className="sm:col-span-3">
            <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2 px-1">
              Incident Report (if needed)
            </h3>
            <ArtifactPanel artifact={safeArtifact} sessionId={null} />
          </div>
        )}

        <button
          onClick={onStartNew}
          className="flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-gray-300 text-sm font-medium transition-all"
        >
          <Car size={14} />
          New Ride Assessment
        </button>
        <button
          onClick={onStartNew}
          className="flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-red-900/20 hover:bg-red-900/30 border border-red-800/30 text-red-400 text-sm font-medium transition-all"
        >
          <Trash2 size={14} />
          Clear & Discard
        </button>
      </div>
    </motion.div>
  );
}

// ── Main Page ──────────────────────────────────────────────────────────────────

export default function CabSafetyPage() {
  // Form state (persists across reassessments)
  const [form, setForm] = useState({
    driver_name: "", vehicle_plate: "", pickup: "", destination: "",
    time_of_day: "day", area_type: "urban",
  });
  const [flags, setFlags] = useState([]);

  // Mode: "assessing" | "monitoring" | "closed"
  const [mode, setMode] = useState("assessing");

  // Assessment results
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isReassessing, setIsReassessing] = useState(false);
  const [error, setError] = useState(null);

  // History for delta display + closure summary
  const historyRef = useRef([]);   // [{score, level}]
  const reassessCountRef = useRef(0);

  const set = (key, val) => setForm((f) => ({ ...f, [key]: val }));

  // ── Initial assessment ──────────────────────────────────────────────────────

  const handleAssess = async () => {
    setIsLoading(true);
    setError(null);
    setResult(null);
    historyRef.current = [];
    reassessCountRef.current = 0;

    try {
      const data = await assessCabSafety({ ...form, behaviour_flags: flags });
      setResult(data);
      setMode("monitoring");
      historyRef.current = [{ score: data.risk.score, level: data.risk.level }];
    } catch (err) {
      setError(err?.response?.data?.error || err.message || "Assessment failed. Is the server running?");
    } finally {
      setIsLoading(false);
    }
  };

  // ── De-escalation reassessment ──────────────────────────────────────────────

  const handleReassess = async ({ updatedFlags, updatedArea }) => {
    setIsReassessing(true);
    try {
      const updatedForm = { ...form, area_type: updatedArea };
      const data = await assessCabSafety({ ...updatedForm, behaviour_flags: updatedFlags });
      setResult(data);
      setForm(updatedForm);
      setFlags(updatedFlags);
      reassessCountRef.current += 1;
      historyRef.current.push({ score: data.risk.score, level: data.risk.level });
    } catch (err) {
      // Silently keep previous result on reassess failure
    } finally {
      setIsReassessing(false);
    }
  };

  // ── Ride closure ────────────────────────────────────────────────────────────

  const handleEndRide = () => {
    setMode("closed");
  };

  const handleStartNew = () => {
    setForm({ driver_name: "", vehicle_plate: "", pickup: "", destination: "", time_of_day: "day", area_type: "urban" });
    setFlags([]);
    setResult(null);
    setError(null);
    historyRef.current = [];
    reassessCountRef.current = 0;
    setMode("assessing");
  };

  // ── Derived values ──────────────────────────────────────────────────────────

  const risk = result?.risk;
  const advice = result?.advice;
  const riskLevel = risk?.level || "LOW";
  const cfg = severityConfig[riskLevel] || severityConfig.MODERATE;
  const banner = levelBannerConfig[riskLevel] || levelBannerConfig.MODERATE;
  const BannerIcon = banner.icon;

  // Score delta from previous assessment
  const prevEntry = historyRef.current.length >= 2
    ? historyRef.current[historyRef.current.length - 2]
    : null;
  const scoreDelta = prevEntry ? deltaLabel(prevEntry.score, risk?.score ?? 0) : null;

  // Closure summary
  const closureSummary = historyRef.current.length > 0 ? {
    initialScore: historyRef.current[0].score,
    initialLevel: historyRef.current[0].level,
    peakScore: Math.max(...historyRef.current.map((h) => h.score)),
    peakLevel: historyRef.current.reduce((a, b) => a.score >= b.score ? a : b).level,
    finalScore: historyRef.current[historyRef.current.length - 1].score,
    finalLevel: historyRef.current[historyRef.current.length - 1].level,
    reassessCount: reassessCountRef.current,
  } : null;

  const complaintArtifact = advice?.complaint_draft
    ? {
        id: "cab-complaint",
        type: "complaint_letter",
        title: "Cab Safety Complaint Draft",
        domain: "protection",
        content: advice.complaint_draft,
        format: "markdown",
        created_at: Date.now() / 1000,
        metadata: { source: "cab_safety_mode" },
      }
    : null;

  // ── Render ──────────────────────────────────────────────────────────────────

  return (
    <div className="p-8 max-w-4xl mx-auto">
      {/* Back link */}
      <Link
        to="/protection"
        className="inline-flex items-center gap-1.5 text-xs text-gray-500 hover:text-gray-300 mb-6 transition-colors"
      >
        <ChevronLeft size={14} />
        Back to Protection
      </Link>

      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-8"
      >
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-red-900/30 border border-red-700/30 text-red-300 text-sm font-medium mb-4">
          <Car size={14} />
          Cab Safety Intelligence Mode
        </div>
        <h1 className="text-4xl font-extrabold text-white mb-3 leading-tight">
          Assess Your{" "}
          <span className="gradient-text">Ride Safety</span>
        </h1>
        <p className="text-gray-400 max-w-xl mx-auto text-sm leading-relaxed">
          Enter your ride details and flag any concerning behaviour. SHE-ORACLE will instantly score
          your risk level and generate an emergency response plan, a safe exit strategy, and a
          formal complaint draft.
        </p>
      </motion.div>

      {/* Privacy notice */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.1 }}
        className="flex items-start gap-3 p-4 rounded-xl bg-blue-900/20 border border-blue-700/30 mb-6 text-sm text-blue-300"
      >
        <Info size={16} className="mt-0.5 flex-shrink-0" />
        <span>
          No data is stored. All processing is discarded immediately after assessment.
          Safe to use even in a moving vehicle.
        </span>
      </motion.div>

      {/* ── CLOSED MODE ─────────────────────────────────────────────────────── */}
      <AnimatePresence mode="wait">
        {mode === "closed" && closureSummary && (
          <motion.div key="closed" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            <RideClosure
              summary={closureSummary}
              form={form}
              advice={advice}
              onStartNew={handleStartNew}
            />
          </motion.div>
        )}

        {/* ── ASSESSING / MONITORING MODES ──────────────────────────────────── */}
        {mode !== "closed" && (
          <motion.div key="active" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>

            {/* Mode status header (monitoring only) */}
            <ModeHeader
              mode={mode}
              riskLevel={riskLevel}
              onEndRide={handleEndRide}
            />

            {/* Input Form */}
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.15 }}
              className="glass rounded-2xl p-6 mb-6 space-y-6"
            >
              {/* Ride Details */}
              <div>
                <h2 className="text-sm font-semibold text-gray-300 mb-4 flex items-center gap-2">
                  <Car size={14} className="text-red-400" />
                  Ride Details
                </h2>
                <div className="grid sm:grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs text-gray-500 mb-1">Driver Name</label>
                    <input
                      type="text"
                      value={form.driver_name}
                      onChange={(e) => set("driver_name", e.target.value)}
                      placeholder="From Ola/Uber app"
                      className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2.5 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-red-500/50 transition-colors"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-gray-500 mb-1">Vehicle Plate</label>
                    <input
                      type="text"
                      value={form.vehicle_plate}
                      onChange={(e) => set("vehicle_plate", e.target.value.toUpperCase())}
                      placeholder="e.g. MH02AB1234"
                      className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2.5 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-red-500/50 transition-colors font-mono"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-gray-500 mb-1">Pickup Location</label>
                    <input
                      type="text"
                      value={form.pickup}
                      onChange={(e) => set("pickup", e.target.value)}
                      placeholder="e.g. Andheri Station"
                      className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2.5 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-red-500/50 transition-colors"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-gray-500 mb-1">Destination</label>
                    <input
                      type="text"
                      value={form.destination}
                      onChange={(e) => set("destination", e.target.value)}
                      placeholder="e.g. Bandra West"
                      className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2.5 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-red-500/50 transition-colors"
                    />
                  </div>
                </div>
              </div>

              {/* Time of Day */}
              <div>
                <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wide mb-3">
                  Time of Ride
                </label>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                  {TIME_OPTIONS.map((opt) => (
                    <button
                      key={opt.value}
                      type="button"
                      onClick={() => set("time_of_day", opt.value)}
                      className={`px-3 py-3 rounded-xl border text-left transition-all ${
                        form.time_of_day === opt.value
                          ? "bg-red-900/40 border-red-600/60 text-white"
                          : "bg-white/3 border-white/8 text-gray-400 hover:bg-white/6 hover:text-gray-300"
                      }`}
                    >
                      <div className="text-sm font-medium">{opt.label}</div>
                      <div className="text-xs text-gray-500 mt-0.5">{opt.sub}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Area Type */}
              <div>
                <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wide mb-3">
                  Area Type
                </label>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                  {AREA_OPTIONS.map((opt) => (
                    <button
                      key={opt.value}
                      type="button"
                      onClick={() => set("area_type", opt.value)}
                      className={`px-3 py-3 rounded-xl border text-left transition-all ${
                        form.area_type === opt.value
                          ? "bg-red-900/40 border-red-600/60 text-white"
                          : "bg-white/3 border-white/8 text-gray-400 hover:bg-white/6 hover:text-gray-300"
                      }`}
                    >
                      <div className="text-sm font-medium">{opt.label}</div>
                      <div className="text-xs text-gray-500 mt-0.5">{opt.sub}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Behaviour Flags */}
              <div>
                <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wide mb-3">
                  What's happening?{" "}
                  <span className="text-gray-600 font-normal normal-case">(check all that apply)</span>
                </label>
                <BehaviourFlags selected={flags} onChange={setFlags} />
              </div>

              {/* Submit */}
              <button
                onClick={handleAssess}
                disabled={isLoading}
                className="w-full flex items-center justify-center gap-2 px-6 py-4 rounded-xl bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-500 hover:to-rose-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold text-sm transition-all"
              >
                {isLoading ? (
                  <><Loader2 size={16} className="animate-spin" /> Assessing your safety...</>
                ) : (
                  <><Shield size={16} /> Assess My Safety</>
                )}
              </button>

              {error && (
                <div className="p-3 rounded-lg bg-red-900/30 border border-red-700/40 text-red-400 text-xs">
                  {error}
                </div>
              )}
            </motion.div>

            {/* Results */}
            <AnimatePresence>
              {result && (
                <motion.div
                  initial={{ opacity: 0, y: 15 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="space-y-5"
                >
                  {/* Risk Banner */}
                  <div className={`flex items-start gap-3 p-4 rounded-xl border ${banner.bg}`}>
                    <BannerIcon size={18} className={`${banner.text} flex-shrink-0 mt-0.5`} />
                    <p className={`text-sm font-medium ${banner.text}`}>{banner.msg}</p>
                  </div>

                  {/* Risk Score + delta */}
                  <div className={`glass rounded-xl p-5 border ${cfg.border}`}>
                    <div className="flex items-center justify-between gap-4">
                      <div className="flex-1">
                        <div className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1 flex items-center gap-2">
                          Risk Assessment Score
                          {/* Score delta badge after reassessment */}
                          {scoreDelta && (
                            <span className={`text-xs px-2 py-0.5 rounded-full font-bold border ${
                              scoreDelta.direction === "down"
                                ? "bg-green-900/40 text-green-400 border-green-700/40"
                                : "bg-red-900/40 text-red-400 border-red-700/40"
                            }`}>
                              {scoreDelta.direction === "down" ? "↓" : "↑"} {scoreDelta.value} pts
                            </span>
                          )}
                        </div>
                        <div className="text-sm text-gray-300">
                          {risk.triggered_factors?.length > 0
                            ? `${risk.triggered_factors.length} risk factor${risk.triggered_factors.length > 1 ? "s" : ""} detected`
                            : "No significant risk factors detected"}
                        </div>
                        {risk.triggered_factors?.length > 0 && (
                          <ul className="mt-2 space-y-1">
                            {risk.triggered_factors.map((f, i) => (
                              <li key={i} className="flex items-start gap-1.5 text-xs text-gray-400">
                                <span className="text-red-400 mt-0.5">•</span>
                                {f}
                              </li>
                            ))}
                          </ul>
                        )}
                      </div>
                      <SeverityMeter score={risk.score} level={risk.level} />
                    </div>
                  </div>

                  {/* Risk Breakdown */}
                  <RiskBreakdown
                    weightBreakdown={risk.weight_breakdown}
                    totalScore={risk.score}
                  />

                  {/* Immediate Actions */}
                  {advice?.immediate_actions?.length > 0 && (
                    <div className="glass rounded-xl p-5">
                      <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
                        <AlertTriangle size={14} className="text-orange-400" />
                        Immediate Actions
                      </h3>
                      <ol className="space-y-2">
                        {advice.immediate_actions.map((action, i) => (
                          <li key={i} className="flex items-start gap-3 text-sm text-gray-300">
                            <span className={`flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                              i === 0
                                ? "bg-red-900/50 border border-red-700/50 text-red-400"
                                : "bg-white/8 border border-white/10 text-gray-400"
                            }`}>
                              {i + 1}
                            </span>
                            {action}
                          </li>
                        ))}
                      </ol>
                    </div>
                  )}

                  {/* Safe Exit Strategy */}
                  <SafeExitPanel
                    safeExit={risk?.safe_exit_strategy}
                    riskLevel={riskLevel}
                  />

                  {/* Emergency Share */}
                  <div>
                    <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-3 px-1">
                      Emergency Share
                    </h3>
                    <EmergencySharePanel
                      emergencyMessage={advice?.emergency_message}
                      safetyCard={advice?.safety_card}
                    />
                  </div>

                  {/* De-escalation Panel (monitoring mode only) */}
                  {mode === "monitoring" && (
                    <DeescalationPanel
                      form={form}
                      flags={flags}
                      onReassess={handleReassess}
                      isReassessing={isReassessing}
                    />
                  )}

                  {/* Escalation Timeline */}
                  {advice?.escalation_steps?.length > 0 && (
                    <div className="glass rounded-xl p-5">
                      <h3 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
                        <Shield size={14} className="text-red-400" />
                        Escalation Path
                      </h3>
                      <EscalationTimeline steps={advice.escalation_steps} />
                    </div>
                  )}

                  {/* Complaint Draft */}
                  {complaintArtifact && (
                    <div>
                      <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-3 px-1">
                        Complaint Document
                      </h3>
                      <ArtifactPanel artifact={complaintArtifact} sessionId={null} />
                    </div>
                  )}

                  {/* Helplines */}
                  {advice?.helplines?.length > 0 && (
                    <div className="glass rounded-xl p-5">
                      <h3 className="text-sm font-semibold text-white mb-4">Emergency Helplines</h3>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                        {advice.helplines.map((h, i) => (
                          <div key={i} className="p-3 rounded-lg bg-gray-900/60 border border-white/10">
                            <div className="text-xs font-bold text-white">{h.name}</div>
                            <div className="text-sm font-mono text-red-300 my-1">{h.number}</div>
                            <div className="text-xs text-gray-500">{h.purpose}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* End Ride (bottom shortcut) */}
                  {mode === "monitoring" && (
                    <button
                      onClick={handleEndRide}
                      className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-green-900/20 hover:bg-green-900/35 border border-green-700/30 text-green-400 hover:text-green-300 text-sm font-medium transition-all"
                    >
                      <CheckCircle2 size={15} />
                      I've arrived safely — End Ride
                    </button>
                  )}
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
