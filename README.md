# Document Types Dependency Visualization

This project visualizes the dependency relationships between document types and systems/portals based on data from an Excel file.

## Project Structure

```
/
├── backend/
│   ├── app.py                # Flask server
│   ├── process_data.py       # Excel processing logic
│   └── users.json            # User credentials
├── frontend/
│   ├── index.html            # Visualization UI
│   └── resources/
│       └── portals.xlsx      # Excel files
├── requirements.txt          # Python dependencies
├── data.json                 # Generated data
└── render.yaml              # Deployment config
```

## Setup

### Quick Start (Recommended)

**Windows:**
```bash
start.bat
```

**Linux/Mac:**
```bash
chmod +x start.sh
./start.sh
```

The startup script will:
- Create a virtual environment (if it doesn't exist)
- Install all dependencies
- Start the Flask server (default port: 8080, may use different port on Windows)

### Manual Setup

1. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Flask application**:
   ```bash
   cd backend
   python app.py
   ```
   The server will start and display its URL in the terminal (e.g., `http://127.0.0.1:8080`)
   
   **Note**: On Windows, if port 8080 is busy, Flask will automatically select an available port.

4. **Access the visualization**:
   - Check the terminal output for the server URL
   - Open your browser and navigate to that URL
   - The data is embedded in the HTML file

## Features

### Excel Upload with Authentication

1. **Login**: Click the floating button (🔒) in the bottom-right corner
2. **Authenticate**: Log in with your credentials
   - Default user: `luis.gonzalez@tecnovait.com`
   - Default password: `luis.gonzalez`
3. **Upload**: Select and upload a new Excel file (.xlsx or .xls)
4. **Auto-Process**: The system will automatically:
   - Process the Excel file
   - Generate new JSON data
   - Embed data in the HTML
   - Refresh the visualization
5. **Update for All**: All users will see the updated data after page refresh

### Managing Users

To add more users, edit `backend/users.json`:
```json
{
  "users": [
    {
      "email": "user@example.com",
      "password": "password123"
    }
  ]
}
```

## Features

- **Document Types Panel (Left)**: Shows all document types from the Excel file
- **Systems Panel (Right)**: Shows platforms/systems with their dependency relationships
- **Interactive Features**:
  - Hover over document types to see which systems use them
  - Hover over systems to see document types and dependencies
  - Click on document types or systems to highlight their relationships
  - Red arrows show dependency flows between systems

## Data Structure

The visualization shows:
- **Document Types** → **Platforms**: Which platforms use each document type
- **Platform Dependencies**: Which system should have uploaded documents to each platform (e.g., "Web Liquidacion" depends on "Denuncio")

## Deployment to Render.com

### Automatic Deployment

1. **Push your code to GitHub/GitLab**

2. **Create a new Web Service on Render**:
   - Go to [render.com](https://render.com) and sign in
   - Click **"New +"** → **"Web Service"**
   - Connect your repository

3. **Render will auto-detect** the `render.yaml` file and configure:
   - **Environment**: Python 3.11
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `cd backend && gunicorn -w 4 -b 0.0.0.0:$PORT app:app`

4. **Set Environment Variables** (optional but recommended):
   - `SECRET_KEY`: A secure random string for session management

5. **Deploy**: Click "Create Web Service" and wait for deployment

### Manual Configuration (if render.yaml is not detected)

| Setting | Value |
|---------|-------|
| **Environment** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `cd backend && gunicorn -w 4 -b 0.0.0.0:$PORT app:app` |
| **Health Check Path** | `/` |

### Post-Deployment

- Your app will be available at `https://your-app-name.onrender.com`
- Login with your credentials to upload Excel files
- Data persists in the deployed files

## Notes

- The visualization uses D3.js (loaded from CDN)
- Red styling matches the diagram aesthetic from the reference image
- Asterisks (*) indicate systems with dependencies

