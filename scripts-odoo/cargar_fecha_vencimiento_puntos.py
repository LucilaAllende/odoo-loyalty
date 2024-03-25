# Obtener la fecha actual
fecha_actual = datetime.date.today()

# Calcular la fecha de vencimiento sumando 6 meses manualmente
meses = fecha_actual.month + 6
año = fecha_actual.year + meses // 12
mes = meses % 12

# Si el mes calculado es 0, establecerlo como 12
if mes == 0:
    mes = 12
    año -= 1

# Crear la fecha de vencimiento
fecha_vencimiento = datetime.date(año, mes, fecha_actual.day)

# Verificar si el campo x_studio_vencimiento ya tiene un valor
if not record.x_studio_vencimiento:
    # Si no tiene un valor, asignar la nueva fecha
    record.write({'x_studio_vencimiento': fecha_vencimiento})
    log('Se actualizó el campo x_studio_vencimiento a la fecha de vencimiento', level='info')
else:
    log('El campo x_studio_vencimiento ya tiene un valor establecido', level='info')