
const navigationItems = [
  { label: "Dashboard", icon: "▦" },
  { label: "Resume Analysis", icon: "📄" },
  { label: "Job Matching", icon: "🎯" },
  { label: "Recommendations", icon: "✦" },
  { label: "Analysis History", icon: "◷" },
];

function Sidebar({ activePage, onNavigate }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="brand-logo">AI</div>
        <div>
          <h2>ResumeAI</h2>
          <span>Career Intelligence</span>
        </div>
      </div>

      <div className="sidebar-section-label">WORKSPACE</div>

      <nav className="sidebar-nav">
        {navigationItems.map((item) => (
          <button
            key={item.label}
            className={`nav-item ${
              activePage === item.label ? "active" : ""
            }`}
            onClick={() => onNavigate(item.label)}>
            <span className="nav-icon">{item.icon}</span>
            <span>{item.label}</span>
          </button>
        ))}
      </nav>

      <div className="sidebar-bottom">
        <div className="sidebar-help">
          <div className="help-icon">?</div>
          <div>
            <strong>Need help?</strong>
            <span>Explore how it works</span>
          </div>
        </div>

        <div className="sidebar-version">AI Resume Analyzer · v1.0</div>
      </div>
    </aside>
  );
}

export default Sidebar;