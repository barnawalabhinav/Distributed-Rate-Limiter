import React from 'react';

function RateControl({ commonRate, setCommonRate, numServers, setNumServers, isRunning }) {
  return (
    <div>
      <h2>Rate Control</h2>
      <div>
        <label>Common Rate Limit:</label>
        <input
          type="number"
          value={commonRate}
          onChange={e => setCommonRate(Number(e.target.value))}
          disabled={isRunning} // Disable based on isRunning
        />
      </div>
      <div>
        <label>Number of Servers:</label>
        <input
          type="number"
          value={numServers}
          min="0"
          max="32"
          onChange={e => setNumServers(Number(e.target.value))}
          disabled={isRunning} // Disable based on isRunning
        />
      </div>
    </div>
  );
}

export default RateControl;
