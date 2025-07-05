import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const ChartContainer = styled.div`
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(23,64,139,0.10);
  padding: 1rem;
  margin-top: 1rem;
`;

const ChartTitle = styled.h3`
  font-family: 'Oswald', Arial, sans-serif;
  color: #17408B;
  text-align: center;
  margin-bottom: 1rem;
  font-size: 1.5rem;
`;

const LoadingMessage = styled.div`
  text-align: center;
  padding: 2rem;
  color: #17408B;
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

const COLORS = ['#C9082A', '#17408B', '#FFD700', '#28a745', '#6f42c1', '#fd7e14'];

const TeamStatsChart = () => {
  const [teamData, setTeamData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadTeamStats();
  }, []);

  const loadTeamStats = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:5000/api/nba/team-stats');
      const data = await response.json();
      setTeamData(data);
      setError(null);
    } catch (err) {
      setError('Fout bij laden van team data');
      console.error('Error loading team stats:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <LoadingMessage>Bezig met laden van team statistieken...</LoadingMessage>;
  }

  if (error) {
    return <ErrorMessage>{error}</ErrorMessage>;
  }

  if (!teamData || teamData.length === 0) {
    return <div>Geen team data gevonden.</div>;
  }

  // Prepare data for charts
  const barChartData = teamData.slice(0, 10).map(team => ({
    name: team.team_code,
    avg_points: parseFloat(team.avg_points || 0).toFixed(1),
    avg_rebounds: parseFloat(team.avg_rebounds || 0).toFixed(1),
    avg_assists: parseFloat(team.avg_assists || 0).toFixed(1),
    player_count: team.player_count
  }));

  const pieChartData = teamData.slice(0, 6).map(team => ({
    name: team.team_code,
    value: team.player_count
  }));

  return (
    <div>
      <ChartTitle>Team Gemiddelde Statistieken (Top 10)</ChartTitle>
      <ChartContainer>
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={barChartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="avg_points" fill="#C9082A" name="Gem. Punten" />
            <Bar dataKey="avg_rebounds" fill="#17408B" name="Gem. Rebounds" />
            <Bar dataKey="avg_assists" fill="#FFD700" name="Gem. Assists" />
          </BarChart>
        </ResponsiveContainer>
      </ChartContainer>

      <ChartTitle>Spelers per Team (Top 6)</ChartTitle>
      <ChartContainer>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={pieChartData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
            >
              {pieChartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </ChartContainer>
    </div>
  );
};

export default TeamStatsChart; 