# test_api.py
from datetime import datetime

import pytest

from models import ClientParking, Parking  # Импортируем модели

# Маркер для тестов парковки
parking = pytest.mark.parking

class TestAPI:

    @pytest.mark.parametrize('url', [
        '/clients',
        '/clients/1'
    ])
    def test_get_methods_return_200(self, client, url):
        """Проверка, что GET-методы возвращают 200."""
        response = client.get(url)
        assert response.status_code == 200

    def test_create_client(self, client):
        """Тест создания клиента."""
        data = {
            'name': 'New',
            'surname': 'Client',
            'credit_card': '1111-2222-3333-4444',
            'car_number': 'B002BB'
        }
        response = client.post('/clients', json=data)
        assert response.status_code == 201
        json_data = response.get_json()
        assert 'id' in json_data
        assert json_data['message'] == 'Client created successfully'

    def test_create_parking(self, client):
        """Тест создания парковки."""
        data = {
            'address': 'New Parking',
            'count_places': 5
        }
        response = client.post('/parkings', json=data)
        assert response.status_code == 201
        json_data = response.get_json()
        assert 'id' in json_data

    @parking
    def test_enter_parking(self, client, db):
        """Тест заезда на парковку."""
        data = {
            'client_id': 1,
            'parking_id': 1
        }
        # Проверяем начальное состояние
        parking = db.session.get(Parking, 1)
        initial_available = parking.count_available_places

        response = client.post('/client_parkings', json=data)
        assert response.status_code == 200

        # Проверяем, что количество свободных мест уменьшилось
        db.session.refresh(parking)
        assert parking.count_available_places == initial_available - 1

    @parking
    def test_exit_parking(self, client, db):
        """Тест выезда с парковки."""
        data = {
            'client_id': 1,
            'parking_id': 1
        }
        # Проверяем начальное состояние
        parking = db.session.get(Parking, 1)
        initial_available = parking.count_available_places

        response = client.delete('/client_parkings', json=data)
        assert response.status_code == 200

        # Проверяем, что количество свободных мест увеличилось
        db.session.refresh(parking)
        assert parking.count_available_places == initial_available + 1

        # Проверяем, что time_out установлен и больше time_in
        log = db.session.execute(
            db.select(ClientParking).filter_by(client_id=1, parking_id=1)
        ).scalar_one()
        assert log.time_out is not None
        assert log.time_out > log.time_in