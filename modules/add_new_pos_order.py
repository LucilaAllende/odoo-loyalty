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
  
  
def create_pos_order():
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
    print('Holaa pos_order',pos_order)
    # Datos quemados para el nuevo pedido
    nuevo_pedido = {
        'date_order': '2024-04-23 16:34:14',
        'user_id': [78, 'Sistemas'],
        'amount_tax': 0.13,
        'amount_total': 1.02,
        'amount_paid': 1.02,
        'amount_return': 0.0,
        'margin': 0.0,
        'margin_percent': 0.0,
        'is_total_cost_computed': False,
        'lines': [279627],
        'company_id': [1, 'PARTESCAT COMPAÑÍA LIMITADA'],
        'pricelist_id': [16, 'LISTA DE PRECIO (40.00 %) (USD)'],
        'partner_id': [51977, 'Juanito'],
        'session_id': [8951, 'POS/08951'],
        'config_id': [3, 'POS-NUEVAA-C1 (Sistemas)'],
        'currency_id': [2, 'USD'],
        'currency_rate': 1.0,
        'invoice_group': True,
        'state': 'paid',
        'account_move': False,
        'picking_ids': [],
        'picking_count': 0,
        'failed_pickings': False,
        'picking_type_id': [190, 'BOD. NUEVA AURORA: PoS Orders'],
        'procurement_group_id': False,
        'note': False,
        'nb_print': 0,
        'pos_reference': 'Orden 08951-001-0002',
        'sale_journal': [9, 'Point of Sale'],
        'fiscal_position_id': False,
        'payment_ids': [210230],
        'session_move_id': False,
        'to_invoice': False,
        'to_ship': False,
        'is_invoiced': False,
        'is_tipped': False,
        'tip_amount': 0.0,
        'refund_orders_count': 0,
        'is_refunded': False,
        'refunded_order_ids': [],
        'has_refundable_lines': True,
        'refunded_orders_count': 0,
        '__last_update': '2024-04-23 16:34:14',
        'display_name': 'NA.C1-008201',
        'create_uid': [78, 'Sistemas'],
        'create_date': '2024-04-23 16:34:14',
        'write_uid': [78, 'Sistemas'],
        'write_date': '2024-04-23 16:34:14',
        'applied_program_ids': [],
        'used_coupon_ids': [273],
        'generated_coupon_ids': [],
        'require_customer': 'order',
        'employee_id': [35, 'Oliver Tobar'],
        'cashier': 'Oliver Tobar',
        'loyalty_points': 0.0,
        'crm_team_id': [3, 'Point of Sale'],
        'sale_order_count': 0,
        'refund_approved_orderline_ids': [],
        'picking_note': False,
        'salesman_id': [78, 'Sistemas'],
        'payment_method': False,
        'accesskey': '2204202401179264343000120090020000868832837998912',
        'inv_seq': '009002000086883',
        'refund_detail': False,
        'res_sap_number_doc': 0,
        'res_sap_number_internal': 0,
        'event_audit_id': [392440, 'sap']
    }

    # Crear el nuevo pedido
    try:
        nuevo_pedido_id = models.execute_kw(db_taller, uid, password_taller, 'pos.order', 'create', [nuevo_pedido])
        print("Nuevo pedido creado con el ID:", nuevo_pedido_id)
    except Exception as e:
        print("Error al crear el nuevo pedido:", e)
    pos_order = models.execute_kw(
        db_taller, 
        uid, 
        password_taller, 
        'pos.order', 
        'search_read', 
        [
          [('id', '=', nuevo_pedido_id)]
        ], 
        {'order': 'date_order DESC', 'limit': 1}
    )
    print('Holaa pos_order AGAGAG',pos_order)
    

  else:
    print("Error de conexión a Odoo")