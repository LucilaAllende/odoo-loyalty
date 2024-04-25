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
  response = requests.post(url_ws, json=data, headers=headers)
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
  

def send_msg_referral():
  # Establece la conexión con Odoo
  uid = get_odoo_connection(url_taller, db_taller, username_taller, password_taller)
  name_client = 'Xavier Tinkin Servicat'
  phone_client = '593999833686'
  points_gained = 32
  points_balance = 196
  if uid:
    message = f"¡Hola {name_client}!👋 ¡Excelentes noticias! Tu código de referido ha sido utilizado. Esto significa que has sumado {points_gained} puntos a tu cuenta, siendo tu saldo total de {points_balance} puntos. Apreciamos mucho tu apoyo y lealtad.  ¡Sigue compartiendo y acumulando más puntos!"
    send_message(phone_client, message)