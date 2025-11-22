from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np
from datetime import datetime
import os
from sqlalchemy import create_engine, text

# Initialize Flask application with CORS enabled for React frontend
app = Flask(__name__)
# Enable CORS for all origins (update this to specific Vercel domain after deployment)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allows all origins for production

# Add request logging middleware for debugging
@app.before_request
def log_request_info():
    print(f'Request: {request.method} {request.path}')

@app.after_request
def after_request(response):
    print(f'Response: {response.status_code} for {request.path}')
    return response

# ============================================================================
# MYSQL CONNECTION CONFIGURATION
# ============================================================================

# Get database connection settings from environment variables
# For Railway: Use MySQL.MYSQL_URL from Railway (automatically set)
MYSQL_URL = os.environ.get('MYSQL_URL') or os.environ.get('MySQL.MYSQL_URL')
MYSQLDATABASE = os.environ.get('MYSQLDATABASE')
MYSQLHOST = os.environ.get('MYSQLHOST')
MYSQLPASSWORD = os.environ.get('MYSQLPASSWORD')
MYSQLPORT = os.environ.get('MYSQLPORT', '3306')
MYSQLUSER = os.environ.get('MYSQLUSER')

# Fallback to individual variables or defaults
if MYSQL_URL:
    # Replace mysql:// with mysql+pymysql:// for SQLAlchemy to use PyMySQL
    if MYSQL_URL.startswith('mysql://'):
        DATABASE_URL = MYSQL_URL.replace('mysql://', 'mysql+pymysql://', 1)
    else:
        DATABASE_URL = MYSQL_URL
else:
    # Build from individual components
    USERNAME = MYSQLUSER or os.environ.get('SQL_USER', 'root')
    PASSWORD = MYSQLPASSWORD or os.environ.get('SQL_PASSWORD', '')
    SERVER = MYSQLHOST or os.environ.get('SQL_SERVER', 'localhost')
    PORT = MYSQLPORT or os.environ.get('SQL_PORT', '3306')
    DATABASE = MYSQLDATABASE or os.environ.get('SQL_DATABASE', 'railway')
    DATABASE_URL = f"mysql+pymysql://{USERNAME}:{PASSWORD}@{SERVER}:{PORT}/{DATABASE}"

# Global connection pool
_db_engine = None

def get_db_connection():
    """Create MySQL connection using SQLAlchemy"""
    global _db_engine
    
    if _db_engine is not None:
        return _db_engine
    
    try:
        print(f"Connecting to MySQL database...")
        _db_engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=3600)
        
        # Test connection
        with _db_engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        
        print("✅ Connected to MySQL successfully!")
        return _db_engine
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        print("\nTroubleshooting:")
        print("1. Check MySQL is running and accessible")
        print("2. Verify connection credentials in environment variables")
        print("3. For Railway: Make sure MYSQL_URL is set (or MySQL.MYSQL_URL)")
        print("4. Check if pymysql is installed: pip install pymysql cryptography")
        raise

def get_dataframe(query=None, params=None):
    """Query MySQL and return pandas DataFrame"""
    engine = get_db_connection()
    
    if query is None:
        # Default query - get all data (be careful with large datasets)
        query = "SELECT * FROM crashes"
    
    try:
        df = pd.read_sql(query, engine, params=params)
        
        # Ensure CRASH_DATE is datetime
        if 'CRASH_DATE' in df.columns:
            df['CRASH_DATE'] = pd.to_datetime(df['CRASH_DATE'], errors='coerce')
        
        # Ensure YEAR column exists
        if 'YEAR' not in df.columns and 'CRASH_DATE' in df.columns:
            df['YEAR'] = df['CRASH_DATE'].dt.year
        
        return df
    except Exception as e:
        print(f"Error executing query: {e}")
        import traceback
        traceback.print_exc()
        raise

print("Flask app initialized with MySQL connection.")

@app.route('/', methods=['GET'])
def root():
    """Root endpoint - provides API information"""
    return jsonify({
        'message': 'NYC Car Crashes API',
        'status': 'running',
        'endpoints': {
            'health': '/api/health',
            'filters': '/api/filters',
            'stats': '/api/stats (POST)',
            'search': '/api/search (POST)',
            'data': '/api/data'
        }
    })

@app.route('/test', methods=['GET'])
def test():
    """Simple test endpoint"""
    return jsonify({'message': 'Test endpoint working!', 'app': 'running'})

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint - tests database connection"""
    try:
        engine = get_db_connection()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) as cnt FROM crashes"))
            count = result.fetchone()[0]
        
        response = {
            'status': 'healthy',
            'database': DATABASE if 'DATABASE' in locals() else 'MySQL',
            'server': SERVER if 'SERVER' in locals() else 'MySQL',
            'total_records': int(count),
            'message': 'Database connected successfully'
        }
        return jsonify(response)
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'message': 'Database connection failed'
        }), 500

@app.route('/api/filters', methods=['GET'])
def get_filter_options():
    """Get all available filter options from MySQL"""
    try:
        engine = get_db_connection()
        
        # Query for filter options using SQL for better performance
        queries = {
            'boroughs': "SELECT DISTINCT BOROUGH FROM crashes WHERE BOROUGH IS NOT NULL ORDER BY BOROUGH",
            'years': "SELECT DISTINCT YEAR FROM crashes WHERE YEAR IS NOT NULL ORDER BY YEAR",
            'vehicle_types': "SELECT `VEHICLE TYPE CODE 1` as vehicle_type FROM crashes WHERE `VEHICLE TYPE CODE 1` IS NOT NULL GROUP BY `VEHICLE TYPE CODE 1` ORDER BY COUNT(*) DESC LIMIT 15",
            'contributing_factors': "SELECT `CONTRIBUTING FACTOR VEHICLE 1` as factor FROM crashes WHERE `CONTRIBUTING FACTOR VEHICLE 1` IS NOT NULL GROUP BY `CONTRIBUTING FACTOR VEHICLE 1` ORDER BY COUNT(*) DESC LIMIT 15",
            'person_types': "SELECT DISTINCT PERSON_TYPE FROM crashes WHERE PERSON_TYPE IS NOT NULL ORDER BY PERSON_TYPE",
            'injury_types': "SELECT DISTINCT PERSON_INJURY FROM crashes WHERE PERSON_INJURY IS NOT NULL ORDER BY PERSON_INJURY"
        }
        
        filters = {}
        with engine.connect() as conn:
            # Boroughs
            result = conn.execute(text(queries['boroughs']))
            filters['boroughs'] = ['All'] + [str(row[0]) for row in result if row[0]]
            
            # Years
            result = conn.execute(text(queries['years']))
            filters['years'] = ['All'] + [str(int(row[0])) for row in result if row[0] is not None]
            
            # Vehicle types
            result = conn.execute(text(queries['vehicle_types']))
            filters['vehicle_types'] = ['All'] + [str(row[0]) for row in result if row[0]]
            
            # Contributing factors
            result = conn.execute(text(queries['contributing_factors']))
            filters['contributing_factors'] = ['All'] + [str(row[0]) for row in result if row[0]]
            
            # Person types
            result = conn.execute(text(queries['person_types']))
            filters['person_types'] = ['All'] + [str(row[0]) for row in result if row[0]]
            
            # Injury types
            result = conn.execute(text(queries['injury_types']))
            filters['injury_types'] = ['All'] + [str(row[0]) for row in result if row[0]]
        
        return jsonify(filters)
    except Exception as e:
        print(f"Error in get_filter_options: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
@app.route('/api/stats', methods=['POST'])
def get_stats():
    """Generate comprehensive statistics based on user-selected filters using MySQL"""
    try:
        filters = request.json or {}
        engine = get_db_connection()
        
        # Build WHERE clause for filters
        where_conditions = []
        params = {}
        
        if filters.get('borough') and filters['borough'] != 'All':
            where_conditions.append("BOROUGH = :borough")
            params['borough'] = filters['borough']
        
        if filters.get('year') and filters['year'] != 'All':
            where_conditions.append("YEAR = :year")
            params['year'] = int(filters['year'])
        
        if filters.get('vehicle_type') and filters['vehicle_type'] != 'All':
            where_conditions.append("`VEHICLE TYPE CODE 1` = :vehicle_type")
            params['vehicle_type'] = filters['vehicle_type']
        
        if filters.get('contributing_factor') and filters['contributing_factor'] != 'All':
            where_conditions.append("`CONTRIBUTING FACTOR VEHICLE 1` = :contributing_factor")
            params['contributing_factor'] = filters['contributing_factor']
        
        if filters.get('person_type') and filters['person_type'] != 'All':
            where_conditions.append("PERSON_TYPE = :person_type")
            params['person_type'] = filters['person_type']
        
        if filters.get('injury_type') and filters['injury_type'] != 'All':
            where_conditions.append("PERSON_INJURY = :injury_type")
            params['injury_type'] = filters['injury_type']
        
        where_clause = " WHERE " + " AND ".join(where_conditions) if where_conditions else ""
        
        # Execute queries using SQLAlchemy
        with engine.connect() as conn:
            # Total unique crashes
            result = conn.execute(text(f"SELECT COUNT(DISTINCT COLLISION_ID) as cnt FROM crashes{where_clause}"), params)
            total_crashes = result.fetchone()[0] or 0
            
            # Total persons
            result = conn.execute(text(f"SELECT COUNT(*) as cnt FROM crashes{where_clause}"), params)
            total_persons = result.fetchone()[0] or 0
            
            # Total injuries and deaths
            result = conn.execute(text(f"SELECT SUM(`NUMBER OF PERSONS INJURED`) as injuries, SUM(`NUMBER OF PERSONS KILLED`) as deaths FROM crashes{where_clause}"), params)
            row = result.fetchone()
            total_injuries = int(row[0] or 0)
            total_deaths = int(row[1] or 0)
            
            # By borough
            result = conn.execute(text(f"SELECT BOROUGH, COUNT(DISTINCT COLLISION_ID) as cnt FROM crashes{where_clause} GROUP BY BOROUGH"), params)
            by_borough = {row[0]: int(row[1]) for row in result if row[0]}
            
            # Top 10 vehicle types
            vehicle_where = where_clause + (" AND" if where_clause else " WHERE") + " `VEHICLE TYPE CODE 1` IS NOT NULL"
            result = conn.execute(text(f"SELECT `VEHICLE TYPE CODE 1`, COUNT(*) as cnt FROM crashes{vehicle_where} GROUP BY `VEHICLE TYPE CODE 1` ORDER BY cnt DESC LIMIT 10"), params)
            by_vehicle = {row[0]: int(row[1]) for row in result if row[0]}
            
            # Top 10 contributing factors
            factor_where = where_clause + (" AND" if where_clause else " WHERE") + " `CONTRIBUTING FACTOR VEHICLE 1` IS NOT NULL"
            result = conn.execute(text(f"SELECT `CONTRIBUTING FACTOR VEHICLE 1`, COUNT(*) as cnt FROM crashes{factor_where} GROUP BY `CONTRIBUTING FACTOR VEHICLE 1` ORDER BY cnt DESC LIMIT 10"), params)
            by_factor = {row[0]: int(row[1]) for row in result if row[0]}
            
            # By person type
            person_where = where_clause + (" AND" if where_clause else " WHERE") + " PERSON_TYPE IS NOT NULL"
            result = conn.execute(text(f"SELECT PERSON_TYPE, COUNT(*) as cnt FROM crashes{person_where} GROUP BY PERSON_TYPE"), params)
            by_person_type = {row[0]: int(row[1]) for row in result if row[0]}
            
            # By injury type
            injury_where = where_clause + (" AND" if where_clause else " WHERE") + " PERSON_INJURY IS NOT NULL"
            result = conn.execute(text(f"SELECT PERSON_INJURY, COUNT(*) as cnt FROM crashes{injury_where} GROUP BY PERSON_INJURY"), params)
            by_injury = {row[0]: int(row[1]) for row in result if row[0]}
            
            # By month
            month_where = where_clause + (" AND" if where_clause else " WHERE") + " CRASH_DATE IS NOT NULL"
            result = conn.execute(text(f"SELECT DATE_FORMAT(CRASH_DATE, '%Y-%m') as month, COUNT(DISTINCT COLLISION_ID) as cnt FROM crashes{month_where} GROUP BY DATE_FORMAT(CRASH_DATE, '%Y-%m') ORDER BY month"), params)
            by_month = {row[0]: int(row[1]) for row in result if row[0]}
            
            # By hour
            hour_where = where_clause + (" AND" if where_clause else " WHERE") + " HOUR IS NOT NULL"
            result = conn.execute(text(f"SELECT HOUR, COUNT(DISTINCT COLLISION_ID) as cnt FROM crashes{hour_where} GROUP BY HOUR ORDER BY HOUR"), params)
            by_hour = {int(row[0]): int(row[1]) for row in result if row[0] is not None}
            
            # Heatmap by day and hour
            day_names = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 
                         4: 'Friday', 5: 'Saturday', 6: 'Sunday'}
            day_hour_where = where_clause + (" AND" if where_clause else " WHERE") + " DAY IS NOT NULL AND HOUR IS NOT NULL"
            result = conn.execute(text(f"SELECT DAY, HOUR, COUNT(DISTINCT COLLISION_ID) as cnt FROM crashes{day_hour_where} GROUP BY DAY, HOUR"), params)
            heatmap_data = {}
            for row in result:
                day, hour, count = row
                if day is not None and hour is not None:
                    day_name = day_names.get(day, f'Day_{day}')
                    if day_name not in heatmap_data:
                        heatmap_data[day_name] = {}
                    heatmap_data[day_name][int(hour)] = int(count)
        
            # By season
            season_where = where_clause + (" AND" if where_clause else " WHERE") + " season IS NOT NULL"
            result = conn.execute(text(f"SELECT season, COUNT(*) as cnt FROM crashes{season_where} GROUP BY season"), params)
            by_season = {row[0]: int(row[1]) for row in result if row[0]}
            
            # Safety stats
            safety_where = where_clause + (" AND" if where_clause else " WHERE") + " SAFETY_USED IS NOT NULL"
            result = conn.execute(text(f"SELECT SAFETY_USED, COUNT(DISTINCT PERSON_ID) as cnt FROM crashes{safety_where} GROUP BY SAFETY_USED"), params)
            safety_stats = {'used': 0, 'not_used': 0}
            for row in result:
                if row[0] == 1:
                    safety_stats['used'] = int(row[1])
                elif row[0] == 0:
                    safety_stats['not_used'] = int(row[1])
            
            # Geo data (limit 500)
            geo_where = where_clause + (" AND" if where_clause else " WHERE") + " LATITUDE IS NOT NULL AND LONGITUDE IS NOT NULL AND LATITUDE BETWEEN 40.4 AND 40.9 AND LONGITUDE BETWEEN -74.5 AND -73.5"
            geo_query = f"SELECT LATITUDE, LONGITUDE, BOROUGH, `VEHICLE TYPE CODE 1`, PERSON_INJURY, HOUR, CRASH_DATE FROM crashes{geo_where} LIMIT 500"
            # Use SQLAlchemy text() with params, then convert to DataFrame
            with engine.connect() as geo_conn:
                result = geo_conn.execute(text(geo_query), params)
                rows = result.fetchall()
                columns = result.keys()
                geo_df = pd.DataFrame(rows, columns=columns)
            
            geo_data = []
            for _, row in geo_df.iterrows():
                try:
                    geo_record = {
                        'LATITUDE': float(row['LATITUDE']),
                        'LONGITUDE': float(row['LONGITUDE']),
                        'BOROUGH': str(row['BOROUGH']) if pd.notna(row['BOROUGH']) else 'Unknown'
                    }
                    vehicle_col = 'VEHICLE TYPE CODE 1'
                    if pd.notna(row.get(vehicle_col)):
                        geo_record['VEHICLE_TYPE'] = str(row[vehicle_col])
                    if pd.notna(row.get('PERSON_INJURY')):
                        geo_record['INJURY_TYPE'] = str(row['PERSON_INJURY'])
                    if pd.notna(row.get('HOUR')):
                        geo_record['HOUR'] = int(row['HOUR'])
                    if pd.notna(row.get('CRASH_DATE')):
                        geo_record['CRASH_DATE'] = str(row['CRASH_DATE'])
                    geo_data.append(geo_record)
                except:
                    continue
        
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
            'by_day_hour': heatmap_data,
            'by_season': by_season,
            'safety_stats': safety_stats,
            'geo_data': geo_data
        })
    except Exception as e:
        print(f"Error in get_stats: {str(e)}")
        import traceback
        traceback.print_exc()
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
        engine = get_db_connection()
        query = "SELECT * FROM crashes LIMIT 100"
        df = pd.read_sql(query, engine)
        sample_data = df.fillna('N/A').to_dict('records')
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

