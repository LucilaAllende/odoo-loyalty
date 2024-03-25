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
  # Ingresar codigo de producto por consola
  #product_code = input("Ingrese el código del producto: ")

  coupon_data = {
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

  """   algo = models.execute_kw(db_taller, uid, password_taller, 'coupon.program', 'create', [coupon_data])
    print("Cupon creado:", algo) """
  """   # Obtener los IDs de los cupones
    # Obtener la estructura del modelo 'coupon.program'
    coupon_fields = models.execute_kw(db_taller, uid, password_taller, 'coupon.program', 'fields_get', [], {})

    # Obtener los nombres de los campos
    all_fields = list(coupon_fields.keys())

    # Eliminar 'valid_partner_ids' de la lista de campos
    if 'valid_partner_ids' in all_fields:
        all_fields.remove('valid_partner_ids')

    # Obtener los datos del cupón excluyendo 'valid_partner_ids'
    coupons = models.execute_kw(db_taller, uid, password_taller, 'coupon.program', 'read', [[83,94]], {'fields': all_fields})

    # Imprimir los detalles de cada cupón
    for coupon in coupons:
        print("Detalle del cupón:", coupon) """
  
  """   result = models.execute_kw(db_taller, uid, password_taller, 'coupon.program', 'generate_coupon', [94])
    print("Cupón generado:", result) """

else:
  print("No se pudo establecer conexión con Odoo.")