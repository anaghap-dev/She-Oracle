// Human-readable labels for factor keys (mirrors cab_risk_scorer.py)
const FACTOR_LABELS = {
  time_of_day:          "Time of day",
  area_type:            "Area type",
  missing_driver_info:  "Driver info missing",
  route_deviation:      "Route deviation",
  doors_locked:         "Doors locked",
  cancel_app:           "Asked to cancel app",
  aggressive:           "Aggressive / intoxicated",
  personal_questions:   "Personal questions",
  phone_distracted:     "Phone distracted",
  speeding:             "Erratic driving",
  uncomfortable:        "Discomfort / gut feeling",
};

// Max possible score per factor (for bar width %)
const FACTOR_MAX = {
  time_of_day:          20,
  area_type:            15,
  missing_driver_info:  10,
  route_deviation:      20,
  doors_locked:         15,
  cancel_app:           15,
  aggressive:           15,
  personal_questions:   10,
  phone_distracted:      5,
  speeding:              5,
  uncomfortable:         3,
};

function barColor(pts) {
  if (pts >= 15) return "bg-red-500";
  if (pts >= 10) return "bg-orange-500";
  if (pts >= 5)  return "bg-yellow-500";
  return "bg-green-500";
}

export default function RiskBreakdown({ weightBreakdown, totalScore }) {
  if (!weightBreakdown || Object.keys(weightBreakdown).length === 0) return null;

  const entries = Object.entries(weightBreakdown).sort((a, b) => b[1] - a[1]);

  return (
    <div className="glass rounded-xl p-5">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-gray-300">Risk Factor Breakdown</h3>
        <span className="text-xs text-gray-500">Total: {totalScore}/100</span>
      </div>

      <div className="space-y-3">
        {entries.map(([key, pts]) => {
          const max = FACTOR_MAX[key] || 20;
          const widthPct = Math.min(100, (pts / max) * 100);
          const label = FACTOR_LABELS[key] || key.replace(/_/g, " ");

          return (
            <div key={key}>
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs text-gray-400 capitalize">{label}</span>
                <span className="text-xs font-mono text-gray-300">+{pts} pts</span>
              </div>
              <div className="h-1.5 bg-white/8 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${barColor(pts)}`}
                  style={{ width: `${widthPct}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>

      <p className="text-xs text-gray-600 mt-4">
        Each factor contributes to your overall risk score based on weighted indicators.
      </p>
    </div>
  );
}
