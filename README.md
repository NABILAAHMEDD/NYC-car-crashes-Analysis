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

## Setup Instructions

### Prerequisites
- Python 3.9 or higher
- Node.js 14 or higher
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Ensure `crashes_cleaned.csv` is in the backend folder

4. Start the Flask server:
```bash
python app.py
```

The backend will run on `http://localhost:5000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install Node dependencies:
```bash
npm install
```

3. Start the React development server:
```bash
npm start
```

The frontend will open automatically at `http://localhost:3000`

## Deployment Instructions

### Deploying with Vercel

This project uses Vercel for frontend deployment. The backend can be deployed separately on platforms like Heroku, Railway, or Render.

#### Frontend Deployment on Vercel

1. **Prepare for Deployment:**
   ```bash
   cd frontend
   ```

2. **Update API URL for Production:**
   - Edit `frontend/src/App.js`
   - Change the `API_URL` constant to your production backend URL:
   ```javascript
   const API_URL = 'https://your-backend-url.com/api';
   ```

3. **Deploy to Vercel:**
   
   **Option A: Using Vercel CLI (Recommended)**
   ```bash
   # Install Vercel CLI globally
   npm install -g vercel
   
   # Login to Vercel
   vercel login
   
   # Deploy from frontend directory
   cd frontend
   vercel
   
   # For production deployment
   vercel --prod
   ```
   
   **Option B: Using Vercel Dashboard**
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import your GitHub repository
   - Set Root Directory to `frontend`
   - Build Command: `npm run build`
   - Output Directory: `build`
   - Add Environment Variables if needed

4. **Vercel Configuration (vercel.json):**
   Create `frontend/vercel.json`:
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
         "src": "/(.*)",
         "dest": "/index.html"
       }
     ]
   }
   ```

#### Backend Deployment (Separate from Vercel)

Since Vercel is primarily for frontend/static sites, deploy the Flask backend separately:

**Option 1: Railway (Recommended)**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

**Option 2: Render**
- Go to [render.com](https://render.com)
- Create new Web Service
- Connect GitHub repo
- Set Root Directory to `backend`
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn app:app`

**Option 3: Heroku**
```bash
# Install Heroku CLI
heroku create your-app-name

# Add Procfile in backend directory:
# web: gunicorn app:app

# Deploy
git push heroku main
```

**Option 4: PythonAnywhere**
- Upload backend files via web interface
- Configure WSGI file to point to `app.py`
- Ensure `crashes_cleaned.csv` is uploaded

#### Important Configuration Steps

1. **Update CORS in Backend:**
   - Edit `backend/app.py`
   - Update CORS to allow your Vercel domain:
   ```python
   CORS(app, origins=["https://your-vercel-app.vercel.app"])
   ```

2. **Environment Variables:**
   - In Vercel: Add `REACT_APP_API_URL` if using environment variables
   - In Backend: Set `FLASK_ENV=production`

3. **File Upload:**
   - Ensure `crashes_cleaned.csv` is in the backend deployment
   - For platforms like Railway/Render, upload via dashboard or include in repo

##  Project Structure

```
nyc-crash-dashboard/
├── backend/
│   ├── app.py                 # Flask API with endpoints
│   ├── requirements.txt       # Python dependencies
│   ├── crashes_cleaned.csv    # Cleaned and integrated data
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
│   └── .gitignore
│
└── README.md
```

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



