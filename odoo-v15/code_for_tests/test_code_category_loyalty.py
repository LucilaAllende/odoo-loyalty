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
  
# Establece la conexión con Odoo
uid = get_odoo_connection(url_taller, db_taller, username_taller, password_taller)

if uid:
  print("Conexión exitosa con Odoo.")
  # Inicializa el punto final de los modelos.
  models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url_taller))

  # Obtener usuario en base al id
  catgory_user = models.execute_kw(db_taller, uid, password_taller, 'res.partner', 'search_read', [[('id', '=', 44632)]],{'fields': ['category_id']})
  print("catgory_user:", catgory_user[0])

  	
  catgory_id = models.execute_kw(db_taller, uid, password_taller, 'res.partner.category', 'search_read', [[]],)
  print("catgory_id:", catgory_id[0]['id'])

  # Escribir la categoria obtenida en el usuario
  write_category = models.execute_kw(db_taller, uid, password_taller, 'res.partner', 'write', [[44632], {'category_id': catgory_id[0]['id']}])

else:
  print("No se pudo establecer conexión con Odoo.")