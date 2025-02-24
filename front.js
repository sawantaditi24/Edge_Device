import React, { useState, useEffect } from 'react';

function SceneChangeDetection() {
  const [status, setStatus] = useState('Monitoring scene...');
  const [imageUrl, setImageUrl] = useState('');
  const [changes, setChanges] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStatus = () => {
      fetch('http://192.168.4.229:5000/scene-status')
        .then((response) => {
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          return response.json();
        })
        .then((data) => {
          setStatus(data.status);
          setImageUrl(data.imageUrl);
          setChanges(data.changes || []);
          setError(null);
        })
        .catch((err) => {
          setError('Failed to fetch scene status');
          setStatus(null);
          setImageUrl('');
          setChanges([]);
        });
    };

    fetchStatus();
    const intervalId = setInterval(fetchStatus, 2000); // Poll every 2 seconds

    return () => clearInterval(intervalId);
  }, []);

  return (
    <div className="max-w-2xl mx-auto p-4">
      <div className="bg-white shadow-lg rounded-lg overflow-hidden">
        <div className="bg-blue-600 text-white px-4 py-3">
          <h2 className="text-xl font-semibold">Scene Monitoring Status</h2>
        </div>

        <div className="p-4">
          <div className={`mb-4 p-3 rounded ${
            error ? 'bg-red-100 text-red-700' :
            status?.includes('Change detected') ? 'bg-yellow-100 text-yellow-700' :
            'bg-green-100 text-green-700'
          }`}>
          {error || status || 'Monitoring scene...'}
          </div>

          {changes.length > 0 && (
            <div className="mb-4">
              <h3 className="font-semibold mb-2">Recent Changes:</h3>
              <ul className="space-y-2">
                {changes.map((change, index) => (
                  <li key={index} className="flex items-center">
                    <span className="w-4 h-4 bg-yellow-400 rounded-full mr-2"></span>
                    {change}
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div className="border rounded-lg overflow-hidden">
            {imageUrl ? (
              <img 
                src={imageUrl} 
                alt="Scene Detection" 
                className="w-full h-auto"
              />
            ) : (
              <div className="h-64 flex items-center justify-center bg-gray-100">
                <p className="text-gray-500">No image available</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default SceneChangeDetection;
