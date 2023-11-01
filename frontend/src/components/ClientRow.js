import React from 'react';
import Visualization from './Visualization';

function ClientRow({ client, setClients, commonRate, isRunning }) { // isRunning prop is added
  const deleteClient = id => {
    setClients(prevClients => prevClients.filter(c => c.id !== id));
  };

  const updateRate = (id, newRate) => {
    setClients(prevClients => prevClients.map(c => (c.id === id ? { ...c, rate: newRate } : c)));
  };

  return (
    <tr>
      <td>{client.name}</td>
      <td>
        <input
          type="range"
          min="0"
          max={commonRate > 40 ? 3 * commonRate : 120}
          value={client.rate}
          onChange={e => updateRate(client.id, Number(e.target.value))}
          disabled={isRunning} // Slider is disabled when the process is running
        />
        <span>{client.rate}</span>
      </td>
      <td>
        <Visualization client={client} />
      </td>
      <td>
        <button onClick={() => deleteClient(client.id)} disabled={isRunning}>Delete</button> {/* Delete button is disabled when the process is running */}
        {/* Add more actions here if needed */}
      </td>
    </tr>
  );
}

export default ClientRow;
