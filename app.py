from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from modules.process_pos_order_by_client import process_order_pos_bulk
from models.user import db, User


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
    print('Solicitud recibida desde Odoo:', request)
    process_order_pos_bulk()
    return jsonify({'mensaje': 'Solicitud recibida desde Odoo'})

if __name__ == '__main__':
    app.run(debug=True)
