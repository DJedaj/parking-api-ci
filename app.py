from flask import Flask
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    from routes import main_bp
    app.register_blueprint(main_bp)

    # Импортируем модели ПОСЛЕ инициализации db. Используется для регистрации моделей.
    from . import models  # noqa: F401

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=8080)
