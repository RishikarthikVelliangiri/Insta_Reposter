#!/usr/bin/env python3
"""
Script to fix hardcoded passwords in Python files
This script searches for hardcoded passwords in Python files and replaces them with
environment variable references.
"""

import os
import re
import glob

# Target pattern to replace
PASSWORD_PATTERN = r'INSTAGRAM_PASSWORD\s*=\s*"[^"]*"'
REPLACEMENT = 'INSTAGRAM_PASSWORD = os.environ.get("INSTAGRAM_PASSWORD", "")'

USERNAME_PATTERN = r'INSTAGRAM_USERNAME\s*=\s*"[^"]*"'
USERNAME_REPLACEMENT = 'INSTAGRAM_USERNAME = os.environ.get("INSTAGRAM_USERNAME", "")'

# Files to check
python_files = glob.glob('*.py')

print(f"Found {len(python_files)} Python files to check.")

for file_path in python_files:
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Check if the file has import os
        has_os_import = re.search(r'import\s+os', content)
        has_dotenv_import = re.search(r'from\s+dotenv\s+import\s+load_dotenv', content)
        has_dotenv_load = re.search(r'load_dotenv\(\)', content)
        
        updated_content = content
        
        # Replace password pattern
        if re.search(PASSWORD_PATTERN, updated_content):
            updated_content = re.sub(PASSWORD_PATTERN, REPLACEMENT, updated_content)
            print(f"Replaced password in {file_path}")
        
        # Replace username pattern
        if re.search(USERNAME_PATTERN, updated_content):
            updated_content = re.sub(USERNAME_PATTERN, USERNAME_REPLACEMENT, updated_content)
            print(f"Replaced username in {file_path}")
        
        # Add missing imports if needed
        if updated_content != content:
            if not has_os_import:
                updated_content = "import os\n" + updated_content
                print(f"Added 'import os' to {file_path}")
            
            if not has_dotenv_import:
                updated_content = "from dotenv import load_dotenv\n" + updated_content
                print(f"Added dotenv import to {file_path}")
            
            if not has_dotenv_load:
                # Find a good spot to add load_dotenv() call
                import_section_end = 0
                for match in re.finditer(r'import [^\n]+', updated_content):
                    end = match.end()
                    if end > import_section_end:
                        import_section_end = end
                
                # Add load_dotenv() after imports
                if import_section_end > 0:
                    before = updated_content[:import_section_end]
                    after = updated_content[import_section_end:]
                    updated_content = before + "\n\n# Load environment variables\nload_dotenv()\n" + after
                    print(f"Added load_dotenv() call to {file_path}")
            
            # Write the updated content
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(updated_content)
            
            print(f"Updated {file_path}")
        else:
            print(f"No changes needed in {file_path}")
    
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

print("All files processed successfully.")
