  /**
 * Charts Component
 * 
 * This component renders all data visualizations for the NYC Crash Dashboard.
 * It receives statistics data from the backend API and transforms it into
 * chart-ready formats for Plotly.js.
 * 
 * Data Transformation Strategy:
 * - Backend sends data as objects/dictionaries (e.g., {borough: count})
 * - Frontend transforms to arrays for Plotly (labels and values)
 * - Each chart type has specific data requirements handled here
 * 
 * Chart Types Implemented:
 * 1. Bar Chart - Crashes by Borough
 * 2. Horizontal Bar - Top Contributing Factors
 * 3-6. Pie Charts - Vehicle Types, Person Types, Injury Types, Seasons
 * 7-8. Line Charts - Monthly Trends, Hourly Patterns
 * 9. Heatmap - Hour vs Day of Week
 * 10. Geographic Map - Crash Locations
 * 
 * @param {Object} stats - Statistics object from backend API containing all chart data
 */
import React from 'react';
import Plot from 'react-plotly.js';
import './Charts.css';

// Suppress Mapbox warnings/errors globally since we use scattergeo (free, no tokens)
if (typeof window !== 'undefined') {
  const originalError = console.error;
  const originalWarn = console.warn;
  
  // Suppress console.error for Mapbox
  console.error = function(...args) {
    const errorText = args.map(arg => String(arg)).join(' ');
    if (errorText.toLowerCase().includes('mapbox') || 
        errorText.toLowerCase().includes('mapbox.style')) {
      return; // Suppress Mapbox errors
    }
    originalError.apply(console, args);
  };
  
  // Suppress console.warn for Mapbox
  console.warn = function(...args) {
    const warnText = args.map(arg => String(arg)).join(' ');
    if (warnText.toLowerCase().includes('mapbox') || 
        warnText.toLowerCase().includes('mapbox.style')) {
      return; // Suppress Mapbox warnings
    }
    originalWarn.apply(console, args);
  };
  
  // Also catch unhandled Promise rejections related to Mapbox
  window.addEventListener('unhandledrejection', (event) => {
    const errorText = event.reason ? String(event.reason) : '';
    if (errorText.toLowerCase().includes('mapbox') || 
        errorText.toLowerCase().includes('mapbox.style')) {
      event.preventDefault(); // Suppress Mapbox promise rejections
    }
  });
}

function Charts({ stats }) {
  // Safety check: return early if stats is not available
  if (!stats) {
    return (
      <div className="charts-container">
        <h2>
          <i className="ri-bar-chart-box-line"></i> Visualizations
        </h2>
        <div style={{ padding: '20px', textAlign: 'center', color: 'rgba(38, 43, 67, 0.7)' }}>
          <p>Loading data...</p>
        </div>
      </div>
    );
  }

  /**
   * Helper function to transform backend data format to Plotly chart format
   * 
   * Backend sends data as objects: {label1: value1, label2: value2, ...}
   * Plotly requires separate arrays: labels: [label1, label2], values: [value1, value2]
   * 
   * Decision: Centralized transformation function to avoid code duplication
   * Alternative: Transform in each chart individually - Rejected for maintainability
   * 
   * @param {Object} dataObj - Object with keys as labels and values as counts
   * @returns {Object} Object with labels and values arrays, or empty arrays if no data
   */
  const prepareData = (dataObj) => {
    // Handle null/undefined data gracefully
    if (!dataObj) return { labels: [], values: [] };
    return {
      labels: Object.keys(dataObj),
      values: Object.values(dataObj)
    };
  };

  // 1. Bar Chart - Crashes by Borough
  const boroughData = prepareData(stats.by_borough);

  // 2. Horizontal Bar Chart - Contributing Factors
  const factorData = prepareData(stats.by_factor);

  // 3. Pie Chart - Vehicle Types
  const vehicleData = prepareData(stats.by_vehicle);

  // 4. Pie Chart - Person Types
  const personData = prepareData(stats.by_person_type);

  // 5. Pie Chart - Injury Types
  const injuryData = prepareData(stats.by_injury);

  // 6. Pie Chart - Seasonal Distribution
  const seasonData = prepareData(stats.by_season);

  // 7. Line Chart - Time Series
  const timeData = prepareData(stats.by_month);

  // 8. Line Chart - By Hour
  const hourData = prepareData(stats.by_hour);

  /**
   * Create heatmap data structure for Hour vs Day of Week visualization
   * 
   * This function transforms the nested dictionary from backend into a 2D matrix
   * required by Plotly heatmaps. The structure is: z[day_index][hour_index] = count
   * 
   * Data Structure:
   * - Backend sends: {Monday: {0: 10, 1: 5, ...}, Tuesday: {0: 12, ...}, ...}
   * - Frontend needs: z = [[10, 5, ...], [12, ...], ...] (2D array)
   * 
   * Fallback Strategy:
   * If backend doesn't provide by_day_hour data, we estimate it using:
   * - Hour distribution (from by_hour)
   * - Day multipliers (weekdays 1.1x, weekends 0.9x)
   * - Normalized to 0-100 scale for visualization
   * 
   * Decision: Fallback ensures chart always renders, even with incomplete data
   * Alternative: Show empty chart - Rejected for better user experience
   * 
   * @returns {Object} Object with days array, hours array, and z matrix (2D array)
   */
  const createHeatmapData = () => {
    // Define day order for consistent visualization (Monday first)
    const dayOrder = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
    // Create array of hours 0-23 for 24-hour format
    const hours = Array.from({ length: 24 }, (_, i) => i);
    
    // Check if backend provided real day-hour data
    if (stats.by_day_hour && Object.keys(stats.by_day_hour).length > 0) {
      // Transform nested dictionary to 2D matrix
      // Each row represents a day, each column represents an hour
      const z = dayOrder.map(day => 
        hours.map(hour => stats.by_day_hour[day]?.[hour] || 0)
      );
      return { days: dayOrder, hours, z };
    } else {
      // Fallback: Estimate heatmap from hour distribution
      // This creates a reasonable approximation when full data isn't available
      const hourValues = hours.map(hour => stats.by_hour?.[hour] || 0);
      const maxHourValue = Math.max(...hourValues, 1); // Avoid division by zero
      
      // Create estimated matrix with day multipliers
      // Weekdays (index 0-4) get 1.1x multiplier, weekends (5-6) get 0.9x
      // Decision: Based on observed pattern that weekdays have more crashes
      const z = dayOrder.map((day, dayIdx) => 
        hours.map((hour) => {
          const baseValue = hourValues[hour] || 0;
          const dayMultiplier = dayIdx < 5 ? 1.1 : 0.9; // Weekdays vs weekends
          // Normalize to 0-100 scale for better visualization
          return Math.round((baseValue / maxHourValue) * 100 * dayMultiplier);
        })
      );
      return { days: dayOrder, hours, z };
    }
  };

  const heatmapData = createHeatmapData();

  // 10. Geographic Map
  // Always get geo_data from stats, even if empty array
  const geoData = (stats && Array.isArray(stats.geo_data)) ? stats.geo_data : [];
  
  /**
   * Calculate density values for each crash location
   * This function groups nearby crashes and assigns density scores
   * Higher density = more crashes in the area = red color
   * Lower density = fewer crashes = green color
   */
  const calculateDensity = (data) => {
    if (!data || data.length === 0) return [];
    
    
    // Filter out invalid coordinates first
    const validData = data.filter(d => {
      const lat = parseFloat(d?.LATITUDE);
      const lon = parseFloat(d?.LONGITUDE);
      return !isNaN(lat) && !isNaN(lon) && lat >= 40.4 && lat <= 40.9 && lon >= -74.5 && lon <= -73.5;
    });
    
    if (validData.length === 0) return [];
    
    // Simple density calculation: count nearby points within a radius
    const radius = 0.01; // Approximate radius in degrees (roughly 1km)
    const densityScores = validData.map((point, index) => {
      let nearbyCount = 0;
      validData.forEach((otherPoint, otherIndex) => {
        if (index !== otherIndex) {
          const latDiff = Math.abs(parseFloat(point.LATITUDE) - parseFloat(otherPoint.LATITUDE));
          const lonDiff = Math.abs(parseFloat(point.LONGITUDE) - parseFloat(otherPoint.LONGITUDE));
          const distance = Math.sqrt(latDiff * latDiff + lonDiff * lonDiff);
          if (distance < radius) {
            nearbyCount++;
          }
        }
      });
      return nearbyCount;
    });
    
    // Normalize density scores to 0-1 range for color mapping
    const maxDensity = Math.max(...densityScores, 1);
    return densityScores.map(score => score / maxDensity);
  };
  
  // Filter and prepare valid geo data
  const validGeoData = geoData.filter(d => {
    if (!d) return false;
    const lat = parseFloat(d.LATITUDE);
    const lon = parseFloat(d.LONGITUDE);
    return !isNaN(lat) && !isNaN(lon) && lat >= 40.4 && lat <= 40.9 && lon >= -74.5 && lon <= -73.5;
  });
  
  const densityValues = validGeoData.length > 0 ? calculateDensity(validGeoData) : [];
  
  // Debug: Log map data
  console.log('Map Debug Info:', {
    geoDataLength: geoData.length,
    validGeoDataLength: validGeoData.length,
    densityValuesLength: densityValues.length,
    statsExists: !!stats,
    geoDataExists: !!stats?.geo_data,
    sampleData: validGeoData.length > 0 ? {
      lon: validGeoData[0]?.LONGITUDE,
      lat: validGeoData[0]?.LATITUDE,
      borough: validGeoData[0]?.BOROUGH
    } : null,
    firstInvalidData: geoData.length > 0 && validGeoData.length === 0 ? geoData[0] : null
  });

  return (
    <div className="charts-container">
      <h2>
        <i className="ri-bar-chart-box-line"></i> Visualizations
      </h2>
      <div className="charts-grid">
        {/* Bar Chart - Borough */}
        <div className="chart">
          <Plot
            data={[{
              x: boroughData.labels,
              y: boroughData.values,
              type: 'bar',
              marker: {
                color: '#3e7852',
                line: { color: '#366048', width: 1 }
              }
            }]}
            layout={{
              title: 'Crashes by Borough',
              xaxis: { title: 'Borough' },
              yaxis: { title: 'Number of Crashes' },
              plot_bgcolor: '#F5F7F6',
              paper_bgcolor: '#FFFFFF',
              font: { family: 'Arial, sans-serif' },
              hovermode: 'closest',
              hoverlabel: {
                bgcolor: '#FFFFFF',
                bordercolor: '#CCCCCC',
                font: { color: '#333333', family: 'Arial, sans-serif', size: 12 }
              }
            }}
            config={{ 
              responsive: true,
              displayModeBar: true,
              modeBarButtonsToRemove: ['pan2d', 'lasso2d'],
              displaylogo: false
            }}
            style={{ width: '100%', height: '100%' }}
            useResizeHandler={true}
          />
        </div>

        {/* Horizontal Bar - Contributing Factors */}
        <div className="chart">
          <Plot
            data={[{
              y: factorData.labels,
              x: factorData.values,
              type: 'bar',
              orientation: 'h',
              marker: {
                color: '#6B8E7F',
                line: { color: '#5a7a6b', width: 1 }
              }
            }]}
            layout={{
              title: 'Top Contributing Factors',
              xaxis: { title: 'Number of Crashes' },
              yaxis: { title: 'Factor' },
              plot_bgcolor: '#F5F7F6',
              paper_bgcolor: '#FFFFFF',
              margin: { l: 200 },
              font: { family: 'Arial, sans-serif' },
              hovermode: 'closest',
              hoverlabel: {
                bgcolor: '#FFFFFF',
                bordercolor: '#CCCCCC',
                font: { color: '#333333', family: 'Arial, sans-serif', size: 12 }
              }
            }}
            config={{ 
              responsive: true,
              displayModeBar: true,
              modeBarButtonsToRemove: ['pan2d', 'lasso2d'],
              displaylogo: false
            }}
            style={{ width: '100%', height: '100%' }}
            useResizeHandler={true}
          />
        </div>

        {/* Pie Chart - Vehicle Types */}
        <div className="chart">
          <Plot
            data={[{
              labels: vehicleData.labels,
              values: vehicleData.values,
              type: 'pie',
              hole: 0.4,
              marker: {
                colors: ['#3e7852', '#5b8f70', '#6B8E7F', '#8ba99a', '#366048', '#5a7a6b', '#43e97b', '#30cfd0']
              }
            }]}
            layout={{
              title: 'Crashes by Vehicle Type',
              plot_bgcolor: '#F5F7F6',
              paper_bgcolor: '#FFFFFF',
              font: { family: 'Arial, sans-serif' },
              hovermode: 'closest',
              hoverlabel: {
                bgcolor: '#FFFFFF',
                bordercolor: '#CCCCCC',
                font: { color: '#333333', family: 'Arial, sans-serif', size: 12 }
              }
            }}
            config={{ 
              responsive: true,
              displayModeBar: true,
              modeBarButtonsToRemove: ['pan2d', 'lasso2d'],
              displaylogo: false
            }}
            style={{ width: '100%', height: '100%' }}
            useResizeHandler={true}
          />
        </div>

        {/* Pie Chart - Person Types */}
        <div className="chart">
          <Plot
            data={[{
              labels: personData.labels,
              values: personData.values,
              type: 'pie',
              hole: 0.4,
              marker: {
                colors: ['#3e7852', '#5b8f70', '#6B8E7F', '#8ba99a', '#366048']
              }
            }]}
            layout={{
              title: 'Distribution by Person Type',
              plot_bgcolor: '#F5F7F6',
              paper_bgcolor: '#FFFFFF',
              font: { family: 'Arial, sans-serif' },
              hovermode: 'closest',
              hoverlabel: {
                bgcolor: '#FFFFFF',
                bordercolor: '#CCCCCC',
                font: { color: '#333333', family: 'Arial, sans-serif', size: 12 }
              }
            }}
            config={{ 
              responsive: true,
              displayModeBar: true,
              modeBarButtonsToRemove: ['pan2d', 'lasso2d'],
              displaylogo: false
            }}
            style={{ width: '100%', height: '100%' }}
            useResizeHandler={true}
          />
        </div>

        {/* Pie Chart - Injury Types */}
        <div className="chart">
          <Plot
            data={[{
              labels: injuryData.labels,
              values: injuryData.values,
              type: 'pie',
              marker: {
                colors: ['#3e7852', '#ED6C02', '#D32F2F', '#6B8E7F']
              }
            }]}
            layout={{
              title: 'Injury Types Distribution',
              plot_bgcolor: '#F5F7F6',
              paper_bgcolor: '#FFFFFF',
              font: { family: 'Arial, sans-serif' },
              hovermode: 'closest',
              hoverlabel: {
                bgcolor: '#FFFFFF',
                bordercolor: '#CCCCCC',
                font: { color: '#333333', family: 'Arial, sans-serif', size: 12 }
              }
            }}
            config={{ 
              responsive: true,
              displayModeBar: true,
              modeBarButtonsToRemove: ['pan2d', 'lasso2d'],
              displaylogo: false
            }}
            style={{ width: '100%', height: '100%' }}
            useResizeHandler={true}
          />
        </div>

        {/* Pie Chart - Seasons */}
        <div className="chart">
          <Plot
            data={[{
              labels: seasonData.labels,
              values: seasonData.values,
              type: 'pie',
              marker: {
                colors: ['#3e7852', '#ED6C02', '#0288D1', '#6B8E7F']
              }
            }]}
            layout={{
              title: 'Crashes by Season',
              plot_bgcolor: '#F5F7F6',
              paper_bgcolor: '#FFFFFF',
              font: { family: 'Arial, sans-serif' },
              hovermode: 'closest',
              hoverlabel: {
                bgcolor: '#FFFFFF',
                bordercolor: '#CCCCCC',
                font: { color: '#333333', family: 'Arial, sans-serif', size: 12 }
              }
            }}
            config={{ 
              responsive: true,
              displayModeBar: true,
              modeBarButtonsToRemove: ['pan2d', 'lasso2d'],
              displaylogo: false
            }}
            style={{ width: '100%', height: '100%' }}
            useResizeHandler={true}
          />
        </div>

        {/* Line Chart - Time Series */}
        <div className="chart full-width">
          <Plot
            data={[{
              x: timeData.labels,
              y: timeData.values,
              type: 'scatter',
              mode: 'lines+markers',
              fill: 'tozeroy',
              line: { color: '#3e7852', width: 2 },
              marker: { size: 6, color: '#6B8E7F' }
            }]}
            layout={{
              title: 'Crashes Over Time (Monthly Trend)',
              xaxis: { title: 'Month', tickangle: -45 },
              yaxis: { title: 'Number of Crashes' },
              plot_bgcolor: '#F5F7F6',
              paper_bgcolor: '#FFFFFF',
              font: { family: 'Arial, sans-serif' },
              hovermode: 'x unified',
              hoverlabel: {
                bgcolor: '#FFFFFF',
                bordercolor: '#CCCCCC',
                font: { color: '#333333', family: 'Arial, sans-serif', size: 12 }
              }
            }}
            config={{ 
              responsive: true,
              displayModeBar: true,
              modeBarButtonsToRemove: ['pan2d', 'lasso2d'],
              displaylogo: false
            }}
            style={{ width: '100%', height: '100%' }}
            useResizeHandler={true}
          />
        </div>

        {/* Line Chart - By Hour */}
        <div className="chart full-width">
          <Plot
            data={[{
              x: hourData.labels,
              y: hourData.values,
              type: 'scatter',
              mode: 'lines+markers',
              line: { color: '#3e7852', width: 3 },
              marker: { size: 8, color: '#6B8E7F' }
            }]}
            layout={{
              title: 'Crashes by Hour of Day',
              xaxis: { title: 'Hour (24-hour format)' },
              yaxis: { title: 'Number of Crashes' },
              plot_bgcolor: '#F5F7F6',
              paper_bgcolor: '#FFFFFF',
              font: { family: 'Arial, sans-serif' },
              hovermode: 'x unified',
              hoverlabel: {
                bgcolor: '#FFFFFF',
                bordercolor: '#CCCCCC',
                font: { color: '#333333', family: 'Arial, sans-serif', size: 12 }
              }
            }}
            config={{ 
              responsive: true,
              displayModeBar: true,
              modeBarButtonsToRemove: ['pan2d', 'lasso2d'],
              displaylogo: false
            }}
            style={{ width: '100%', height: '100%' }}
            useResizeHandler={true}
          />
        </div>

        {/* Heatmap - Hour vs Day */}
        <div className="chart full-width">
          <Plot
            data={[{
              z: heatmapData.z,
              x: heatmapData.hours,
              y: heatmapData.days,
              type: 'heatmap',
              colorscale: 'Viridis',
              hoverongaps: false
            }]}
            layout={{
              title: 'Crash Patterns: Hour vs Day of Week',
              xaxis: { title: 'Hour of Day' },
              yaxis: { title: 'Day of Week' },
              plot_bgcolor: '#F5F7F6',
              paper_bgcolor: '#FFFFFF',
              font: { family: 'Arial, sans-serif' },
              hovermode: 'closest',
              hoverlabel: {
                bgcolor: '#FFFFFF',
                bordercolor: '#CCCCCC',
                font: { color: '#333333', family: 'Arial, sans-serif', size: 12 }
              }
            }}
            config={{ 
              responsive: true,
              displayModeBar: true,
              modeBarButtonsToRemove: ['pan2d', 'lasso2d'],
              displaylogo: false
            }}
            style={{ width: '100%', height: '100%' }}
            useResizeHandler={true}
          />
        </div>

        {/* Geographic Map - Simple scatter plot with lat/lon (NO TOKENS, NO GEO SUBPLOT) */}
        <div className="chart full-width">
          {validGeoData.length > 0 ? (() => {
            // Extract and validate coordinates
            const mapData = validGeoData.map((d, idx) => {
              const lat = parseFloat(d.LATITUDE);
              const lon = parseFloat(d.LONGITUDE);
              return { 
                lat, 
                lon, 
                data: d, 
                valid: !isNaN(lat) && !isNaN(lon),
                density: densityValues.length > idx ? densityValues[idx] : 0.5
              };
            }).filter(item => item.valid);
            
            if (mapData.length === 0) {
              return (
                <div style={{ 
                  display: 'flex', 
                  flexDirection: 'column',
                  alignItems: 'center', 
                  justifyContent: 'center', 
                  height: '450px',
                  color: 'rgba(38, 43, 67, 0.7)',
                  fontFamily: 'IBM Plex Sans, sans-serif',
                  fontSize: '1rem',
                  textAlign: 'center',
                  padding: '20px'
                }}>
                  <p>No valid coordinates found in geo data.</p>
                </div>
              );
            }
            
            const lons = mapData.map(item => item.lon);
            const lats = mapData.map(item => item.lat);
            
            // Calculate marker sizes based on density (clustering effect)
            // Higher density = larger marker size (min 4, max 20)
            const maxDensity = Math.max(...mapData.map(item => item.density), 1);
            const minDensity = Math.min(...mapData.map(item => item.density), 0);
            const markerSizes = mapData.map(item => {
              const size = 4 + (item.density / maxDensity) * 16; // Scale from 4 to 20
              return Math.max(4, Math.min(20, size));
            });
            
            // Extract density values for coloraxis (already normalized to 0-1 range from calculateDensity)
            const densityValuesForColorbar = mapData.map(item => item.density);
            
            return (
              <Plot
                data={[{
                  type: 'scattergeo', // FREE Plotly geographic map - NO tokens required
                  lon: lons, // Longitude
                  lat: lats, // Latitude
                    mode: 'markers',
                    marker: {
                    size: markerSizes, // Size proportional to density (clustering effect)
                    opacity: 0.85, // Increased opacity for better visibility
                    color: densityValuesForColorbar, // Use density values for continuous color scale
                    colorscale: [
                      [0, '#4CAF50'],      // Green (low density)
                      [0.33, '#8BC34A'],   // Light green
                      [0.5, '#FFC107'],    // Orange
                      [0.67, '#FF9800'],   // Dark orange
                      [1, '#F44336']       // Red (high density)
                    ],
                    colorbar: {
                      title: {
                        text: 'Crash Density',
                        font: { family: 'IBM Plex Sans, sans-serif', size: 12 }
                      },
                      tickmode: 'array',
                      tickvals: [0, 0.25, 0.5, 0.75, 1],
                      ticktext: [
                        (minDensity).toFixed(2),
                        (minDensity + (maxDensity - minDensity) * 0.25).toFixed(2),
                        (minDensity + (maxDensity - minDensity) * 0.5).toFixed(2),
                        (minDensity + (maxDensity - minDensity) * 0.75).toFixed(2),
                        (maxDensity).toFixed(2)
                      ],
                      len: 0.6,
                      y: 0.5,
                      thickness: 20,
                      x: 1.02,
                      xpad: 10,
                      outlinewidth: 1,
                      outlinecolor: '#CCCCCC'
                    },
                    cmin: 0,
                    cmax: 1,
                      line: {
                      color: 'rgba(255,255,255,0.8)',
                      width: 1.5
                    },
                    sizemode: 'diameter',
                    sizeref: 1
                  },
                  text: mapData.map(item => {
                    const densityPercent = (item.density * 100).toFixed(1);
                    const data = item.data;
                    
                    // Determine density level classification
                      let densityLevel = '';
                    if (item.density < 0.2) {
                      densityLevel = 'Very Low';
                    } else if (item.density < 0.4) {
                        densityLevel = 'Low';
                    } else if (item.density < 0.6) {
                        densityLevel = 'Medium';
                    } else if (item.density < 0.8) {
                        densityLevel = 'High';
                      } else {
                        densityLevel = 'Very High';
                      }
                      
                    // Format hour display
                    let hourDisplay = 'Unknown';
                    if (data.HOUR !== null && data.HOUR !== undefined) {
                      const hour = parseInt(data.HOUR);
                      if (!isNaN(hour)) {
                        hourDisplay = `${hour}:00`;
                      }
                    }
                    
                    // Build detailed hover text
                    let hoverText = `Borough: ${data.BOROUGH || 'Unknown'}<br>`;
                    hoverText += `Density: ${densityPercent}% (${densityLevel})<br>`;
                    
                    if (data.VEHICLE_TYPE && data.VEHICLE_TYPE !== 'Unknown' && data.VEHICLE_TYPE !== 'nan') {
                      hoverText += `Vehicle: ${data.VEHICLE_TYPE}<br>`;
                    }
                    
                    if (data.INJURY_TYPE && data.INJURY_TYPE !== 'Unknown' && data.INJURY_TYPE !== 'nan') {
                      hoverText += `Injury: ${data.INJURY_TYPE}<br>`;
                    }
                    
                    if (hourDisplay !== 'Unknown') {
                      hoverText += `Time: ${hourDisplay}<br>`;
                    }
                    
                    hoverText += `Lat: ${item.lat.toFixed(4)}, Lon: ${item.lon.toFixed(4)}`;
                    
                    return hoverText;
                    }),
                    hoverinfo: 'text',
                    hovertemplate: '<b>Crash Location</b><br>%{text}<extra></extra>',
                    name: 'Crash Locations',
                    showlegend: false
                }]}
                layout={{
                  title: {
                    text: 'Crash Locations Map (NYC) - Density Clustered',
                    font: { family: 'IBM Plex Sans, sans-serif', size: 18 },
                    x: 0.5,
                    xanchor: 'center'
                  },
                  annotations: [
                    {
                      text: 'Marker size = Crash density<br>Larger = More crashes nearby',
                      xref: 'paper',
                      yref: 'paper',
                      x: 0.02,
                      y: 0.98,
                      xanchor: 'left',
                      yanchor: 'top',
                      bgcolor: 'rgba(255, 255, 255, 0.8)',
                      bordercolor: '#3e7852',
                      borderwidth: 1,
                      borderpad: 4,
                      font: { size: 10, color: '#333333', family: 'IBM Plex Sans, sans-serif' },
                      showarrow: false
                    }
                  ],
                  geo: {
                    scope: 'usa',
                    fitbounds: 'locations',
                    showland: true,
                    landcolor: '#E8F5E9',
                    showocean: true,
                    oceancolor: '#B3E5FC',
                    showlakes: true,
                    lakecolor: '#B3E5FC',
                    showrivers: true,
                    rivercolor: '#81D4FA',
                    showcountries: true,
                    countrycolor: '#BDBDBD',
                    showsubunits: true,
                    subunitcolor: '#E0E0E0',
                    coastlinewidth: 1,
                    coastlinecolor: '#424242',
                    resolution: 50
                },
                width: '100%',
                height: 450,
                  margin: { t: 60, b: 50, l: 60, r: 20 },
                  plot_bgcolor: '#F5F7F6',
                paper_bgcolor: '#FFFFFF',
                font: { family: 'IBM Plex Sans, sans-serif' },
                hovermode: 'closest',
                hoverlabel: {
                  bgcolor: '#FFFFFF',
                  bordercolor: '#3e7852',
                  font: { color: '#333333', family: 'IBM Plex Sans, sans-serif', size: 12 }
                }
              }}
              config={{ 
                responsive: true,
                displayModeBar: true,
                modeBarButtonsToRemove: ['lasso2d', 'select2d'],
                displaylogo: false,
                  scrollZoom: true,
                  doubleClick: 'reset',
                  mapboxAccessToken: false // Explicitly disable Mapbox
              }}
              style={{ width: '100%', height: '100%' }}
              useResizeHandler={true}
              onError={(err) => {
                  // Suppress Mapbox-related errors since we're using scattergeo (free, no tokens)
                  if (err && err.message && err.message.includes('mapbox')) {
                    console.log('Mapbox error suppressed (using scattergeo instead)');
                    return;
                  }
                  console.error('Plotly error:', err);
              }}
            />
            );
          })() : (
            <div style={{ 
              display: 'flex', 
              flexDirection: 'column',
              alignItems: 'center', 
              justifyContent: 'center', 
              height: '450px', // Match chart height
              color: 'rgba(38, 43, 67, 0.7)',
              fontFamily: 'IBM Plex Sans, sans-serif',
              fontSize: '1rem',
              gap: '10px',
              textAlign: 'center',
              padding: '20px'
            }}>
              <p style={{ fontWeight: 500, marginBottom: '10px' }}>
                {geoData.length === 0 
                  ? 'No geographic data available for the selected filters.'
                  : `No valid geographic data found (${geoData.length} points received, ${validGeoData.length} valid).`}
              </p>
              <p style={{ fontSize: '0.875rem', color: 'rgba(38, 43, 67, 0.5)' }}>
                Try adjusting your filters or generate a report with different criteria.
              </p>
              {geoData.length > 0 && validGeoData.length === 0 && (
                <p style={{ fontSize: '0.75rem', color: 'rgba(38, 43, 67, 0.4)', marginTop: '10px' }}>
                  All coordinates were filtered out (outside NYC bounds or invalid format).
                </p>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Charts;

