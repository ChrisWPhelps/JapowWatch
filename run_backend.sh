#!/bin/bash

echo "Backend pipeline started..."

cd backend

python crawler.py
CRAWL_EXIT=$?
if [ "$CRAWL_EXIT" -ne 0 ]; then
    echo "Crawler failed (exit $CRAWL_EXIT). Aborting pipeline."
    exit 1
fi

# validation tests Navigate back to root to run pytest on the tests directory
cd ..
pytest tests/test_parsers.py

# Check the exit code of pytest ($?)
# If it is 0 (Success), proceed to export.
if [ $? -eq 0 ]; then
    echo "Tests passed. Proceeding to export..."
    cd backend
    python export_to_frontend.py
    echo "Backend export complete."
    echo "Next step (optional frontend):"
    echo "  cd frontend && npm start"
else
    echo "Tests failed. Export aborted to prevent data corruption."
    exit 1
fi