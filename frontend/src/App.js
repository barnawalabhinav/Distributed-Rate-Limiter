import React, { useState, useEffect } from 'react';
import './App.css';
import ClientTable from './components/ClientTable';
import RateControl from './components/RateControl';
import axios from 'axios';

function App() {
    const [clients, setClients] = useState([]); 
    const [commonRate, setCommonRate] = useState(100);
    const [numServers, setNumServers] = useState(3);
    const [isRunning, setIsRunning] = useState(false);
    const [elapsedTime, setElapsedTime] = useState(0);

    const updateBackendConstants = () => {
        const clientRates = clients.map(client => client.rate);
        axios.post('http://localhost:5000/update_constants', {
            N_SERVERS: numServers,
            N_CLIENTS: clients.length,
            CLIENT_RATES: clientRates, // Sending client rates to the backend
        })
        .then(response => {
            console.log("Backend updated successfully:", response.data);
        })
        .catch(error => {
            console.error('Error updating constants:', error);
        });
    };

    useEffect(() => {
        let timer;
        if (isRunning) {
            timer = setInterval(() => {
                setElapsedTime(prevTime => prevTime + 100);
            }, 100);
        } else {
            setElapsedTime(0);
        }
        return () => clearInterval(timer);
    }, [isRunning]);

    useEffect(updateBackendConstants, [numServers, clients]);

    return (
        <div className="App">
            <h1>Distributed Rate Limiter</h1>
            <button 
                onClick={() => setIsRunning(prev => !prev)}
                style={{
                    backgroundColor: isRunning ? 'red' : 'green',
                    color: 'white',
                    padding: '10px 20px',
                    border: 'none',
                    borderRadius: '5px',
                    cursor: 'pointer',
                    fontSize: '16px'
                }}
            >
                {isRunning ? 'Stop' : 'Start'}
            </button>
            {isRunning && (
                <div className="timer">
                    Time: {Math.floor(elapsedTime / 60000)}:
                          {Math.floor((elapsedTime % 60000) / 1000)}.
                          {(elapsedTime % 1000)}
                </div>
            )}
            <RateControl 
                commonRate={commonRate} 
                setCommonRate={setCommonRate} 
                numServers={numServers} 
                setNumServers={setNumServers}
                isRunning={isRunning} 
            />
            <ClientTable clients={clients} setClients={setClients} isRunning={isRunning} />
        </div>
    );
}

export default App;
