# NYC Traffic Crash Data Dashboard

An interactive web application for visualizing and analyzing traffic crash data in New York City. This project integrates crash and person data from NYC Data, providing dynamic filtering, search capabilities, and comprehensive visualizations.

**Repository**: [https://github.com/NABILAAHMEDD/NYC-car-crashes-Analysis](https://github.com/NABILAAHMEDD/NYC-car-crashes-Analysis)

## Project Overview

This project fulfills the requirements for **Milestone 1: Cleaning, Integration, and Visualization** of the Data Engineering course. It demonstrates:

- **Data Cleaning**: Pre and post-integration cleaning of NYC crash data
- **Data Integration**: Joining crash data with person data via COLLISION_ID
- **Interactive Visualization**: React-based dashboard with multiple chart types
- **Dynamic Filtering**: Multiple dropdown filters and natural language search
- **Real-time Updates**: Generate Report button that updates all visualizations

**Colab Notebook**: [https://colab.research.google.com/drive/1Al1659ZqNsxALQQEkykkSo5-7cCleDzU#scrollTo=fQApycfd5gER]

## Technology Stack

### Backend
- **Flask** (Python 3.9+) - REST API
- **Pandas** - Data processing and analysis
- **Flask-CORS** - Cross-origin resource sharing

### Frontend
- **React** (18.2.0) - UI framework
- **Plotly.js** - Interactive visualizations
- **Axios** - HTTP client for API calls

##  Features

### 1. Multiple Dropdown Filters
- Borough (Bronx, Brooklyn, Manhattan, Queens, Staten Island)
- Year (2012-2025)
- Vehicle Type
- Contributing Factor
- Person Type (Pedestrian, Cyclist, Occupant)
- Injury Type (Killed, Injured, Unspecified)

### 2. Natural Language Search
Type queries like:
- "Brooklyn 2022 pedestrian crashes"
- "Manhattan cyclist killed"
- "Queens 2021 injured"

The system automatically parses and applies appropriate filters.

### 3. Generate Report Button
Click to dynamically update all visualizations based on selected filters.

### 4. Comprehensive Visualizations
- **Bar Charts**: Crashes by Borough, Injury Types
- **Horizontal Bar Chart**: Top Contributing Factors
- **Pie Charts**: Vehicle Types, Person Types, Seasonal Distribution
- **Line Charts**: Time Series (Monthly), Crashes by Hour
- **Heatmap**: Hour vs Day of Week patterns
- **Geographic Map**: 
  - Interactive crash location map using Plotly's free scattergeo (no tokens required)
  - Density-based clustering with color-coded markers (green = low, orange = medium, red = high)
  - Marker size proportional to crash density
  - Color scale legend showing density values
  - Detailed hover tooltips with borough, density level, vehicle type, injury type, and time
  - Auto-zoom to show all crash locations

### 5. Summary Statistics Cards

The dashboard displays four key summary statistics at the top:

- **Total Crashes**: The number of unique crash events (distinct COLLISION_IDs) that match the selected filters. This counts crash incidents, not individual people, since one crash can involve multiple people.

- **Total Persons**: The total number of people involved in crashes that match the selected filters. This counts all person records in the filtered dataset. Since the data integrates crash and person information, one crash can have multiple person records (e.g., driver, passenger, pedestrian), so this number is typically higher than Total Crashes.

- **Total Injuries**: The sum of all injuries across all crashes in the filtered dataset. This is calculated by summing the "NUMBER OF PERSONS INJURED" field from all person records.

- **Total Deaths**: The sum of all fatalities across all crashes in the filtered dataset. This is calculated by summing the "NUMBER OF PERSONS KILLED" field from all person records.

**Note**: These statistics update dynamically based on the selected filters and are recalculated each time you click "Generate Report".

##  Live Deployment

- **Frontend (Vercel)**: [https://nyc-car-crashes-analysis-ggaivve4n-nabilaahmedds-projects.vercel.app/](https://nyc-car-crashes-analysis-ggaivve4n-nabilaahmedds-projects.vercel.app/)
- **Backend API (Railway)**: [https://nyc-car-crashes-analysis-production-f7fd.up.railway.app](https://nyc-car-crashes-analysis-production-f7fd.up.railway.app)
- **API Health Check**: [https://nyc-car-crashes-analysis-production-f7fd.up.railway.app/api/health](https://nyc-car-crashes-analysis-production-f7fd.up.railway.app/api/health)

## Setup Instructions

### Prerequisites
- Python 3.11 or higher
- Node.js 14 or higher
- npm or yarn
- MySQL database (for production) or local MySQL (for local development)

### Local Development Setup

#### Backend Setup (Local)

1. **Navigate to the backend directory:**
```bash
cd backend
```

2. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up local MySQL database:**
   - Install MySQL locally or use a cloud MySQL instance
   - Create a database (e.g., `nyc_crashes`)
   - Note your MySQL connection details

4. **Configure environment variables for local development:**
   
   Create a `.env` file in the `backend` folder (or set environment variables):
   ```bash
   # For Windows PowerShell:
   $env:MYSQLHOST="localhost"
   $env:MYSQLPORT="3306"
   $env:MYSQLUSER="root"
   $env:MYSQLPASSWORD="your_password"
   $env:MYSQLDATABASE="nyc_crashes"
   
   # For Linux/Mac:
   export MYSQLHOST="localhost"
   export MYSQLPORT="3306"
   export MYSQLUSER="root"
   export MYSQLPASSWORD="your_password"
   export MYSQLDATABASE="nyc_crashes"
   ```
   
   **OR** use a MySQL connection URL:
   ```bash
   # Windows PowerShell:
   $env:MYSQL_URL="mysql://root:your_password@localhost:3306/nyc_crashes"
   
   # Linux/Mac:
   export MYSQL_URL="mysql://root:your_password@localhost:3306/nyc_crashes"
   ```

5. **Import data to local MySQL:**
```bash
# Make sure crashes_cleaned.csv is in the backend folder
python import_csv_to_mysql.py
```

6. **Start the Flask server:**
```bash
python app.py
```

The backend will run on `http://localhost:5000`

**Note for Local Development:** The app automatically detects if you're running locally (no Railway MYSQL_URL) and will use your local MySQL connection. No code changes needed!

#### Frontend Setup (Local)

1. **Navigate to the frontend directory:**
```bash
cd frontend
```

2. **Install Node dependencies:**
```bash
npm install
```

3. **Start the React development server:**
```bash
npm start
```

The frontend will open automatically at `http://localhost:3000`

**Note:** The frontend automatically uses `http://localhost:5000/api` when running locally (no environment variable needed).

## Deployment Instructions

### Backend Deployment on Railway

1. **Create Railway Account and Project:**
   - Go to [railway.app](https://railway.app)
   - Sign up/login with GitHub
   - Create a new project
   - Connect your GitHub repository

2. **Add MySQL Database Service:**
   - In your Railway project, click "New" → "Database" → "MySQL"
   - Railway will automatically create a MySQL database
   - Note the connection details (automatically set as environment variables)

3. **Add Backend Service:**
   - Click "New" → "GitHub Repo" → Select your repository
   - Railway will detect the backend folder

4. **Configure Backend Service:**
   - Go to your backend service → Settings
   - Set **Root Directory** to: `/backend`
   - The `backend/Procfile` will be automatically detected
   - Railway will use: `gunicorn app:app --bind 0.0.0.0:$PORT --timeout 600 --workers 1 --preload`

5. **Set Environment Variables:**
   - Railway automatically sets `MYSQL_URL` when you add a MySQL service
   - If needed, you can manually set:
     - `MYSQL_URL` (automatically set by Railway)
     - Or individual variables: `MYSQLHOST`, `MYSQLPORT`, `MYSQLUSER`, `MYSQLPASSWORD`, `MYSQLDATABASE`

6. **Import Data to Railway MySQL:**
   ```bash
   cd backend
   # Set Railway MySQL connection URL
   $env:MYSQL_URL="mysql://root:YOUR_PASSWORD@YOUR_HOST:YOUR_PORT/railway"
   # Import all data (set SAMPLE_ROWS=0 or remove it for full import)
   $env:SAMPLE_ROWS=0
   python import_csv_to_mysql.py
   ```
   
   Or import a sample first (100 rows):
   ```bash
   $env:SAMPLE_ROWS=100
   python import_csv_to_mysql.py
   ```

7. **Generate Domain:**
   - Go to your backend service → Settings → Networking
   - Click "Generate Domain" or use a custom domain
   - Copy the Railway URL (e.g., `https://your-app.railway.app`)

8. **Verify Deployment:**
   - Check logs: Railway Dashboard → Your Service → Deployments → View Logs
   - Should see: "Flask app initialized with MySQL connection"
   - Test: Visit `https://your-railway-url.railway.app/api/health`

### Frontend Deployment on Vercel

1. **Create Vercel Account and Project:**
   - Go to [vercel.com](https://vercel.com)
   - Sign up/login with GitHub
   - Click "New Project"
   - Import your GitHub repository

2. **Configure Project Settings:**
   - **Root Directory**: Set to `frontend`
   - **Framework Preset**: React (auto-detected)
   - **Build Command**: `npm run build` (auto-detected)
   - **Output Directory**: `build` (auto-detected)

3. **Set Environment Variables:**
   - Go to Project Settings → Environment Variables
   - Add:
     - **Key**: `REACT_APP_API_URL`
     - **Value**: `https://your-railway-backend-url.railway.app/api`
     - **Environments**: Production, Preview, Development
   - Save

4. **Deploy:**
   - Click "Deploy"
   - Vercel will automatically build and deploy
   - Wait for deployment to complete

5. **Verify Deployment:**
   - Visit your Vercel URL
   - Open browser console (F12)
   - Should see: `API_URL: https://your-railway-backend-url.railway.app/api`
   - Test: Generate a report to verify backend connection

### Vercel Configuration

The `frontend/vercel.json` file is already configured:
```json
{
  "version": 2,
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "build"
      }
    }
  ],
  "routes": [
    {
      "src": "/static/(.*)",
      "dest": "/static/$1"
    },
    {
      "src": "/(.*\\.(js|css|ico|png|jpg|svg|woff|woff2|ttf|eot))",
      "dest": "/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ]
}
```

This ensures static files are served correctly and React Router works properly.

##  Project Structure

```
nyc-crash-dashboard/
├── backend/
│   ├── app.py                 # Flask API with endpoints
│   ├── requirements.txt       # Python dependencies
│   ├── Procfile               # Railway deployment configuration
│   ├── runtime.txt            # Python version specification
│   ├── crashes_cleaned.csv    # Cleaned and integrated data (CSV)
│   ├── import_csv_to_mysql.py # Script to import CSV to MySQL
│   ├── create_table_mysql.sql # MySQL table creation script
│   └── .gitignore
│
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── components/
│   │   │   ├── Charts.js      # All visualizations (maps, charts, graphs)
│   │   │   ├── Charts.css     # Chart styling
│   │   │   ├── Filters.js     # Dropdown filters component
│   │   │   ├── Filters.css    # Filter styling
│   │   │   ├── FilterSearch.js # Combined filters and search component
│   │   │   ├── FilterSearch.css # FilterSearch styling
│   │   │   ├── SearchBar.js   # Search functionality
│   │   │   ├── SearchBar.css  # SearchBar styling
│   │   │   ├── StatsCards.js  # Summary statistics cards
│   │   │   └── StatsCards.css # StatsCards styling
│   │   ├── App.js             # Main application component
│   │   ├── App.css            # Main app styling
│   │   ├── index.js           # React entry point
│   │   ├── index.css          # Global styles
│   │   └── theme.css          # Design system theme variables
│   ├── package.json
│   ├── vercel.json            # Vercel deployment configuration
│   └── .gitignore
│
└── README.md
```

## Database Configuration

### Production (Railway MySQL)
- The app automatically uses Railway's MySQL database
- Connection is configured via Railway's `MYSQL_URL` environment variable
- No code changes needed for Railway deployment

### Local Development
- Set up a local MySQL database
- Configure connection via environment variables (see Local Development Setup above)
- The app automatically detects local vs. production environment

##  API Endpoints

### GET `/api/health`
Health check endpoint
- Returns: Server status and data info

### GET `/api/filters`
Get all available filter options
- Returns: Lists of boroughs, years, vehicle types, etc.

### POST `/api/stats`
Generate statistics based on filters
- Body: Filter object
- Returns: Comprehensive statistics and chart data

### POST `/api/search`
Parse natural language search query
- Body: `{ "query": "search string" }`
- Returns: Extracted filters

### GET `/api/data`
Get sample data for table view
- Returns: First 100 rows of data


##  Data Sources

- **NYC Motor Vehicle Collisions - Crashes**: [NYC Open Data](https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Crashes/h9gi-nx95)
- **NYC Motor Vehicle Collisions - Person**: [NYC Open Data](https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Person/f55k-p6yu)

##  Team Contributions

<!-- Add team member contributions here -->

### [Aliaa]

-Data cleaning and preparation before integration

-Data cleaning and preparation after integration

### [Rawan]

-Data visualization

-Analyzing the data to extract insights

### [Nabila]

-Creating an interactive dashboard with dynamic and suitable graphs and KPIs

-Deploying the website

##  Key Insights

The dashboard reveals several important patterns:

1. **Peak Hours**: Most crashes occur during rush hours (8-9 AM, 5-6 PM)
2. **Borough Distribution**: Brooklyn and Queens have the highest crash counts
3. **Contributing Factors**: Driver inattention/distraction is the leading cause
4. **Seasonal Patterns**: Crashes peak during summer and fall months
5. **Safety Equipment**: Analysis shows correlation between safety equipment use and injury severity



