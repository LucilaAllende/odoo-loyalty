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

  print("Generar cupón referido")

  # Ingresar nombre del técnico dueño del cupón
  technician_name = input("Ingrese el nombre del técnico dueño del cupón: ")

  # Ingresar codigo de producto por consola
  product_code = input("Ingrese el código de refencia interna del producto: ")

  # Ingresar cantidad de días de validez del cupón
  coupon_validity = int(input("Ingrese la cantidad de días de validez del cupón: "))

  # Buscar el programa de cupón del técnico
  coupon_program_technician = models.execute_kw(db_taller, uid, password_taller, 'coupon.program', 'search_read',
      [[['name', 'ilike','%' + technician_name + '%']]], {'fields': ['id', 'name']})
  
  print("Programa de cupón del técnico:", coupon_program_technician)

  if coupon_program_technician:
    print("Programa de cupón encontrado.")
    # Datos a actualizar
    update_data = {
      'rule_products_domain': '["&",["sale_ok","=",True],["default_code","=","%s"]]' % product_code,
      'validity_duration': coupon_validity,
    }

    # Actualizar el registro
    models.execute_kw(db_taller, uid, password_taller, 'coupon.program', 'write', [[coupon_program_technician[0]['id']], update_data])
    print("Programa de cupón actualizado.")
  else:
    # Buscar al técnico por nombre
    technician = models.execute_kw(db_taller, uid, password_taller, 'res.partner', 'search_read',
      [[['name', 'ilike', technician_name]]])
    program_coupon_data = {
      'name': 'Cupon %s' % technician_name,  
      'rule_products_domain': '["&",["sale_ok","=",True],["default_code","=","%s"]]' % product_code,
      'rule_min_quantity': 1,
      'rule_minimum_amount': 1,
      'rule_minimum_amount_tax_inclusion': 'tax_excluded',
      'coupon_type': 'referred',
      'assigned_customer': technician[0]['id'],
      'reward_type': 'discount',
      'discount_line_product_id': 4757,
      'validity_duration': coupon_validity,
      'discount_type': 'percentage',
      'discount_percentage': 10,
      'discount_apply_on': 'on_order',
      'active': True,
      'program_type': 'coupon_program',
    }

    program_coupon_created_id = models.execute_kw(db_taller, uid, password_taller, 'coupon.program', 'create', [program_coupon_data])
    print("Programa de cupón creado:", program_coupon_created_id)
    program_coupon_created = models.execute_kw(db_taller, uid, password_taller, 'coupon.program', 'search_read',
      [[['id', '=', program_coupon_created_id]]])

  print("Crear cupon de referido")
  # Ingresar cantidad de cupones a generar
  coupon_quantity = int(input("Ingrese la cantidad de cupones a generar: "))
  # Crear cupones de referido
  for i in range(coupon_quantity):
    if coupon_program_technician:
      print("Programa de cupón del técnico encontrado.", coupon_program_technician[0]['id'])
      coupon_data = {
        'program_id': coupon_program_technician[0]['id'],
      }
    else:
      print("Programa de cupón creado.", program_coupon_created[0]['id'])
      coupon_data = {
        'program_id': program_coupon_created[0]['id'],
      }
    coupon_created = models.execute_kw(db_taller, uid, password_taller, 'coupon.coupon', 'create', [coupon_data])
    print("Cupón de referido creado:", coupon_created)
    coupon_code = models.execute_kw(db_taller, uid, password_taller, 'coupon.coupon', 'search_read',
      [[['id', '=', coupon_created]]], {'fields': ['code']})
    print("Código del cupón:", coupon_code[0]['code'])
else:
  print("No se pudo establecer conexión con Odoo.")