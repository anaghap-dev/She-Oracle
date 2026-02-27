import { useState, useEffect } from "react";
import { Send, Loader2, X, MessageSquarePlus } from "lucide-react";

const DOMAINS = [
  { value: "general",   label: "General"   },
  { value: "career",    label: "Career"    },
  { value: "legal",     label: "Legal"     },
  { value: "financial", label: "Financial" },
  { value: "education", label: "Education" },
  { value: "grants",    label: "Grants"    },
];

const EXAMPLE_GOALS = [
  "I want to launch a sustainable fashion startup and find funding",
  "My employer is not paying me maternity leave. What are my rights?",
  "I want to achieve financial independence within 3 years as a freelance designer",
  "Help me find scholarships for my MBA in data science",
  "I faced workplace sexual harassment and don't know what to do",
];

export default function GoalInput({ onSubmit, isLoading, defaultDomain = "general", hideDomainSelector = false, prefillValue = "" }) {
  const [goal, setGoal] = useState("");
  const [domain, setDomain] = useState(defaultDomain);
  const [hasSubmitted, setHasSubmitted] = useState(false);

  useEffect(() => {
    if (prefillValue) {
      setGoal(prefillValue);
      setHasSubmitted(false);
    }
  }, [prefillValue]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!goal.trim() || isLoading) return;
    setHasSubmitted(true);
    onSubmit({ goal: goal.trim(), domain });
  };

  const useExample = (example) => {
    setGoal(example);
  };

  const showEmptyState = hideDomainSelector && !hasSubmitted && !goal.trim();

  return (
    <div className="space-y-4">
      {/* Empty state hint — shown on section pages before first interaction */}
      {showEmptyState && (
        <div className="flex flex-col items-center gap-2 py-4 text-center">
          <div className="w-10 h-10 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center mb-1">
            <MessageSquarePlus size={18} className="text-gray-500" />
          </div>
          <p className="text-sm font-medium text-gray-300">Describe your situation</p>
          <p className="text-xs text-gray-500 max-w-xs">
            Be as specific as possible. The more context you give, the more tailored your plan will be.
          </p>
        </div>
      )}

      {/* Domain selector — only shown on Dashboard */}
      {!hideDomainSelector && (
        <div className="flex flex-wrap gap-2">
          {DOMAINS.map((d) => (
            <button
              key={d.value}
              onClick={() => setDomain(d.value)}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
                domain === d.value
                  ? "bg-oracle-600 text-white"
                  : "bg-white/5 text-gray-400 hover:bg-white/10 hover:text-white"
              }`}
            >
              {d.label}
            </button>
          ))}
        </div>
      )}

      {/* Main input */}
      <form onSubmit={handleSubmit} className="relative">
        <textarea
          value={goal}
          onChange={(e) => setGoal(e.target.value)}
          placeholder="Describe your goal in detail... (e.g. 'I want to start a food business and need funding and legal guidance')"
          rows={3}
          className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 pr-14 text-white placeholder-gray-500 resize-none focus:outline-none focus:border-oracle-500 focus:ring-1 focus:ring-oracle-500 transition-all text-sm"
          onKeyDown={(e) => {
            if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) handleSubmit(e);
          }}
        />
        <div className="absolute right-3 bottom-3 flex items-center gap-2">
          {goal && (
            <button
              type="button"
              onClick={() => setGoal("")}
              className="text-gray-500 hover:text-gray-300 transition-colors"
            >
              <X size={16} />
            </button>
          )}
          <button
            type="submit"
            disabled={!goal.trim() || isLoading}
            className="w-9 h-9 rounded-lg bg-oracle-600 hover:bg-oracle-500 disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center transition-all"
          >
            {isLoading ? (
              <Loader2 size={16} className="text-white animate-spin" />
            ) : (
              <Send size={15} className="text-white" />
            )}
          </button>
        </div>
      </form>

      {/* Example goals — only on Dashboard */}
      {!hideDomainSelector && (
        <div className="space-y-1.5">
          <p className="text-xs text-gray-600 font-medium uppercase tracking-wide">Try an example</p>
          <div className="flex flex-wrap gap-2">
            {EXAMPLE_GOALS.slice(0, 3).map((eg, i) => (
              <button
                key={i}
                onClick={() => useExample(eg)}
                className="text-xs text-gray-400 hover:text-oracle-300 bg-white/3 hover:bg-oracle-900/30 border border-white/5 hover:border-oracle-700/30 px-2.5 py-1 rounded-lg transition-all text-left max-w-xs truncate"
              >
                {eg}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
