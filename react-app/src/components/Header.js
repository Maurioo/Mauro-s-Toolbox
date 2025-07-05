import React from 'react';
import styled from 'styled-components';

const HeaderContainer = styled.header`
  background: #fff;
  padding: 1.5rem 0 1rem 0;
  text-align: center;
  box-shadow: 0 4px 16px rgba(0,0,0,0.08);
  margin-bottom: 2rem;
  position: relative;
`;

const BasketballIcon = styled.svg`
  position: absolute;
  left: 2rem;
  top: 50%;
  transform: translateY(-50%);
  width: 60px;
  height: 60px;
`;

const Title = styled.h1`
  font-family: 'Oswald', Arial, sans-serif;
  color: #17408B;
  font-size: 2.8rem;
  letter-spacing: 2px;
  margin: 0;
  text-transform: uppercase;
  text-shadow: 2px 2px 0 #C9082A, 4px 4px 0 #fff;
`;

const Header = () => {
  return (
    <HeaderContainer>
      <BasketballIcon viewBox="0 0 64 64">
        <circle cx="32" cy="32" r="30" fill="#F58220" stroke="#C9082A" strokeWidth="4"/>
        <path d="M32 2 A30 30 0 0 1 32 62" stroke="#C9082A" strokeWidth="3" fill="none"/>
        <path d="M2 32 A30 30 0 0 1 62 32" stroke="#C9082A" strokeWidth="3" fill="none"/>
        <path d="M12 12 Q32 32 52 52" stroke="#C9082A" strokeWidth="2" fill="none"/>
        <path d="M52 12 Q32 32 12 52" stroke="#C9082A" strokeWidth="2" fill="none"/>
      </BasketballIcon>
      <Title>NBA Dashboard</Title>
    </HeaderContainer>
  );
};

export default Header; 