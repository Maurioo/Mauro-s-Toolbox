import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import Header from './components/Header';
import NBADashboard from './components/NBADashboard';
import './App.css';

const AppContainer = styled.div`
  background: linear-gradient(135deg, #17408B 0%, #C9082A 100%);
  color: #fff;
  font-family: 'Roboto', Arial, sans-serif;
  margin: 0;
  min-height: 100vh;
`;

const MainContent = styled.main`
  width: 100vw;
  max-width: 100vw;
  background: rgba(23, 64, 139, 0.95);
  margin: 0;
  border-radius: 0;
  box-shadow: none;
  padding: 2rem 2vw;
  display: flex;
  flex-wrap: wrap;
  gap: 2rem;
  justify-content: space-between;
`;

function App() {
  const [apiStatus, setApiStatus] = useState('checking');

  useEffect(() => {
    // Check if Flask API is running
    fetch('http://localhost:5000/api/health')
      .then(response => response.json())
      .then(data => {
        if (data.status === 'healthy') {
          setApiStatus('connected');
        } else {
          setApiStatus('error');
        }
      })
      .catch(error => {
        console.error('API connection error:', error);
        setApiStatus('error');
      });
  }, []);

  return (
    <AppContainer>
      <Header />
      <MainContent>
        <NBADashboard apiStatus={apiStatus} />
      </MainContent>
    </AppContainer>
  );
}

export default App; 