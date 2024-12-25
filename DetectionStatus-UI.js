import React, { useState, useEffect } from 'react';

function DetectionStatus() {
  const [message, setMessage] = useState('Loading...');
  const [error, setError] = useState(null);
  const [imageUrl, setImageUrl] = useState('');
  const [selectedObject, setSelectedObject] = useState(() => {
    return localStorage.getItem('selectedObject') || 'cup';
  });

  const objects = [
    "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train",
    "truck", "boat", "traffic light", "fire hydrant", "cup", "bowl", "bottle"
    // Add the full list of objects here
  ];

  const handleObjectChange = (event) => {
    const newObject = event.target.value;
    setSelectedObject(newObject);
    localStorage.setItem('selectedObject', newObject);
  };

  useEffect(() => {
    const fetchStatus = () => {
      fetch(`http://192.168.4.182:5000/status?object=${selectedObject}`)
        .then((response) => {
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          return response.json();
        })
        .then((data) => {
          if (data.message) {
            setMessage(data.message);
          } else {
            setMessage('No status available');
          }

          if (data.imageUrl) {
            setImageUrl(data.imageUrl);
          } else {
            setImageUrl('');
          }

          setError(null);
        })
        .catch((err) => {
          setError('Failed to fetch detection status');
          setMessage(null);
          setImageUrl('');
        });
    };

    fetchStatus();
    const intervalId = setInterval(fetchStatus, 5000);

    return () => clearInterval(intervalId);
  }, [selectedObject]);

  return (
    <div>
      <div className="header-bar">Object Detection Status</div>
      <div className="dropdown-container">
        <label htmlFor="object-select">Select Object:</label>
        <select
          id="object-select"
          value={selectedObject}
          onChange={handleObjectChange}
        >
          {objects.map((obj) => (
            <option key={obj} value={obj}>
              {obj}
            </option>
          ))}
        </select>
      </div>
      <div
        className={`notification ${
          error
            ? 'notification-error'
            : message && message.includes('missing!')
            ? 'notification-warning'
            : message
            ? 'notification-success'
            : 'notification-warning' // Default warning if message is undefined or null
        }`}
       >
       {error || message || 'No status available'}
      </div>

      <div className="image-container">
        {imageUrl ? (
          <img src={imageUrl} alt={message || 'Detection Result'} className="detected-image" />
        ) : (
          <p>No image available</p>
        )}
      </div>
    </div>
  );
}

export default DetectionStatus;
