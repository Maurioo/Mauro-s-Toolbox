import React, { useState, useEffect } from 'react';
import styled from 'styled-components';

const FiltersContainer = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1.5rem;
  align-items: center;
`;

const FilterButton = styled.button`
  font-family: 'Oswald', Arial, sans-serif;
  font-size: 1.1rem;
  background: ${props => props.active ? '#C9082A' : '#fff'};
  color: ${props => props.active ? '#fff' : '#17408B'};
  border: none;
  border-radius: 6px;
  padding: 0.6rem 1.2rem;
  cursor: pointer;
  transition: background 0.2s, color 0.2s, box-shadow 0.2s;
  box-shadow: 0 2px 8px rgba(23,64,139,0.10);
  
  &:hover {
    background: #C9082A;
    color: #fff;
  }
`;

const FilterGroup = styled.div`
  position: relative;
  display: inline-block;
  min-width: 200px;
`;

const FilterInput = styled.input`
  font-family: 'Oswald', Arial, sans-serif;
  font-size: 1.1rem;
  background: #fff;
  color: #17408B;
  border: none;
  border-radius: 6px;
  padding: 0.6rem 1.2rem;
  min-width: 180px;
  box-shadow: 0 2px 8px rgba(23,64,139,0.10);
  position: relative;
`;

const AutocompleteList = styled.div`
  position: absolute;
  z-index: 10;
  background: #fff;
  color: #17408B;
  border-radius: 0 0 8px 8px;
  box-shadow: 0 4px 16px rgba(23,64,139,0.15);
  width: 100%;
  max-height: 220px;
  overflow-y: auto;
  margin-top: -2px;
  display: ${props => props.show ? 'block' : 'none'};
`;

const AutocompleteItem = styled.div`
  padding: 0.6rem 1.2rem;
  cursor: pointer;
  font-family: 'Oswald', Arial, sans-serif;
  font-size: 1.05rem;
  
  &:hover, &.active {
    background: #C9082A;
    color: #fff;
  }
`;

const StatFilters = ({ currentStat, onStatChange }) => {
  const [teamFilter, setTeamFilter] = useState('');
  const [playerFilter, setPlayerFilter] = useState('');
  const [showTeamAutocomplete, setShowTeamAutocomplete] = useState(false);
  const [showPlayerAutocomplete, setShowPlayerAutocomplete] = useState(false);
  const [teams, setTeams] = useState([]);
  const [players, setPlayers] = useState([]);

  // Load teams and players for autocomplete
  useEffect(() => {
    loadTeams();
    loadPlayers();
  }, []);

  const loadTeams = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/nba/team-stats');
      const data = await response.json();
      setTeams(data.map(team => team.team_code));
    } catch (error) {
      console.error('Error loading teams:', error);
    }
  };

  const loadPlayers = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/nba/top-players');
      const data = await response.json();
      setPlayers(data.map(player => player.player_name));
    } catch (error) {
      console.error('Error loading players:', error);
    }
  };

  const handleStatClick = (stat) => {
    onStatChange(stat);
  };

  const handleTeamInput = (value) => {
    setTeamFilter(value);
    setShowTeamAutocomplete(value.length > 0);
  };

  const handlePlayerInput = (value) => {
    setPlayerFilter(value);
    setShowPlayerAutocomplete(value.length > 0);
  };

  const handleTeamSelect = (team) => {
    setTeamFilter(team);
    setShowTeamAutocomplete(false);
  };

  const handlePlayerSelect = (player) => {
    setPlayerFilter(player);
    setShowPlayerAutocomplete(false);
  };

  const filteredTeams = teams.filter(team => 
    team.toLowerCase().includes(teamFilter.toLowerCase())
  ).slice(0, 10);

  const filteredPlayers = players.filter(player => 
    player.toLowerCase().includes(playerFilter.toLowerCase())
  ).slice(0, 10);

  return (
    <FiltersContainer>
      <FilterButton 
        active={currentStat === 'PPG'} 
        onClick={() => handleStatClick('PPG')}
      >
        PPG
      </FilterButton>
      <FilterButton 
        active={currentStat === 'RPG'} 
        onClick={() => handleStatClick('RPG')}
      >
        RPG
      </FilterButton>
      <FilterButton 
        active={currentStat === 'APG'} 
        onClick={() => handleStatClick('APG')}
      >
        APG
      </FilterButton>
      <FilterButton 
        active={currentStat === 'TP'} 
        onClick={() => handleStatClick('TP')}
      >
        TP
      </FilterButton>
      <FilterButton 
        active={currentStat === 'TR'} 
        onClick={() => handleStatClick('TR')}
      >
        TR
      </FilterButton>
      <FilterButton 
        active={currentStat === 'TA'} 
        onClick={() => handleStatClick('TA')}
      >
        TA
      </FilterButton>
      <FilterButton 
        active={currentStat === 'MPG'} 
        onClick={() => handleStatClick('MPG')}
      >
        MP
      </FilterButton>
      
      <FilterGroup>
        <FilterInput
          placeholder="Zoek team..."
          value={teamFilter}
          onChange={(e) => handleTeamInput(e.target.value)}
          onFocus={() => setShowTeamAutocomplete(teamFilter.length > 0)}
        />
        <AutocompleteList show={showTeamAutocomplete}>
          {filteredTeams.map((team, index) => (
            <AutocompleteItem 
              key={index}
              onClick={() => handleTeamSelect(team)}
            >
              {team}
            </AutocompleteItem>
          ))}
        </AutocompleteList>
      </FilterGroup>
      
      <FilterGroup>
        <FilterInput
          placeholder="Zoek speler..."
          value={playerFilter}
          onChange={(e) => handlePlayerInput(e.target.value)}
          onFocus={() => setShowPlayerAutocomplete(playerFilter.length > 0)}
        />
        <AutocompleteList show={showPlayerAutocomplete}>
          {filteredPlayers.map((player, index) => (
            <AutocompleteItem 
              key={index}
              onClick={() => handlePlayerSelect(player)}
            >
              {player}
            </AutocompleteItem>
          ))}
        </AutocompleteList>
      </FilterGroup>
    </FiltersContainer>
  );
};

export default StatFilters; 