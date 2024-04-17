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

# Establece la conexión con Odoo
uid = get_odoo_connection(url_taller, db_taller, username_taller, password_taller)

if uid:
  print("Conexión exitosa con Odoo.")
  # Inicializa el punto final de los modelos.
  models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url_taller))
  order_data = fetch_order_data(models, db_taller, uid, password_taller, 121115)
  print("Datos del pedido:", order_data)
  """   fields_get = models.execute_kw(db_taller, uid, password_taller, 'pos.order', 'fields_get', [])
  print("Campos del modelo pos.order.line:")
  for field_name, field_props in fields_get.items():
      print("Nombre del campo:", field_name)
      print("Tipo de datos:", field_props['type'])
      print("Descripción:", field_props.get('string', ''))
      print("todo", field_props)
      print()"""
else:
  print("Error al conectar con Odoo.")