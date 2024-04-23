import xmlrpc.client
import requests
import time 
import re

import os
from dotenv import load_dotenv

from models.user import User, db

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
  #response = requests.post(url_ws, json=data, headers=headers)
  time.sleep(10)
  return []

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
  print('Holaa is_program_reward',product)
  if product[0]['default_code'] == 'DISC':
    return True
  else:
    return False

def process_multiple(product, point_cost, points_gained, loyalty_points_actual, loyalty_points_bd):
  """Procesa un producto que aparece más de una vez en la lista."""
  if(loyalty_points_bd+points_gained-point_cost == loyalty_points_actual):
    print("El costo de puntos es igual a la cantidad de puntos gastados")
    return point_cost
  return 0

def get_points_cost(db, uid, password, product_ids, loyalty_points_actual, loyalty_points_bd, point_cost):
  """Obtiene el costo en puntos de un programa de lealtad."""
  models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url_taller))
  # Obtener todos los programas de lealtad
  loyalty_programs = models.execute_kw(db, uid, password, 'loyalty.program', 'search_read', [[]])
  
  total_points_cost = 0.0  # Variable para almacenar la suma de los puntos
  
  for loyalty_program in loyalty_programs:
      # Obtener detalles de las recompensas de lealtad asociadas al programa
      reward_ids = loyalty_program['reward_ids']
      loyalty_rewards = models.execute_kw(db, uid, password, 'loyalty.reward', 'read', [reward_ids])
      for reward in loyalty_rewards:
          if reward['reward_type']== 'gift' and reward['gift_product_id'][0] in product_ids:  # Verificar si el product_id está en la lista
            total_points_cost += reward['point_cost']
          if reward['reward_type']== 'discount':
            for product in reward['discount_specific_product_ids']:
              # Verifica si el producto está más de una vez en la lista
              if product_ids.count(product) > 0:
                  # Llama al método process_multiple si el producto aparece más de una vez
                  total_points_cost += process_multiple(product, reward['point_cost'], point_cost, loyalty_points_actual, loyalty_points_bd)
              elif product in product_ids:
                  print('Holaa get_points_cost reward product', product)
                  total_points_cost += reward['point_cost']
  
  return total_points_cost

def build_accounting_entries(order, order_lines):
    negative_line = None
    for line in order_lines:
        if line['price_subtotal_incl'] < 0:
            negative_line = line
            break

    if negative_line:
        for line in order_lines:
            if line['price_subtotal_incl'] == abs(negative_line['price_subtotal_incl']):
                return line['product_id'][0]
    
    return None

def get_order_details(db, uid, password, order_id, loyalty_points_bd):
  """Obtiene los detalles de un pedido específico y crea un mensaje personalizado."""
  models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url_taller))
  fields = ['id','partner_id', 'session_id', 'amount_total', 'lines', 'config_id', 'loyalty_points']
  order_data = models.execute_kw(db, uid, password, 'pos.order', 'search_read', [[('id', '=', order_id)], fields])
  if order_data and order_data[0]['partner_id']:
    order = order_data[0]
    #print('Holaa order',order)
    name_client = order['partner_id'][1]
    amount_total = order['amount_total']
    # Eliminar texto agregado por Odoo
    name_shop = order['config_id'][1].replace(" (Sistemas)", "")
    mobile = models.execute_kw(db, uid, password, 'res.partner', 'search_read', [[('id', '=', order['partner_id'][0])]], {'fields': ['mobile']})
    # Eliminar caracteres especiales
    mobile = re.sub(r"[^0-9]", "", mobile[0]['mobile'])
    # Obtener los puntos gastado y el programa de lealtad
    order_lines = models.execute_kw(db, uid, password, 'pos.order.line', 'search_read', [[('order_id', '=', order['id'])]])
    #print('Holaa order_lines',order_lines)
    # Obtener la información de lealtad del cliente
    loyalty_points_actual = order['loyalty_points']
    if loyalty_points_actual:
      client = models.execute_kw(db, uid, password, 'res.partner', 'search_read', [[('id', '=', order['partner_id'][0])]])
      balance_points = client[0]['loyalty_points']
      points_gained = loyalty_points_actual
    else:
      balance_points = 0
      points_gained = 0
    generated_entries = build_accounting_entries(order, order_lines)
    points_cost = 0.0
    for line in order_lines:
      if(is_program_reward(db, uid, password, line['product_id'][0])):
        points_cost = get_points_cost(db, uid, password, [generated_entries], balance_points, loyalty_points_bd, points_gained)

    msg = f"¡Hola {name_client}! 👋\n\nGracias por tu compra de ${amount_total} en nuestro punto de venta ${name_shop}. Con esta transacción, has acumulado {points_gained} puntos y gastado {points_cost} . Ahora, tu saldo total de puntos es de {balance_points}.\n\nRecuerda que puedes canjear tus puntos en cualquier momento. Para más información sobre cómo redimir tus puntos, por favor visita este enlace: https://www.google.com \n\n¡Esperamos verte pronto!\nQue tengas un gran día."
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

def create_user(username, phone, identification, points=0, type_identify='Cédula'):
    # Crea una instancia del modelo User con los datos proporcionados
    nuevo_usuario = User(name=username, phone=phone, identify=identification, points=points, type_identify=type_identify)
    # Agrega el nuevo usuario a la sesión
    db.session.add(nuevo_usuario)
    # Guarda los cambios en la base de datos
    db.session.commit()
    
def exist_user(identification):
  # Busca un usuario por su número de identificación
  usuario = User.query.filter_by(identify=identification).first()
  return usuario

def update_user_points(identification, points):
  print('Holaa update_user_points',identification, points)
  # Busca un usuario por su número de identificación
  usuario = User.query.filter_by(identify=identification).first()
  # Actualiza los puntos del usuario
  usuario.points = points
  # Guarda los cambios en la base de datos
  db.session.commit()  

def process_order_pos_bulk():
  # Establece la conexión con Odoo
  uid = get_odoo_connection(url_taller, db_taller, username_taller, password_taller)

  if uid:
    models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url_taller))
    # Obtiene el último pedido pagado del cliente
    pos_order = models.execute_kw(
        db_taller, 
        uid, 
        password_taller, 
        'pos.order', 
        'search_read', 
        [
          [('state', 'in', ('paid', 'done', 'invoiced')), ('partner_id', '=', 51974)]
        ], 
        {'order': 'date_order DESC', 'limit': 1}
    )
    print('Holaa pos_order',pos_order)
    user = models.execute_kw(db_taller, uid, password_taller, 'res.partner', 'search_read', [[('id', '=', 51974)]], {'fields': ['id','name','mobile', 'email_normalized', 'l10n_latam_identification_type_id', 'loyalty_points', 'classification_id', 'vat']})
    loyalty_points_bd = 0
    userBD = exist_user(user[0]['vat'])
    if not userBD:
      create_user(user[0]['name'], user[0]['mobile'], user[0]['vat'], user[0]['loyalty_points'], user[0]['l10n_latam_identification_type_id'][1])
    else:
      print('El usuario ya existe')
      loyalty_points_bd = userBD.points

    order_details = get_order_details(db_taller, uid, password_taller, pos_order[0]['id'], loyalty_points_bd)
    if order_details:
      # Procesa la información del pedido
      name_client = order_details['name_client']
      mobile = order_details['mobile']
      amount_total = order_details['amount_total']
      points_cost = order_details['points_cost']
      balance_points = order_details['balance_points']
      points_gained = order_details['points_gained']
      message = order_details['message']
      update_user_points(user[0]['vat'], balance_points)
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
        print("Marcando el pedido", pos_order[0]['id'], "como incluido en el programa de lealtad")
        #models.execute_kw(db_taller, uid, password_taller, 'pos.order', 'write', [[pos_order['id']], {'x_studio_incluye_loyalty': True}])
        # Enviar mensaje al cliente
        if mobile:
          print("Enviando mensaje a:", mobile)
          send_message(mobile, message)
    
      # Marcar el pedido como procesado
      #print("Marcando el pedido", pos_order['id'], "como procesado")
      #models.execute_kw(db_taller, uid, password_taller, 'pos.order', 'write', [[pos_order['id']], {'x_studio_esta_procesado': True}])

    else:
      print("No se encontraron detalles para el pedido", pos_order['id'])
      # Marcar el pedido como procesado
      #print("Marcando el pedido", pos_order['id'], "como procesado")
      #models.execute_kw(db_taller, uid, password_taller, 'pos.order', 'write', [[pos_order['id']], {'x_studio_esta_procesado_1': True}])
  else:
    print("Error de conexión a Odoo")