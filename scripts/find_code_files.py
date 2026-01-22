#!/usr/bin/env python3
"""
Find code files in a project directory for review.
Excludes common non-code directories and binary files.
"""

import os
import sys
from pathlib import Path

# Directories to exclude from scanning
EXCLUDE_DIRS = {
    'node_modules', '.git', '__pycache__', '.next', '.nuxt', 'dist', 'build',
    '.cache', 'coverage', '.pytest_cache', '.mypy_cache', 'vendor', 'venv',
    '.venv', 'env', '.env', 'target', 'out', '.gradle', '.idea', '.vscode',
    'bower_components', '.sass-cache', 'tmp', 'temp', '.DS_Store'
}

# File extensions to include (common code files)
CODE_EXTENSIONS = {
    '.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.c', '.cpp', '.h', '.hpp',
    '.cs', '.go', '.rs', '.rb', '.php', '.swift', '.kt', '.scala', '.sh',
    '.bash', '.zsh', '.fish', '.sql', '.r', '.m', '.mm', '.dart', '.lua',
    '.pl', '.pm', '.vue', '.svelte', '.astro', '.elm', '.ex', '.exs', '.erl',
    '.clj', '.cljs', '.cljc', '.hs', '.ml', '.fs', '.fsx', '.vb', '.groovy',
    '.gradle', '.cmake', '.yaml', '.yml', '.json', '.toml', '.xml', '.html',
    '.css', '.scss', '.sass', '.less', '.md', '.rst', '.tex'
}

def should_exclude_dir(dir_name):
    """Check if directory should be excluded."""
    return dir_name in EXCLUDE_DIRS or dir_name.startswith('.')

def is_code_file(file_path):
    """Check if file is a code file we should review."""
    # Check extension
    if file_path.suffix.lower() not in CODE_EXTENSIONS:
        return False
    
    # Skip files that are too large (> 1MB)
    try:
        if file_path.stat().st_size > 1_000_000:
            return False
    except:
        return False
    
    return True

def find_code_files(root_dir, max_files=None):
    """
    Find all code files in the project directory.
    
    Args:
        root_dir: Root directory to search
        max_files: Optional maximum number of files to return
    
    Returns:
        List of relative file paths
    """
    root_path = Path(root_dir).resolve()
    code_files = []
    
    for dirpath, dirnames, filenames in os.walk(root_path):
        # Remove excluded directories from search
        dirnames[:] = [d for d in dirnames if not should_exclude_dir(d)]
        
        current_dir = Path(dirpath)
        
        for filename in filenames:
            file_path = current_dir / filename
            
            if is_code_file(file_path):
                # Store relative path
                try:
                    rel_path = file_path.relative_to(root_path)
                    code_files.append(str(rel_path))
                except ValueError:
                    continue
        
        # Stop if we've reached max_files
        if max_files and len(code_files) >= max_files:
            break
    
    return sorted(code_files[:max_files] if max_files else code_files)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: find_code_files.py <directory> [max_files]")
        sys.exit(1)
    
    root_dir = sys.argv[1]
    max_files = int(sys.argv[2]) if len(sys.argv) > 2 else None
    
    files = find_code_files(root_dir, max_files)
    
    for file in files:
        print(file)