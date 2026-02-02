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

def process_excel_data(excel_path='../frontend/resources/portals.xlsx'):
    """
    Read Excel file and extract relationships between:
    1. Document types and platforms that use them
    2. Platform dependencies (which system should have uploaded documents)
    """
    df = pd.read_excel(excel_path)
    
    # Extract document types to platforms relationships
    dt_platform = df[['TipoDocumentos(AS IS) CM v2', 'Plataforma que lo usa']].dropna()
    
    # Build document type to platforms mapping AND document-type-specific dependencies
    doc_to_platforms = defaultdict(set)
    # This will store: documentType -> { platform -> dependency }
    document_type_platform_dependencies = defaultdict(dict)
    # This will store: documentType -> { platform -> obligation text }
    document_platform_obligation_text = defaultdict(dict)
    
    # Build grid data structure for filtering
    # Each row contains: ItemType, DocumentType, Platform
    grid_data = []
    
    # Process all rows that have document type and platform
    for _, row in df.iterrows():
        item_type = str(row['ItemType(AS IS)']).strip() if pd.notna(row['ItemType(AS IS)']) else ''
        
        # Try CM v2 first, if empty fall back to CM v1
        doc_type_v2 = str(row['TipoDocumentos(AS IS) CM v2']).strip() if pd.notna(row['TipoDocumentos(AS IS) CM v2']) else ''
        doc_type_v1 = str(row['TipoDocumentos(AS IS) CM v1']).strip() if pd.notna(row['TipoDocumentos(AS IS) CM v1']) else ''
        
        # Use v2 if it exists, otherwise use v1
        if doc_type_v2 and doc_type_v2 != 'nan':
            doc_type = doc_type_v2
        elif doc_type_v1 and doc_type_v1 != 'nan':
            doc_type = doc_type_v1
        else:
            doc_type = ''
        
        platform = normalize_platform_name(row['Plataforma que lo usa']) if pd.notna(row['Plataforma que lo usa']) else None
        dependency = normalize_platform_name(row['Cual sistema/portal lo debio haber subido']) if pd.notna(row['Cual sistema/portal lo debio haber subido']) else None
        obligation_text = str(row['Es obligatorio subirlo?']).strip() if pd.notna(row['Es obligatorio subirlo?']) else ''
        
        if doc_type and doc_type != 'nan' and platform:
            # Add platform to document type
            doc_to_platforms[doc_type].add(platform)
            
            # Store dependency for this specific document type + platform combination
            # Only store if dependency exists (column G has a value)
            if dependency:
                document_type_platform_dependencies[doc_type][platform] = dependency
            # If no dependency, we don't store it (or store as null - but we'll skip nulls)
            
            # Store obligation text for this document type + platform combination
            if obligation_text and obligation_text.lower() != 'nan':
                document_platform_obligation_text[doc_type][platform] = obligation_text
            
            # Add row to grid data with all columns
            grid_data.append({
                'itemType': item_type if item_type and item_type != 'nan' else '',
                'documentTypeCMv1': doc_type_v1 if doc_type_v1 and doc_type_v1 != 'nan' else '',
                'documentTypeCMv2': doc_type_v2 if doc_type_v2 and doc_type_v2 != 'nan' else '',
                'documentType': doc_type,
                'platform': platform,
                'usoEnPlataforma': str(row['Uso en la plataforma']).strip() if pd.notna(row['Uso en la plataforma']) else '',
                'tipoEjecucion': str(row['Tipo ejecucion']).strip() if pd.notna(row['Tipo ejecucion']) else '',
                'documentoDeQuienEs': str(row['Documento de quien es?(Asegurado, conductor, liquidador, etc)']).strip() if pd.notna(row['Documento de quien es?(Asegurado, conductor, liquidador, etc)']) else '',
                'esObligatorio': obligation_text,
                'ordenSubida': str(row['Orden de subida del documento']).strip() if pd.notna(row['Orden de subida del documento']) else '',
                'flujo': str(row['Flujo(Para Gestor Documental)']).strip() if pd.notna(row['Flujo(Para Gestor Documental)']) else '',
                'sistemaSubio': str(row['Si existe, que sistema subio este documento?(Gestor Documental)']).strip() if pd.notna(row['Si existe, que sistema subio este documento?(Gestor Documental)']) else '',
                'ojo': str(row['Ojo']).strip() if pd.notna(row['Ojo']) else '',
                'sistemasInteractua': str(row['Sistemas con los que interectua']).strip() if pd.notna(row['Sistemas con los que interectua']) else '',
                'dependeOtroSistema': str(row['Depende que otro sistema lo haya subido']).strip() if pd.notna(row['Depende que otro sistema lo haya subido']) else '',
                'cualSistemaSubio': str(row['Cual sistema/portal lo debio haber subido']).strip() if pd.notna(row['Cual sistema/portal lo debio haber subido']) else ''
            })
    
    # Build legacy platform dependency mapping (for backward compatibility, but won't be used)
    # This is kept for reference but the new structure is document-type-specific
    platform_dependencies = {}
    
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
        'documentTypePlatformDependencies': dict(document_type_platform_dependencies),
        'documentPlatformObligationText': dict(document_platform_obligation_text),  # For tooltips on warning icons
        'platformDependencies': platform_dependencies,  # Legacy, kept for backward compatibility
        'platformIconStatus': platform_icon_status,
        'gridData': grid_data  # Grid data for filtering: array of {itemType, documentType, platform}
    }
    
    return data

def embed_data_in_html(data, html_path='../frontend/index.html'):
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
                # Find where the old data ends - look for "let globalPlatformNodes" directly
                # This is more reliable than looking for the comment, which might have junk after it
                second_part = parts[1]
                
                # Find the actual "let globalPlatformNodes" line, skipping any junk in between
                import re
                # Look for the pattern: newline, then whitespace, then "let globalPlatformNodes"
                # This will skip any junk lines like "for reuse" that might appear
                match = re.search(r'\n\s+let\s+globalPlatformNodes', second_part)
                if match:
                    # Extract everything from "let globalPlatformNodes" onwards (skip any junk before it)
                    preserved_content = second_part[match.start():]
                else:
                    # Fallback: try other markers
                    end_marker = second_part.find('\n        // Initialize')
                    if end_marker == -1:
                        end_marker = second_part.find('\n        const data = embeddedData')
                    preserved_content = second_part[end_marker:] if end_marker != -1 else ''
                
                if match or end_marker != -1:
                    # Replace everything between "const embeddedData =" and the global variables
                    # Write clean code: comment + preserved content (which starts with "let globalPlatformNodes")
                    # Strip leading newlines from preserved_content to avoid double newlines
                    preserved_content = preserved_content.lstrip('\n')
                    new_content = (parts[0] + 
                                 'const embeddedData = ' + json_str + ';\n\n' +
                                 '        // Initialize with embedded data\n' +
                                 '        const data = embeddedData;\n' +
                                 '        \n' +
                                 '        // Store global references for reuse\n' +
                                 preserved_content)
                    
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
    output_file = '../data.json'
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

