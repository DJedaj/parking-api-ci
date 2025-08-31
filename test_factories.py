# test_factories.py
import pytest

from factories import ClientFactory, ParkingFactory


class TestFactoryBoy:

    def test_create_client_with_factory(self, db):
        """Тест создания клиента с использованием ClientFactory."""
        # Создаем клиента с помощью фабрики
        client = ClientFactory()

        # Проверяем, что объект был сохранен в БД (у него есть ID)
        assert client.id is not None
        # Проверяем, что поля заполнены
        assert client.name is not None
        assert client.surname is not None
        # credit_card может быть None или строкой
        assert client.car_number is not None

    def test_create_parking_with_factory(self, db):
        """Тест создания парковки с использованием ParkingFactory."""
        # Создаем парковку с помощью фабрики
        parking = ParkingFactory()

        # Проверяем, что объект был сохранен в БД (у него есть ID)
        assert parking.id is not None
        # Проверяем, что адрес сгенерирован
        assert parking.address is not None
        # Проверяем, что количество мест валидно
        assert parking.count_places >= 1
        # Проверяем, что count_available_places равно count_places
        assert parking.count_available_places == parking.count_places