# -*- coding: utf-8 -*-
"""Configuration settings for Fantasy Football Fix parser."""

import os

__author__ = 'Vadim Arsenev'
__version__ = '2.0.0'
__date__ = '13.06.2025'

# =============================================================================
# API Configuration
# =============================================================================

# Fantasy Football Fix API base URL
API_URL = 'https://www.fantasyfootballfix.com/api/stats'

# Current season year
YEAR = '2024'

# =============================================================================
# Authentication Configuration
# =============================================================================

# Option 1: Use email/password for automatic authentication (recommended)
# Replace with your actual credentials
EMAIL = os.getenv('FFF_EMAIL', 'your-email@example.com')
PASSWORD = os.getenv('FFF_PASSWORD', 'your-password')

# Option 2: Use manual session ID (fallback method)
# If you manually copy session ID from browser, put it here
# This will be used only if EMAIL/PASSWORD authentication fails
SESSIONID = os.getenv('FFF_SESSION_ID', '')

# =============================================================================
# File Paths Configuration
# =============================================================================

# Base directory for all files
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Data directory
DATA_DIR = os.path.join(BASE_DIR, 'data')

# Settings directory
SETTINGS_DIR = os.path.join(BASE_DIR, 'settings')

# Logs directory
LOGS_DIR = os.path.join(BASE_DIR, 'logs')

# =============================================================================
# Players Configuration
# =============================================================================

# Column definitions file for players
COLUMNS = os.path.join(SETTINGS_DIR, 'FFFplayers.txt')

# Output files for players data
RESULT_FILE = [
    os.path.join(DATA_DIR, 'FFFplayers.csv'),
    # Add more output files if needed
    # os.path.join(DATA_DIR, 'FFFplayers_backup.csv'),
]

# =============================================================================
# Teams Configuration
# =============================================================================

# Column definitions file for teams
COLUMNS_TEAMS = os.path.join(SETTINGS_DIR, 'FFFteams.txt')

# Output files for teams data
RESULT_FILE_TEAMS = [
    os.path.join(DATA_DIR, 'FFFteams.csv'),
    # Add more output files if needed
    # os.path.join(DATA_DIR, 'FFFteams_backup.csv'),
]

# =============================================================================
# Logging Configuration
# =============================================================================

# Log level (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL = 'INFO'

# Enable/disable detailed request logging
DETAILED_LOGGING = True

# =============================================================================
# Request Configuration
# =============================================================================

# Request timeout in seconds
REQUEST_TIMEOUT = 30

# Number of retry attempts for failed requests
REQUEST_RETRIES = 3

# Delay between requests in seconds (be respectful to the server)
REQUEST_DELAY = 1

# =============================================================================
# Data Processing Configuration
# =============================================================================

# Enable/disable data validation
ENABLE_VALIDATION = True

# Enable/disable automatic data cleanup
ENABLE_DATA_CLEANUP = True

# Fields to exclude from output (if any)
EXCLUDED_FIELDS = [
    # Add field names to exclude from CSV output
    # 'some_field_name',
]

# =============================================================================
# Advanced Configuration
# =============================================================================

# User-Agent for HTTP requests
USER_AGENT = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
    'AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/91.0.4472.124 Safari/537.36'
)

# Custom headers for requests
CUSTOM_HEADERS = {
    'Accept': 'application/json',
    'Accept-Language': 'en-US,en;q=0.9',
    # Add more custom headers if needed
}

# Session persistence configuration
SESSION_CACHE_FILE = os.path.join(DATA_DIR, '.fff_session_cache.json')
SESSION_MAX_AGE_DAYS = 14  # Auto re-authenticate after 14 days

# =============================================================================
# Environment-specific overrides
# =============================================================================

# Override settings based on environment
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

if ENVIRONMENT == 'production':
    # Production settings
    LOG_LEVEL = 'WARNING'
    REQUEST_DELAY = 2  # Be more conservative in production
    DETAILED_LOGGING = False
    
elif ENVIRONMENT == 'development':
    # Development settings
    LOG_LEVEL = 'DEBUG'
    REQUEST_DELAY = 0.5  # Faster for development
    DETAILED_LOGGING = True

# =============================================================================
# Validation and Setup
# =============================================================================

def validate_settings():
    """Validate and create necessary directories."""
    import os
    
    # Create directories if they don't exist
    directories = [DATA_DIR, LOGS_DIR]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    # Validate required files exist
    required_files = [COLUMNS, COLUMNS_TEAMS]
    for file_path in required_files:
        if not os.path.exists(file_path):
            print(f"Warning: Required file not found: {file_path}")
    
    # Validate authentication
    if not EMAIL or EMAIL == 'your-email@example.com':
        print("Warning: EMAIL not configured. Please set your FFF email address.")
    
    if not PASSWORD or PASSWORD == 'your-password':
        print("Warning: PASSWORD not configured. Please set your FFF password.")
    
    print("Settings validation completed.")


# Auto-validate settings when module is imported
if __name__ != '__main__':
    validate_settings()


# =============================================================================
# Usage Examples
# =============================================================================

"""
Environment Variables Setup:

# Linux/Mac:
export FFF_EMAIL="your-email@example.com"
export FFF_PASSWORD="your-password"
export ENVIRONMENT="production"

# Windows:
set FFF_EMAIL=your-email@example.com
set FFF_PASSWORD=your-password
set ENVIRONMENT=production

Alternative: Create a .env file in the project root:
FFF_EMAIL=your-email@example.com
FFF_PASSWORD=your-password
ENVIRONMENT=development
"""
