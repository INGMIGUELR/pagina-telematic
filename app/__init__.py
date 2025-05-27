from flask import Flask
import os
from pymongo import MongoClient

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'docx'

def create_app():
    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'templates'),
        static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static')
    )

    app.secret_key = 'clave_super_segura'
    upload_path = os.path.join(os.path.dirname(__file__), '..', 'uploads')
    app.config['UPLOAD_FOLDER'] = upload_path

    # 📦 CONEXIÓN A MONGODB
    client = MongoClient("mongodb://localhost:27017/")
    db = client["mantenimientos"]
    app.config['MONGO_CLIENT'] = client
    app.config['MONGO_DB'] = db

    from .routes import main
    app.register_blueprint(main)

    return app

__all__ = ['allowed_file']
