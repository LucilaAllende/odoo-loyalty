import xmlrpc.client
import requests
import time 
import re

import os
from dotenv import load_dotenv

# Carga las variables de entorno desde el archivo .env
load_dotenv()

url = os.getenv('URL')
db = os.getenv('DB')
username = os.getenv('USERNAME')
password = os.getenv('PASSWORD') 

url_ws = os.getenv('URL_API_WS')

def send_message(para, mensaje):
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

def get_odoo_connection(url, db, username, password):
  """Establece conexión con el servidor Odoo y devuelve el uid del usuario."""
  print('Holaa get_odoo_connection',url, db, username, password)
  common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
  try:
    uid = common.authenticate(db, username, password, {})
    return uid
  except xmlrpc.client.ProtocolError as error:
    print("Error de conexión:", error)
    return None

def get_order_details(db, uid, password, order_id):
  """Obtiene los detalles de un pedido específico y crea un mensaje personalizado."""
  models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
  fields = ['id','partner_id', 'session_id', 'amount_total', 'lines', 'config_id']
  order_data = models.execute_kw(db, uid, password, 'pos.order', 'search_read', [[('id', '=', order_id)], fields])
  if order_data and order_data[0]['partner_id']:
    order = order_data[0]
    name_client = order['partner_id'][1]
    amount_total = order['amount_total']
    # Eliminar texto agregado por Odoo
    name_shop = order['config_id'][1].replace(" (no usado)", "")
    mobile = models.execute_kw(db, uid, password, 'res.partner', 'search_read', [[('id', '=', order['partner_id'][0])]], {'fields': ['mobile']})
    # Eliminar caracteres especiales
    mobile = re.sub(r"[^0-9]", "", mobile[0]['mobile'])
    # Obtener los puntos gastado y el programa de lealtad
    points_cost = 0
    reward_identifier_code = ''
    order_lines = models.execute_kw(db, uid, password, 'pos.order.line', 'search_read', [[('order_id', '=', order['id'])]])
    for line in order_lines:
      points_cost += line['points_cost']
      reward_identifier_code = line['reward_identifier_code']
    # Obtener la información de lealtad del cliente
    loyalty_info = get_loyalty_info(db, uid, password, order['partner_id'][0])
    if loyalty_info:
      balance_points = loyalty_info['balance_points']
      points_gained = loyalty_info['points_gained']
    else:
      balance_points = 0
      points_gained = 0
    msg = "Hola " + name_client + " le informamos que en su última compra realizada en "+ name_shop +" por $" + str(amount_total) + " sumo "+ str(points_gained) + " puntos y gasto "+ str(points_cost) +" puntos. Recuerde que posee un total de " + str(balance_points) +" puntos de lealtad disponibles para usar."
    return {
      'name_client': name_client,
      'sesion_payment': order['session_id'],
      'amount_total': amount_total,
      'points_cost': points_cost,
      'reward_identifier_code': reward_identifier_code,
      'balance_points': balance_points,
      'points_gained': points_gained,
      'mobile': mobile,
      'message': msg,
      'name_shop': name_shop
    }
  else:
    return None

def get_loyalty_info(db, uid, password, customer_id):
  """Obtiene la información de lealtad del cliente."""
  models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
  coupon_data = models.execute_kw(db, uid, password, 'loyalty.card', 'search_read', [[('partner_id', '=', customer_id)], ['points', 'message_ids']])
  if coupon_data:
    coupon = coupon_data[0]
    message_ids = coupon['message_ids']
    for message_id in message_ids:
      message_data = models.execute_kw(db, uid, password, 'mail.message', 'search_read', [[('id', '=', message_id)], ['tracking_value_ids']])
      if message_data and message_data[0]['tracking_value_ids']:
        tracking_id = message_data[0]['tracking_value_ids'][0]
        tracking_data = models.execute_kw(db, uid, password, 'mail.tracking.value', 'search_read', [[('id', '=', tracking_id), ('new_value_float', '=', coupon['points'])]])
        if tracking_data:
          points_old = tracking_data[0]['old_value_float']
          points_diff = coupon['points'] - points_old
          points_gained = max(0, points_diff)
          return {
            'balance_points': coupon['points'],
            'points_gained': points_gained
          }
    return {'balance_points': coupon['points'], 'points_gained': 0}
  else:
    return None

# Establece la conexión con Odoo
uid = get_odoo_connection(url, db, username, password)
print('Holaa uid',uid)
if uid:
  # Obtiene los pedidos no procesados
  models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
  pos_orders = models.execute_kw(db, uid, password, 'pos.order', 'search_read', [[('x_studio_esta_procesado_1', '=', False), ('state', 'in', ('paid', 'done', 'invoiced')) ]], {'order': 'id'})
  # Recorre la lista de pedidos y obtiene los detalles de cada uno
  for pos_order in pos_orders:
    order_details = get_order_details(db, uid, password, pos_order['id'])
    if order_details:
      # Procesa la información del pedido
      name_client = order_details['name_client']
      mobile = order_details['mobile']
      amount_total = order_details['amount_total']
      points_cost = order_details['points_cost']
      reward_identifier_code = order_details['reward_identifier_code']
      balance_points = order_details['balance_points']
      points_gained = order_details['points_gained']
      message = order_details['message']

      # Imprime la información del pedido
      print("Nombre del cliente:", name_client)
      print("Monto total:", amount_total)
      print("Código de identificación de la recompensa:", reward_identifier_code)
      print("Puntos gastados:", points_cost)
      print("Puntos de lealtad:", balance_points)
      print("Puntos ganados:", points_gained)
      print("-----------------------------------")
      print("Mensaje:", message)

      # Marca el pedido como incluido en el programa de lealtad
      if points_cost > 0 or points_gained > 0:
        print("Marcando el pedido", pos_order['id'], "como incluido en el programa de lealtad")
        models.execute_kw(db, uid, password, 'pos.order', 'write', [[pos_order['id']], {'x_studio_incluye_loyalty_1': True}])
        # Enviar mensaje al cliente
        if mobile:
          print("Enviando mensaje a:", mobile)
          send_message(mobile, message)
    
      # Marcar el pedido como procesado
      print("Marcando el pedido", pos_order['id'], "como procesado")
      models.execute_kw(db, uid, password, 'pos.order', 'write', [[pos_order['id']], {'x_studio_esta_procesado_1': True}])

    else:
      print("No se encontraron detalles para el pedido", pos_order['id'])
      # Marcar el pedido como procesado
      print("Marcando el pedido", pos_order['id'], "como procesado")
      models.execute_kw(db, uid, password, 'pos.order', 'write', [[pos_order['id']], {'x_studio_esta_procesado_1': True}])
else:
  print("Error de conexión a Odoo")

