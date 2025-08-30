# routes.py
from flask import Blueprint, request, jsonify
from app import db
from models import Client, Parking, ClientParking
from datetime import datetime

# Создаем Blueprint для организации маршрутов
main_bp = Blueprint('main', __name__)


# --- Маршруты для клиентов ---
@main_bp.route('/clients', methods=['GET'])
def get_clients():
    """Получить список всех клиентов."""
    clients = Client.query.all()
    return jsonify([{
        'id': client.id,
        'name': client.name,
        'surname': client.surname,
        'credit_card': client.credit_card,
        'car_number': client.car_number
    } for client in clients])


@main_bp.route('/clients/<int:client_id>', methods=['GET'])
def get_client(client_id):
    """Получить информацию о клиенте по ID."""
    client = Client.query.get_or_404(client_id)
    return jsonify({
        'id': client.id,
        'name': client.name,
        'surname': client.surname,
        'credit_card': client.credit_card,
        'car_number': client.car_number
    })


@main_bp.route('/clients', methods=['POST'])
def create_client():
    """Создать нового клиента."""
    data = request.get_json()

    # Проверка обязательных полей
    if not data or not data.get('name') or not data.get('surname'):
        return jsonify({'error': 'Name and surname are required'}), 400

    new_client = Client(
        name=data['name'],
        surname=data['surname'],
        credit_card=data.get('credit_card'),
        car_number=data.get('car_number')
    )

    db.session.add(new_client)
    db.session.commit()

    return jsonify({'id': new_client.id, 'message': 'Client created successfully'}), 201


# --- Маршруты для парковок ---
@main_bp.route('/parkings', methods=['POST'])
def create_parking():
    """Создать новую парковочную зону."""
    data = request.get_json()

    # Проверка обязательных полей
    if not data or not data.get('address') or data.get('count_places') is None:
        return jsonify({'error': 'Address and count_places are required'}), 400

    # По умолчанию парковка открыта, если явно не указано иное
    opened = data.get('opened', True)

    new_parking = Parking(
        address=data['address'],
        opened=opened,
        count_places=data['count_places'],
        count_available_places=data['count_places']  # Изначально все места свободны
    )

    db.session.add(new_parking)
    db.session.commit()

    return jsonify({'id': new_parking.id, 'message': 'Parking created successfully'}), 201


# --- Маршруты для заезда/выезда ---
@main_bp.route('/client_parkings', methods=['POST'])
def enter_parking():
    """Заезд на парковку."""
    data = request.get_json()

    # Проверка обязательных полей
    if not data or not data.get('client_id') or not data.get('parking_id'):
        return jsonify({'error': 'client_id and parking_id are required'}), 400

    client_id = data['client_id']
    parking_id = data['parking_id']

    # Проверяем существование клиента и парковки
    client = Client.query.get_or_404(client_id, description="Client not found")
    parking = Parking.query.get_or_404(parking_id, description="Parking not found")

    # Проверяем, открыта ли парковка
    if not parking.opened:
        return jsonify({'error': 'Parking is closed'}), 400

    # Проверяем, есть ли свободные места
    if parking.count_available_places <= 0:
        return jsonify({'error': 'No available places'}), 400

    # Проверяем, не находится ли клиент уже на этой парковке
    existing_log = ClientParking.query.filter_by(client_id=client_id, parking_id=parking_id).first()
    if existing_log and not existing_log.time_out:
        return jsonify({'error': 'Client is already on this parking'}), 400

    # Создаем новую запись о заезде
    parking_log = ClientParking(client_id=client_id, parking_id=parking_id)

    # Уменьшаем количество свободных мест
    parking.count_available_places -= 1

    db.session.add(parking_log)
    db.session.commit()

    return jsonify({'message': 'Client entered parking successfully'}), 200


@main_bp.route('/client_parkings', methods=['DELETE'])
def exit_parking():
    """Выезд с парковки."""
    data = request.get_json()

    # Проверка обязательных полей
    if not data or not data.get('client_id') or not data.get('parking_id'):
        return jsonify({'error': 'client_id and parking_id are required'}), 400

    client_id = data['client_id']
    parking_id = data['parking_id']

    # Проверяем существование клиента и парковки
    client = Client.query.get_or_404(client_id, description="Client not found")
    parking = Parking.query.get_or_404(parking_id, description="Parking not found")

    # Проверяем, что клиент находится на этой парковке и еще не выехал
    parking_log = ClientParking.query.filter_by(client_id=client_id, parking_id=parking_id, time_out=None).first()
    if not parking_log:
        return jsonify({'error': 'Client is not on this parking or has already exited'}), 400

    # Рекомендация: Производим оплату
    # Проверяем, привязана ли карта
    if not client.credit_card:
        return jsonify({'error': 'Client has no credit card linked for payment'}), 400

    # Здесь должна быть логика расчета стоимости и списания средств
    # Например: calculate_and_charge(client, parking_log.time_in)
    # Для упрощения, просто считаем, что оплата прошла успешно

    # Фиксируем время выезда
    parking_log.time_out = datetime.utcnow()

    # Увеличиваем количество свободных мест
    parking.count_available_places += 1

    db.session.commit()

    return jsonify({'message': 'Client exited parking successfully, payment processed'}), 200
