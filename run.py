from flask import Flask
from app.routes import main  # importa tu Blueprint

app = Flask(__name__)
app.secret_key = 'clave_super_segura'  # Define la clave antes de ejecutar

app.register_blueprint(main)

if __name__ == '__main__':
    app.run(debug=True)

