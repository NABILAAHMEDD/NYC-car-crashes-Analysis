import React, { useState } from 'react';
import { Select, MenuItem, FormControl, TextField, InputAdornment, InputLabel } from '@mui/material';
import './FilterSearch.css';

function FilterSearch({ filters, setFilters, filterOptions, onSearch }) {
  const [searchQuery, setSearchQuery] = useState('');
  const loading = false; // Add loading state if needed

  // Dropdown styling variables - Green only
  const dropdownLabelText = '#3e7852'; // Primary green
  const dropdownContainerBg = '#FFFFFF'; // var(--dashboard-bg-paper)
  const dropdownText = '#000000'; // Black text for options
  const dropdownSelectedText = '#3e7852'; // Green text for selected
  const dropdownBorder = '#3e7852'; // Primary green border
  const dropdownHoverBg = 'rgba(62, 120, 82, 0.08)'; // Light green hover
  const dropdownSelectedBg = 'rgba(62, 120, 82, 0.16)'; // Light green background for selected

  const handleFilterChange = (field, value) => {
    setFilters({ ...filters, [field]: value });
  };

  const getDisplayName = (value) => {
    return value || 'All';
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      onSearch(searchQuery);
    }
  };

  const filterFields = [
    { key: 'borough', label: 'Borough', options: filterOptions.boroughs },
    { key: 'year', label: 'Year', options: filterOptions.years },
    { key: 'vehicle_type', label: 'Vehicle Type', options: filterOptions.vehicle_types },
    { key: 'contributing_factor', label: 'Contributing Factor', options: filterOptions.contributing_factors },
    { key: 'person_type', label: 'Person Type', options: filterOptions.person_types },
    { key: 'injury_type', label: 'Injury Type', options: filterOptions.injury_types }
  ];

  // Split filters into rows of 3
  const filterRows = [];
  for (let i = 0; i < filterFields.length; i += 3) {
    filterRows.push(filterFields.slice(i, i + 3));
  }

  return (
    <div className="filter-search-container">
      {/* Search Container Header */}
      <div className="search-container-header">
        <i className="ri-filter-3-line filter-icon"></i>
        <span className="filter-text">Filter Crashes</span>
      </div>

      {/* Filter Row - Search Input */}
      <div className="filter-row">
        <div className="input-outlined search-input-wrapper">
          <TextField
            placeholder="Search..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter') {
                handleSearchSubmit(e);
              }
            }}
            sx={{
              width: '100%',
              '& .MuiOutlinedInput-root': {
                height: '36px',
                borderRadius: '12px',
                fontSize: '0.875rem',
                color: '#000000',
                backgroundColor: '#FFFFFF',
                '& fieldset': {
                  borderColor: 'rgba(38, 43, 67, 0.22)', // Normal gray border when closed
                  borderRadius: '12px',
                },
                '&:hover fieldset': {
                  borderColor: 'rgba(38, 43, 67, 0.4)', // Darker gray on hover
                },
                '&.Mui-focused fieldset': {
                  borderColor: '#3e7852', // Green when focused
                  borderWidth: '2px',
                },
                '&.Mui-focused': {
                  color: '#3e7852', // Green text when focused
                },
                '&.Mui-focused .search-icon-input': {
                  color: '#3e7852', // Green icon when focused
                },
                '& .MuiInputBase-input': {
                  padding: '8px 14px',
                  fontSize: '0.875rem',
                  color: '#000000',
                  '&::placeholder': {
                    color: 'rgba(38, 43, 67, 0.6)',
                  }
                }
              }
            }}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <i className="ri-search-line search-icon-input"></i>
                </InputAdornment>
              ),
            }}
          />
        </div>
      </div>

      {/* Filter Rows - Dropdowns */}
      {filterRows.map((row, rowIndex) => (
        <div key={rowIndex} className="filter-row filter-dropdowns-row">
          {row.map((field) => (
            <div key={field.key} className="input-outlined">
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
                      handleFilterChange(field.key, val);
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
                        handleFilterChange(field.key, 'All');
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
      ))}
    </div>
  );
}

export default FilterSearch;

