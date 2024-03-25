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

  # Ingresar nombre del técnico dueño del cupón
  technician_name = input("Ingrese el nombre del técnico dueño del cupón: ")

  # Buscar el programa de cupón del técnico
  coupon_program_technician = models.execute_kw(db_taller, uid, password_taller, 'coupon.program', 'search_read',
      [[['name', 'ilike','%' + technician_name + '%']]], {'fields': ['id', 'name']})
  
  print("Programa de cupón del técnico:", coupon_program_technician)

  # Agregar el programa de cupón del técnico al punto de venta
  
  # Ingresar nombre del punto de venta
  pos_name = input("Ingrese el nombre del punto de venta: ")
  # Buscar el punto de venta
  pos = models.execute_kw(db_taller, uid, password_taller, 'pos.config', 'search_read',
    [[['name', 'ilike', pos_name]]])
  if pos:
    print("Punto de venta encontrado.", pos)
    if coupon_program_technician:
      print("Programa de cupón del técnico encontrado.")
      # Actualizar el registro
      models.execute_kw(db_taller, uid, password_taller, 'pos.config', 'write', [[pos[0]['id']], {'coupon_program_ids': coupon_program_technician[0]['id']}])
      print("Programa de cupón del técnico agregado al punto de venta.")
  """     else:
        print("Programa de cupón creado.")
        # Actualizar el registro
        models.execute_kw(db_taller, uid, password_taller, 'pos.config', 'write', [[pos[0]['id']], {'coupon_program_ids': program_coupon_created[0]['id']}])
        print("Programa de cupón creado agregado al punto de venta.") """
else:
  print("No se pudo establecer conexión con Odoo.")