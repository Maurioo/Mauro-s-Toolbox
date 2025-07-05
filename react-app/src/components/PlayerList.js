import React from 'react';
import styled from 'styled-components';

const StatsList = styled.ul`
  list-style: none;
  padding: 0;
  margin: 0;
`;

const PlayerItem = styled.li`
  display: grid;
  grid-template-columns: 2.5fr 1.5fr 1fr;
  align-items: center;
  margin-bottom: 1rem;
  font-size: 1.2rem;
  background: rgba(255,255,255,0.13);
  padding: 0.9rem 1.2rem;
  border-radius: 8px;
  font-family: 'Roboto', Arial, sans-serif;
  box-shadow: 0 1px 4px rgba(23,64,139,0.08);
  cursor: pointer;
  transition: background 0.15s, box-shadow 0.15s;
  
  &:hover, &.active {
    background: #C9082A;
    color: #fff;
    box-shadow: 0 2px 8px rgba(23,64,139,0.18);
  }
`;

const PlayerName = styled.span`
  font-weight: bold;
  color: #fff;
  font-family: 'Oswald', Arial, sans-serif;
  font-size: 1.1em;
`;

const PlayerValue = styled.span`
  color: #FFD700;
  font-family: 'Oswald', Arial, sans-serif;
  font-size: 1.1em;
`;

const PlayerTeam = styled.span`
  display: flex;
  align-items: center;
  gap: 0.5em;
  min-width: 120px;
  justify-content: flex-start;
  max-width: 220px;
  flex-shrink: 0;
`;

const TeamEmblem = styled.span`
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: inline-block;
  border: 2px solid #fff;
  margin-right: 0.3em;
  box-shadow: 0 1px 4px rgba(23,64,139,0.10);
  min-width: 24px;
  min-height: 24px;
  background: ${props => props.color || '#888'};
`;

const LoadingMessage = styled.div`
  text-align: center;
  padding: 2rem;
  color: #fff;
  font-size: 1.1rem;
`;

const EmptyMessage = styled.div`
  text-align: center;
  padding: 2rem;
  color: #fff;
  font-size: 1.1rem;
  background: rgba(255,255,255,0.13);
  border-radius: 8px;
`;

// NBA teamkleuren mapping
const TEAM_COLORS = {
  ATL: '#E03A3E', BOS: '#007A33', BKN: '#000000', CHA: '#1D1160', CHI: '#CE1141',
  CLE: '#6F263D', DAL: '#00538C', DEN: '#0E2240', DET: '#C8102E', GSW: '#1D428A',
  HOU: '#CE1141', IND: '#002D62', LAC: '#C8102E', LAL: '#552583', MEM: '#5D76A9',
  MIA: '#98002E', MIL: '#00471B', MIN: '#0C2340', NOP: '#0C2340', NYK: '#006BB6',
  OKC: '#007AC1', ORL: '#0077C0', PHI: '#006BB6', PHO: '#1D1160', POR: '#E03A3E',
  SAC: '#5A2D81', SAS: '#C4CED4', TOR: '#CE1141', UTA: '#002B5C', WAS: '#002B5C'
};

const PlayerList = ({ players, currentStat, onPlayerSelect, loading }) => {
  const getStatValue = (player, stat) => {
    switch(stat) {
      case 'PPG': case 'TP': return player.PTS;
      case 'RPG': case 'TR': return player.TRB;
      case 'APG': case 'TA': return player.AST;
      case 'MPG': return player.MP;
      default: return '-';
    }
  };

  const getTeamColor = (teamCode) => {
    return TEAM_COLORS[teamCode] || '#888';
  };

  if (loading) {
    return <LoadingMessage>Bezig met laden...</LoadingMessage>;
  }

  if (!players || players.length === 0) {
    return <EmptyMessage>Geen data gevonden.</EmptyMessage>;
  }

  return (
    <StatsList>
      {players.map((player, index) => (
        <PlayerItem 
          key={index}
          onClick={() => onPlayerSelect(player)}
        >
          <PlayerName>
            {index + 1}. {player.player_name || 'Onbekend'}
          </PlayerName>
          <PlayerTeam>
            <TeamEmblem 
              color={getTeamColor(player.team_code)}
              title={player.team_code}
            />
            {player.team_code || '-'}
          </PlayerTeam>
          <PlayerValue>
            {getStatValue(player, currentStat)} {currentStat}
          </PlayerValue>
        </PlayerItem>
      ))}
    </StatsList>
  );
};

export default PlayerList; 