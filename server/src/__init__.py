from flask import Flask

app = Flask(__name__)

from server.src.main.route import main as main

# Register blueprint(s)
app.register_blueprint(main)




