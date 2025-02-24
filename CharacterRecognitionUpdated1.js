import React, { useState, useEffect } from "react";

function CharacterRecognitionUpdated1() {
  const [message, setMessage] = useState("Monitoring for text...");
  const [imageUrl, setImageUrl] = useState("");
  const [lastUpdate, setLastUpdate] = useState(null);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await fetch("http://192.168.4.229:5000/text-status");
        if (!response.ok) throw new Error("Network response was not ok");

        const data = await response.json();
        setMessage(data.message);
        setImageUrl(data.imageUrl);
        if (data.timestamp) {
          setLastUpdate(new Date(data.timestamp * 1000).toLocaleTimeString());
        }
      } catch (error) {
        setMessage("Failed to fetch text detection status.");
        setImageUrl("");
        setLastUpdate(null);
      }
    };

    const intervalId = setInterval(fetchStatus, 1000);
    return () => clearInterval(intervalId);
  }, []);

  return (
    <div>
      <h1>Character Recognition System</h1>
      <p>{message}</p>
      {lastUpdate && <p>Last update: {lastUpdate}</p>}
      {imageUrl ? <img src={imageUrl} alt="Text Detection" /> : <p>No image available</p>}
    </div>
  );
}

export default CharacterRecognitionUpdated1;


