export default function StatusBadge({ label, variant = "default" }) {
  const variants = {
    default: "bg-gray-800 text-gray-300",
    success: "bg-green-900/50 text-green-400 border border-green-700/30",
    warning: "bg-yellow-900/50 text-yellow-400 border border-yellow-700/30",
    error:   "bg-red-900/50 text-red-400 border border-red-700/30",
    oracle:  "bg-oracle-900/50 text-oracle-400 border border-oracle-700/30",
  };
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${variants[variant] || variants.default}`}>
      {label}
    </span>
  );
}
