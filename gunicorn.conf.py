# Sample gunicorn configuration file.
bind= '0.0.0.0:' + str(os.getenv("PORT", 8000))
# bind = '0.0.0.0:8000'
workers = 4
accesslog = '-'
loglevel = 'info'
capture_output = True
enable_stdio_inheritance = True
