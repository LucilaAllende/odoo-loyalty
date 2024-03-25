import xmlrpc.client
import os
from dotenv import load_dotenv

# Carga las variables de entorno desde el archivo .env
load_dotenv()

url_taller = os.getenv('URL_TALLER')
db_taller = os.getenv('DB_TALLER')
username_taller = os.getenv('USERNAME_TALLER')
password_taller = os.getenv('PASSWORD_TALLER')

# This is to test the connection with odoo server.
common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url_taller))

output = common.version()
print(str("Version: "), output)

# This call tests the credentials and returns the user ID for the next calls.
uid = common.authenticate(db_taller, username_taller, password_taller, {})
print(str("User ID: "), uid)

# Initialize the models endpoint.
models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url_taller))

# Obtener los pedidos no procesados
pos_orders = models.execute_kw(db_taller, uid, password_taller, 'pos.order', 'search_read', [[('partner_id', '=', 'Lucila Tinkin'), ('state', 'in', ('paid', 'done', 'invoiced'))]], {'order': 'id'})
print("Cantidad de pedidos:", len(pos_orders))

pos_order = pos_orders[11]
#print("Pedido:", pos_order)

name_client = pos_order['partner_id'][1]
print("Nombre del cliente:", name_client)
sesion_payment = pos_order['session_id']
print("Sesión de pago:", sesion_payment)
amount_total = pos_order['amount_total']
print("Monto total:", amount_total)
name_shop = pos_order['config_id'][1]
print("Nombre de la tienda:", name_shop)

loyalty_points = pos_order['loyalty_points']
print("Puntos de lealtad:", loyalty_points)

mobile = models.execute_kw(db_taller, uid, password_taller, 'res.partner', 'search_read', [[('id', '=', pos_order['partner_id'][0])]], {'fields': ['mobile']})
print("Teléfono:", mobile[0]['mobile'])

client = models.execute_kw(db_taller, uid, password_taller, 'res.partner', 'search_read', [[('id', '=', pos_order['partner_id'][0])]])
print("Cliente:", client[0]['loyalty_points'])
client_points = client[0]['loyalty_points']

# Obtener los productos del pedido
order_lines = models.execute_kw(db_taller, uid, password_taller, 'pos.order.line', 'search_read', [[('order_id', '=', pos_order['id'])]])
print("Cantidad de productos:", order_lines[2])

""" fields_get = models.execute_kw(db_taller, uid, password_taller, 'pos.order.line', 'fields_get', [])
print("Campos del modelo pos.order.line:")
for field_name, field_props in fields_get.items():
    print("Nombre del campo:", field_name)
    print("Tipo de datos:", field_props['type'])
    print("Descripción:", field_props.get('string', ''))
    print("todo", field_props)
    print() """


# Obtener los puntos gastado y el programa de lealtad
id_product = order_lines[2]['product_id'][0]
product = models.execute_kw(db_taller, uid, password_taller, 'product.template', 'search_read', [[('id', '=', id_product)]])
print("Producto:", product[0])

follower_messages = models.execute_kw(db_taller, uid, password_taller, 'mail.followers', 'search_read', [[('id', '=', 753672)]])
#print("Mensajes seguidos:", follower_messages)

partner_messages = models.execute_kw(db_taller, uid, password_taller, 'mail.message', 'search_read', [[('id', '=', 3)]])
#print("Mensajes del cliente:", partner_messages)

general_messages = models.execute_kw(db_taller, uid, password_taller, 'mail.message', 'search_read', [[('id', '=', 1340814)]])
#print("Mensajes generales:", general_messages)

# Obtener el programa de lealtad
loyalty_program = models.execute_kw(db_taller, uid, password_taller, 'loyalty.program', 'search_read', [[]])
print("Programa de lealtad:", loyalty_program)

# Suponiendo que tienes la variable 'loyalty_program' que contiene la respuesta de tu consulta anterior

# Obtener detalles de las reglas de lealtad asociadas al programa
rule_ids = loyalty_program[0]['rule_ids']
loyalty_rules = models.execute_kw(db_taller, uid, password_taller, 'loyalty.rule', 'read', [rule_ids])

# Obtener detalles de las recompensas de lealtad asociadas al programa
reward_ids = loyalty_program[0]['reward_ids']
loyalty_rewards = models.execute_kw(db_taller, uid, password_taller, 'loyalty.reward', 'read', [reward_ids])

# Ahora puedes trabajar con los detalles de las reglas y recompensas recuperadas
#print("Reglas de lealtad:", loyalty_rules)
print("Recompensas de lealtad:", loyalty_rewards)

points_cost = loyalty_rewards[0]['point_cost']
print("Costo en puntos:", points_cost)

msg = "Hola " + name_client + " le informamos que en su última compra realizada en "+ name_shop +" por $" + str(amount_total) + " sumo "+ str(loyalty_points) + " puntos y gasto "+ str(points_cost) +" puntos. Recuerde que posee un total de " + str(client_points) +" puntos de lealtad disponibles para usar."
print(msg)