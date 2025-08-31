import factory
from faker import Faker

from models import Client, ClientParking, Parking

# Создаём экземпляр Faker с явным указанием локали (например, 'ru_RU' для русского)
fake = Faker("ru_RU")


class ClientFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Client
        # sqlalchemy_session = db.session  # Если нужно, укажите сессию

    id = factory.Sequence(lambda n: n)
    name = fake.first_name()
    surname = fake.last_name()
    credit_card = fake.credit_card_number()
    car_number = fake.license_plate()


class ParkingFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Parking
        # sqlalchemy_session = db.session

    id = factory.Sequence(lambda n: n)
    address = fake.address()
    opened = True
    count_places = factory.Faker("random_int", min=10, max=100)
    count_available_places = factory.SelfAttribute("count_places")


class ClientParkingFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = ClientParking
        # sqlalchemy_session = db.session

    id = factory.Sequence(lambda n: n)
    client = factory.SubFactory(ClientFactory)
    parking = factory.SubFactory(ParkingFactory)
    time_in = factory.Faker("date_time_this_year")
    time_out = None
