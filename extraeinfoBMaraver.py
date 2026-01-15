import pandas as pd
from datetime import datetime
 
# Cargar archivo de movimientos
archivo_movimientos = "Asignar/Movimientos MID Ene Jul 2024.xlsx"
df_movimientos = pd.read_excel(archivo_movimientos)
 
# Cargar lotes disponibles
lotes = pd.read_excel("Asignar/Consolidado Lotes Nadro-Fanasa-Marzam.xlsx")
lotes['fecha'] = pd.to_datetime(lotes['fecha'], format='%Y-%m-%d')
lotes = lotes.to_dict("records")
 
# Ordenar lotes por fecha
lotes = sorted(lotes, key=lambda x: x["fecha"])
 
# Filtrar solo movimientos que "reducen" inventario
df_movimientos = df_movimientos[df_movimientos["Reduce"] > 0].copy()
 
# Convertir fecha del movimiento
df_movimientos["Fecha"] = pd.to_datetime(df_movimientos["Fecha"], errors='coerce', dayfirst=True)
df_movimientos = df_movimientos.sort_values(by="Fecha")
 
# Agregar columnas de asignación
df_movimientos["Lote Asignado"] = ""
df_movimientos["Cantidad Asignada"] = 0
df_movimientos["Fecha de Caducidad"] = ""
 
# Asignación de lotes
for index, movimiento in df_movimientos.iterrows():
    producto = movimiento["Código de Producto"]
    cantidad_requerida = movimiento["Reduce"]
    fecha_movimiento = movimiento["Fecha"]
   
    for lote in lotes:
        if lote["codigo"] == producto and lote["cantidad"] > 0 and fecha_movimiento >= lote["fecha"]:
            cantidad_a_asignar = min(cantidad_requerida, lote["cantidad"])
            df_movimientos.at[index, "Lote Asignado"] = lote["lote"]
            df_movimientos.at[index, "Fecha de Caducidad"] = lote["caducidad"]
            df_movimientos.at[index, "Cantidad Asignada"] = cantidad_a_asignar
            lote["cantidad"] -= cantidad_a_asignar
            cantidad_requerida -= cantidad_a_asignar
            if cantidad_requerida == 0:
                break
 
# Guardar el archivo con asignaciones
df_movimientos.to_excel("Asignar/movimientos_MID_lotes_asignados.xlsx", index=False)
 
print("Lotes asignados para movimientos y guardados en el archivo.")