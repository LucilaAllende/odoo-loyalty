from flask import Flask, request, jsonify

app = Flask(__name__)

# Definimos una ruta para un endpoint
@app.route('/api/hola', methods=['GET'])
def hola_mundo():
    return jsonify({'mensaje': '¡Hola, mundo!'})

@app.route('/webhook/odoo', methods=['POST'])
def odoo_webhook():
    print('Solicitud recibida desde Odoo:', request)
    return jsonify({'mensaje': 'Solicitud recibida desde Odoo'})

if __name__ == '__main__':
    app.run(debug=True)
