from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np
from datetime import datetime

# Initialize Flask application with CORS enabled for React frontend
app = Flask(__name__)
# Enable CORS for all origins (update this to specific Vercel domain after deployment)
CORS(app, resources={r"/api/*": {"origins": "*"}})  # Allows all origins for production

# ============================================================================
# DATA LOADING AND PREPROCESSING
# ============================================================================

# Load the pre-cleaned and integrated dataset
# Note: This CSV file contains data that has already been cleaned and integrated
# in a separate data exploration notebook. The cleaning process included:
# 1. Pre-integration cleaning of individual datasets
# 2. Integration via COLLISION_ID foreign key
# 3. Post-integration cleaning (handling duplicates, missing values, outliers)

import os
import urllib.request
import requests
from io import StringIO

# CSV file path - checks multiple possible locations
if os.path.exists('crashes_cleaned.csv'):
    CSV_FILE = 'crashes_cleaned.csv'  # Same directory as app.py (backend/)
elif os.path.exists('backend/crashes_cleaned.csv'):
    CSV_FILE = 'backend/crashes_cleaned.csv'  # If running from project root
else:
    CSV_FILE = 'crashes_cleaned.csv'  # Default - will download if not found
CSV_URL = os.environ.get('CSV_URL', None)  # Set this in Render environment variables

# Check if CSV file exists locally first (for local testing)
if os.path.exists(CSV_FILE):
    print(f"Using local CSV file: {CSV_FILE}")

# Download CSV only if it doesn't exist locally and URL is provided (for production)
elif CSV_URL and not os.path.exists(CSV_FILE):
    print(f"CSV file not found. Downloading from {CSV_URL}...")
    try:
        # Handle Google Drive downloads with virus scan warning
        if 'drive.google.com' in CSV_URL:
            # Use requests to handle cookies and redirects
            session = requests.Session()
            response = session.get(CSV_URL, stream=True)
            
            # Check if we got HTML (virus scan warning) instead of the file
            if response.headers.get('Content-Type', '').startswith('text/html'):
                print("Received HTML page (virus scan warning), extracting download link...")
                # Parse HTML to find the actual download URL
                html_content = response.text
                # Look for the form action URL
                if 'drive.usercontent.google.com/download' in html_content:
                    # Extract the form action URL and parameters
                    import re
                    # Find the form action
                    form_match = re.search(r'action="([^"]+)"', html_content)
                    if form_match:
                        form_url = form_match.group(1)
                        # Extract hidden form fields
                        id_match = re.search(r'name="id"\s+value="([^"]+)"', html_content)
                        if id_match:
                            file_id = id_match.group(1)
                            # Construct direct download URL
                            direct_url = f"https://drive.usercontent.google.com/download?id={file_id}&export=download&confirm=t&uuid="
                            print(f"Using direct download URL...")
                            response = session.get(direct_url, stream=True)
                        else:
                            # Try alternative: use the form URL directly
                            response = session.get(form_url, stream=True)
            
            # Download the file in chunks
            total_size = int(response.headers.get('content-length', 0))
            print(f"Downloading {total_size / (1024*1024):.2f} MB...")
            
            # Download the full file in chunks
            with open(CSV_FILE, 'wb') as f:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            if downloaded % (50 * 1024 * 1024) == 0:  # Print every 50MB
                                print(f"Downloaded {downloaded / (1024*1024):.2f} MB ({percent:.1f}%)")
            
            print(f"Download complete! Total: {downloaded / (1024*1024):.2f} MB")
        else:
            # For non-Google Drive URLs, use urllib
            urllib.request.urlretrieve(CSV_URL, CSV_FILE)
            print("Download complete!")
    except Exception as e:
        print(f"Error downloading CSV: {e}")
        raise

print("CSV file ready. Flask app starting...")

# Global cache for dataframe (lazy loading)
_df_cache = None

def get_dataframe():
    """Lazy-load the CSV file on first request to avoid startup timeout"""
    global _df_cache
    
    # Return cached dataframe if already loaded
    if _df_cache is not None:
        return _df_cache
    
    print("Loading data...")
    # Load the full CSV file (Railway has more memory than Render free tier)
    try:
        # Use engine='python' if 'c' engine fails, and handle errors gracefully
        try:
            df = pd.read_csv(CSV_FILE, engine='c', on_bad_lines='skip', low_memory=False)
            print(f"Full dataset loaded: {len(df)} rows")
        except Exception as c_engine_error:
            print(f"C engine failed, trying Python engine: {c_engine_error}")
            # Fallback to Python engine if C engine fails
            df = pd.read_csv(CSV_FILE, engine='python', on_bad_lines='skip', low_memory=False)
            print(f"Full dataset loaded with Python engine: {len(df)} rows")
    except MemoryError as e:
        print(f"Memory error loading full file: {e}")
        print("If this happens on Railway, consider upgrading the plan or optimizing the dataset")
        raise
    except Exception as e:
        print(f"Error loading CSV: {e}")
        import traceback
        traceback.print_exc()
        raise

    # Debug: Print column names to see what we have
    print(f"CSV columns: {list(df.columns)[:10]}...")  # Print first 10 columns

    # Convert date columns to datetime format
    # Using 'errors=coerce' to handle invalid dates gracefully (converts to NaT)
    # Decision: We use 'coerce' instead of 'raise' because some records may have
    # malformed dates, and we want to preserve other data in those records

    # Check which date column exists and standardize to 'CRASH_DATE'
    date_column = None
    if 'CRASH_DATE' in df.columns:
        date_column = 'CRASH_DATE'
    elif 'CRASH DATE' in df.columns:
        date_column = 'CRASH DATE'
    elif 'crash_date' in df.columns:
        date_column = 'crash_date'
    elif 'Crash Date' in df.columns:
        date_column = 'Crash Date'
    else:
        # Try to find any column with 'date' in the name (case insensitive)
        date_cols = [col for col in df.columns if 'date' in col.lower()]
        if date_cols:
            date_column = date_cols[0]
            print(f"Using date column: {date_column}")
        else:
            raise ValueError("No date column found in CSV file. Columns: " + str(list(df.columns)))

    # Always convert CRASH_DATE to datetime (standardize the column)
    if date_column == 'CRASH_DATE':
        # Column already has the right name, just convert to datetime
        df['CRASH_DATE'] = pd.to_datetime(df['CRASH_DATE'], errors='coerce')
    elif date_column:
        # Column has different name, convert and rename
        df['CRASH_DATE'] = pd.to_datetime(df[date_column], errors='coerce')
    else:
        raise ValueError("Could not determine date column")

    # Extract year from crash date for filtering and time series analysis
    # This allows us to filter by year and create yearly trend visualizations
    df['YEAR'] = df['CRASH_DATE'].dt.year

    print(f"Data loaded: {len(df)} records")
    print(f"Columns: {list(df.columns)}")

    # Verify required columns for geo_data exist
    required_geo_columns = ['LATITUDE', 'LONGITUDE', 'BOROUGH']
    missing_columns = [col for col in required_geo_columns if col not in df.columns]
    if missing_columns:
        print(f"⚠️ WARNING: Missing required columns for geo_data: {missing_columns}")
    else:
        # Check if we have any valid coordinates
        geo_check = df[['LATITUDE', 'LONGITUDE']].dropna()
        if len(geo_check) > 0:
            print(f"✅ Geo data available: {len(geo_check)} records with coordinates")
            print(f"   Lat range: {geo_check['LATITUDE'].min():.4f} to {geo_check['LATITUDE'].max():.4f}")
            print(f"   Lon range: {geo_check['LONGITUDE'].min():.4f} to {geo_check['LONGITUDE'].max():.4f}")
        else:
            print(f"⚠️ WARNING: No records with valid coordinates found in dataset")
    
    # Cache the dataframe
    _df_cache = df
    return _df_cache
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint - triggers data loading on first call"""
    csv_exists = os.path.exists(CSV_FILE)
    
    # Trigger lazy load if not already loaded
    if not _df_cache and csv_exists:
        try:
            print("⏳ Health check triggering data load (this may take 30-60 seconds)...")
            df = get_dataframe()
            print(f"✅ Data loaded successfully via health check!")
        except Exception as e:
            print(f"❌ Failed to load data: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'status': 'unhealthy',
                'error': f'Failed to load data: {str(e)}',
                'csv_file_exists': csv_exists
            }), 500
    
    data_loaded = _df_cache is not None
    
    response = {
        'status': 'healthy',
        'csv_file_exists': csv_exists,
        'data_loaded': data_loaded
    }
    
    if data_loaded:
        df = _df_cache
        geo_check = df[['LATITUDE', 'LONGITUDE']].dropna() if 'LATITUDE' in df.columns and 'LONGITUDE' in df.columns else pd.DataFrame()
        response.update({
            'total_records': len(df),
            'columns': len(df.columns),
            'has_geo_data': len(geo_check) > 0,
            'geo_data_count': len(geo_check),
            'required_columns': {
                'LATITUDE': 'LATITUDE' in df.columns,
                'LONGITUDE': 'LONGITUDE' in df.columns,
                'BOROUGH': 'BOROUGH' in df.columns
            }
        })
    
    return jsonify(response)

@app.route('/api/filters', methods=['GET'])
def get_filter_options():
    """Get all available filter options"""
    try:
        df = get_dataframe()
        boroughs = df['BOROUGH'].dropna().unique().tolist()
        years = sorted(df['YEAR'].dropna().unique().astype(int).tolist())
        vehicle_types = df['VEHICLE TYPE CODE 1'].dropna().value_counts().head(15).index.tolist()
        contributing_factors = df['CONTRIBUTING FACTOR VEHICLE 1'].dropna().value_counts().head(15).index.tolist()
        person_types = df['PERSON_TYPE'].dropna().unique().tolist()
        injury_types = df['PERSON_INJURY'].dropna().unique().tolist()
        
        return jsonify({
            'boroughs': ['All'] + sorted([str(b) for b in boroughs if str(b) != 'nan']),
            'years': ['All'] + [str(y) for y in years],
            'vehicle_types': ['All'] + [str(v) for v in vehicle_types],
            'contributing_factors': ['All'] + [str(f) for f in contributing_factors],
            'person_types': ['All'] + [str(p) for p in person_types],
            'injury_types': ['All'] + [str(i) for i in injury_types]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['POST'])
def get_stats():
    """
    Generate comprehensive statistics based on user-selected filters.
    
    This endpoint applies multiple filters to the dataset and calculates various
    statistics for visualization. The filtering approach uses sequential filtering
    (AND logic) - all selected filters must match for a record to be included.
    
    Filtering Strategy:
    - We use df.copy() to avoid modifying the original dataframe
    - Each filter is applied sequentially, reducing the dataset size progressively
    - Decision: Sequential filtering is more memory-efficient than creating multiple
      boolean masks and combining them, especially for large datasets
    
    Statistical Calculations:
    - Total crashes: Uses nunique() on COLLISION_ID to count distinct crashes
      (not persons, since one crash can involve multiple people)
    - Total persons: Uses len() to count all person records in filtered data
    - Aggregations: Group by various dimensions for chart data
    
    Returns:
        JSON object containing all statistics and chart-ready data
    """
    try:
        df = get_dataframe()
        # Get filter parameters from request body
        filters = request.json
        filtered_df = df.copy()  # Create a copy to avoid modifying original data
        
        # ========================================================================
        # APPLY FILTERS (Sequential Filtering Approach)
        # ========================================================================
        # Each filter is applied only if it's not 'All' (which means no filter)
        # Decision: We check for 'All' explicitly rather than checking for None
        # because the frontend always sends 'All' as a string when no filter is selected
        
        if filters.get('borough') and filters['borough'] != 'All':
            filtered_df = filtered_df[filtered_df['BOROUGH'] == filters['borough']]
        
        if filters.get('year') and filters['year'] != 'All':
            # Convert year to int for proper comparison
            # Decision: We convert here rather than storing as int in dataframe
            # to allow 'All' as a string option in the frontend
            filtered_df = filtered_df[filtered_df['YEAR'] == int(filters['year'])]
        
        if filters.get('vehicle_type') and filters['vehicle_type'] != 'All':
            filtered_df = filtered_df[filtered_df['VEHICLE TYPE CODE 1'] == filters['vehicle_type']]
        
        if filters.get('contributing_factor') and filters['contributing_factor'] != 'All':
            filtered_df = filtered_df[filtered_df['CONTRIBUTING FACTOR VEHICLE 1'] == filters['contributing_factor']]
        
        if filters.get('person_type') and filters['person_type'] != 'All':
            filtered_df = filtered_df[filtered_df['PERSON_TYPE'] == filters['person_type']]
        
        if filters.get('injury_type') and filters['injury_type'] != 'All':
            filtered_df = filtered_df[filtered_df['PERSON_INJURY'] == filters['injury_type']]
        
        # ========================================================================
        # CALCULATE SUMMARY STATISTICS
        # ========================================================================
        
        # Total unique crashes (not persons) - important distinction
        # Decision: Use nunique() on COLLISION_ID because one crash can involve
        # multiple persons. This gives us the actual number of crash events.
        total_crashes = filtered_df['COLLISION_ID'].nunique()
        
        # Total persons involved in crashes (all person records in filtered data)
        total_persons = len(filtered_df)
        
        # Sum of injuries and deaths across all crashes
        # Note: These are aggregated at the person level, so we sum the values
        total_injuries = filtered_df['NUMBER OF PERSONS INJURED'].sum()
        total_deaths = filtered_df['NUMBER OF PERSONS KILLED'].sum()
        
        # ========================================================================
        # CALCULATE AGGREGATED STATISTICS FOR CHARTS
        # ========================================================================
        
        # Crashes grouped by borough
        # Using nunique() to count distinct crashes per borough (not person count)
        by_borough = filtered_df.groupby('BOROUGH')['COLLISION_ID'].nunique().to_dict()
        
        # Top 10 vehicle types by frequency
        # Decision: Limit to top 10 to keep charts readable and focus on most common types
        by_vehicle = filtered_df['VEHICLE TYPE CODE 1'].value_counts().head(10).to_dict()
        
        # Top 10 contributing factors by frequency
        # Decision: Limit to top 10 for visualization clarity
        by_factor = filtered_df['CONTRIBUTING FACTOR VEHICLE 1'].value_counts().head(10).to_dict()
        
        # Distribution by person type (Pedestrian, Cyclist, Occupant)
        by_person_type = filtered_df['PERSON_TYPE'].value_counts().to_dict()
        
        # Distribution by injury severity (Killed, Injured, Unspecified)
        by_injury = filtered_df['PERSON_INJURY'].value_counts().to_dict()
        
        # ========================================================================
        # TIME-BASED ANALYSIS
        # ========================================================================
        
        # Time series: Crashes grouped by month
        # Using to_period('M') to group by month-year (e.g., '2022-01')
        # Decision: We group by month rather than day to reduce data points
        # and show clearer trends. For daily analysis, we could use 'D' period.
        time_series = filtered_df.groupby(filtered_df['CRASH_DATE'].dt.to_period('M'))['COLLISION_ID'].nunique()
        by_month = {str(k): int(v) for k, v in time_series.items()}
        
        # Crashes by hour of day (0-23)
        # This helps identify peak crash hours (rush hours, etc.)
        by_hour = filtered_df.groupby('HOUR')['COLLISION_ID'].nunique().to_dict()
        
        # Heatmap data: Crashes by day of week AND hour
        # This creates a 2D pattern showing when crashes are most likely
        # Map day numbers to day names for better readability
        # Day encoding: 0=Monday, 1=Tuesday, ..., 6=Sunday
        # Note: This mapping is for data transformation only, not static data
        # All actual crash counts come from the CSV file via groupby operations
        day_names = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 
                     4: 'Friday', 5: 'Saturday', 6: 'Sunday'}
        by_day_hour = filtered_df.groupby(['DAY', 'HOUR'])['COLLISION_ID'].nunique()
        
        # Convert to nested dictionary structure: {day_name: {hour: count}}
        # This format is easier for the frontend to process for heatmap visualization
        heatmap_data = {}
        for (day, hour), count in by_day_hour.items():
            day_name = day_names.get(day, f'Day_{day}')  # Fallback if day number not in mapping
            if day_name not in heatmap_data:
                heatmap_data[day_name] = {}
            heatmap_data[day_name][int(hour)] = int(count)
        
        # Seasonal distribution (Spring, Summer, Fall, Winter)
        # The 'season' column was created during data cleaning based on crash date
        by_season = filtered_df['season'].value_counts().to_dict()
        
        # ========================================================================
        # SAFETY EQUIPMENT ANALYSIS
        # ========================================================================
        
        # Safety equipment usage statistics
        # SAFETY_USED is a binary indicator (1=used, 0=not used) created during cleaning
        # Decision: We count unique persons rather than total records to avoid
        # double-counting if a person appears in multiple crash records
        safety_stats = {
            'used': int(filtered_df[filtered_df['SAFETY_USED'] == 1]['PERSON_ID'].nunique()),
            'not_used': int(filtered_df[filtered_df['SAFETY_USED'] == 0]['PERSON_ID'].nunique())
        }
        
        # ========================================================================
        # GEOGRAPHIC DATA FOR MAP VISUALIZATION
        # ========================================================================
        
        # Extract geographic coordinates for map visualization
        # Decision: We limit to 500 points to avoid performance issues with
        # large datasets. For production, consider implementing pagination or
        # clustering for better performance with very large datasets.
        # We dropna() to ensure we only include records with valid coordinates
        # Convert to float to ensure proper numeric format for frontend
        # IMPORTANT: Always return geo_data, even if empty, so frontend can handle it properly
        # Include additional fields for enhanced map visualization
        geo_columns = ['LATITUDE', 'LONGITUDE', 'BOROUGH', 'VEHICLE TYPE CODE 1', 
                      'PERSON_INJURY', 'HOUR', 'CRASH_DATE']
        # Only include columns that exist in the dataframe
        available_columns = [col for col in geo_columns if col in filtered_df.columns]
        geo_df = filtered_df[available_columns].dropna(subset=['LATITUDE', 'LONGITUDE'])
        
        # Filter to NYC bounds only if we have data
        if len(geo_df) > 0:
            geo_df = geo_df[(geo_df['LATITUDE'] >= 40.4) & (geo_df['LATITUDE'] <= 40.9) & 
                            (geo_df['LONGITUDE'] >= -74.5) & (geo_df['LONGITUDE'] <= -73.5)]
            geo_data = geo_df.head(500).to_dict('records')
        else:
            # Return empty list if no data after filtering
            geo_data = []
        
        # Ensure numeric types for coordinates and filter invalid records
        valid_geo_data = []
        for record in geo_data:
            if record and isinstance(record, dict):  # Check if record exists and is a dict
                try:
                    lat = float(record.get('LATITUDE', 0))
                    lon = float(record.get('LONGITUDE', 0))
                    # Validate coordinates are within NYC bounds
                    if 40.4 <= lat <= 40.9 and -74.5 <= lon <= -73.5:
                        geo_record = {
                            'LATITUDE': lat,
                            'LONGITUDE': lon,
                            'BOROUGH': record.get('BOROUGH', 'Unknown')
                        }
                        # Add additional fields if available
                        if 'VEHICLE TYPE CODE 1' in record:
                            geo_record['VEHICLE_TYPE'] = str(record.get('VEHICLE TYPE CODE 1', 'Unknown'))
                        if 'PERSON_INJURY' in record:
                            geo_record['INJURY_TYPE'] = str(record.get('PERSON_INJURY', 'Unknown'))
                        if 'HOUR' in record:
                            hour_val = record.get('HOUR')
                            if pd.notna(hour_val):
                                geo_record['HOUR'] = int(float(hour_val))
                            else:
                                geo_record['HOUR'] = None
                        if 'CRASH_DATE' in record:
                            crash_date = record.get('CRASH_DATE')
                            if pd.notna(crash_date):
                                geo_record['CRASH_DATE'] = str(crash_date)
                        valid_geo_data.append(geo_record)
                except (ValueError, TypeError, KeyError) as e:
                    # Skip invalid records
                    continue
        
        # Use the cleaned geo_data
        geo_data = valid_geo_data
        
        # Ensure geo_data is always a list, even if empty (important for frontend)
        if not isinstance(geo_data, list):
            geo_data = []
        
        # Debug: Log geo_data info for troubleshooting
        print(f"[DEBUG] Geo data processing:")
        print(f"  - Initial filtered records: {len(filtered_df)}")
        print(f"  - Records with coordinates: {len(geo_df) if len(geo_df) > 0 else 0}")
        print(f"  - Final valid geo_data count: {len(geo_data)}")
        if len(geo_data) > 0:
            print(f"  - Sample geo data: {geo_data[0]}")
            print(f"  - Lat range: {min([r['LATITUDE'] for r in geo_data]):.4f} to {max([r['LATITUDE'] for r in geo_data]):.4f}")
            print(f"  - Lon range: {min([r['LONGITUDE'] for r in geo_data]):.4f} to {max([r['LONGITUDE'] for r in geo_data]):.4f}")
        else:
            print(f"  - WARNING: No valid geo_data to return!")
            # Check if we have data but it's being filtered out
            if len(filtered_df) > 0:
                sample_coords = filtered_df[['LATITUDE', 'LONGITUDE']].dropna().head(5)
                if len(sample_coords) > 0:
                    print(f"  - Sample coordinates from filtered_df: {sample_coords.to_dict('records')}")
        
        return jsonify({
            'total_crashes': int(total_crashes),
            'total_persons': int(total_persons),
            'total_injuries': int(total_injuries),
            'total_deaths': int(total_deaths),
            'by_borough': by_borough,
            'by_vehicle': by_vehicle,
            'by_factor': by_factor,
            'by_person_type': by_person_type,
            'by_injury': by_injury,
            'by_month': by_month,
            'by_hour': by_hour,
            'by_day_hour': heatmap_data,  # Real heatmap data
            'by_season': by_season,
            'safety_stats': safety_stats,
            'geo_data': geo_data
        })
    except Exception as e:
        print(f"Error in get_stats: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/search', methods=['POST'])
def search():
    """
    Parse natural language search queries and extract relevant filters.
    
    This endpoint implements a simple keyword-based search parser that extracts
    filter values from natural language queries. It uses pattern matching to
    identify boroughs, years, person types, and injury types.
    
    Parsing Strategy:
    - Case-insensitive matching (convert query to lowercase)
    - Keyword-based extraction (simple but effective for common queries)
    - Priority-based matching (first match wins for mutually exclusive categories)
    
    Limitations:
    - Does not handle complex queries with multiple conditions well
    - No fuzzy matching or typo tolerance
    - Alternative: Could use NLP libraries (spaCy, NLTK) for more sophisticated parsing
    
    Example queries:
    - "Brooklyn 2022 pedestrian crashes" → {borough: 'BROOKLYN', year: '2022', person_type: 'Pedestrian'}
    - "Manhattan cyclist killed" → {borough: 'MANHATTAN', person_type: 'Cyclist', injury_type: 'Killed'}
    
    Returns:
        JSON object with extracted filters that can be applied to get_stats()
    """
    try:
        # Get and normalize search query
        query = request.json.get('query', '').lower()
        filters = {}
        
        # ========================================================================
        # EXTRACT BOROUGH
        # ========================================================================
        # Match borough names in query (case-insensitive)
        # Decision: We check for full borough names rather than abbreviations
        # to avoid false matches. Could be enhanced with fuzzy matching.
        boroughs = ['bronx', 'brooklyn', 'manhattan', 'queens', 'staten island']
        for borough in boroughs:
            if borough in query:
                filters['borough'] = borough.upper()  # Store in uppercase to match data format
                break  # Take first match only
        
        # ========================================================================
        # EXTRACT YEAR
        # ========================================================================
        # Use regex to find 4-digit years starting with 20 (2000-2099)
        # Pattern: \b(20\d{2})\b ensures we match complete years, not partial numbers
        import re
        years = re.findall(r'\b(20\d{2})\b', query)
        if years:
            filters['year'] = years[0]  # Take first year found
        
        # ========================================================================
        # EXTRACT PERSON TYPE
        # ========================================================================
        # Match keywords for person types
        # Decision: Use if-elif chain to ensure only one person type is selected
        # (mutually exclusive categories)
        if 'pedestrian' in query:
            filters['person_type'] = 'Pedestrian'
        elif 'cyclist' in query or 'bicycle' in query or 'bike' in query:
            filters['person_type'] = 'Cyclist'
        elif 'driver' in query or 'motorist' in query:
            filters['person_type'] = 'Occupant'
        
        # ========================================================================
        # EXTRACT INJURY TYPE
        # ========================================================================
        # Match keywords for injury severity
        # Decision: Check for 'killed' first as it's more specific than 'injured'
        # (fatal crashes are a subset of all crashes)
        if 'killed' in query or 'fatal' in query or 'death' in query:
            filters['injury_type'] = 'Killed'
        elif 'injured' in query:
            filters['injury_type'] = 'Injured'
        
        return jsonify({'filters': filters})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/data', methods=['GET'])
def get_data():
    """Get sample data for table view"""
    try:
        df = get_dataframe()
        # Return first 100 rows
        sample_data = df.head(100).fillna('N/A').to_dict('records')
        return jsonify({
            'data': sample_data,
            'total': len(df)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Confirm app is ready (for production with gunicorn, this prints when module loads)
print("Flask app initialized and ready to serve requests!")

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')

