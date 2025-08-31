# factories.py
import factory
from faker import Faker

from models import Client, Parking

fake = Faker()


class ClientFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Фабрика для создания экземпляров модели Client."""

    class Meta:
        model = Client
        sqlalchemy_session = None  # Будет установлено в тестах
        sqlalchemy_session_persistence = (
            "commit"  # Автоматически сохраняет объекты в БД
        )

    name = factory.LazyAttribute(lambda x: fake.first_name())
    surname = factory.LazyAttribute(lambda x: fake.last_name())
    credit_card = factory.Maybe(
        factory.Faker("boolean", chance_of_getting_true=50),
        yes_declaration=factory.LazyAttribute(lambda x: fake.credit_card_number()),
        no_declaration=None,
    )
    car_number = factory.LazyAttribute(lambda x: fake.license_plate())


class ParkingFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Фабрика для создания экземпляров модели Parking."""

    class Meta:
        model = Parking
        sqlalchemy_session = None  # Будет установлено в тестах
        sqlalchemy_session_persistence = (
            "commit"  # Автоматически сохраняет объекты в БД
        )

    address = factory.LazyAttribute(lambda x: fake.address())
    opened = factory.Faker("boolean")
    count_places = factory.Faker("random_int", min=1, max=100)

    # count_available_places зависит от count_places
    count_available_places = factory.LazyAttribute(lambda obj: obj.count_places)
