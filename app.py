from flask import Flask
from flask_sqlalchemy import SQLAlchemy

<<<<<<< HEAD
=======

>>>>>>> 1bac4452c2659be602c228bf938dc7c10ecf295b
db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    from routes import main_bp
    app.register_blueprint(main_bp)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=8080)
