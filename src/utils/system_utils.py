"""System utilities for checking runtime environment."""

import os
import logging

logger = logging.getLogger(__name__)

def is_running_in_container() -> bool:
    """Check if the application is running inside a container.
    
    This function uses multiple methods to detect container environment:
    1. Check for .dockerenv file
    2. Check cgroup for docker
    3. Check for container-specific environment variables
    
    Returns:
        bool: True if running in container, False otherwise
    """
    try:
        # Method 1: Check for .dockerenv file
        if os.path.exists('/.dockerenv'):
            logger.debug("Container detected via /.dockerenv")
            return True
            
        # Method 2: Check cgroup
        try:
            with open('/proc/1/cgroup', 'r') as f:
                for line in f:
                    if 'docker' in line:
                        logger.debug("Container detected via cgroup")
                        return True
        except (IOError, FileNotFoundError):
            pass
            
        # Method 3: Check environment variables
        container_envs = ['KUBERNETES_SERVICE_HOST', 'DOCKER_CONTAINER']
        if any(env in os.environ for env in container_envs):
            logger.debug(f"Container detected via environment variables")
            return True
            
        logger.debug("No container environment detected")
        return False
        
    except Exception as e:
        logger.error(f"Error checking container status: {str(e)}")
        return False

def get_container_info() -> dict:
    """Get detailed information about the container environment.
    
    Returns:
        dict: Container information including:
            - is_container (bool): Whether running in container
            - container_id (str): Container ID if available
            - container_name (str): Container name if available
            - container_type (str): Type of container (docker, k8s, etc)
    """
    info = {
        'is_container': False,
        'container_id': None,
        'container_name': None,
        'container_type': None
    }
    
    try:
        info['is_container'] = is_running_in_container()
        
        if info['is_container']:
            # Try to get container ID
            try:
                with open('/proc/1/cpuset', 'r') as f:
                    content = f.read().strip()
                    if 'docker' in content:
                        info['container_id'] = content.split('/')[-1]
                        info['container_type'] = 'docker'
            except (IOError, FileNotFoundError):
                pass
                
            # Get container name from environment
            info['container_name'] = os.environ.get('HOSTNAME')
            
            # Check for Kubernetes
            if 'KUBERNETES_SERVICE_HOST' in os.environ:
                info['container_type'] = 'kubernetes'
                
        logger.debug(f"Container info: {info}")
        return info
        
    except Exception as e:
        logger.error(f"Error getting container info: {str(e)}")
        return info 