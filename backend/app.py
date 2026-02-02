"""
Flask application for Document Types Dependency Visualization.
Provides Excel upload functionality with authentication.
"""

import os
import json
from flask import Flask, render_template, request, jsonify, session, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from process_data import process_excel_data, embed_data_in_html

app = Flask(__name__, 
            static_folder='../frontend',
            static_url_path='')
CORS(app)

# Secret key for session management (change this in production)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Upload configuration
UPLOAD_FOLDER = '../frontend/resources'
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_users():
    """Load users from users.json file."""
    try:
        with open('users.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('users', [])
    except Exception as e:
        print(f"Error loading users: {e}")
        return []

def verify_credentials(email, password):
    """Verify user credentials against users.json."""
    users = load_users()
    for user in users:
        if user.get('email') == email and user.get('password') == password:
            return True
    return False

@app.route('/')
def index():
    """Serve the main visualization page."""
    return send_from_directory('../frontend', 'index.html')

@app.route('/resources/<path:filename>')
def serve_resources(filename):
    """Serve resources like Excel files and images."""
    return send_from_directory('../frontend/resources', filename)

@app.route('/<path:path>')
def serve_static(path):
    """Serve other static files."""
    try:
        return send_from_directory('../frontend', path)
    except:
        # If file not found, return index.html (for SPA routing)
        return send_from_directory('../frontend', 'index.html')

@app.route('/api/auth-status')
def auth_status():
    """Check if the user is authenticated."""
    return jsonify({
        'authenticated': session.get('authenticated', False),
        'email': session.get('email', None)
    })

@app.route('/api/login', methods=['POST'])
def login():
    """Handle user login."""
    try:
        data = request.get_json()
        email = data.get('email', '')
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'success': False, 'message': 'Email and password are required'}), 400
        
        if verify_credentials(email, password):
            session['authenticated'] = True
            session['email'] = email
            return jsonify({'success': True, 'message': 'Login successful'})
        else:
            return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Login error: {str(e)}'}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    """Handle user logout."""
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'})

@app.route('/api/upload-excel', methods=['POST'])
def upload_excel():
    """Handle Excel file upload and processing."""
    # Check authentication
    if not session.get('authenticated', False):
        return jsonify({'success': False, 'message': 'Authentication required'}), 401
    
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file uploaded'}), 400
        
        file = request.files['file']
        
        # Check if filename is empty
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'}), 400
        
        # Validate file extension
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'message': 'Invalid file type. Only .xlsx and .xls files are allowed'}), 400
        
        # Save the file
        filename = secure_filename('portals.xlsx')  # Always save as portals.xlsx
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process the Excel file
        print("Processing uploaded Excel file...")
        data = process_excel_data(filepath)
        
        # Save to JSON file
        output_file = '../data.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # Embed data in HTML file
        embed_success = embed_data_in_html(data)
        
        if embed_success:
            return jsonify({
                'success': True, 
                'message': f'File uploaded and processed successfully. Found {len(data["documentTypes"])} document types and {len(data["platforms"])} platforms.'
            })
        else:
            return jsonify({
                'success': True, 
                'message': 'File uploaded and JSON generated, but HTML embedding failed. Please check the logs.'
            })
        
    except Exception as e:
        print(f"Upload error: {e}")
        return jsonify({'success': False, 'message': f'Error processing file: {str(e)}'}), 500

@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file size limit exceeded."""
    return jsonify({'success': False, 'message': 'File size exceeds the 16MB limit'}), 413

if __name__ == '__main__':
    # Create directories if they don't exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # Run the Flask app (using port 8080 and localhost for Windows compatibility)
    port = int(os.environ.get('PORT', 8080))
    app.run(host='127.0.0.1', port=port, debug=True)
