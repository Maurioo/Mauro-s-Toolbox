import React from 'react';
import styled from 'styled-components';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const ChartContainer = styled.div`
  flex: 1 1 500px;
  min-width: 320px;
  max-width: 900px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(23,64,139,0.10);
  margin-bottom: 0;
  padding: 1rem;
`;

const ChartRow = styled.div`
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  justify-content: flex-start;
  gap: 2rem;
  margin-top: 2rem;
`;

const BackButton = styled.button`
  background: #C9082A;
  color: #fff;
  font-family: 'Oswald', Arial, sans-serif;
  font-size: 1.2rem;
  border: none;
  padding: 0.8rem 2.2rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(23,64,139,0.10);
  cursor: pointer;
  letter-spacing: 1px;
  margin-left: 2rem;
  margin-top: 0;
  align-self: flex-start;
`;

const ChartTitle = styled.h3`
  font-family: 'Oswald', Arial, sans-serif;
  color: #17408B;
  text-align: center;
  margin-bottom: 1rem;
  font-size: 1.5rem;
`;

const PlayerStatsChart = ({ player, stat, onClose }) => {
  if (!player) return null;

  // Prepare data for the chart
  const chartData = [
    {
      name: 'PTS',
      value: player.PTS || 0,
      fill: '#C9082A'
    },
    {
      name: 'TRB',
      value: player.TRB || 0,
      fill: '#17408B'
    },
    {
      name: 'AST',
      value: player.AST || 0,
      fill: '#FFD700'
    },
    {
      name: 'MP',
      value: player.MP || 0,
      fill: '#28a745'
    }
  ];

  const getStatLabel = (stat) => {
    switch(stat) {
      case 'PPG': return 'Points Per Game';
      case 'RPG': return 'Rebounds Per Game';
      case 'APG': return 'Assists Per Game';
      case 'TP': return 'Total Points';
      case 'TR': return 'Total Rebounds';
      case 'TA': return 'Total Assists';
      case 'MPG': return 'Minutes Per Game';
      default: return stat;
    }
  };

  return (
    <ChartRow>
      <ChartContainer>
        <ChartTitle>
          {player.player_name} - {getStatLabel(stat)}
        </ChartTitle>
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="value" fill="#C9082A" />
          </BarChart>
        </ResponsiveContainer>
      </ChartContainer>
      <BackButton onClick={onClose}>
        Terug
      </BackButton>
    </ChartRow>
  );
};

export default PlayerStatsChart; 