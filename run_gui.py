"""
GUI Application Entry Point
"""
import sys
import os

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sora_tool.gui.main_window import main

if __name__ == "__main__":
    main()
