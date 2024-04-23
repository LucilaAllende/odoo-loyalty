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
  # Busca un usuario por su número de identificación
  usuario = User.query.filter_by(identify=identification).first()
  # Actualiza los puntos del usuario
  usuario.points = points
  # Guarda los cambios en la base de datos
  db.session.commit()  
  
def process_order_pos_referral():
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
          [('state', 'in', ('paid', 'done', 'invoiced')), ('partner_id', '=', 51977)]
        ], 
        {'order': 'date_order DESC', 'limit': 1}
    )
    pos_order_id = pos_order[0]['id']
    coupon_data = models.execute_kw(db_taller, uid, password_taller, 'coupon.coupon', 'search', [[['pos_order_id', '=', pos_order_id]]])
    if coupon_data:
      print("Cupón referido encontrado.")
      program_id = coupon_data[0]['program_id'][0]
      program_data = models.execute_kw(db_taller, uid, password_taller, 'coupon.program', 'read', [[program_id]])
      if program_data:
        print("Programa de cupón encontrado.")
        partner_id = program_data[0]['assigned_customer'][0]
        user_data = models.execute_kw(db, uid, password_taller, 'res.partner', 'search_read', [[('id', '=', partner_id)]], {'fields': ['mobile', 'name', 'loyalty_points', 'vat', 'l10n_latam_identification_type_id']})
        if user_data:
          print("Técnico encontrado.")
          phone = user_data[0]['mobile']
          name = user_data[0]['name']
          points_balance = user_data[0]['loyalty_points']
          points_gained = pos_order[0]['loyalty_points']
          userBD = exist_user(user_data[0]['vat'])
          if not userBD:
            create_user(name, phone, user_data[0]['vat'], points_balance, user_data[0]['l10n_latam_identification_type_id'][1])
          else:
            print('El usuario ya existe')
            update_user_points(user_data[0]['vat'], points_balance)
          message = f"¡Hola {name}!👋 ¡Excelentes noticias! Tu código de referido ha sido utilizado. Esto significa que has sumado {points_gained} puntos a tu cuenta, siendo tu saldo total de {points_balance} puntos. Apreciamos mucho tu apoyo y lealtad.  ¡Sigue compartiendo y acumulando más puntos!"
          send_message(phone, message)
        else:
          print("Número de teléfono no encontrado.")
      else:
        print("Programa de cupón no encontrado.")
    else:
      print("Cupón referido no encontrado.")
  else:
    print("Error de conexión a Odoo")