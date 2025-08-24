import React, { useState, useEffect } from 'react';
import './App.css';
import { healthCheck, getHello } from './services/api';

function App() {
  const [backendStatus, setBackendStatus] = useState<string>('Checking...');
  const [message, setMessage] = useState<string>('');

  useEffect(() => {
    const checkBackend = async () => {
      try {
        const healthResponse = await healthCheck();
        setBackendStatus(healthResponse.data.status);
        
        const helloResponse = await getHello();
        setMessage(helloResponse.data.message);
      } catch (error) {
        setBackendStatus('Backend not connected');
        setMessage('Unable to connect to Flask backend');
      }
    };

    checkBackend();
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <h1>Full Stack App</h1>
        <div>
          <h2>Backend Status: {backendStatus}</h2>
          <p>{message}</p>
        </div>
        <div>
          <h3>React Frontend + Flask Backend</h3>
          <p>Your full-stack application is ready!</p>
        </div>
      </header>
    </div>
  );
}

export default App;
