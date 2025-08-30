# app.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Создаем экземпляр SQLAlchemy с отложенной инициализацией
db = SQLAlchemy()


def create_app():
    """Application Factory для создания экземпляра Flask-приложения."""
    app = Flask(__name__)

    # Конфигурация для SQLite (для простоты)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Инициализируем SQLAlchemy с приложением
    db.init_app(app)

    # Импортируем и регистрируем Blueprint
    # Импорт внутри функции предотвращает проблемы с циклическими зависимостями
    from routes import main_bp
    app.register_blueprint(main_bp)

    return app


# Этот блок нужен только для запуска приложения напрямую (python app.py)
# В реальном проекте лучше использовать отдельный файл run.py
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=8080)