#!/usr/bin/env python3
"""
BitScript Wrapper - Automated Testing Tool

This wrapper automates the process of running BitScript programs:
1. Reads script from file or stdin
2. Calculates script size
3. Runs through bitscript binary
4. Captures and displays output
5. Handles errors gracefully
"""

import sys
import os
import subprocess
import tempfile
from pathlib import Path

class BitScriptWrapper:
    def __init__(self, bitscript_path="./bitscript"):
        """Initialize wrapper with path to bitscript binary."""
        self.bitscript_path = bitscript_path
        if not os.path.exists(bitscript_path):
            raise FileNotFoundError(f"bitscript binary not found: {bitscript_path}")
        if not os.access(bitscript_path, os.X_OK):
            raise PermissionError(f"bitscript binary is not executable: {bitscript_path}")
    
    def calculate_size(self, script_content):
        """Calculate script size in bytes."""
        return len(script_content.encode('utf-8'))
    
    def run_script(self, script_content, show_output=True, capture_output=True):
        """
        Run a BitScript program.
        
        Args:
            script_content: The script to run (string)
            show_output: Whether to print output to stdout
            capture_output: Whether to capture and return output
        
        Returns:
            tuple: (exit_code, stdout, stderr)
        """
        script_size = self.calculate_size(script_content)
        
        # Prepare input: size + script
        # Note: bitscript prints "Input file size :" then reads size, then reads script
        script_size_padded = str(script_size).ljust(0xf)
        input_data = f"{script_size_padded}\n{script_content}".encode('utf-8')
        
        try:
            # Run bitscript
            process = subprocess.Popen(
                [self.bitscript_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # Merge stderr into stdout to capture all output
                cwd=os.path.dirname(self.bitscript_path) or ".",
                bufsize=0  # Unbuffered for immediate input
            )
            
            stdout, _ = process.communicate(input=input_data, timeout=30)
            
            exit_code = process.returncode
            
            # Decode output
            stdout_text = stdout.decode('utf-8', errors='replace') if stdout else ""
            
            # Filter out the prompt "Input file size :" if present
            # This prompt is printed by bitscript before reading size
            if stdout_text.startswith("Input file size :"):
                # Remove the prompt line
                lines = stdout_text.split('\n', 1)
                if len(lines) > 1:
                    stdout_text = lines[1]
                else:
                    stdout_text = ""
            
            # Display output if requested
            if show_output and stdout_text:
                print(stdout_text, end='')
            
            return exit_code, stdout_text, ""
            
        except subprocess.TimeoutExpired:
            process.kill()
            if show_output:
                print("ERROR: Script execution timed out (>30 seconds)", file=sys.stderr)
            return -1, "", "Timeout"
        except Exception as e:
            if show_output:
                print(f"ERROR: {e}", file=sys.stderr)
            return -1, "", str(e)
    
    def test_file(self, script_file, show_output=True):
        """Run a script from a file."""
        try:
            with open(script_file, 'r', encoding='utf-8') as f:
                script_content = f.read()
            
            print(f"Running: {script_file}")
            print(f"Size: {self.calculate_size(script_content)} bytes")
            print("-" * 60)
            
            exit_code, stdout, stderr = self.run_script(script_content, show_output)
            
            print("-" * 60)
            if exit_code == 0:
                print(f"Exit code: {exit_code} ✓")
            else:
                print(f"Exit code: {exit_code} ✗")
                if stderr:
                    print(f"Error: {stderr}")
            
            return exit_code == 0
            
        except FileNotFoundError:
            print(f"ERROR: File not found: {script_file}", file=sys.stderr)
            return False
        except Exception as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return False
    
    def test_string(self, script_content, show_output=True):
        """Run a script from a string."""
        print(f"Size: {self.calculate_size(script_content)} bytes")
        print("-" * 60)
        
        exit_code, stdout, stderr = self.run_script(script_content, show_output)
        
        print("-" * 60)
        if exit_code == 0:
            print(f"Exit code: {exit_code} ✓")
        else:
            print(f"Exit code: {exit_code} ✗")
            if stderr:
                print(f"Error: {stderr}")
        
        return exit_code == 0

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="BitScript Wrapper - Automated Testing Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run a script file
  python3 bitscript_wrapper.py script.bs

  # Run script from stdin
  echo 'print "Hello";' | python3 bitscript_wrapper.py -

  # Run with custom bitscript path
  python3 bitscript_wrapper.py --bitscript /path/to/bitscript script.bs

  # Run multiple scripts
  python3 bitscript_wrapper.py script1.bs script2.bs script3.bs
        """
    )
    
    parser.add_argument(
        'scripts',
        nargs='+',
        help='Script file(s) to run, or "-" for stdin'
    )
    
    parser.add_argument(
        '--bitscript',
        default='./bitscript',
        help='Path to bitscript binary (default: ./bitscript)'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress script output (only show exit codes)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed information'
    )
    
    args = parser.parse_args()
    
    try:
        wrapper = BitScriptWrapper(args.bitscript)
    except (FileNotFoundError, PermissionError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    
    results = []
    
    for script_arg in args.scripts:
        if script_arg == '-':
            # Read from stdin
            if args.verbose:
                print("Reading script from stdin...")
            script_content = sys.stdin.read()
            success = wrapper.test_string(script_content, show_output=not args.quiet)
            results.append(('stdin', success))
        else:
            # Read from file
            success = wrapper.test_file(script_arg, show_output=not args.quiet)
            results.append((script_arg, success))
        
        if len(args.scripts) > 1:
            print()  # Blank line between scripts
    
    # Summary
    if len(results) > 1:
        print("=" * 60)
        print("Summary:")
        print("=" * 60)
        for name, success in results:
            status = "✓ PASS" if success else "✗ FAIL"
            print(f"  {status}: {name}")
        
        passed = sum(1 for _, success in results if success)
        total = len(results)
        print(f"\nTotal: {passed}/{total} passed")
    
    # Exit with error if any script failed
    sys.exit(0 if all(success for _, success in results) else 1)

if __name__ == "__main__":
    main()


