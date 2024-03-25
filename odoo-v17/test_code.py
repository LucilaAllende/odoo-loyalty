import xmlrpc.client

import requests
import json
import time

import os
from dotenv import load_dotenv

# Carga las variables de entorno desde el archivo .env
load_dotenv()

url = os.getenv('URL')
db = os.getenv('DB')
username = os.getenv('USERNAME')
password = os.getenv('PASSWORD') 

url_ws = os.getenv('URL_API_WS')

def sendMessage(para, mensaje):
  data = {
      "message": mensaje,
      "phone": para
  }
  headers = {
      'Content-Type':'application/json'
  }
  print('Holaa send_message',data)
  response = requests.post('http://localhost:3001/lead', json=data, headers=headers)
  time.sleep(10)
  return response

# Reemplaza con la URL de tu instancia de Odoo Online y el token de acceso
token_acceso = ""

# Obtén el token de acceso desde la configuración de tu cuenta de Odoo Online
data = {
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
        "model": "pos.order",
        "method": "get_available_methods",
        "args": [],
    },
    "id": 1,
}

headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + token_acceso,
}

response = requests.post(url, headers=headers, data=json.dumps(data))

if response.status_code == 200:
    # Solicitud exitosa
    metodos = response.json().get("result")
    print("Métodos disponibles para el modelo pos.order:", metodos)
else:
    # Manejar error
    print("Error:", response.status_code)
    print(response)

"""
# Buscar el cliente por su ID
customer_id = 13  # Aquí reemplaza 1 con el ID del cliente que deseas consultar

 # Buscar los puntos de lealtad del cliente
loyalty_points = models.execute_kw(db, uid, password, 'loyalty.points', 'search_count', [[('partner_id', '=', customer_id)]])

# Imprimir la cantidad de puntos de lealtad del cliente
print("El cliente con ID", customer_id, "tiene", loyalty_points, "puntos de lealtad.") """

""" # Obtener los campos del modelo res.partner
fields = models.execute_kw(db, uid, password, 'res.partner', 'fields_get', [])

# Filtrar los campos que incluyen la palabra "sale"
sale_fields = {field_name: field_props for field_name, field_props in fields.items() if 'sale' in field_name}

# Imprimir los campos filtrados
print("Campos del modelo res.partner que incluyen la palabra 'sale':")
for field_name, field_props in sale_fields.items():
    print("Nombre del campo:", field_name)
    print("Tipo de datos:", field_props['type'])
    print("Descripción:", field_props.get('string', ''))
    print()
 """

""" fields = models.execute_kw(db, uid, password, 'loyalty.card', 'fields_get', [])
order11 = models.execute_kw(db, uid, password, 'loyalty.card', 'read', [2], {'fields': ['program_id', 'program_type', 'partner_id', 'points', 'point_name', 'points_display', 'code', 'use_count', 'source_pos_order_id', 'order_id']})
print("order11 selected fields:", order11)

try:
  fields = models.execute_kw(db, uid, password, 'hr.employee', 'fields_get', [])
  employee = models.execute_kw(db, uid, password, 'hr.employee', 'read', [1], {'fields': ['name', 'last_activity_time', 'last_activity', 'activity_summary', 'my_activity_date_deadline', 'activity_type_id',
  'activity_user_id', 'activity_state', ]})

  print("employee selected fields:", employee)
except Exception as e:
  print("Error: ", e)
  print("Error: ", e.args)
  print("Error: ", e.message) """


""" # Llamada a la API para obtener los mensajes del hilo de mensajes
thread_id = 4  # ID del hilo de mensajes
limit = 30  # Límite de mensajes a obtener
params = {
    'thread_id': thread_id,
    'thread_model': 'loyalty.card',
    'limit': limit
}
response = models.execute_kw(db, uid, password, 'mail.thread', 'message_fetch', [params])

# Imprimir el objeto `trackingValues` de cada mensaje
for message in response['messages']:
    tracking_values = message.get('trackingValues', [])
    print("Mensajes de seguimiento:")
    for tracking_value in tracking_values:
        print(tracking_value) """

""" # Llamada a la API para buscar mensajes en un hilo de mensajes
thread_id = 4  # ID del hilo de mensajes
message_ids = models.execute_kw(db, uid, password, 'mail.message', 'search', [[('model', '=', 'loyalty.card'), ('res_id', '=', thread_id)]])
messages = models.execute_kw(db, uid, password, 'mail.message', 'read', [message_ids], {'fields': ['body', 'date', 'author_id', 'tracking_values']})

# Imprimir los mensajes y sus trackingValues
for message in messages:
    print("Mensaje:")
    print("Fecha:", message['date'])
    print("Autor:", message['author_id'][1])
    print("Cuerpo:", message['body'])
    print("Tracking Values:", message['tracking_values'])
    print() """

""" # Llamada a la API para obtener la lista de modelos disponibles
model_list = models.execute_kw(db, uid, password, 'sale.loyalty.coupon', 'fields_get', [], {})

# Imprimir la lista de modelos disponibles
print("Modelos disponibles:",model_list) """
""" for model in model_list:
    print("Modelo:", model['model']) """

""" Modelo: sale.loyalty.coupon.wizard
Modelo: sale.loyalty.reward.wizard """


# This is to test the connection with odoo server.
common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
output = common.version()
print(str("Version: "), output)

# This call tests the credentials and returns the user ID for the next calls.
uid = common.authenticate(db, username, password, {})
print(str("User ID: "), uid)

# Initialize the models endpoint.
models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

# Example to read fields from a specific partner.
fields = models.execute_kw(db, uid, password, 'res.partner', 'search', [[['is_company', '=', True]]])

print(str("Contact selected fields: "), fields)

orders = models.execute_kw(db, uid, password, 'pos.order', 'search', [[]])

print(str("orders selected fields: "), orders)

loya = models.execute_kw(db, uid, password, 'loyalty.card', 'search', [[]])

print(str("loya selected fields: "), loya)

#order11 = models.execute_kw(db, uid, password, 'pos.order', 'read', [orders], {'fields': ['name', 'amount_total', 'x_studio_incluye_loyalty', 'x_studio_incluye_loyalty_1']})

#print(str("order11 selected fields: "), order11)

# Obtener los campos del modelo pos.order
fields = models.execute_kw(db, uid, password, 'pos.order', 'fields_get', [])

# Imprimir los campos disponibles
""" print("Campos del modelo pos.order:")
for field_name, field_props in fields.items():
    print("Nombre del campo:", field_name)
    print("Tipo de datos:", field_props['type'])
    print("Descripción:", field_props.get('string', ''))
    print() """

# Buscar la orden con ID 11
order_id = models.execute_kw(db, uid, password, 'pos.order', 'search', [[('id', '=', 3)]], {'limit': 1})
loya_id = models.execute_kw(db, uid, password, 'loyalty.card', 'search', [[('id', '=', 2)]], {'limit': 1})

print("loya_id:", loya_id)

# Leer los campos especificados para la orden encontrada
if order_id:
    order11 = models.execute_kw(db, uid, password, 'pos.order', 'read', [order_id], {'fields': ['name', 'amount_total', 'x_studio_incluye_loyalty', 'x_studio_incluye_loyalty_1']})
    print("order11 selected fields:", order11)

    loya11 = models.execute_kw(db, uid, password, 'loyalty.card', 'read', [loya_id], {'fields': ['points_display']})  
    print("loya11 selected fields:", loya11)

    sendMessage('542804363636', 'Hola, gastaste un total de ' + str(order11[0]['amount_total']) + ' en tu orden y te sumo ' + str(loya11[0]['points_display'] ))
else:
    print("No se encontró la orden con ID 11")