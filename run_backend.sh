#!/bin/bash

echo "Backend pipeline started..."

cd backend

# runs scrapers
python crawler.py

# runs export-the weather is addeed to scraper results.
python export_to_frontend.py

echo "created resort_data.json for export"
