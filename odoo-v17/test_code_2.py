import xmlrpc.client

import os
from dotenv import load_dotenv

# Carga las variables de entorno desde el archivo .env
load_dotenv()

url = os.getenv('URL')
db = os.getenv('DB')
username = os.getenv('USERNAME')
password = os.getenv('PASSWORD') 

# This is to test the connection with odoo server.
common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))

output = common.version()
print(str("Version: "), output)

# This call tests the credentials and returns the user ID for the next calls.
uid = common.authenticate(db, username, password, {})
print(str("User ID: "), uid)

# Initialize the models endpoint.
models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

# Obtener los pedidos no procesados
pos_orders = models.execute_kw(db, uid, password, 'pos.order', 'search_read', [[('x_studio_esta_procesado_1', '=', False), ('state', 'in', ('paid', 'done', 'invoiced'))]], {'order': 'id'})
print("Cantidad de pedidos:", len(pos_orders))

pos_order = pos_orders[0]
print("Pedido:", pos_order)
name_client = pos_order['partner_id'][1]
print("Nombre del cliente:", name_client)
sesion_payment = pos_order['session_id']
print("Sesión de pago:", sesion_payment)
amount_total = pos_order['amount_total']
print("Monto total:", amount_total)
name_shop = pos_order['config_id'][1]
print("Nombre de la tienda:", name_shop)

mobile = models.execute_kw(db, uid, password, 'res.partner', 'search_read', [[('id', '=', pos_order['partner_id'][0])]], {'fields': ['mobile']})
print("Teléfono:", mobile[0]['mobile'])
# Obtener los productos del pedido
order_lines = models.execute_kw(db, uid, password, 'pos.order.line', 'search_read', [[('order_id', '=', pos_order['id'])]])
print("Cantidad de productos:", order_lines)

# Obtener los puntos gastado y el programa de lealtad
points_cost = order_lines[2]['points_cost']
print("Costo en puntos:", points_cost)
reward_identifier_code = order_lines[2]['reward_identifier_code']
print("Código de identificación de la recompensa:", reward_identifier_code)
reward_id = order_lines[2]['reward_id']
print("ID de la recompensa:", reward_id)
price_unit = order_lines[2]['price_unit']
print("Precio unitario:", price_unit)
product_id = order_lines[2]['product_id']
print("ID del producto:", product_id)


# Obtener el programa de lealtad
loyalty_program = models.execute_kw(db, uid, password, 'loyalty.program', 'search_read', [[('id', '=', reward_id[0])]])
print("Programa de lealtad:", len(loyalty_program))

# Obtener el cupón
coupon_ids = loyalty_program[0]['coupon_ids']

coupon = models.execute_kw(db, uid, password, 'loyalty.card', 'search_read', [[('partner_id', '=', pos_order['partner_id'][0])]])
print("Cupón:", coupon[0]['id'])
balance_points = coupon[0]['points']
print("Puntos de lealtad:", balance_points)

message_ids = coupon[0]['message_ids']
print("Mensajes:", message_ids)
for message_id in message_ids:
    message = models.execute_kw(db, uid, password, 'mail.message', 'search_read', [[('id', '=', message_id)]])
    if message[0]['tracking_value_ids']:
        for tracking_value in message[0]['tracking_value_ids']:
            tracking_value_for_order = models.execute_kw(db, uid, password, 'mail.tracking.value', 'search_read', [[('id', '=', tracking_value), ('new_value_float', '=', balance_points )]])
            if tracking_value_for_order:
                points_old = tracking_value_for_order[0]['old_value_float']
                print("Puntos anteriores:", points_old)
                
msg = "Hola " + name_client + " le informamos que en su última compra por $" + str(amount_total) + " sumo "+ str(balance_points-points_old) + " puntos para un total de "+ str(balance_points) +" puntos de lealtad."
print(msg)