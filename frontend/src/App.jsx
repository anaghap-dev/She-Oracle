import { Routes, Route } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import Dashboard from "./pages/Dashboard";
import CareerPage from "./pages/CareerPage";
import LegalPage from "./pages/LegalPage";
import FinancialPage from "./pages/FinancialPage";
import EducationPage from "./pages/EducationPage";
import GrantsPage from "./pages/GrantsPage";
import ProtectionPage from "./pages/ProtectionPage";
import CabSafetyPage from "./pages/CabSafetyPage";

export default function App() {
  return (
    <div className="flex h-screen overflow-hidden bg-gray-950">
      <Sidebar />
      <main className="flex-1 overflow-y-auto scrollbar-thin">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/career" element={<CareerPage />} />
          <Route path="/legal" element={<LegalPage />} />
          <Route path="/financial" element={<FinancialPage />} />
          <Route path="/education" element={<EducationPage />} />
          <Route path="/grants" element={<GrantsPage />} />
          <Route path="/protection" element={<ProtectionPage />} />
          <Route path="/protection/cab-safety" element={<CabSafetyPage />} />
        </Routes>
      </main>
    </div>
  );
}
