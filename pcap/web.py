#!/usr/bin/env python3
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "flask",
# ]
# ///
"""
Simple Web Viewer for PCAP Conversation JSON files
"""

from flask import Flask, render_template, jsonify, send_from_directory
import json
import os
from pathlib import Path

app = Flask(__name__)

# Configuration
JSON_DIR = os.environ.get('JSON_DIR', './round_json')

def load_json_files():
    """Load all JSON files from the directory."""
    json_files = []
    json_dir = Path(JSON_DIR)
    
    if not json_dir.exists():
        return []
    
    # Get all JSON files and sort them
    json_file_list = sorted(json_dir.glob('*.json'), key=lambda x: int(x.stem) if x.stem.isdigit() else 999, reverse=True)

    for json_file in json_file_list:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                json_files.append({
                    'filename': json_file.name,
                    'data': data
                })
        except Exception as e:
            print(f"Error loading {json_file}: {e}")

    return json_files

@app.route('/f3aR-tH3-01D-610Od')
def index():
    """Main page showing all conversations."""
    json_files = load_json_files()
    return render_template('index.html', json_files=json_files)

# @app.route('/api/files')
# def api_files():
    # """API endpoint to get all JSON files."""
    # json_files = load_json_files()
    # return jsonify(json_files)

if __name__ == '__main__':
    # Create JSON directory if it doesn't exist
    os.makedirs(JSON_DIR, exist_ok=True)
    print(f"Reading JSON files from: {JSON_DIR}")
    print(f"Starting web server on http://localhost:9000")
    app.run(debug=False, host='0.0.0.0', port=9000)
