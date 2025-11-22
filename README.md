# NYC Traffic Crash Data Dashboard

An interactive web application for visualizing and analyzing traffic crash data in New York City. This project integrates crash and person data from NYC Data, providing dynamic filtering, search capabilities, and comprehensive visualizations.

** Live Website**: [https://nyc-car-crashes-analysis.vercel.app/](https://nyc-car-crashes-analysis.vercel.app/)

** Repository**: [https://github.com/NABILAAHMEDD/NYC-car-crashes-Analysis](https://github.com/NABILAAHMEDD/NYC-car-crashes-Analysis)

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
  - Density-based clustering with color 
  - Low density areas: Green  and Light Green 
  - Medium density areas: Orange  and Dark Orange 
  - High density areas: Red 
  - Marker size proportional to crash density
  - Color scale legend showing density values
  - Detailed hover tooltips with borough, density level, vehicle type, injury type, and time
  - Auto-zoom to show all crash locations

### 5. Summary Statistics Cards

Four key metrics are displayed at the top of the dashboard to give you a quick overview:

- **Total Crashes**: Shows how many unique crash incidents match your current filters. Each crash is counted once, even if multiple people were involved.

- **Total Persons**: Counts everyone involved in the filtered crashes - drivers, passengers, pedestrians, and cyclists. This number is usually higher than Total Crashes since one accident can involve multiple people.

- **Total Injuries**: The combined count of all injuries across the filtered crashes.

- **Total Deaths**: The combined count of all fatalities in the filtered dataset.

All statistics update automatically when you apply filters and click "Generate Report".

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

Here's how I deployed the backend to Railway:

1. **First, I created a Railway account and project:**
   - Went to [railway.app](https://railway.app)
   - Signed up using my GitHub account
   - Created a new project and connected my GitHub repository

2. **Then I added a MySQL database:**
   - In my Railway project, I clicked "New" → "Database" → "MySQL"
   - Railway automatically created the database and set up the connection details as environment variables

3. **Next, I added the backend service:**
   - Clicked "New" → "GitHub Repo" → Selected my repository
   - Railway detected the backend folder automatically

4. **I configured the backend service:**
   - Went to my backend service → Settings
   - Set the **Root Directory** to `/backend`
   - Railway automatically detected the `backend/Procfile` and used: `gunicorn app:app --bind 0.0.0.0:$PORT --timeout 600 --workers 1 --preload`

5. **Environment variables were set automatically:**
   - Railway automatically set `MYSQL_URL` when I added the MySQL service
   - I didn't need to manually configure anything, but you can set individual variables if needed: `MYSQLHOST`, `MYSQLPORT`, `MYSQLUSER`, `MYSQLPASSWORD`, `MYSQLDATABASE`

6. **I imported the data to Railway MySQL:**
   ```bash
   cd backend
   # Set Railway MySQL connection URL
   $env:MYSQL_URL="mysql://root:YOUR_PASSWORD@YOUR_HOST:YOUR_PORT/railway"
   # Import all data (set SAMPLE_ROWS=0 or remove it for full import)
   $env:SAMPLE_ROWS=0
   python import_csv_to_mysql.py
   ```
   
   I tested with a sample first (100 rows) to make sure everything worked:
   ```bash
   $env:SAMPLE_ROWS=100
   python import_csv_to_mysql.py
   ```

7. **I generated a domain:**
   - Went to my backend service → Settings → Networking
   - Clicked "Generate Domain"
   - Copied the Railway URL (e.g., `https://your-app.railway.app`)

8. **Finally, I verified the deployment:**
   - Checked the logs: Railway Dashboard → My Service → Deployments → View Logs
   - Confirmed I saw: "Flask app initialized with MySQL connection"
   - Tested by visiting `https://your-railway-url.railway.app/api/health`

### Frontend Deployment on Vercel

Here's how I deployed the frontend to Vercel:

1. **First, I created a Vercel account and project:**
   - Went to [vercel.com](https://vercel.com)
   - Signed up using my GitHub account
   - Clicked "New Project" and imported my GitHub repository

2. **I configured the project settings:**
   - Set **Root Directory** to `frontend`
   - Vercel auto-detected React as the framework
   - Build command (`npm run build`) and output directory (`build`) were auto-detected

3. **I set the environment variable:**
   - Went to Project Settings → Environment Variables
   - Added:
     - **Key**: `REACT_APP_API_URL`
     - **Value**: `https://your-railway-backend-url.railway.app/api`
     - Selected all environments: Production, Preview, Development
   - Saved the changes

4. **I deployed:**
   - Clicked "Deploy"
   - Vercel automatically built and deployed the app
   - Waited for the deployment to complete

5. **I verified the deployment:**
   - Visited my Vercel URL
   - Opened the browser console (F12)
   - Confirmed I saw: `API_URL: https://your-railway-backend-url.railway.app/api`
   - Tested by generating a report to verify the backend connection

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

### Local Development
- Set up a local MySQL database
- Configure connection via environment variables (see Local Development Setup above)
- The app automatically detects local vs. production environment
- **Note**: We loaded 300,000 rows from the CSV file as the dataset is too large to load entirely
- **Important**: When filtering the data, some results may show empty graphs and summary cards because only 300,000 rows were loaded (not the full dataset)

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

While working with the dashboard and exploring the data, I noticed some interesting patterns that stood out:

1. **Peak Hours**: I found that most crashes happen during the typical rush hours - between 8-9 AM and 5-6 PM. This makes sense since that's when the most traffic is on the roads.

2. **Borough Distribution**: What really caught my attention was that Brooklyn and Queens consistently had the highest number of crashes compared to the other boroughs. Manhattan, despite being busy, actually had fewer incidents.

3. **Contributing Factors**: When I looked at what causes crashes, driver inattention and distraction kept appearing as the top reason. It's a reminder of how important it is to stay focused while driving.

4. **Seasonal Patterns**: I noticed that crashes tend to peak during the summer and fall months. This could be related to more people being on the road during warmer weather or back-to-school traffic.
