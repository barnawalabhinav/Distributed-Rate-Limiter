import React, { useState, useEffect } from 'react';

function Visualization({ client }) {
  const [requests, setRequests] = useState([]);

  useEffect(() => {
    const interval = setInterval(() => {
      const newRequest = Math.random() > 0.5 ? 'accepted' : 'rejected';
      setRequests(prev => [...prev, newRequest].slice(-30)); // keep the last 30 requests
    }, 1000 * client.rate); // Adjust the interval based on the client's rate

    return () => clearInterval(interval);
  }, [client.rate]);

  return (
    <div className="visualization">
      {requests.map((status, index) => (
        <span
          key={index}
          className={`request-dot ${status}`}
          title={status}
        ></span>
      ))}
    </div>
  );
}

export default Visualization;
