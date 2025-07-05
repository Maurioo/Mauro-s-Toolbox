import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import axios from 'axios';
import PlayerStatsChart from './PlayerStatsChart';
import TeamStatsChart from './TeamStatsChart';
import PlayerList from './PlayerList';
import StatFilters from './StatFilters';

const DashboardContainer = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 2rem;
  justify-content: space-between;
`;

const Section = styled.section`
  flex: 1 1 400px;
  min-width: 350px;
  background: rgba(255,255,255,0.08);
  border-radius: 16px;
  padding: 2rem 2rem 2.5rem 2rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.10);
  margin-bottom: 2rem;
`;

const SectionTitle = styled.h2`
  font-family: 'Oswald', Arial, sans-serif;
  text-transform: uppercase;
  font-size: 2rem;
  margin-top: 0;
  margin-bottom: 1.5rem;
  letter-spacing: 1px;
  text-shadow: 1px 1px 0 #fff;
  background: #C9082A;
  color: #fff;
  padding: 0.7rem 2rem;
  border-radius: 8px;
  display: inline-block;
  font-weight: 700;
  box-shadow: 0 2px 8px rgba(23,64,139,0.10);
`;

const TrendsTable = styled.table`
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 1.5rem;
  
  th, td {
    border: 1px solid #ddd;
    padding: 0.5rem 0.7rem;
    text-align: center;
    background: rgba(255,255,255,0.10);
    color: #fff;
  }
  
  th {
    background: #C9082A;
    color: #fff;
    font-family: 'Oswald', Arial, sans-serif;
    font-size: 1.1rem;
  }
  
  tr:nth-child(even) td {
    background: rgba(255,255,255,0.07);
  }
`;

const LoadingMessage = styled.div`
  text-align: center;
  padding: 2rem;
  color: #fff;
  font-size: 1.1rem;
`;

const ErrorMessage = styled.div`
  background: #f8d7da;
  border: 1px solid #f5c6cb;
  color: #721c24;
  padding: 1rem;
  border-radius: 5px;
  margin-top: 1rem;
`;

const NBADashboard = ({ apiStatus }) => {
  const [currentStat, setCurrentStat] = useState('PPG');
  const [players, setPlayers] = useState([]);
  const [trendsData, setTrendsData] = useState([]);
  const [selectedPlayer, setSelectedPlayer] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Load initial data
  useEffect(() => {
    if (apiStatus === 'connected') {
      loadTopPlayers();
      loadTrendsData();
    }
  }, [apiStatus]);

  const loadTopPlayers = async () => {
    try {
      setLoading(true);
      const response = await fetch(`http://localhost:5000/api/nba/player-stats/${currentStat.toLowerCase()}`);
      const data = await response.json();
      setPlayers(data);
      setError(null);
    } catch (err) {
      setError('Fout bij laden van speler data');
      console.error('Error loading players:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadTrendsData = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/nba/top-players');
      const data = await response.json();
      setTrendsData(data.slice(0, 10)); // Top 10
    } catch (err) {
      console.error('Error loading trends data:', err);
    }
  };

  const handleStatChange = (newStat) => {
    setCurrentStat(newStat);
    loadTopPlayers();
  };

  const handlePlayerSelect = (player) => {
    setSelectedPlayer(player);
  };

  if (apiStatus === 'checking') {
    return <LoadingMessage>Verbinden met API...</LoadingMessage>;
  }

  if (apiStatus === 'error') {
    return <ErrorMessage>Kan geen verbinding maken met de API. Zorg ervoor dat de Flask server draait op localhost:5000</ErrorMessage>;
  }

  return (
    <DashboardContainer>
      {/* Overzicht Statistieken Sectie */}
      <Section>
        <SectionTitle>Overzicht Statistieken</SectionTitle>
        <StatFilters 
          currentStat={currentStat} 
          onStatChange={handleStatChange} 
        />
        <PlayerList 
          players={players} 
          currentStat={currentStat}
          onPlayerSelect={handlePlayerSelect}
          loading={loading}
        />
        {selectedPlayer && (
          <PlayerStatsChart 
            player={selectedPlayer} 
            stat={currentStat}
            onClose={() => setSelectedPlayer(null)}
          />
        )}
      </Section>

      {/* Trends: Top 10 per Stat Sectie */}
      <Section>
        <SectionTitle>Trends: Top 10 per Stat</SectionTitle>
        <TrendsTable>
          <thead>
            <tr>
              <th>Rk</th>
              <th>Speler</th>
              <th>Team</th>
              <th>GS</th>
              <th>MP</th>
              <th>PTS</th>
              <th>TRB</th>
              <th>AST</th>
            </tr>
          </thead>
          <tbody>
            {trendsData.map((player, index) => (
              <tr key={index}>
                <td>{index + 1}</td>
                <td>{player.player_name || '-'}</td>
                <td>{player.team_code || '-'}</td>
                <td>{player.GS || '-'}</td>
                <td>{player.MP || '-'}</td>
                <td>{player.PTS || '-'}</td>
                <td>{player.TRB || '-'}</td>
                <td>{player.AST || '-'}</td>
              </tr>
            ))}
          </tbody>
        </TrendsTable>
        {trendsData.length === 0 && !loading && (
          <div>Geen data gevonden.</div>
        )}
      </Section>

      {/* Team Statistieken Sectie */}
      <Section>
        <SectionTitle>Team Statistieken</SectionTitle>
        <TeamStatsChart />
      </Section>
    </DashboardContainer>
  );
};

export default NBADashboard; 