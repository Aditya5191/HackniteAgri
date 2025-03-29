import React from "react";
import { Link } from "react-router-dom";

const Header = () => {
  return (
    <header className="header">
      {/* Wrapper to Center Content */}
      <div className="header-wrapper">
        {/* Header Content with Logo and Nav Links */}
        <div className="header-content">
          {/* Logo */}
          <img
            src="/logo.png" // Replace with the path to your logo
            alt="Logo"
            className="logo"
          />
          {/* Navigation Links */}
          <nav className="nav-links">
            <Link to="/" className="nav-link">Live Stats</Link>
            <Link to="/satellite-data" className="nav-link">Satellite Data</Link>
            <Link to="/crop-disease-management" className="nav-link">Crop Disease Management</Link>
          </nav>
        </div>
      </div>
    </header>
  );
};

export default Header;