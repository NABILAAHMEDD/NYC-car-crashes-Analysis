import pandas as pd
import os
from datetime import datetime
import sys
from sqlalchemy import create_engine, text

# Database connection settings
# For Railway: Use MySQL.MYSQL_URL from Railway (automatically set)
MYSQL_URL = os.environ.get('MYSQL_URL') or os.environ.get('MySQL.MYSQL_URL')
MYSQLDATABASE = os.environ.get('MYSQLDATABASE')
MYSQLHOST = os.environ.get('MYSQLHOST')
MYSQLPASSWORD = os.environ.get('MYSQLPASSWORD')
MYSQLPORT = os.environ.get('MYSQLPORT', '3306')
MYSQLUSER = os.environ.get('MYSQLUSER')

# Sample import size (set to None or 0 to import all data)
# Set SAMPLE_ROWS environment variable to limit import (e.g., 50000 for testing)
SAMPLE_ROWS = os.environ.get('SAMPLE_ROWS')
if SAMPLE_ROWS:
    try:
        SAMPLE_ROWS = int(SAMPLE_ROWS)
    except:
        SAMPLE_ROWS = None
else:
    SAMPLE_ROWS = None

# CSV file path
CSV_FILE = 'crashes_cleaned.csv'
if not os.path.exists(CSV_FILE):
    CSV_FILE = os.path.join('backend', 'crashes_cleaned.csv')

def get_connection():
    """Create MySQL connection"""
    # Build connection URL
    if MYSQL_URL:
        # Replace mysql:// with mysql+pymysql:// for SQLAlchemy to use PyMySQL
        if MYSQL_URL.startswith('mysql://'):
            DATABASE_URL = MYSQL_URL.replace('mysql://', 'mysql+pymysql://', 1)
        else:
            DATABASE_URL = MYSQL_URL
    else:
        USERNAME = MYSQLUSER or os.environ.get('SQL_USER', 'root')
        PASSWORD = MYSQLPASSWORD or os.environ.get('SQL_PASSWORD', '')
        SERVER = MYSQLHOST or os.environ.get('SQL_SERVER', 'localhost')
        PORT = MYSQLPORT or os.environ.get('SQL_PORT', '3306')
        DATABASE = MYSQLDATABASE or os.environ.get('SQL_DATABASE', 'railway')
        DATABASE_URL = f"mysql+pymysql://{USERNAME}:{PASSWORD}@{SERVER}:{PORT}/{DATABASE}"
    
    try:
        engine = create_engine(DATABASE_URL, pool_pre_ping=True)
        print(f"✅ Connected to MySQL database")
        return engine
    except Exception as e:
        print(f"❌ Connection error: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure MySQL is running")
        print("2. Check connection credentials")
        print("3. Install required packages: pip install pymysql sqlalchemy cryptography")
        sys.exit(1)

def import_data():
    """Import CSV data into MySQL"""
    # Check if CSV file exists
    if not os.path.exists(CSV_FILE):
        print(f"❌ CSV file not found: {CSV_FILE}")
        sys.exit(1)
    
    print(f"📄 Reading CSV file: {CSV_FILE}")
    start_time = datetime.now()
    
    engine = get_connection()
    
    # Create table if it doesn't exist
    print("📋 Checking if table exists...")
    with engine.connect() as conn:
        # Check if table exists
        result = conn.execute(text("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = DATABASE() 
            AND table_name = 'crashes'
        """))
        table_exists = result.fetchone()[0] > 0
        
        if not table_exists:
            print(" Table doesn't exist. Creating optimized table (only used columns)...")
        else:
            print("⚠️  Table exists but may have wrong schema. Dropping and recreating...")
            conn.execute(text("DROP TABLE IF EXISTS crashes"))
            conn.commit()
            print("✅ Old table dropped")
        
        # Create the table with only columns actually used by the application
        conn.execute(text("""
            CREATE TABLE crashes (
                COLLISION_ID BIGINT,
                CRASH_DATE DATETIME,
                PERSON_ID VARCHAR(50),
                PERSON_TYPE VARCHAR(50),
                PERSON_INJURY VARCHAR(50),
                BOROUGH VARCHAR(50),
                LATITUDE FLOAT,
                LONGITUDE FLOAT,
                `NUMBER OF PERSONS INJURED` INT,
                `NUMBER OF PERSONS KILLED` INT,
                `CONTRIBUTING FACTOR VEHICLE 1` VARCHAR(200),
                `VEHICLE TYPE CODE 1` VARCHAR(100),
                HOUR INT,
                DAY INT,
                season VARCHAR(20),
                SAFETY_USED INT,
                YEAR INT GENERATED ALWAYS AS (YEAR(CRASH_DATE)) STORED
            )
        """))
        
        # Create indexes
        print("📊 Creating indexes...")
        conn.execute(text("CREATE INDEX IX_COLLISION_ID ON crashes(COLLISION_ID)"))
        conn.execute(text("CREATE INDEX IX_CRASH_DATE ON crashes(CRASH_DATE)"))
        conn.execute(text("CREATE INDEX IX_YEAR ON crashes(YEAR)"))
        conn.execute(text("CREATE INDEX IX_BOROUGH ON crashes(BOROUGH)"))
        conn.execute(text("CREATE INDEX IX_PERSON_TYPE ON crashes(PERSON_TYPE)"))
        conn.execute(text("CREATE INDEX IX_LAT_LON ON crashes(LATITUDE, LONGITUDE)"))
        conn.commit()
        print("✅ Table created successfully!")
    
    # Only import columns actually used by the application (optimized)
    # This list tells pandas to ONLY read these columns from CSV (much faster!)
    columns = [
        'COLLISION_ID', 
        'CRASH_DATE', 
        'PERSON_ID',
        'PERSON_TYPE', 
        'PERSON_INJURY', 
        'BOROUGH', 
        'LATITUDE',
        'LONGITUDE', 
        'NUMBER OF PERSONS INJURED',
        'NUMBER OF PERSONS KILLED', 
        'CONTRIBUTING FACTOR VEHICLE 1',
        'VEHICLE TYPE CODE 1', 
        'HOUR', 
        'DAY', 
        'season', 
        'SAFETY_USED'
    ]
    
    # Read and insert data in chunks
    # Using usecols to ONLY read the columns we need from CSV (much faster!)
    if SAMPLE_ROWS:
        print(f"\n📊 IMPORTING SAMPLE: {SAMPLE_ROWS:,} rows (for testing)")
        print(f"   Set SAMPLE_ROWS=0 to import full dataset")
        # For small samples, read all at once, then chunk for insert
        print(f"   Only reading {len(columns)} columns from CSV (optimized for speed)")
        
        # Read sample directly (no chunking for reading)
        df = pd.read_csv(
            CSV_FILE,
            nrows=SAMPLE_ROWS,
            usecols=columns,
            engine='python',
            on_bad_lines='skip',
            encoding='utf-8',
            encoding_errors='ignore'
        )
        
        # Convert CRASH_DATE to datetime
        if 'CRASH_DATE' in df.columns:
            df['CRASH_DATE'] = pd.to_datetime(df['CRASH_DATE'], errors='coerce')
        
        # Replace NaN with None for MySQL
        df = df.where(pd.notnull(df), None)
        
        # Insert all at once (small sample)
        print(f"   Inserting {len(df):,} rows...")
        df.to_sql('crashes', engine, if_exists='append', index=False, method='multi')
        total_rows = len(df)
        print(f"  ✓ Imported {total_rows:,} rows")
        
    else:
        # Full dataset - use chunking
        chunk_size = 50000
        print(f"\n📊 IMPORTING FULL DATASET in chunks of {chunk_size} rows...")
        print(f"   Only reading {len(columns)} columns from CSV (optimized for speed)")
        
        reader = pd.read_csv(
            CSV_FILE,
            chunksize=chunk_size,
            usecols=columns,
            engine='python',
            on_bad_lines='skip',
            encoding='utf-8',
            encoding_errors='ignore'
        )
        
        chunk_count = 0
        total_rows = 0
        
        for chunk in reader:
            # Convert CRASH_DATE to datetime
            if 'CRASH_DATE' in chunk.columns:
                chunk['CRASH_DATE'] = pd.to_datetime(chunk['CRASH_DATE'], errors='coerce')
            
            # Replace NaN with None for MySQL
            chunk = chunk.where(pd.notnull(chunk), None)
            
            # Insert data using pandas to_sql
            chunk.to_sql('crashes', engine, if_exists='append', index=False, method='multi')
            
            chunk_count += 1
            total_rows += len(chunk)
            
            elapsed = (datetime.now() - start_time).total_seconds()
            print(f"  ✓ Imported chunk {chunk_count}: {len(chunk):,} rows (Total: {total_rows:,} rows in {elapsed:.1f}s)")
    
    # Verify import
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM crashes"))
        count = result.fetchone()[0]
        
        result = conn.execute(text("SELECT COUNT(DISTINCT COLLISION_ID) FROM crashes"))
        unique_crashes = result.fetchone()[0]
    
    elapsed_total = (datetime.now() - start_time).total_seconds()
    print(f"\n✅ Import complete!")
    print(f"   Total rows imported: {count:,}")
    print(f"   Time taken: {elapsed_total:.1f} seconds")
    print(f"   Rate: {count/elapsed_total:.0f} rows/second")
    print(f"\n📈 Statistics:")
    print(f"   Unique crashes: {unique_crashes:,}")
    print(f"   Total records: {count:,}")

if __name__ == '__main__':
    print("=" * 60)
    print("NYC Car Crashes - CSV to MySQL Import")
    print("=" * 60)
    print(f"CSV File: {CSV_FILE}")
    if SAMPLE_ROWS:
        print(f"⚠️  SAMPLE MODE: Importing only {SAMPLE_ROWS:,} rows")
        print(f"   To import full dataset: Remove SAMPLE_ROWS or set SAMPLE_ROWS=0")
    else:
        print(f"Full dataset import")
    print("=" * 60)
    print()
    
    import_data()

