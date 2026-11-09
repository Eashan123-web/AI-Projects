
import { useState } from "react";
import Sidebar from "./components/layout/Sidebar";
import Navbar from "./components/layout/Navbar";
import Dashboard from "./pages/Dashboard";
import ResumeUpload from "./components/resume/ResumeUpload";
import ResumeJobMatching from "./components/analysis/ResumeJobMatching";
import AnalysisHistory from "./pages/AnalysisHistory";
import "./styles/global.css";

function App() {
  const [activePage, setActivePage] = useState("Dashboard");

  return (<div className="app-layout">
      <Sidebar activePage={activePage}
        onNavigate={setActivePage}/>

      <div className="main-layout">
        <Navbar pageTitle={activePage} />

        <main className="main-content">
          {activePage === "Dashboard" && (<Dashboard onNavigate={setActivePage} />)}
          {activePage === "Resume Analysis" && (<ResumeUpload />)}
          {activePage === "Job Matching" && (<ResumeJobMatching />)}
          {activePage === "Analysis History" && <AnalysisHistory />}

          {!["Dashboard", "Resume Analysis", "Job Matching", "Analysis History"].includes(activePage) && (
            <div className="page-placeholder">
              <h1>{activePage}</h1>
              <p>This section will be developed in the upcoming steps.</p>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

export default App;