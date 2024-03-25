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

def buscar_programa_cupon(models, db, uid, password, technician_name):
  """Busca el programa de cupón del técnico por su nombre."""
  return models.execute_kw(db, uid, password, 'coupon.program', 'search_read',
            [[['name', 'ilike', '%' + technician_name + '%']]],{'fields': ['id', 'name']})

def update_programa_cupon(models, db, uid, password, coupon_program_technician, product_code, coupon_validity):
  update_data = {
      'rule_products_domain': '["&",["sale_ok","=",True],["default_code","=","%s"]]' % product_code,
      'validity_duration': coupon_validity,
  }
  models.execute_kw(db, uid, password, 'coupon.program', 'write', [[coupon_program_technician[0]['id']], update_data])
  print("Programa de cupón actualizado.")

def create_programa_cupon(models, db, uid, password, technician_name, product_code, coupon_validity):
  technician = models.execute_kw(db, uid, password, 'res.partner', 'search_read',
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
  program_coupon_created_id = models.execute_kw(db, uid, password, 'coupon.program', 'create', [program_coupon_data])
  print("Programa de cupón creado:", program_coupon_created_id)
  program_coupon_created = models.execute_kw(db_taller, uid, password_taller, 'coupon.program', 'search_read',
      [[['id', '=', program_coupon_created_id]]])

def crear_cupon_referido(models, db, uid, password, coupon_program_id):
    """Crea un cupón de referido asociado al programa de cupón dado."""
    coupon_data = {'program_id': coupon_program_id}
    coupon_created = models.execute_kw(db, uid, password, 'coupon.coupon', 'create', [coupon_data])
    print("Cupón de referido creado:", coupon_created)
    coupon_code = models.execute_kw(db, uid, password, 'coupon.coupon', 'search_read',
                                    [[['id', '=', coupon_created]]], {'fields': ['code']})
    print("Código del cupón:", coupon_code[0]['code'])

def actualizar_punto_venta(models, db, uid, password, pos_name, coupon_program_id):
  """Actualiza el punto de venta con el programa de cupón del técnico."""
  pos = models.execute_kw(db, uid, password, 'pos.config', 'search_read',
                          [[['name', 'ilike', pos_name]]])
  if pos:
      existing_coupon_program_ids = pos[0]['coupon_program_ids']
      existing_coupon_program_ids.append(coupon_program_id)
      models.execute_kw(db, uid, password, 'pos.config', 'write',
                        [[pos[0]['id']], {'coupon_program_ids': [(6, 0, existing_coupon_program_ids)]}])
      print("Programa de cupón del técnico agregado al punto de venta.")
  else:
      print("Punto de venta no encontrado.")

def crear_o_actualizar_programa_cupon(models, db, uid, password, technician_name, product_code, coupon_validity):
  """Crea o actualiza el programa de cupón del técnico."""
  coupon_program_technician = buscar_programa_cupon(models, db, uid, password, technician_name)
  if coupon_program_technician:
    print("Programa de cupón encontrado.")
    update_programa_cupon(models, db, uid, password, coupon_program_technician, product_code, coupon_validity)
  else:
    print("Programa de cupón no encontrado.")
    create_programa_cupon(models, db, uid, password, technician_name, product_code, coupon_validity)

# Establece la conexión con Odoo
uid = get_odoo_connection(url_taller, db_taller, username_taller, password_taller)

if uid:
  print("Conexión exitosa con Odoo.")
  # Inicializa el punto final de los modelos.
  models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url_taller))

  # Ingresar datos para crear cupón de referido
  technician_name = input("Ingrese el nombre del técnico dueño del cupón: ")
  product_code = input("Ingrese el código de refencia interna del producto: ")
  coupon_validity = int(input("Ingrese la cantidad de días de validez del cupón: "))

  crear_o_actualizar_programa_cupon(models, db_taller, uid, password_taller, technician_name, product_code, coupon_validity)
  
  print("Crear cupón de referido")
  coupon_quantity = int(input("Ingrese la cantidad de cupones a generar: "))
  
  coupon_program_technician = buscar_programa_cupon(models, db_taller, uid, password_taller, technician_name)

  if coupon_program_technician:
    print("Programa de cupón del técnico encontrado.")
    coupon_program_id = coupon_program_technician[0]['id']
  else:
    print("Programa de cupón creado.")
    coupon_program_created = models.execute_kw(db_taller, uid, password_taller, 'coupon.program', 'search_read',[[['name', '=', 'Cupon %s' % technician_name]]])
    coupon_program_id = coupon_program_created[0]['id']

  for i in range(coupon_quantity):
    crear_cupon_referido(models, db_taller, uid, password_taller, coupon_program_id)
  
 # Actualizar el punto de venta con el programa de cupón del técnico
  pos_names = input("Ingrese los nombres de los puntos de venta separados por coma: ").split(',')
  for pos_name in pos_names:
    actualizar_punto_venta(models, db_taller, uid, password_taller, pos_name.strip(), coupon_program_id)
else:
  print("No se pudo establecer conexión con Odoo.")