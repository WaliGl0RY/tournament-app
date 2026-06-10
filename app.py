import os
import secrets
from flask import Flask
from database import init_db
from auth import auth_bp
from routes import routes_bp

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))

app.register_blueprint(auth_bp)
app.register_blueprint(routes_bp)

init_db()

if __name__ == '__main__':
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(debug=debug)
