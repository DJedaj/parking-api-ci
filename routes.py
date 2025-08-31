from flask import Blueprint, request, jsonify
from app import db
from models import Client, Parking, ClientParking
from datetime import datetime


main_bp = Blueprint('main', __name__)


@main_bp.route('/clients', methods=['GET'])
def get_clients():
    clients = Client.query.all()
    return jsonify([
        {
            'id': client.id,
            'name': client.name,
            'surname': client.surname,
            'credit_card': client.credit_card,
            'car_number': client.car_number
        }
        for client in clients
    ])


@main_bp.route('/clients/<int:client_id>', methods=['GET'])
def get_client(client_id):
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
    data = request.get_json()

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


@main_bp.route('/parkings', methods=['POST'])
def create_parking():
    data = request.get_json()

    if not data or not data.get('address') or data.get('count_places') is None:
        return jsonify({'error': 'Address and count_places are required'}), 400

    opened = data.get('opened', True)

    new_parking = Parking(
        address=data['address'],
        opened=opened,
        count_places=data['count_places'],
        count_available_places=data['count_places']
    )

    db.session.add(new_parking)
    db.session.commit()

    return jsonify({'id': new_parking.id, 'message': 'Parking created successfully'}), 201


@main_bp.route('/client_parkings', methods=['POST'])
def enter_parking():
    data = request.get_json()

    if not data or not data.get('client_id') or not data.get('parking_id'):
        return jsonify({'error': 'client_id and parking_id are required'}), 400

    client_id = data['client_id']
    parking_id = data['parking_id']

    Client.query.get_or_404(client_id, description="Client not found")
    parking = Parking.query.get_or_404(parking_id, description="Parking not found")

    if not parking.opened:
        return jsonify({'error': 'Parking is closed'}), 400

    if parking.count_available_places <= 0:
        return jsonify({'error': 'No available places'}), 400

    existing_log = ClientParking.query.filter_by(
        client_id=client_id,
        parking_id=parking_id
    ).first()
    if existing_log and not existing_log.time_out:
        return jsonify({'error': 'Client is already on this parking'}), 400

    parking_log = ClientParking(
        client_id=client_id,
        parking_id=parking_id
    )
    parking.count_available_places -= 1

    db.session.add(parking_log)
    db.session.commit()

    return jsonify({'message': 'Client entered parking successfully'}), 200


@main_bp.route('/client_parkings', methods=['DELETE'])
def exit_parking():
    data = request.get_json()

    if not data or not data.get('client_id') or not data.get('parking_id'):
        return jsonify({'error': 'client_id and parking_id are required'}), 400

    client_id = data['client_id']
    parking_id = data['parking_id']

    Client.query.get_or_404(client_id, description="Client not found")
    Parking.query.get_or_404(parking_id, description="Parking not found")

    parking_log = ClientParking.query.filter_by(
        client_id=client_id,
        parking_id=parking_id,
        time_out=None
    ).first()
    if not parking_log:
        return jsonify({'error': 'Client is not on this parking or has already exited'}), 400

    if not Client.query.get_or_404(client_id).credit_card:
        return jsonify({'error': 'Client has no credit card linked for payment'}), 400

    parking_log.time_out = datetime.utcnow()
    parking = Parking.query.get(parking_id)
    parking.count_available_places += 1

    db.session.commit()

    return jsonify({'message': 'Client exited parking successfully, payment processed'}), 200
