"""Configuration settings for Flask application."""

# File upload configuration
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

# Allowed file extensions and MIME types for uploads
ALLOWED_EXTENSIONS = {
    'html': {'text/html', 'application/xhtml+xml'},
    'xlsx': {
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.ms-excel'
    },
    'xls': {'application/vnd.ms-excel'}
}

# Maximum file sizes per file type (in bytes)
MAX_FILE_SIZES = {
    'html': 5 * 1024 * 1024,   # 5MB for HTML files
    'xlsx': 10 * 1024 * 1024,  # 10MB for Excel files
    'xls': 10 * 1024 * 1024    # 10MB for Excel files
}

