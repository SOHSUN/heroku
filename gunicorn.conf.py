import os

# Sample gunicorn configuration file.
bind = '0.0.0.0:' + str(os.environ.get('PORT', 8000))  # Default port is 8000 if PORT is not set
workers = 4
accesslog = '-'
loglevel = 'info'
capture_output = True
enable_stdio_inheritance = True
