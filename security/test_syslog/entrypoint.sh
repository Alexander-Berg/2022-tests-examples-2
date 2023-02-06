#!/bin/bash

# Fill config template
/fill_templates.py

# Create certificates
/crt/create_certs.sh

# Run CMD-section of Dockerfile
exec "$@"