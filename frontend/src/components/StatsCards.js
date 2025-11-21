import React from 'react';
import { Box } from '@mui/material';
import './StatsCards.css';

function StatsCards({ stats }) {
  const statsData = [
    {
      count: stats.total_crashes?.toLocaleString() || '0',
      label: 'Total Crashes',
      icon: 'ri-roadster-fill',
      borderColor: '#3e7852',
      iconColor: '#3e7852'
    },
    {
      count: stats.total_persons?.toLocaleString() || '0',
      label: 'Total Persons',
      icon: 'ri-group-line',
      borderColor: '#9E9E9E',
      iconColor: '#424242',
      iconOpacity: 0.1
    },
    {
      count: stats.total_injuries?.toLocaleString() || '0',
      label: 'Total Injuries',
      icon: 'ri-hospital-fill',
      borderColor: '#ED6C02',
      iconColor: '#ED6C02'
    },
    {
      count: stats.total_deaths?.toLocaleString() || '0',
      label: 'Total Deaths',
      icon: 'ri-heart-pulse-fill',
      borderColor: '#D32F2F',
      iconColor: '#D32F2F'
    }
  ];

  return (
    <Box className='stats-summary'>
      {statsData.map((stat, index) => (
        <Box
          key={index}
          className='stat-card'
          style={{
            borderBottom: `3px solid ${stat.borderColor}`
          }}
        >
          <Box className='stat-card-content'>
            <Box className='stat-card-left'>
              <Box
                className='stat-number'
                style={{
                  fontFamily: 'IBM Plex Sans',
                  color: 'rgba(38, 43, 67, 0.7)'
                }}
              >
                {stat.count}
              </Box>
              <Box
                className='stat-label'
                style={{
                  fontFamily: 'IBM Plex Sans',
                  color: 'rgba(38, 43, 67, 0.7)'
                }}
              >
                {stat.label}
              </Box>
            </Box>

            <Box className='stat-icon-wrapper'>
              <i
                className={stat.icon}
                style={{
                  fontSize: '81px',
                  color: stat.iconColor || stat.borderColor,
                  opacity: stat.iconOpacity !== undefined ? stat.iconOpacity : 0.3
                }}
              />
            </Box>
          </Box>
        </Box>
      ))}
    </Box>
  );
}

export default StatsCards;

