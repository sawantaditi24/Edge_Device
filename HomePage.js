import React from 'react';
import { Link } from 'react-router-dom';

function HomePage() {
  return (
    <div className="home-page">
      <div className="header-bar">
        ObjectFaceVision
      </div>
      <div className="card">
        <div className="card-title">
         What would you like to do today?
        </div>
       <div className="card-options">
        <div className="options">
        <Link to="/detection-status">
          <button className="card-button">Object Detection</button>
        </Link>
        {/* Add other detection options if needed */}
        <Link to="/face-recognition">
          <button className="card-button">Face Recognition</button>
        </Link>
        <Link to="/feature-recognition">
          <button className="card-button">Feature Recognition</button>
        </Link> 
      </div>
      </div>
     </div>
    </div>
  );
}

export default HomePage;

