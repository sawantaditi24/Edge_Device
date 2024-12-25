import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import DetectionStatus from './DetectionStatus50';
import FaceRecognition from './FaceRecognition';
import FeatureRecognition from './FeatureRecognition';
import HomePage from './HomePage';
import './styles.css';

function App() {
  return (
    <Router>
      <div>
        {/* Routes go here */}
        <Routes>
          {/* Home Page */}
          <Route exact path="/" element={<HomePage />} />
          
          {/* Object Detection */}
          <Route path="/detection-status" element={<DetectionStatus />} />
          
          {/* Future routes for other detection types */}
          <Route path="/face-recognition" element={<FaceRecognition />} /> 
          <Route path="/feature-recognition" element={<FeatureRecognition />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;

