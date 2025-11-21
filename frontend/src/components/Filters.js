import React from 'react';
import { Select, MenuItem, FormControl, InputLabel } from '@mui/material';
import './Filters.css';

function Filters({ filters, setFilters, filterOptions }) {
  const loading = false; // Add loading state if needed

  // Dropdown styling variables - Green only
  const dropdownLabelText = '#3e7852'; // Primary green
  const dropdownContainerBg = '#FFFFFF'; // var(--dashboard-bg-paper)
  const dropdownText = '#000000'; // Black text for options
  const dropdownSelectedText = '#3e7852'; // Green text for selected
  const dropdownBorder = '#3e7852'; // Primary green border
  const dropdownHoverBg = 'rgba(62, 120, 82, 0.08)'; // Light green hover
  const dropdownSelectedBg = 'rgba(62, 120, 82, 0.16)'; // Light green background for selected

  const handleChange = (field, value) => {
    setFilters({ ...filters, [field]: value });
  };

  const getDisplayName = (value) => {
    return value || 'All';
  };

  const filterFields = [
    { key: 'borough', label: 'Borough', options: filterOptions.boroughs },
    { key: 'year', label: 'Year', options: filterOptions.years },
    { key: 'vehicle_type', label: 'Vehicle Type', options: filterOptions.vehicle_types },
    { key: 'contributing_factor', label: 'Contributing Factor', options: filterOptions.contributing_factors },
    { key: 'person_type', label: 'Person Type', options: filterOptions.person_types },
    { key: 'injury_type', label: 'Injury Type', options: filterOptions.injury_types }
  ];

  return (
    <div className="filters-container">
      <h2>
        <i className="ri-filter-3-line"></i> Filter Crashes
      </h2>
      <div className="filters-grid">
        {filterFields.map((field) => (
          <div key={field.key} className="select-custom">
            <FormControl fullWidth variant='outlined' required disabled={loading}>
              <InputLabel 
                id={`dropdown-label-${field.key}`}
                className="text-sm"
                shrink={true}
                sx={{ 
                  color: dropdownLabelText,
                  fontSize: '0.75rem', // Smaller label
                  '&.Mui-focused': {
                    color: '#3e7852',
                  },
                  '&.MuiInputLabel-shrink': {
                    color: '#3e7852',
                    fontSize: '0.75rem',
                  }
                }}
              >
                {field.label}
              </InputLabel>
              <div style={{ position: 'relative', width: '100%' }}>
                <Select
                  labelId={`dropdown-label-${field.key}`}
                  value={filters[field.key] === 'All' || !filters[field.key] ? '' : filters[field.key]}
                  label={field.label}
                  onChange={e => {
                    const val = String(e.target.value);
                    handleChange(field.key, val);
                  }}
                  renderValue={(value) => {
                    if (!value || value === '') {
                      return 'All';
                    }
                    return value;
                  }}
                  displayEmpty
                  onOpen={() => {
                    // Force label to shrink when opened
                    const label = document.getElementById(`dropdown-label-${field.key}`);
                    if (label) {
                      label.classList.add('MuiInputLabel-shrink');
                    }
                  }}
                  onClose={() => {
                    // Keep label shrunk if there's a value
                    if (!filters[field.key] || filters[field.key] === 'All') {
                      const label = document.getElementById(`dropdown-label-${field.key}`);
                      if (label) {
                        label.classList.remove('MuiInputLabel-shrink');
                      }
                    }
                  }}
                  sx={{
                    backgroundColor: dropdownContainerBg,
                    color: 'rgba(38, 43, 67, 0.7)', // Text color
                    borderRadius: '12px', // More rounded
                    height: '36px', // Smaller height
                    fontSize: '0.875rem', // Smaller font
                    width: '100%',
                    '& .MuiOutlinedInput-notchedOutline': {
                      borderColor: 'rgba(38, 43, 67, 0.22)', // Normal gray border when closed
                      borderRadius: '12px',
                    },
                    '&:hover .MuiOutlinedInput-notchedOutline': {
                      borderColor: 'rgba(38, 43, 67, 0.4)', // Darker gray on hover
                    },
                    '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                      borderColor: '#3e7852', // Green when focused/opened
                      borderWidth: '2px',
                    },
                    '&.Mui-focused': {
                      color: '#3e7852', // Green text when focused/opened
                    },
                    '& .MuiSelect-icon': { 
                      color: 'rgba(38, 43, 67, 0.7)', // Icon color
                      '&.MuiSelect-iconOpen': {
                        color: '#3e7852', // Green icon when open
                      }
                    },
                    '&.MuiInputBase-root': {
                      paddingRight: filters[field.key] && filters[field.key] !== 'All' ? '40px' : '14px',
                    }
                  }}
                  MenuProps={{
                    PaperProps: {
                      sx: {
                        backgroundColor: dropdownContainerBg,
                        color: dropdownText,
                        borderRadius: '12px',
                        marginTop: '4px',
                        '& .MuiMenuItem-root': {
                          color: 'rgba(38, 43, 67, 0.7)', // Menu item text color
                          fontSize: '0.875rem',
                          minHeight: '36px',
                          borderRadius: '8px',
                          margin: '2px 4px',
                          '&.Mui-selected': {
                            backgroundColor: dropdownSelectedBg,
                            color: dropdownSelectedText,
                            '&:hover': {
                              backgroundColor: dropdownSelectedBg,
                            }
                          },
                          '&:hover': {
                            backgroundColor: dropdownHoverBg
                          }
                        }
                      }
                    },
                    anchorOrigin: {
                      vertical: 'bottom',
                      horizontal: 'left',
                    },
                    transformOrigin: {
                      vertical: 'top',
                      horizontal: 'left',
                    }
                  }}
                >
                  {field.options?.map((option) => (
                    <MenuItem key={option} value={String(option)}>
                      {option}
                    </MenuItem>
                  ))}
                </Select>
                {filters[field.key] && filters[field.key] !== 'All' && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleChange(field.key, 'All');
                    }}
                    style={{
                      position: 'absolute',
                      right: '32px',
                      top: '50%',
                      transform: 'translateY(-50%)',
                      background: 'transparent',
                      border: 'none',
                      cursor: 'pointer',
                      padding: '4px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      zIndex: 1
                    }}
                  >
                    <i className="ri-close-line" style={{ color: '#666', fontSize: '18px' }}></i>
                  </button>
                )}
              </div>
            </FormControl>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Filters;

