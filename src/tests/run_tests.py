import unittest
import sys
import os
import logging
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent.parent
sys.path.append(str(src_dir))

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_tests():
    """Run all test cases."""
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = os.path.join(src_dir, 'tests/unit')
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return 0 if tests passed, 1 if any failed
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    sys.exit(run_tests()) 