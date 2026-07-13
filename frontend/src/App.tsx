import { Route, Routes } from "react-router-dom";
import { Chrome } from "./components/Chrome";
import { Dashboard } from "./views/Dashboard";
import { AgentDetail } from "./views/AgentDetail";
import { Recommend } from "./views/Recommend";

export default function App() {
  return (
    <Chrome>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/agent/:agentName" element={<AgentDetail />} />
        <Route path="/recommend" element={<Recommend />} />
        <Route path="*" element={<Dashboard />} />
      </Routes>
    </Chrome>
  );
}
