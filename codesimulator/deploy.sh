#!/bin/bash

# Step 1: Clean the project
echo "Cleaning the project..."
find . -type d -name "__pycache__" -exec rm -r {} +
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete
echo "Project cleaned."

# Step 2: Build the project
echo "Building the project..."
# Add your build commands here, for example:
python setup.py build
echo "Project built."

# Step 3: Deploy the project
echo "Deploying the project..."
# Add your deployment commands here, for example:
# scp -r ./build user@server:/path/to/deploy
echo "Project deployed."

echo "All steps completed successfully."