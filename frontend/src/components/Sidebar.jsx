import { NavLink } from "react-router-dom";
import { motion } from "framer-motion";
import {
  LayoutDashboard,
  Briefcase,
  Scale,
  TrendingUp,
  GraduationCap,
  Landmark,
  Sparkles,
  ShieldAlert,
  Car,
} from "lucide-react";

const navItems = [
  { to: "/",           icon: LayoutDashboard, label: "Dashboard",   color: "text-oracle-400" },
  {
    to: "/protection", icon: ShieldAlert, label: "Protection", color: "text-rose-400",
    children: [
      { to: "/protection/cab-safety", icon: Car, label: "Cab Safety", color: "text-red-400" },
    ],
  },
  { to: "/career",     icon: Briefcase,        label: "Career",      color: "text-blue-400"   },
  { to: "/legal",      icon: Scale,            label: "Legal Rights",color: "text-red-400"    },
  { to: "/financial",  icon: TrendingUp,       label: "Financial",   color: "text-green-400"  },
  { to: "/education",  icon: GraduationCap,    label: "Education",   color: "text-yellow-400" },
  { to: "/grants",     icon: Landmark,         label: "Grants",      color: "text-pink-400"   },
];

export default function Sidebar() {
  return (
    <aside className="w-64 flex-shrink-0 bg-gray-900 border-r border-white/10 flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-white/10">
        <div className="flex items-center gap-3">
          <img src="/oracle-icon.png" alt="SHE-ORACLE logo" className="w-9 h-9 rounded-xl" />
          <div>
            <h1 className="font-bold text-lg leading-tight gradient-text">SHE-ORACLE</h1>
            <p className="text-xs text-gray-500">AI Strategist for Women</p>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 p-4 space-y-1">
        {navItems.map(({ to, icon: Icon, label, color, children }) => (
          <div key={to}>
            <NavLink
              to={to}
              end={to === "/"}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 group ${
                  isActive
                    ? "bg-oracle-900/60 text-white border border-oracle-700/40"
                    : "text-gray-400 hover:text-white hover:bg-white/5"
                }`
              }
            >
              {({ isActive }) => (
                <>
                  <Icon size={18} className={isActive ? color : "text-gray-500 group-hover:text-gray-300"} />
                  <span>{label}</span>
                  {isActive && (
                    <motion.div
                      layoutId="active-dot"
                      className="ml-auto w-1.5 h-1.5 rounded-full bg-oracle-400"
                    />
                  )}
                </>
              )}
            </NavLink>

            {/* Sub-items */}
            {children?.map(({ to: childTo, icon: ChildIcon, label: childLabel, color: childColor }) => (
              <NavLink
                key={childTo}
                to={childTo}
                className={({ isActive }) =>
                  `flex items-center gap-3 pl-9 pr-3 py-2 rounded-xl text-xs font-medium transition-all duration-200 group mt-0.5 ${
                    isActive
                      ? "bg-red-900/40 text-white border border-red-700/30"
                      : "text-gray-500 hover:text-gray-300 hover:bg-white/4"
                  }`
                }
              >
                {({ isActive }) => (
                  <>
                    <ChildIcon size={14} className={isActive ? childColor : "text-gray-600 group-hover:text-gray-400"} />
                    <span>{childLabel}</span>
                  </>
                )}
              </NavLink>
            ))}
          </div>
        ))}
      </nav>

    </aside>
  );
}
