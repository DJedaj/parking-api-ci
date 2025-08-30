# conftest.py
import pytest
from app import create_app
from models import db as _db, Client, Parking, ClientParking
from datetime import datetime, timedelta, timezone
from factories import ClientFactory, ParkingFactory

@pytest.fixture(scope='session')
def app():
    """Создает приложение для тестирования."""
    app = create_app()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False

    with app.app_context():
        _db.create_all()

        # Создаем тестовые объекты, используя КОНКРЕТНЫЕ модели
        client = Client(
            name='Test',
            surname='User',
            credit_card='1234-5678-9012-3456',
            car_number='A001AA'
        )
        parking = Parking(
            address='Test Address',
            opened=True,
            count_places=10,
            count_available_places=10
        )
        _db.session.add(client)
        _db.session.add(parking)
        _db.session.commit()

        # ВАЖНО: Запись о заезде НЕ создается здесь.
        # Она должна создаваться только в соответствующем тесте.

    yield app

    with app.app_context():
        _db.drop_all()

@pytest.fixture(scope='function')
def db(app):
    """Фикстура для работы с БД."""
    with app.app_context():
        # Устанавливаем сессию для фабрик
        ClientFactory._meta.sqlalchemy_session = _db.session
        ParkingFactory._meta.sqlalchemy_session = _db.session
        yield _db

@pytest.fixture(scope='function')
def client(app):
    """Фикстура для создания тестового клиента."""
    with app.test_client() as c:
        yield c