import { MapPin, Clock, AlertOctagon, Navigation } from "lucide-react";

const levelColors = {
  LOW:      "border-green-700/40 bg-green-900/15",
  MODERATE: "border-yellow-700/40 bg-yellow-900/15",
  HIGH:     "border-orange-600/50 bg-orange-900/20",
  CRITICAL: "border-red-500/60 bg-red-900/25",
};

const timingColors = {
  LOW:      "text-green-400",
  MODERATE: "text-yellow-400",
  HIGH:     "text-orange-400",
  CRITICAL: "text-red-400",
};

export default function SafeExitPanel({ safeExit, riskLevel }) {
  if (!safeExit) return null;

  const borderBg = levelColors[riskLevel] || levelColors.MODERATE;
  const timingColor = timingColors[riskLevel] || timingColors.MODERATE;

  return (
    <div className={`glass rounded-xl overflow-hidden border ${borderBg}`}>
      {/* Header */}
      <div className="flex items-center gap-2 px-5 py-3 border-b border-white/8">
        <Navigation size={14} className="text-orange-400" />
        <span className="text-xs font-bold text-white uppercase tracking-wide">
          Recommended Safe Exit Strategy
        </span>
      </div>

      <div className="px-5 py-4 space-y-4">
        {/* Timing */}
        <div className="flex items-start gap-3">
          <Clock size={14} className={`${timingColor} flex-shrink-0 mt-0.5`} />
          <div>
            <p className="text-xs font-semibold text-gray-400 mb-0.5">When to exit</p>
            <p className={`text-sm font-medium ${timingColor}`}>{safeExit.timing_advice}</p>
          </div>
        </div>

        {/* Recommended spots */}
        <div className="flex items-start gap-3">
          <MapPin size={14} className="text-blue-400 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-xs font-semibold text-gray-400 mb-2">Exit near</p>
            <ul className="space-y-1.5">
              {safeExit.recommended_spots?.map((spot, i) => (
                <li key={i} className="flex items-start gap-2 text-xs text-gray-300">
                  <span className="text-blue-400 mt-0.5 flex-shrink-0">→</span>
                  {spot}
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* How to exit */}
        <div className="flex items-start gap-3 pt-1 border-t border-white/8">
          <AlertOctagon size={14} className="text-orange-400 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-xs font-semibold text-gray-400 mb-0.5">How to exit safely</p>
            <p className="text-xs text-gray-300 leading-relaxed">{safeExit.exit_signal}</p>
          </div>
        </div>

        {/* Avoid note */}
        {safeExit.avoid_note && (
          <div className="px-3 py-2 rounded-lg bg-red-900/20 border border-red-800/30">
            <p className="text-xs text-red-300">
              <span className="font-semibold">Avoid: </span>
              {safeExit.avoid_note}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
