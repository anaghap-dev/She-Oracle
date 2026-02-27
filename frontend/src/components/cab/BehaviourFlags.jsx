const FLAGS = [
  { id: "route_deviation",    label: "Driver taking wrong or unfamiliar route",       risk: "HIGH" },
  { id: "doors_locked",       label: "Doors locked / central locking activated",       risk: "HIGH" },
  { id: "cancel_app",         label: "Driver asked to cancel app or go offline",        risk: "HIGH" },
  { id: "aggressive",         label: "Driver aggressive or appears intoxicated",        risk: "HIGH" },
  { id: "personal_questions", label: "Driver asking personal questions",                risk: "MEDIUM" },
  { id: "phone_distracted",   label: "Driver distracted / on phone while driving",     risk: "MEDIUM" },
  { id: "speeding",           label: "Driving erratically or speeding",                risk: "MEDIUM" },
  { id: "uncomfortable",      label: "General discomfort / gut feeling",               risk: "MEDIUM" },
];

const riskColors = {
  HIGH:   "text-red-400 bg-red-900/20 border-red-700/40",
  MEDIUM: "text-yellow-400 bg-yellow-900/20 border-yellow-700/40",
};

export default function BehaviourFlags({ selected, onChange }) {
  const toggle = (id) => {
    if (selected.includes(id)) {
      onChange(selected.filter((f) => f !== id));
    } else {
      onChange([...selected, id]);
    }
  };

  return (
    <div className="space-y-2">
      {FLAGS.map((flag) => {
        const isChecked = selected.includes(flag.id);
        return (
          <button
            key={flag.id}
            type="button"
            onClick={() => toggle(flag.id)}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl border text-left transition-all ${
              isChecked
                ? "bg-red-900/30 border-red-600/50 text-white"
                : "bg-white/3 border-white/8 text-gray-400 hover:bg-white/6 hover:text-gray-300 hover:border-white/15"
            }`}
          >
            {/* Checkbox */}
            <div className={`flex-shrink-0 w-5 h-5 rounded-md border-2 flex items-center justify-center transition-all ${
              isChecked ? "bg-red-600 border-red-500" : "border-gray-600"
            }`}>
              {isChecked && (
                <svg width="10" height="8" viewBox="0 0 10 8" fill="none">
                  <path d="M1 4L3.5 6.5L9 1" stroke="white" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              )}
            </div>

            {/* Label */}
            <span className="flex-1 text-sm">{flag.label}</span>

            {/* Risk badge */}
            <span className={`flex-shrink-0 text-xs font-semibold px-2 py-0.5 rounded-full border ${riskColors[flag.risk]}`}>
              {flag.risk}
            </span>
          </button>
        );
      })}
    </div>
  );
}
