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

  # Ingresar cantidad de cupones a generar
  coupon_quantity = int(input("Ingrese la cantidad de cupones a generar: "))

  # Ingresar cantidad de días de validez del cupón
  coupon_validity = int(input("Ingrese la cantidad de días de validez del cupón: "))

  # Buscar el programa de cupón del técnico
  """   coupon_program_technician = models.execute_kw(db_taller, uid, password_taller, 'coupon.program', 'search_read',
      [[83]], {'fields': ['id', 'name']})
    
    print("Programa de cupón del técnico:", coupon_program_technician) """

  # Obtener la estructura del modelo 'coupon.program'
  coupon_fields = models.execute_kw(db_taller, uid, password_taller, 'coupon.program', 'fields_get', [], {})

  # Obtener los nombres de los campos
  all_fields = list(coupon_fields.keys())

  # Eliminar 'valid_partner_ids' de la lista de campos
  if 'valid_partner_ids' in all_fields:
      all_fields.remove('valid_partner_ids')

  # Obtener los datos del cupón excluyendo 'valid_partner_ids'
  coupons = models.execute_kw(db_taller, uid, password_taller, 'coupon.program', 'read', [[83]], {'fields': all_fields})

  # Imprimir los detalles de cada cupón
  for coupon in coupons:
      print("Detalle del programa cupón:", coupon)

  """  if coupon_program_technician:
      print("Programa de cupón encontrado.")
    else:
      print("Programa de cupón no encontrado.") """
  """ program_coupon_data = {
          'name': 'Cupon Prueba',  
          'rule_products_domain': '["&",["sale_ok","=",True],["default_code","=","1004"]]',
          'rule_min_quantity': 1,
          'rule_minimum_amount': 1,
          'rule_minimum_amount_tax_inclusion': 'tax_excluded',
          'coupon_type': 'referred',
          'assigned_customer': 44603,
          'reward_type': 'discount',
          'discount_line_product_id': 4757,
          'validity_duration': 3, # Siempre en días
          'discount_type': 'percentage',
          'discount_percentage': 10,
          'discount_apply_on': 'on_order',
          'active': True,
          'program_type': 'coupon_program',
        }

        program_coupon_created = models.execute_kw(db_taller, uid, password_taller, 'coupon.program', 'create', [program_coupon_data])
        print("Programa de cupón creado:", program_coupon_created) """
  
  """   # Obtener los IDs de los cupones
    # Obtener la estructura del modelo 'coupon.program'
    coupon_fields = models.execute_kw(db_taller, uid, password_taller, 'coupon.program', 'fields_get', [], {})

    # Obtener los nombres de los campos
    all_fields = list(coupon_fields.keys())

    # Eliminar 'valid_partner_ids' de la lista de campos
    if 'valid_partner_ids' in all_fields:
        all_fields.remove('valid_partner_ids')

    # Obtener los datos del cupón excluyendo 'valid_partner_ids'
    coupons = models.execute_kw(db_taller, uid, password_taller, 'coupon.program', 'read', [[83]], {'fields': all_fields})

    # Imprimir los detalles de cada cupón
    for coupon in coupons:
        print("Detalle del programa cupón:", coupon) """
  
  """   result = models.execute_kw(db_taller, uid, password_taller, 'coupon.program', 'generate_coupon', [94])
    print("Cupón generado:", result) """
  
  """   coupon_fields = models.execute_kw(db_taller, uid, password_taller, 'coupon.coupon', 'fields_get', [], {})

    # Obtener los nombres de los campos
    all_fields = list(coupon_fields.keys())

    # Imprimir los nombres de los campos
    #print("Campos del modelo 'coupon.coupon':", all_fields)

    coupon = models.execute_kw(db_taller, uid, password_taller, 'coupon.coupon', 'read', [[6]], {'fields': all_fields})

    print("Detalle del cupón:", coupon)

    coupon_data = {
      'program_id': 83,
    }

    coupon_id = models.execute_kw(db_taller, uid, password_taller, 'coupon.coupon', 'create', [coupon_data])
    print("Cupón creado:", coupon_id) """

else:
  print("No se pudo establecer conexión con Odoo.")