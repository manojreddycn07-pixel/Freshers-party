import sys

project_home = '/home/YOUR_PYTHONANYWHERE_USERNAME/freshers'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

from app import app as application
app = application
