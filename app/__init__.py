from flask import Flask
import os
import secrets

def create_app():
    app = Flask(
        __name__,
        static_folder=os.path.join(os.path.dirname(__file__), 'static'),
        template_folder=os.path.join(os.path.dirname(__file__), 'templates')
    )

    UPLOAD_FOLDER = os.path.join('app', 'static', 'uploads')
    PDF_FOLDER = os.path.join('app', 'static', 'pdfs')
    os.makedirs(PDF_FOLDER, exist_ok=True)
    VISUALIZATION_FOLDER = os.path.join('app', 'static', 'visualization')
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['PDF_FOLDER'] = PDF_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB, adjust as needed


    app.secret_key = secrets.token_hex(32)  # Secure random secret key
    from app.routes import main
    app.register_blueprint(main)
    return app
