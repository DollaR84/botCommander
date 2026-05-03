#!/bin/bash
# init.sh

# List of directories to prepare
DIRS=("sessions" "shared_downloads")

for dir in "${DIRS[@]}"; do
    if [ ! -d "$dir" ]; then
        echo "Creating directory: $dir"
        mkdir -p "$dir"
    fi

    # Set permissions to 1000:1000 so that the container appuser has access
    chown -R 1000:1000 "$dir"
    echo "Permissions set for: $dir"
done

echo "Environment ready for Docker."
