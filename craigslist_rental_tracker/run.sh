#!/bin/bash
# Convenience script to run the Craigslist Rental Tracker

# Activate virtual environment
source venv/bin/activate

# Run the main script with all arguments passed through
python main.py "$@"
