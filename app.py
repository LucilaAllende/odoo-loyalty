from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from modules.add_new_pos_order import create_pos_order
from modules.process_pos_order_loyalty_by_client import process_order_pos_bulk
from models.user import db, User
from modules.process_pos_order_referral_by_client import process_order_pos_referral
from modules.send_msj_referral import send_msg_referral


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///servicat.db'  # Nombre del archivo de la base de datos
db.init_app(app)
migrate = Migrate(app, db)


# Definimos una ruta para un endpoint
@app.route('/api/hola', methods=['GET'])
def hola_mundo():
    return jsonify({'mensaje': '¡Hola, mundo!'})

@app.route('/webhook/odoo', methods=['POST'])
def odoo_webhook():
    # Obtener el cuerpo de la solicitud como datos brutos
    raw_data = request.data
    print('Datos brutos recibidos desde Odoo:', raw_data)

    # Obtener el cuerpo de la solicitud como JSON si es aplicable
    json_data = request.json
    print('Datos JSON recibidos desde Odoo:', json_data)
    if json_data['cod'] == 1:
        process_order_pos_bulk()
    elif json_data['cod'] == 2:
        send_msg_referral()
    #process_order_pos_referral()
    #create_pos_order()
    return jsonify({'mensaje': 'Solicitud recibida desde Odoo'})

if __name__ == '__main__':
    app.run(debug=True)
