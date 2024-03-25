import xmlrpc.client
import requests
import time 
import re

import os
from dotenv import load_dotenv

# Carga las variables de entorno desde el archivo .env
load_dotenv()

url_taller = os.getenv('URL_TALLER')
db_taller = os.getenv('DB_TALLER')
username_taller = os.getenv('USERNAME_TALLER')
password_taller = os.getenv('PASSWORD_TALLER')

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
  response = requests.post(url_ws, json=data, headers=headers)
  time.sleep(10)
  return response

def get_odoo_connection(url, db, username, password):
  """Establece conexión con el servidor Odoo y devuelve el uid del usuario."""
  common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
  try:
    uid = common.authenticate(db, username, password, {})
    return uid
  except xmlrpc.client.ProtocolError as error:
    print("Error de conexión:", error)
    return None

def is_program_reward(db, uid, password, product_id):
  """Verifica si un producto es una recompensa."""
  models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url_taller))
  product = models.execute_kw(db, uid, password, 'product.product', 'search_read', [[('id', '=', product_id)]], {'fields': ['default_code']})
  if product[0]['default_code'] == 'TEST_POINTS':
    return True
  else:
    return False

def get_points_cost(db, uid, password, product_id):
  """Obtiene el costo en puntos de un programa de lealtad."""
  models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url_taller))
  # Obtener todos los programas de lealtad
  loyalty_programs = models.execute_kw(db, uid, password, 'loyalty.program', 'search_read', [[]])
  for loyalty_program in loyalty_programs:
    # Obtener detalles de las recompensas de lealtad asociadas al programa
    reward_ids = loyalty_program['reward_ids']
    loyalty_rewards = models.execute_kw(db, uid, password, 'loyalty.reward', 'read', [reward_ids])
    for reward in loyalty_rewards:
      if reward['discount_product_id'] == product_id:
        return reward['point_cost']
      else:
        return 0

def get_order_details(db, uid, password, order_id):
  """Obtiene los detalles de un pedido específico y crea un mensaje personalizado."""
  models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url_taller))
  fields = ['id','partner_id', 'session_id', 'amount_total', 'lines', 'config_id', 'loyalty_points']
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
    order_lines = models.execute_kw(db, uid, password, 'pos.order.line', 'search_read', [[('order_id', '=', order['id'])]])
    for line in order_lines:
      #print('Holaa get_order_details',line)
      if(is_program_reward(db, uid, password, line['product_id'][0])):
        points_cost = get_points_cost(db, uid, password, line['product_id'][0])
    # Obtener la información de lealtad del cliente
    loyalty_points_actual = order['loyalty_points']
    if loyalty_points_actual:
      client = models.execute_kw(db, uid, password, 'res.partner', 'search_read', [[('id', '=', order['partner_id'][0])]])
      balance_points = client[0]['loyalty_points']
      points_gained = loyalty_points_actual
    else:
      balance_points = 0
      points_gained = 0
    msg = f"¡Hola {name_client}! 👋\n\nGracias por tu compra de ${amount_total}. Con esta transacción, has acumulado {points_gained} puntos y gastado {points_cost} . Ahora, tu saldo total de puntos es de {balance_points}.\n\nRecuerda que puedes canjear tus puntos en cualquier momento. Para más información sobre cómo redimir tus puntos, por favor visita este enlace: https://www.google.com \n\n¡Esperamos verte pronto!\nQue tengas un gran día."
    return {
      'name_client': name_client,
      'sesion_payment': order['session_id'],
      'amount_total': amount_total,
      'points_cost': points_cost,
      'balance_points': balance_points,
      'points_gained': points_gained,
      'mobile': mobile,
      'message': msg,
      'name_shop': name_shop
    }
  else:
    return None

# Solicitar al usuario que ingrese id de pedido
pos_order_id = input("Por favor, ingresa numero de pedido: ")
models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url_taller))

# Establece la conexión con Odoo
uid = get_odoo_connection(url_taller, db_taller, username_taller, password_taller)

if uid:
  order_details = get_order_details(db_taller, uid, password_taller, pos_order_id)
  if order_details:
    # Procesa la información del pedido
    name_client = order_details['name_client']
    mobile = order_details['mobile']
    amount_total = order_details['amount_total']
    points_cost = order_details['points_cost']
    balance_points = order_details['balance_points']
    points_gained = order_details['points_gained']
    message = order_details['message']

    # Imprime la información del pedido
    print("Nombre del cliente:", name_client)
    print("Monto total:", amount_total)
    print("Puntos gastados:", points_cost)
    print("Puntos de lealtad:", balance_points)
    print("Puntos ganados:", points_gained)
    print("-----------------------------------")
    print("Mensaje:", message)

    # Marca el pedido como incluido en el programa de lealtad
    if points_cost != 0 or points_gained != 0:
      print("Marcando el pedido", pos_order_id, "como incluido en el programa de lealtad")
      models.execute_kw(db_taller, uid, password_taller, 'pos.order', 'write', [[int(pos_order_id)], {'x_studio_incluye_loyalty': True}])
      # Enviar mensaje al cliente
      if mobile:
        print("Enviando mensaje a:", mobile)
        send_message(mobile, message)
  
    # Marcar el pedido como procesado
    print("Marcando el pedido", pos_order_id, "como procesado")
    models.execute_kw(db_taller, uid, password_taller, 'pos.order', 'write', [[int(pos_order_id)], {'x_studio_esta_procesado': True}])

  else:
    print("No se encontraron detalles para el pedido", pos_order_id)
    # Marcar el pedido como procesado
    print("Marcando el pedido", pos_order_id, "como procesado")
    models.execute_kw(db_taller, uid, password_taller, 'pos.order', 'write', [[int(pos_order_id)], {'x_studio_esta_procesado': True}])
else:
  print("Error de conexión a Odoo")