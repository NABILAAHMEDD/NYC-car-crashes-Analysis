/**
 * Main Application Component
 * 
 * This is the root component of the NYC Traffic Crash Data Dashboard.
 * It manages application state, API communication, and coordinates all child components.
 * 
 * State Management Strategy:
 * - filters: Current filter selections (all default to 'All')
 * - filterOptions: Available options for each filter (loaded from backend)
 * - stats: Statistics data from backend (null until report is generated)
 * - loading: Loading state for async operations
 * - error: Error messages for user feedback
 * 
 * Data Flow:
 * 1. Component mounts → Load filter options from backend
 * 2. User selects filters → Update filters state
 * 3. User clicks "Generate Report" → Fetch statistics from backend
 * 4. Backend responds → Update stats state → Charts and cards re-render
 * 
 * @component
 */
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { CircularProgress } from '@mui/material';
import MinorCrashIcon from '@mui/icons-material/MinorCrash';
import './App.css';
import FilterSearch from './components/FilterSearch';
import StatsCards from './components/StatsCards';
import Charts from './components/Charts';

// API base URL - Update this for production deployment
const API_URL = 'http://localhost:5000/api';

function App() {
  /**
   * Filter state - tracks user selections for all 6 filter types
   * Default value 'All' means no filter applied (show all data)
   */
  const [filters, setFilters] = useState({
    borough: 'All',
    year: 'All',
    vehicle_type: 'All',
    contributing_factor: 'All',
    person_type: 'All',
    injury_type: 'All'
  });

  /**
   * Filter options - populated from backend on mount
   * Contains lists of available values for each filter dropdown
   */
  const [filterOptions, setFilterOptions] = useState({});
  
  /**
   * Statistics data - null until user generates a report
   * Contains all chart data and summary statistics from backend
   */
  const [stats, setStats] = useState(null);
  
  /**
   * Loading state - true during API calls
   * Used to show loading indicators and disable buttons
   */
  const [loading, setLoading] = useState(false);
  
  /**
   * Error state - stores error messages for user feedback
   * Displayed as error banner at top of page
   */
  const [error, setError] = useState(null);

  /**
   * Load filter options when component mounts
   * 
   * This runs once on initial render to populate dropdown options.
   * Empty dependency array [] ensures it only runs once.
   * 
   * Decision: Load options on mount rather than on demand
   * Alternative: Lazy load when dropdown opens - Rejected for better UX (instant options)
   */
  useEffect(() => {
    loadFilterOptions();
    checkBackendHealth();
  }, []);

  /**
   * Check backend health and geo_data availability
   * Helps identify issues early
   */
  const checkBackendHealth = async () => {
    try {
      const response = await axios.get(`${API_URL}/health`);
      console.log('Backend Health Check:', response.data);
      
      if (!response.data.has_geo_data) {
        console.warn('⚠️ Backend reports no geo_data available!');
        if (response.data.geo_data_count === 0) {
          console.warn('   This might indicate missing LATITUDE/LONGITUDE columns in the CSV file.');
        }
      } else {
        console.log(`✅ Backend has ${response.data.geo_data_count} records with geo_data`);
      }
    } catch (error) {
      console.error('Error checking backend health:', error);
    }
  };

  /**
   * Load available filter options from backend
   * 
   * Fetches lists of boroughs, years, vehicle types, etc. to populate dropdowns.
   * Called once on component mount.
   * 
   * Error Handling: Sets error state if backend is unreachable
   * This provides user feedback instead of silent failure
   */
  const loadFilterOptions = async () => {
    try {
      const response = await axios.get(`${API_URL}/filters`);
      setFilterOptions(response.data);
    } catch (error) {
      console.error('Error loading filters:', error);
      setError('Error connecting to backend. Make sure Flask server is running on port 5000.');
    }
  };

  /**
   * Handle natural language search queries
   * 
   * This function processes user search queries and extracts filter values.
   * The backend parses the query and returns extracted filters, which are then
   * applied and a report is automatically generated.
   * 
   * Flow:
   * 1. Validate query is not empty
   * 2. Send query to backend for parsing
   * 3. Update filters state with extracted values
   * 4. Auto-generate report with new filters
   * 
   * Decision: Auto-generate report after search for better UX
   * Alternative: Require manual "Generate Report" click - Rejected for convenience
   * 
   * @param {string} query - Natural language search query from user
   */
  const handleSearch = async (query) => {
    // Validate query is not empty or whitespace-only
    if (!query.trim()) {
      alert('Please enter a search query');
      return;
    }

    try {
      // Send query to backend for parsing
      const response = await axios.post(`${API_URL}/search`, { query });
      const searchFilters = response.data.filters;

      // Merge extracted filters with existing filters
      // Spread operator preserves filters not mentioned in search
      setFilters(prevFilters => ({
        ...prevFilters,
        ...searchFilters
      }));

      // Auto-generate report with extracted filters
      // Small delay ensures state update completes before API call
      setTimeout(() => generateReport(searchFilters), 100);
    } catch (error) {
      console.error('Error searching:', error);
      alert('Error processing search query');
    }
  };

  /**
   * Generate statistics report based on current filters
   * 
   * This is the main data fetching function. It sends current filter selections
   * to the backend, which processes the data and returns comprehensive statistics.
   * 
   * Parameters:
   * - customFilters: Optional parameter to override current filters
   *   Used when search extracts filters, or when applying preset filter sets
   * 
   * State Updates:
   * - Sets loading to true at start, false at end (finally block)
   * - Clears any previous errors
   * - Updates stats with response data
   * 
   * Error Handling:
   * - Catches API errors and sets user-friendly error message
   * - Loading state is cleared in finally block (always executes)
   * 
   * @param {Object} customFilters - Optional filter object to use instead of state filters
   */
  const generateReport = async (customFilters = null) => {
    setLoading(true);
    setError(null);

    // Use custom filters if provided, otherwise use current state filters
    // This allows the function to be called with different filters (e.g., from search)
    const filtersToUse = customFilters || filters;

    try {
      // Send POST request with filters to backend
      const response = await axios.post(`${API_URL}/stats`, filtersToUse);
      // Update stats state, which triggers re-render of Charts and StatsCards
      setStats(response.data);
      
      // Debug: Log response to help troubleshoot
      console.log('API Response received:', {
        hasGeoData: !!response.data?.geo_data,
        geoDataLength: response.data?.geo_data?.length || 0,
        totalCrashes: response.data?.total_crashes,
        sampleGeoData: response.data?.geo_data?.slice(0, 3) || null
      });
      
      // Warn if no geo_data
      if (!response.data?.geo_data || response.data.geo_data.length === 0) {
        console.warn('⚠️ WARNING: No geo_data received from API! Check backend logs.');
      } else {
        console.log('✅ Geo data received successfully:', response.data.geo_data.length, 'points');
      }
    } catch (error) {
      console.error('Error generating report:', error);
      if (error.response) {
        // Server responded with error status
        setError(`Error generating report: ${error.response.data?.error || error.response.statusText}. Make sure the backend server is running on port 5000.`);
      } else if (error.request) {
        // Request was made but no response received
        setError('Cannot connect to backend server. Make sure Flask server is running on port 5000.');
      } else {
        // Something else happened
        setError('Error generating report. Please try again.');
      }
    } finally {
      // Always clear loading state, even if request fails
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="app-header">
        <h1>
          <MinorCrashIcon className="header-icon" />
          NYC Traffic Crash Data Dashboard
        </h1>
      </header>

      <div className="container">
        {error && (
          <div className="error-message">
            <p>⚠️ {error}</p>
          </div>
        )}

        <FilterSearch
          filters={filters}
          setFilters={setFilters}
          filterOptions={filterOptions}
          onSearch={handleSearch}
        />

        <button
          className="generate-btn"
          onClick={() => generateReport()}
          disabled={loading}
        >
          {loading ? (
            <>
              <i className="ri-hourglass-fill"></i> Generating...
            </>
          ) : (
            <>
              <i className="ri-file-chart-line"></i> Generate Report
            </>
          )}
        </button>

        {loading && (
          <div className="loading-indicator">
            <CircularProgress disableShrink className="circular-progress" />
          </div>
        )}

        {stats && !loading && (
          <>
            <StatsCards stats={stats} />
            <Charts stats={stats} />
          </>
        )}
      </div>
    </div>
  );
}

export default App;

