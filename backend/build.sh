#!/usr/bin/env bash
# Exit on error
set -o errexit

pip install --upgrade pip

# Install CPU-only PyTorch first to avoid downloading 2.5GB+ of unused CUDA/GPU wheels on Render
pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Install application dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

