# Document Types Dependency Visualization

This project visualizes the dependency relationships between document types and systems/portals based on data from an Excel file.

## Files

- `resources/portals.xlsx` - Source Excel file with document types and system relationships
- `process_data.py` - Python script to process Excel data and generate JSON
- `data.json` - Generated JSON file with structured data (created by process_data.py)
- `index.html` - Interactive HTML visualization

## Setup

1. **Install Python dependencies** (if not already installed):
   ```bash
   pip install pandas openpyxl
   ```

2. **Process the Excel data and embed it in HTML**:
   ```bash
   python process_data.py
   ```
   This will generate `data.json` with the structured data.
   
   **Note**: The data is embedded directly in `index.html`, so you can open it directly in a browser without needing a web server. If you update the Excel file, run `process_data.py` again and then use the `embed_data.py` script (or manually update the embedded data in the HTML).

3. **Open the visualization**:
   - Simply open `index.html` directly in any web browser (no web server needed!)
   - The data is embedded in the HTML file to avoid CORS issues

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

## Notes

- The visualization uses D3.js (loaded from CDN)
- Red styling matches the diagram aesthetic from the reference image
- Asterisks (*) indicate systems with dependencies

