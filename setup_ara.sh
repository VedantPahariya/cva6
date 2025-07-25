#!/bin/bash

# CVA6 + ARA Integration Setup Script
# This script sets up the ARA vector processor with CVA6

set -e

echo "=== CVA6 + ARA Integration Setup ==="

# Step 1: Clone ARA repository
echo "Step 1: Cloning ARA repository..."
if [ ! -d "/home/vedant/Desktop/Summer_Project/ara" ]; then
    cd /home/vedant/Desktop/Summer_Project
    git clone https://github.com/pulp-platform/ara.git
    cd ara
    git submodule update --init --recursive
    echo "ARA repository cloned successfully"
else
    echo "ARA repository already exists"
fi

# Step 2: Check directory structure
echo "Step 2: Checking directory structure..."
echo "CVA6 location: /home/vedant/Desktop/Summer_Project/cva6"
echo "ARA location: /home/vedant/Desktop/Summer_Project/ara"

# Step 3: Create integration directories
echo "Step 3: Creating integration directories..."
mkdir -p /home/vedant/Desktop/Summer_Project/cva6/ara_integration
mkdir -p /home/vedant/Desktop/Summer_Project/tests/vector_tests

echo "=== Setup Complete ==="
echo "Next steps:"
echo "1. Run this script: chmod +x setup_ara.sh && ./setup_ara.sh"
echo "2. Follow the integration steps in docs/ARA_INTEGRATION_PLAN.md"
echo "3. Update CVA6 configuration as described in the plan"
