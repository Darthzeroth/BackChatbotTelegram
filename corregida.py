import pandas as pd
from collections import defaultdict
from tqdm import tqdm
import time

inicio = time.time()

# Rutas de archivos (ajusta si usas Google Drive)
archivo_movimientos = "/content/Movimientos MID Ene Jul 2024.xlsx"
archivo_lotes = "/content/Consolidado Lotes Nadro-Fanasa-Marzam.xlsx"

# Leer archivo de movimientos
print("Leyendo archivo de movimientos...")
df_movimientos = pd.read_excel(archivo_movimientos, engine='openpyxl')
print("Archivo de movimientos cargado.")

# Cargar lotes disponibles
print("Cargando archivo de lotes...")
lotes_df = pd.read_excel(archivo_lotes, engine='openpyxl')
lotes_df['fecha'] = pd.to_datetime(lotes_df['fecha'], format='%Y-%m-%d', errors='coerce')

# Agrupar lotes por código de producto y ordenarlos por fecha
print("Agrupando y ordenando lotes por producto...")
lotes_por_producto = defaultdict(list)
for row in tqdm(lotes_df.itertuples(index=False), desc="Procesando lotes"):
    lotes_por_producto[row.codigo].append({
        'lote': row.lote,
        'fecha': row.fecha,
        'caducidad': row.caducidad,
        'cantidad': row.cantidad
    })

for codigo in lotes_por_producto:
    lotes_por_producto[codigo].sort(key=lambda x: x['fecha'])

# Filtrar solo movimientos que reducen inventario
print("Filtrando movimientos que reducen inventario...")
df_movimientos = df_movimientos[df_movimientos["Reduce"] > 0].copy()

# Convertir fecha del movimiento
df_movimientos["Fecha"] = pd.to_datetime(df_movimientos["Fecha"], errors='coerce', dayfirst=True)
df_movimientos = df_movimientos.sort_values(by="Fecha")

# Agregar columnas de asignación
df_movimientos["Lote Asignado"] = ""
df_movimientos["Cantidad Asignada"] = 0
df_movimientos["Fecha de Caducidad"] = ""

# Asignación de lotes con tqdm
print("Iniciando asignación de lotes...")
for movimiento in tqdm(df_movimientos.itertuples(index=True), total=len(df_movimientos), desc="Asignando lotes"):
    producto = movimiento.Código_de_Producto
    cantidad_requerida = movimiento.Reduce
    fecha_movimiento = movimiento.Fecha
    index = movimiento.Index

    if producto in lotes_por_producto:
        for lote in lotes_por_producto[producto]:
            if lote["cantidad"] > 0 and fecha_movimiento >= lote["fecha"]:
                cantidad_a_asignar = min(cantidad_requerida, lote["cantidad"])
                df_movimientos.at[index, "Lote Asignado"] = lote["lote"]
                df_movimientos.at[index, "Fecha de Caducidad"] = lote["caducidad"]
                df_movimientos.at[index, "Cantidad Asignada"] = cantidad_a_asignar
                lote["cantidad"] -= cantidad_a_asignar
                cantidad_requerida -= cantidad_a_asignar
                if cantidad_requerida == 0:
                    break

# Guardar el archivo con asignaciones
df_movimientos.to_excel("/content/movimientos_MID_lotes_asignados.xlsx", index=False)

fin = time.time()
print(f"\n✅ Lotes asignados y archivo guardado. Tiempo total: {round(fin - inicio, 2)} segundos.")
