"""
Process Excel file to extract document type and system dependency relationships.
Generates JSON data for the visualization.
"""

import pandas as pd
import json
from collections import defaultdict

def normalize_platform_name(name):
    """
    Normalize platform names to handle variations.
    Returns a canonical name and a mapping of variations.
    """
    name = str(name).strip()
    if not name or name == 'nan':
        return None
    
    # Normalize common variations
    name_lower = name.lower()
    
    # Handle Denuncio/Denuncios
    if 'denuncio' in name_lower:
        return 'Denuncios'
    
    # Handle Web Liquidacion variations
    if 'web liquidacion' in name_lower or 'web liquidaci' in name_lower:
        return 'Web Liquidacion'
    
    # Handle DJS variations
    if 'djs' in name_lower or 'declaracion jurada simple' in name_lower:
        return 'DJS(Declaracion Jurada Simple)'
    
    # Return original if no normalization needed
    return name

def process_excel_data(excel_path='resources/portals.xlsx'):
    """
    Read Excel file and extract relationships between:
    1. Document types and platforms that use them
    2. Platform dependencies (which system should have uploaded documents)
    """
    df = pd.read_excel(excel_path)
    
    # Extract document types to platforms relationships
    dt_platform = df[['TipoDocumentos(AS IS) CM v2', 'Plataforma que lo usa']].dropna()
    
    # Extract platform dependencies
    platform_deps = df[['Plataforma que lo usa', 'Cual sistema/portal lo debio haber subido']].dropna()
    
    # Build document type to platforms mapping
    doc_to_platforms = defaultdict(set)
    for _, row in dt_platform.iterrows():
        doc_type = str(row['TipoDocumentos(AS IS) CM v2']).strip()
        platform = normalize_platform_name(row['Plataforma que lo usa'])
        if doc_type and platform and doc_type != 'nan':
            doc_to_platforms[doc_type].add(platform)
    
    # Build platform dependency mapping
    platform_dependencies = {}
    for _, row in platform_deps.iterrows():
        platform = normalize_platform_name(row['Plataforma que lo usa'])
        depends_on = normalize_platform_name(row['Cual sistema/portal lo debio haber subido'])
        if platform and depends_on:
            platform_dependencies[platform] = depends_on
    
    # Build platform obligation status mapping
    # Collect all "Es obligatorio subirlo?" values for each platform
    platform_obligation = defaultdict(list)
    obligation_df = df[['Plataforma que lo usa', 'Es obligatorio subirlo?']].dropna(subset=['Plataforma que lo usa'])
    
    for _, row in obligation_df.iterrows():
        platform = normalize_platform_name(row['Plataforma que lo usa'])
        obligation = str(row['Es obligatorio subirlo?']).strip() if pd.notna(row['Es obligatorio subirlo?']) else ''
        if platform and obligation:
            platform_obligation[platform].append(obligation)
    
    # Determine icon status for each platform
    platform_icon_status = {}
    for platform, obligations in platform_obligation.items():
        # Filter out empty values
        non_empty = [o for o in obligations if o and o.lower() != 'nan']
        
        if not non_empty:
            # All empty - no icon
            platform_icon_status[platform] = None
        else:
            # Check if all are "SI" or "Si"
            all_si = all(o.upper().strip() == 'SI' for o in non_empty)
            # Check if all are "NO" or "No"
            all_no = all(o.upper().strip() == 'NO' for o in non_empty)
            
            if all_si:
                platform_icon_status[platform] = 'SI'
            elif all_no:
                platform_icon_status[platform] = 'NO'
            else:
                # Mixed or other values - show exclamation
                platform_icon_status[platform] = 'OTHER'
    
    # Convert sets to lists for JSON serialization
    doc_to_platforms_dict = {k: list(v) for k, v in doc_to_platforms.items()}
    
    # Build the data structure
    data = {
        'documentTypes': list(doc_to_platforms_dict.keys()),
        'platforms': list(set([p for platforms in doc_to_platforms_dict.values() for p in platforms])),
        'documentTypeToPlatforms': doc_to_platforms_dict,
        'platformDependencies': platform_dependencies,
        'platformIconStatus': platform_icon_status
    }
    
    return data

def embed_data_in_html(data, html_path='index.html'):
    """Embed JSON data into HTML file to avoid CORS issues."""
    try:
        # Read the HTML file
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Convert data to JavaScript format
        json_str = json.dumps(data, ensure_ascii=False, indent=8)
        
        # Find the line with "const embeddedData ="
        if 'const embeddedData =' in html_content:
            # Split by the embeddedData line
            parts = html_content.split('const embeddedData =', 1)
            if len(parts) == 2:
                # Find where the old data ends (look for "let globalPlatformNodes" or "// Initialize")
                second_part = parts[1]
                # Find the next "let globalPlatformNodes" or "// Initialize" comment
                end_marker = second_part.find('\n        // Store global references')
                if end_marker == -1:
                    end_marker = second_part.find('\n        let globalPlatformNodes')
                if end_marker == -1:
                    end_marker = second_part.find('\n        // Initialize')
                if end_marker == -1:
                    end_marker = second_part.find('\n        const data = embeddedData')
                
                if end_marker != -1:
                    # Replace everything between "const embeddedData =" and the global variables
                    new_content = (parts[0] + 
                                 'const embeddedData = ' + json_str + ';\n\n' +
                                 '        // Initialize with embedded data\n' +
                                 '        const data = embeddedData;\n' +
                                 '        \n' +
                                 '        // Store global references for reuse\n' +
                                 second_part[end_marker + len('\n        // Store global references'):])
                    
                    # Write back
                    with open(html_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    print(f"Data embedded in {html_path}")
                    return True
        
        print(f"Warning: Could not find embeddedData marker in {html_path}")
        return False
    except Exception as e:
        print(f"Warning: Could not embed data in HTML: {e}")
        return False

def main():
    """Process data and save to JSON file."""
    print("Processing Excel file...")
    data = process_excel_data()
    
    # Save to JSON file
    output_file = 'data.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"Processed {len(data['documentTypes'])} document types")
    print(f"Found {len(data['platforms'])} unique platforms")
    print(f"Found {len(data['platformDependencies'])} platform dependencies")
    print(f"Data saved to {output_file}")
    
    # Embed data in HTML file
    embed_data_in_html(data)

if __name__ == '__main__':
    main()

