
function Navbar({ pageTitle }) {
  return (
    <header className="navbar">
      <div className="navbar-heading">
        <span className="breadcrumb">Workspace /</span>
        <h2>{pageTitle}</h2>
      </div>

      <div className="navbar-actions">
        <div className="status-indicator">
          <span className="status-dot"></span>
          System Online
        </div>

        <div className="profile">
          <div className="profile-avatar">U</div>
          <div className="profile-details">
            <strong>User</strong>
            <span>Free Account</span>
          </div>
        </div>
      </div>
    </header>
  );
}

export default Navbar;