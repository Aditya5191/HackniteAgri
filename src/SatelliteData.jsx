import React from "react";
import Header from "./Header"; // Import the Header component

const SatelliteData = () => {
  return (
    <div>
      {/* Include the Header */}
      <Header />

      {/* Main Content */}
      <div className="container" style={{ paddingTop: "60px" }}>
        <h1>Satellite Data</h1>
        <p>This page will display satellite imagery and related data.</p>
      </div>
    </div>
  );
};

export default SatelliteData;