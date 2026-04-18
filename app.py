"""
Streamlit Dashboard Application
Interactive web interface for Poll Results Visualizer
"""

import sys
import os

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from dashboard import main as dashboard_main

if __name__ == "__main__":
    dashboard_main()
