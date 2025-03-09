#!/usr/bin/env python3

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent.parent
sys.path.append(str(src_dir))

from utils.system_utils import is_running_in_container, get_container_info

def main():
    """Check if application is running in a container and print details."""
    
    # Check container status
    is_container = is_running_in_container()
    print(f"\nContainer Check Results:")
    print("-" * 50)
    print(f"Running in container: {'Yes' if is_container else 'No'}")
    
    # Get detailed container info
    container_info = get_container_info()
    print("\nContainer Details:")
    print("-" * 50)
    for key, value in container_info.items():
        print(f"{key}: {value}")
        
    # Print environment info
    print("\nEnvironment Variables:")
    print("-" * 50)
    container_related_vars = [
        'DOCKER_CONTAINER',
        'KUBERNETES_SERVICE_HOST',
        'HOSTNAME',
        'PYTHONPATH',
        'FLASK_APP',
        'FLASK_ENV'
    ]
    for var in container_related_vars:
        if var in os.environ:
            print(f"{var}: {os.environ[var]}")

if __name__ == '__main__':
    main() 