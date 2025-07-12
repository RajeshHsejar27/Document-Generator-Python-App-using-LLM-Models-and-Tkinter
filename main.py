#!/usr/bin/env python3
"""
Personal Documentation Assistant - Main Entry Point
A local GUI application for collecting daily notes and images,
generating summaries with local LLM, and exporting reports.
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox
import logging

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui import DocumentationApp
from llm import LLMManager
from reporter import ReportGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def check_dependencies():
    """Check if all required dependencies and model files are available."""
    try:
        # Check if model directory exists
        models_dir = os.path.join(os.path.dirname(__file__), 'models')
        if not os.path.exists(models_dir):
            os.makedirs(models_dir)
            logger.warning(f"Created models directory: {models_dir}")
        
        # Check for model files
        model_files = [f for f in os.listdir(models_dir) if f.endswith('.gguf')]
        if not model_files:
            logger.warning("No .gguf model files found in models/ directory")
            return False
        
        # Check reports directory
        reports_dir = os.path.join(os.path.dirname(__file__), 'reports')
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir)
            logger.info(f"Created reports directory: {reports_dir}")
        
        # Check images directory
        images_dir = os.path.join(os.path.dirname(__file__), 'images')
        if not os.path.exists(images_dir):
            os.makedirs(images_dir)
            logger.info(f"Created images directory: {images_dir}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error checking dependencies: {e}")
        return False


def main():
    """Main application entry point."""
    logger.info("Starting Personal Documentation Assistant")
    
    # Check dependencies
    if not check_dependencies():
        root = tk.Tk()
        root.withdraw()  # Hide main window
        messagebox.showerror(
            "Missing Dependencies",
            "No LLM model files found in models/ directory.\n\n"
            "Please download a compatible .gguf model file and place it in the models/ folder.\n"
            "Recommended: mistral-7b-openorca.Q4_0.gguf\n\n"
            "See README.md for download instructions."
        )
        return 1
    
    try:
        # Initialize core components
        llm_manager = LLMManager()
        report_generator = ReportGenerator()
        
        # Create and run GUI application
        app = DocumentationApp(llm_manager, report_generator)
        app.run()
        
        logger.info("Application closed successfully")
        return 0
        
    except Exception as e:
        logger.error(f"Application error: {e}")
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Application Error",
            f"An error occurred while running the application:\n\n{str(e)}\n\n"
            "Check app.log for more details."
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())