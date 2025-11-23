#!/usr/bin/env python3

import sys

def format_script(script_content):
    # Add padding on the first line
    if script_content and not script_content.startswith('\n'):
        script_content = '\n' + script_content
    
    script_size = len(script_content.encode('utf-8'))
    # Pad script_size to 0xf (15 characters)
    script_size_padded = str(script_size).ljust(0xf)
    input_data = f"{script_size_padded}\n{script_content}".encode('utf-8')
    return input_data

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python warpper.py <script_file>")
        sys.exit(1)
    
    script_file = sys.argv[1]
    with open(script_file, 'r', encoding='utf-8') as f:
        script_content = f.read()
    
    input_data = format_script(script_content)
    sys.stdout.buffer.write(input_data)
