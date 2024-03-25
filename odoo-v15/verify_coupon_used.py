import xmlrpc.client
import os
from dotenv import load_dotenv

# Carga las variables de entorno desde el archivo .env
load_dotenv()

url_taller = os.getenv('URL_TALLER')
db_taller = os.getenv('DB_TALLER')
username_taller = os.getenv('USERNAME_TALLER')
password_taller = os.getenv('PASSWORD_TALLER')

def get_odoo_connection(url, db, username, password):
  """Establece conexión con el servidor Odoo y devuelve el uid del usuario."""
  common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
  try:
    uid = common.authenticate(db, username, password, {})
    return uid
  except xmlrpc.client.ProtocolError as error:
    print("Error de conexión:", error)
    return None
  
def fetch_order_data(models, db, uid, password, order_id):
    """Recupera los datos del pedido desde Odoo."""
    return models.execute_kw(
        db, uid, password, 'pos.order', 'search_read',
        [[('id', '=', order_id), ('state', 'in', ('paid', 'done', 'invoiced'))]],
        {'order': 'id'}
    )

def fetch_order_lines(models, db, uid, password, order_lines_ids):
    """Recupera las líneas de pedido desde Odoo."""
    return models.execute_kw(
        db, uid, password, 'pos.order.line', 'search_read',
        [[('id', 'in', order_lines_ids)]],
        {'fields': ['product_id', 'qty', 'price_unit']}
    )

def fetch_partner_data(models, db, uid, password, partner_id):
    """Recupera los datos del socio desde Odoo."""
    return models.execute_kw(
        db, uid, password, 'res.partner', 'search_read',
        [[('id', '=', partner_id)]]
    )

def update_partner_loyalty_points(models, db, uid, password, partner_id, new_points):
    """Actualiza los puntos de lealtad del socio en Odoo."""
    models.execute_kw(
        db, uid, password, 'res.partner', 'write',
        [[partner_id], {'loyalty_points': new_points}]
    )
    
# Establece la conexión con Odoo
uid = get_odoo_connection(url_taller, db_taller, username_taller, password_taller)

if uid:
  print("Conexión exitosa con Odoo.")
  # Inicializa el punto final de los modelos.
  models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url_taller))
 
 # Solicitar al usuario que ingrese el número de pedido
  pos_order_id = input("Por favor, ingresa el número de pedido: ")
  pos_orders = fetch_order_data(models, db_taller, uid, password_taller, pos_order_id) # Habria que validar que el cupon este en estado usado?
  if pos_orders:
    pos_order = pos_orders[0]
    amount_total = ((pos_order['amount_total']*12)/100) + pos_order['amount_total']
    print("Monto total del pedido:", amount_total)
    
    order_lines_ids = pos_order['lines']
    productos_in_order = fetch_order_lines(models, db_taller, uid, password_taller, order_lines_ids)
    print("Productos en el pedido:", productos_in_order)
    
    # Inicializa una lista vacía para almacenar los IDs de los productos
    lista_ids_productos = [linea_pedido['product_id'][0] for linea_pedido in productos_in_order]
    # Imprime la lista de IDs de los productos
    print("Lista de IDs de los productos:", lista_ids_productos)
    
    program_coupon_id = pos_order['applied_program_ids'][0]
    program_coupon = models.execute_kw(db_taller, uid, password_taller, 'coupon.program', 'search_read', [[('id', '=', program_coupon_id)]], {'fields': ['name']})
    asigment_coupon = models.execute_kw(db_taller, uid, password_taller, 'coupon.program', 'search_read', [[('id', '=', program_coupon_id)]], {'fields': ['assigned_customer']})
    print("Asignacion de cupon:", asigment_coupon)
    partner_id = asigment_coupon[0]['assigned_customer'][0]
    partner = fetch_partner_data(models, db_taller, uid, password_taller, partner_id)
    balance_points = partner[0]['loyalty_points']
    print("Puntos acumulados:", balance_points)
    
    loyalty_program = models.execute_kw(db_taller, uid, password_taller, 'loyalty.program', 'search_read', [[('name', '=', 'AcumulaYGana')]])
    print("Programa de lealtad:", loyalty_program)
    
    points_won = 0
    rules_id = loyalty_program[0]['rule_ids']
    for rule_id in rules_id:
      rule = models.execute_kw(db_taller, uid, password_taller, 'loyalty.rule', 'search_read', [[('id', '=', rule_id)]])
      # Verifica si los productos guardados anteriormente están dentro de los productos de la regla
      valid_product_ids = rule[0]['valid_product_ids']
      for product_id in lista_ids_productos:
        if product_id in valid_product_ids:
          # Suma los puntos de la regla al total de puntos ganados
          points_won += int(rule[0]['points_currency'] * amount_total)
    print("Puntos ganados:", points_won)
    
    # Actualiza el saldo de puntos del cliente
    balance_points += points_won
    # Redondea el balance de puntos a dos decimales
    balance_points = round(balance_points, 2)
    
    update_partner_loyalty_points(models, db_taller, uid, password_taller, partner_id, balance_points)
    print("Saldo de puntos actualizado:", balance_points)
  else:
    print("No se encontró el pedido.")
else:
    print("No se pudo establecer conexión con Odoo.")