import sys, os
activate_this = 'D:/python/perch-mount-flask-app/venv/Scripts/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))
sys.path.insert(0, os.path.dirname(__file__))
from app import app
application = app