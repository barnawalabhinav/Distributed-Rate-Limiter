import React from 'react';
import ClientRow from './ClientRow';

function ClientTable({ clients, setClients, commonRate, isRunning }) { // isRunning prop is added
  const addClient = () => {
    const newId = clients.length ? Math.max(...clients.map(c => c.id)) + 1 : 1;
    setClients([...clients, { id: newId, name: `Client ${newId}`, rate: 1 }]);
  };

  return (
    <div>
      <button onClick={addClient} disabled={isRunning}>Add Client</button> {/* Disable based on isRunning */}
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Rate Control</th>
            <th>Request Visualization</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {clients.map(client => (
            <ClientRow 
              key={client.id} 
              client={client} 
              setClients={setClients} 
              commonRate={commonRate} 
              isRunning={isRunning} // Pass isRunning prop
            />
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default ClientTable;
