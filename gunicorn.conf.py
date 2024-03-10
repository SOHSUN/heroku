# Sample gunicorn configuration file.
bind= '0.0.0.0:$PORT'
# bind = '0.0.0.0:8000'
workers = 4
accesslog = '-'
loglevel = 'info'
capture_output = True
enable_stdio_inheritance = True
