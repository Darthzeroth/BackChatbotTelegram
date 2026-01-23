import pyodbc
import random
import requests
import logging
from datetime import datetime, timedelta
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from telegram.request import HTTPXRequest
from config_db import *

# ============================================================================
# CONFIGURACIÓN
# ============================================================================
TIEMPO_LIMITE_MINUTOS = 3  # 3 Minutos exactos desde el inicio

# Configuración de LOG
logging.basicConfig(
    filename='historial_usuarios.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# ============================================================================
# CLASE SOFMEX SMS
# ============================================================================
class SofmexSMS:
    def __init__(self, token):
        self.token = token
        self.base_url = "https://sofmex.com/api/sms/v3/asignacion"
    
    def enviar_sms(self, numero, mensaje):
        if not self.token: return {"status": -1, "message": "Token no configurado"}
        try:
            headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json", "accept": "application/json"}
            payload = {"registros": [{"telefono": str(numero), "mensaje": mensaje}]}
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=20)
            if response.status_code in [200, 201]: return {"status": 0, "message": "Enviado exitosamente"}
            else: return {"status": response.status_code, "message": response.text}
        except Exception as e:
            print(f"❌ Error SMS: {str(e)}")
            return {"status": -1, "message": str(e)}

sms_client = SofmexSMS(token=SofmexConfig['token'])

# ============================================================================
# GESTIÓN DE BASE DE DATOS
# ============================================================================
def get_db_connection():
    try:
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={DB_CONFIG_PakarPruebas['server']};"
            f"DATABASE={DB_CONFIG_PakarPruebas['database']};"
            f"UID={DB_CONFIG_PakarPruebas['username']};"
            f"PWD={DB_CONFIG_PakarPruebas['password']}"
        )
        return pyodbc.connect(conn_str)
    except Exception as e:
        print(f"❌ Error conectando a BD: {e}")
        return None

# ============================================================================
# ESTADOS
# ============================================================================
(MENU, VERIFICAR_NOMBRE, SOLICITAR_FECHA, VERIFICAR_CODIGO) = range(4)

reply_keyboard = [
    ['1️⃣ Beneficios', '2️⃣ Documentos requeridos'],
    ['3️⃣ Información para pagos', '4️⃣ Hablar con un asesor'],
    ['5️⃣ Consultar saldo', '6️⃣ Estado de cuenta'],
    ['7️⃣ Incremento de crédito', '8️⃣ Estatus de solicitud'],
    ['❌ Finalizar']
]

# ============================================================================
# SISTEMA DE LOGS Y CONTROL DE TIEMPO
# ============================================================================

def log_evento(user, accion):
    try:
        nombre = user.first_name or "Desconocido"
        user_id = user.id
        mensaje = f"ID: {user_id} | Usuario: {nombre} | Acción: {accion}"
        print(f"📝 {mensaje}")
        logging.info(mensaje)
    except Exception as e:
        print(f"Error logging: {e}")

async def verificar_expiracion(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    Retorna True si la sesión YA expiró.
    Si expiró, notifica al usuario, limpia datos y loguea el cierre.
    """
    hora_inicio = context.user_data.get('hora_inicio')
    
    # Si no hay hora de inicio, es una sesión fantasma (expirada o reiniciada)
    if not hora_inicio:
        return True 
    
    tiempo_transcurrido = datetime.now() - hora_inicio
    
    if tiempo_transcurrido >= timedelta(minutes=TIEMPO_LIMITE_MINUTOS):
        # ❌ TIEMPO AGOTADO
        log_evento(update.effective_user, "SESIÓN EXPIRADA (Hard Stop)")
        context.user_data.clear() # Borrado total
        
        await update.message.reply_text(
            "⏳ **Tu sesión ha expirado por inactividad.**\n"
            "Por seguridad hemos cerrado tu sesión.\n"
            "Escribe 'Hola' para comenzar de nuevo.",
            reply_markup=ReplyKeyboardRemove()
        )
        return True # Expiró
    
    return False # Sigue viva

# ============================================================================
# FLUJO PRINCIPAL
# ============================================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """INICIO: Único lugar donde se crea el reloj"""
    
    # 1. Limpieza total
    context.user_data.clear()
    
    # 2. Iniciar Cronómetro
    context.user_data['hora_inicio'] = datetime.now()
    
    log_evento(update.effective_user, "INICIO DE CHAT (Nueva Sesión)")
    
    await update.message.reply_text(
        f'Hola {update.effective_user.first_name}, soy tu asistente de Realmente Más. ¿En qué puedo ayudarte hoy?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return MENU

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # 🛑 1. VALIDACIÓN ESTRICTA DE TIEMPO
    if await verificar_expiracion(update, context):
        return ConversationHandler.END # Cortamos flujo aquí

    text = update.message.text.lower()
    user = update.effective_user
    
    # --- Opciones Públicas ---
    if any(x in text for x in ['1️⃣', 'beneficios']):
        log_evento(user, "Consulta Beneficios")
        await update.message.reply_text('📌 Beneficios: \n- Aumenta tus ventas\n- Ahorras tiempo\n- Historial crediticio sano\n\n')
        return MENU
    elif any(x in text for x in ['2️⃣', 'documentos']):
        log_evento(user, "Consulta Documentos")
        await update.message.reply_text('📋 Requisitos:\n- Mayor de edad\n- Socio PAKAR\n- Identificación oficial\n- Comprobante de domicilio\n- 4 referencias personales')
        await update.message.reply_photo(
        photo=open('requisitos.jpg', 'rb')
        )
        return MENU
    elif any(x in text for x in ['3️⃣', 'pagos']):
        log_evento(user, "Consulta Pagos")
        await update.message.reply_text('💳 Puedes realizar tus pagos a la cuenta: XXXX-XXXX-XXXX en BBVA. Enviar comprobante al WhatsApp 2228500632.')
        return MENU
    elif any(x in text for x in ['4️⃣', 'asesor']):
        log_evento(user, "Solicita Asesor")
        await update.message.reply_text('👨🏽‍💻 Un asesor se pondrá en contacto contigo muy pronto.')
        return MENU
    
    # --- Opciones Privadas ---
    mop = 0
    if any(x in text for x in ['5️⃣', 'saldo']): mop = 5
    elif any(x in text for x in ['6️⃣', 'estado']): mop = 6
    elif any(x in text for x in ['7️⃣', 'incremento']): mop = 7
    elif any(x in text for x in ['8️⃣', 'estatus']): mop = 8
    
    if mop > 0:
        context.user_data['mop'] = mop
        
        # Validar si ya pasó por el SMS (Autenticado)
        if context.user_data.get('autenticado') is True:
            await update.message.reply_text("🔓 Sesión activa. Procesando...")
            return await ejecutar_operacion_final(update, context)
        else:
            await update.message.reply_text('🔒 Para ver esta información necesito validar tu identidad.\nIngresa tu nombre completo:')
            return VERIFICAR_NOMBRE

    elif any(x in text for x in ['❌', 'finalizar']):
        log_evento(user, "CIERRE MANUAL")
        context.user_data.clear()
        await update.message.reply_text('✅ Sesión cerrada. ¡Hasta luego!', reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    else:
        await update.message.reply_text(
            'Opción no válida. Selecciona una opción del menú:',
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
        )
        return MENU

async def verificar_nombre(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # 🛑 VALIDACIÓN ESTRICTA
    if await verificar_expiracion(update, context): return ConversationHandler.END

    nombre_input = update.message.text.strip()
    context.user_data['nombre_busqueda'] = nombre_input
    
    conn = get_db_connection()
    if not conn:
        await update.message.reply_text("Error de conexión.")
        return MENU
    
    try:
        cursor = conn.cursor()
        sql_nombre = "LTRIM(RTRIM(ISNULL(nombre, '') + ' ' + ISNULL(apellido_paterno, '') + ' ' + ISNULL(apellido_materno, '')))"
        
        cursor.execute(f"SELECT COUNT(*) FROM [rmm].[dbo].[dato] WHERE {sql_nombre} LIKE ?", (f'%{nombre_input}%',))
        row_count = cursor.fetchone()
        count = int(row_count[0]) if row_count else 0
            
        if count == 0:
            await update.message.reply_text('❌ No encontré ese nombre. Intenta de nuevo:', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
            conn.close()
            return MENU
        
        elif count == 1:
            cursor.execute(f"SELECT telefono_celular, {sql_nombre} FROM [rmm].[dbo].[dato] WHERE {sql_nombre} LIKE ?", (f'%{nombre_input}%',))
            row = cursor.fetchone()
            context.user_data['telefono'] = row[0]
            context.user_data['nombre_final'] = row[1]
            conn.close()
            return await enviar_codigo_verificacion(update, context)
        
        else:
            conn.close()
            await update.message.reply_text('⚠️ Hay homónimos. Ingresa tu fecha de nacimiento (dd/mm/aaaa):')
            return SOLICITAR_FECHA
            
    except Exception as e:
        print(f"Error BD: {e}")
        if conn: conn.close()
        await update.message.reply_text("Error consultando datos.")
        return MENU

async def solicitar_fecha(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # 🛑 VALIDACIÓN ESTRICTA
    if await verificar_expiracion(update, context): return ConversationHandler.END

    fecha_txt = update.message.text.strip()
    nombre_input = context.user_data.get('nombre_busqueda')
    
    conn = get_db_connection()
    if not conn: return MENU

    try:
        cursor = conn.cursor()
        fecha_obj = datetime.strptime(fecha_txt, '%d/%m/%Y').date()
        sql_nombre = "LTRIM(RTRIM(ISNULL(nombre, '') + ' ' + ISNULL(apellido_paterno, '') + ' ' + ISNULL(apellido_materno, '')))"
        
        query = f'''
            SELECT telefono_celular, {sql_nombre}
            FROM [rmm].[dbo].[dato] 
            WHERE {sql_nombre} LIKE ? AND fecha_nacimiento = ?
        '''
        cursor.execute(query, (f'%{nombre_input}%', fecha_obj))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            context.user_data['telefono'] = row[0]
            context.user_data['nombre_final'] = row[1]
            return await enviar_codigo_verificacion(update, context)
        else:
            await update.message.reply_text('❌ Datos no coinciden.')
            return MENU
    except ValueError:
        if conn: conn.close()
        await update.message.reply_text('Formato incorrecto. Usa dd/mm/aaaa')
        return SOLICITAR_FECHA

async def enviar_codigo_verificacion(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # 🛑 VALIDACIÓN ESTRICTA
    if await verificar_expiracion(update, context): return ConversationHandler.END

    raw_telefono = str(context.user_data.get('telefono', ''))
    solo_numeros = ''.join(filter(str.isdigit, raw_telefono))
    
    if len(solo_numeros) < 10:
        await update.message.reply_text(f"⚠️ El celular registrado no es válido.")
        return MENU

    telefono_final = f"52{solo_numeros[-10:]}"
    codigo = random.randint(100000, 999999)
    context.user_data['codigo_verificacion'] = str(codigo)
    context.user_data['intentos'] = 0
    
    log_evento(update.effective_user, f"Enviando SMS con el codigo {codigo} a terminación {telefono_final[-4:]}")
    #telefono_final = f"522226757385"
    #resultado = sms_client.enviar_sms(telefono_final, f"Tu codigo RM es: {codigo}")
    resultado = {}
    resultado['status'] = 0
    if resultado['status'] == 0:
        await update.message.reply_text(f'🔒 Código enviado al ****{telefono_final[-4:]}. Ingrésalo:')
        return VERIFICAR_CODIGO
    else:
        await update.message.reply_text(f"⚠️ Error enviando SMS.")
        return MENU

async def verificar_codigo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # 🛑 VALIDACIÓN ESTRICTA
    if await verificar_expiracion(update, context): return ConversationHandler.END

    if update.message.text.strip() == context.user_data.get('codigo_verificacion'):
        
        # ✅ SMS CORRECTO: Marcamos autenticación pero NO reiniciamos el reloj
        context.user_data['autenticado'] = True
        log_evento(update.effective_user, "AUTENTICACIÓN EXITOSA")
        
        await update.message.reply_text(f"✅ Acceso concedido.")
        return await ejecutar_operacion_final(update, context)
    else:
        context.user_data['intentos'] += 1
        log_evento(update.effective_user, f"Fallo código intento {context.user_data['intentos']}")
        
        if context.user_data['intentos'] >= 3:
            await update.message.reply_text('❌ Demasiados intentos.')
            return MENU
        await update.message.reply_text('❌ Código incorrecto. Intenta de nuevo:')
        return VERIFICAR_CODIGO

async def ejecutar_operacion_final(update, context):
    # 🛑 VALIDACIÓN ESTRICTA (Incluso al final, por si tardó en llegar)
    if await verificar_expiracion(update, context): return ConversationHandler.END

    mop = context.user_data.get('mop')
    nombre_final = context.user_data.get('nombre_final')
    user = update.effective_user
    
    if mop == 5:
        log_evento(user, "Vio Saldo")
        await mostrar_saldo(update, context, nombre_final)
    elif mop == 6:
        log_evento(user, "Vio Edo Cuenta")
        await mostrar_estado_cuenta(update, context)
        await update.message.reply_document(
           document=open('estadocuenta.pdf', 'rb'),
           filename='estadocuenta.pdf',
           caption='📄 ¡Aquí tienes tu estado de cuenta!' 
        )
    elif mop == 7:
        log_evento(user, "Solicitó Incremento")
        await update.message.reply_text(f"👨🏽‍💻 {nombre_final}, solicitud enviada.")
    elif mop == 8:
        log_evento(user, "Vio Estatus Solicitud")
        await mostrar_estatus_solicitud(update, context, nombre_final)
        
    await update.message.reply_text('¿Algo más?', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True))
    return MENU

# ============================================================================
# FUNCIONES FINANCIERAS
# ============================================================================
async def mostrar_saldo(update, context, nombre_cliente):
    conn = get_db_connection()
    if not conn: return
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT credito_actual, saldo FROM [rmm].[dbo].[cliente] WHERE nombre = ?', (nombre_cliente,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            limite = float(row[0]) if row[0] else 0.0
            saldo = float(row[1]) if row[1] else 0.0
            await update.message.reply_text(
                f'💰 **TU SALDO**\nLínea: ${limite:,.2f}\nDisponible: ${limite-saldo:,.2f}\nDeuda: ${saldo:,.2f}'
            )
        else:
            await update.message.reply_text(f"⚠️ No hay datos financieros para: '{nombre_cliente}'.")
    except Exception as e:
        if conn: conn.close()
        print(f"Error Saldo: {e}")
        await update.message.reply_text("Error consultando saldo.")

async def mostrar_estatus_solicitud(update, context, nombre_cliente):
    conn = get_db_connection()
    if not conn: return
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT id_solicitud FROM [rmm].[dbo].[cliente] WHERE nombre = ?', (nombre_cliente,))
        row = cursor.fetchone()
        conn.close()
        estatus = row[0] if row and row[0] else "Sin solicitud activa"
        await update.message.reply_text(f'📄 ID Solicitud: {estatus}')
    except:
        if conn: conn.close()
        await update.message.reply_text("No se encontró información.")

async def mostrar_estado_cuenta(update, context):
    await update.message.reply_text("📄 Estado de cuenta simulado.")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    log_evento(update.effective_user, "CANCELACIÓN COMANDO")
    context.user_data.clear()
    await update.message.reply_text('Cancelado.', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# ============================================================================
# MAIN
# ============================================================================
if __name__ == '__main__':
    request = HTTPXRequest(connection_pool_size=20, read_timeout=30.0, write_timeout=30.0, connect_timeout=30.0)
    app = ApplicationBuilder().token(TelegramToken['token']).request(request).build()
    
    app.bot.delete_webhook(drop_pending_updates=True)

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
            # Detecta CUALQUIER texto inicial para arrancar el bot
            MessageHandler(filters.TEXT & ~filters.COMMAND, start) 
        ],
        states={
            MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, menu)],
            VERIFICAR_NOMBRE: [MessageHandler(filters.TEXT & ~filters.COMMAND, verificar_nombre)],
            SOLICITAR_FECHA: [MessageHandler(filters.TEXT & ~filters.COMMAND, solicitar_fecha)],
            VERIFICAR_CODIGO: [MessageHandler(filters.TEXT & ~filters.COMMAND, verificar_codigo)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    app.add_handler(conv_handler)
    print('✅ Bot iniciado (Validación estricta de 3 min). Presiona Ctrl+C para detener.')
    app.run_polling(allowed_updates=Update.ALL_TYPES)