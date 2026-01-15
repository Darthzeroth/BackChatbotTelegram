import pyodbc
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from config_db import *


# Conectar a la base de datos SQL Server
def conectar_db():
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={DB_CONFIG_PakarPruebas['server']};"
        f"DATABASE={DB_CONFIG_PakarPruebas['database']};"
        f"UID={DB_CONFIG_PakarPruebas['username']};"
        f"PWD={DB_CONFIG_PakarPruebas['password']}"
    )
    return pyodbc.connect(conn_str)

conn = conectar_db()
cursor = conn.cursor()

# Estados de la conversación
MENU, CONSULTA_SALDO, ESTATUS_SOLICITUD, ESTADO_CUENTA = range(4)

# Teclado de opciones
reply_keyboard = [
    ['1️⃣ Beneficios', '2️⃣ Documentos requeridos'],
    ['3️⃣ Información para pagos', '4️⃣ Hablar coimport pyodbc
import random
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from config_db import *
import requests

# ============================================================================
# CLASE SOFMEX SMS
# ============================================================================
class SofmexSMS:
    """Cliente para enviar SMS usando la API de Sofmex"""
    
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.token = None
        self.base_url = "https://sofmex.com/api"
    
    def obtener_token(self):
        """Obtiene el token de autenticación desde la API"""
        try:
            url = f"{self.base_url}/login"
            payload = {"username": self.username, "password": self.password}
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 0:
                    self.token = data.get('token')
                    print(f"✅ Token Sofmex obtenido")
                    return self.token
            return None
        except Exception as e:
            print(f"❌ Error obteniendo token: {str(e)}")
            return None
    
    def enviar_sms(self, numero, mensaje):
        """Envía un SMS a un número específico"""
        if not self.token:
            if not self.obtener_token():
                return {"status": -1, "message": "No se pudo obtener el token"}
        
        try:
            url = f"{self.base_url}/sms/v2/send"
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            payload = {"messages": [{"number": numero, "message": mensaje}]}
            
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 0:
                    print(f"✅ SMS enviado a {numero}")
                return data
            return {"status": -1, "message": f"Error HTTP {response.status_code}"}
        except Exception as e:
            print(f"❌ Error enviando SMS: {str(e)}")
            return {"status": -1, "message": str(e)}

# ============================================================================
# INICIALIZAR SERVICIOS
# ============================================================================

# Conectar a la base de datos SQL Server
def conectar_db():
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={DB_CONFIG_PakarPruebas['server']};"
        f"DATABASE={DB_CONFIG_PakarPruebas['database']};"
        f"UID={DB_CONFIG_PakarPruebas['username']};"
        f"PWD={DB_CONFIG_PakarPruebas['password']}"
    )
    return pyodbc.connect(conn_str)

conn = conectar_db()
cursor = conn.cursor()

# Inicializar cliente SMS Sofmex
# IMPORTANTE: Reemplaza con tus credenciales reales
sms_client = SofmexSMS(
    username=SofmexConfig['username'],  # Agregar en config_db.py
    password=SofmexConfig['password']   # Agregar en config_db.py
)

# ============================================================================
# ESTADOS Y CONFIGURACIÓN
# ============================================================================

# Estados de la conversación
(MENU, CONSULTA_SALDO, ESTATUS_SOLICITUD, ESTADO_CUENTA, 
 VERIFICAR_NOMBRE, SOLICITAR_FECHA, VERIFICAR_CODIGO) = range(7)

# Teclado de opciones
reply_keyboard = [
    ['1️⃣ Beneficios', '2️⃣ Documentos requeridos'],
    ['3️⃣ Información para pagos', '4️⃣ Hablar con un asesor'],
    ['5️⃣ Consultar saldo', '6️⃣ Estado de cuenta'],
    ['7️⃣ Incremento de crédito', '8️⃣ Estatus de solicitud'],
    ['❌ Finalizar']
]

# ============================================================================
# FUNCIONES DEL BOT
# ============================================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    print("Se inició una conversación")
    context.user_data.clear()
    
    await update.message.reply_text(
        'Hola, soy tu asistente de Realmente Más. ¿En qué puedo ayudarte hoy?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return MENU

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.lower()
    
    if text.startswith('1️⃣') or text.startswith('1') or 'beneficios' in text:
        print('Se consultaron Beneficios - Op 1')
        await update.message.reply_text(
            '📌 Beneficios: \n- Aumenta tus ventas\n- Ahorras tiempo\n- Historial crediticio sano\n\n'
        )
        return MENU

    elif text.startswith('2️⃣') or text.startswith('2') or 'requeridos' in text or 'documentos' in text:
        print('Se consultó Documentos Requeridos - Op 2')
        await update.message.reply_text(
            '📋 Requisitos:\n- Mayor de edad\n- Socio PAKAR\n- Identificación oficial\n- Comprobante de domicilio\n- 4 referencias personales'
        )
        try:
            await update.message.reply_photo(photo=open('requisitos.jpg', 'rb'))
        except:
            print("No se pudo enviar la imagen requisitos.jpg")
        return MENU
    
    elif text.startswith('3️⃣') or text.startswith('3') or 'información' in text or 'pagos' in text:
        print('Se consultó Información de Pagos - Op 3')
        await update.message.reply_text('💳 Puedes realizar tus pagos a la cuenta: XXXX-XXXX-XXXX en BBVA. Enviar comprobante al WhatsApp 2228500632.')
        return MENU
    
    elif text.startswith('4️⃣') or text.startswith('4') or 'ayuda' in text or 'asesor' in text or 'hablar' in text:
        print('Se consultó Hablar con Asesor - Op 4')
        await update.message.reply_text('👨🏽‍💻 Un asesor se pondrá en contacto contigo muy pronto.')
        return MENU
    
    elif text.startswith('5️⃣') or text.startswith('5') or 'consultar saldo' in text or 'saldo' in text:
        print('Se consultó saldo - Op 5')
        context.user_data['mop'] = 5
        await update.message.reply_text('Por favor, ingresa tu nombre completo')
        return VERIFICAR_NOMBRE
    
    elif text.startswith('6️⃣') or text.startswith('6') or 'estado' in text or 'cuenta' in text:
        print('Se consultó Estado de cuenta - Op 6')
        context.user_data['mop'] = 6
        await update.message.reply_text('Por favor, ingresa tu nombre completo')
        return VERIFICAR_NOMBRE
        
    elif text.startswith('7️⃣') or text.startswith('7') or 'incremento' in text:
        print('Se consultó Incremento Crédito - Op 7')
        context.user_data['mop'] = 7
        await update.message.reply_text('Por favor, ingresa tu nombre completo')
        return VERIFICAR_NOMBRE
    
    elif text.startswith('8️⃣') or text.startswith('8') or 'estatus' in text:
        print('Se consultó Estatus de solicitud - Op 8')
        context.user_data['mop'] = 8
        await update.message.reply_text('Por favor, ingresa tu nombre completo')
        return VERIFICAR_NOMBRE

    elif text.startswith('❌') or text.startswith('0') or 'finalizar' in text or 'acabar' in text or 'terminar' in text or 'adios' in text or 'bye' in text:
        print('Se Finalizó - Op 0')
        await update.message.reply_text(
            '✅ Conversación finalizada. ¡Gracias por contactarnos!',
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

    else:
        await update.message.reply_text(
            'Disculpa, no comprendo. Por favor selecciona una opción del menú.',
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
        )
        return MENU

async def verificar_nombre(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    nombre = update.message.text
    context.user_data['nombre'] = nombre
    
    # Buscar cuántos clientes tienen ese nombre
    cursor.execute('''
        SELECT COUNT(*) 
        FROM rmm.dbo.cliente 
        WHERE nombre LIKE ?
    ''', (f'%{nombre}%',))
    
    count = cursor.fetchone()[0]
    
    if count == 0:
        await update.message.reply_text(
            '❌ No encontré información para este nombre.',
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
        )
        return MENU
    
    elif count == 1:
        # Si solo hay una persona, obtener su información
        cursor.execute('''
            SELECT c.id_cliente, c.telefono, c.fecha_nacimiento
            FROM rmm.dbo.cliente AS c
            WHERE c.nombre LIKE ?
        ''', (f'%{nombre}%',))
        
        resultado = cursor.fetchone()
        context.user_data['id_cliente'] = resultado[0]
        context.user_data['telefono'] = resultado[1]
        
        # Generar y enviar código de verificación
        return await enviar_codigo_verificacion(update, context)
    
    else:
        # Hay más de una persona con ese nombre
        await update.message.reply_text(
            'Por favor, ingresa tu fecha de nacimiento\n'
            'Formato: dd/mm/aaaa\n'
            'Ejemplo: 23/03/1991'
        )
        return SOLICITAR_FECHA

async def solicitar_fecha(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    fecha_texto = update.message.text
    nombre = context.user_data.get('nombre', '')
    
    try:
        # Validar formato de fecha
        fecha = datetime.strptime(fecha_texto, '%d/%m/%Y')
        
        # Buscar cliente con nombre y fecha de nacimiento
        cursor.execute('''
            SELECT c.id_cliente, c.telefono
            FROM rmm.dbo.cliente AS c
            WHERE c.nombre LIKE ? AND c.fecha_nacimiento = ?
        ''', (f'%{nombre}%', fecha.date()))
        
        resultado = cursor.fetchone()
        
        if resultado:
            context.user_data['id_cliente'] = resultado[0]
            context.user_data['telefono'] = resultado[1]
            
            # Generar y enviar código de verificación
            return await enviar_codigo_verificacion(update, context)
        else:
            await update.message.reply_text(
                '❌ La información que proporcionas no es correcta.',
                reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
            )
            return MENU
            
    except ValueError:
        await update.message.reply_text(
            'Formato de fecha incorrecto. Por favor ingresa la fecha en formato dd/mm/aaaa\n'
            'Ejemplo: 23/03/1991'
        )
        return SOLICITAR_FECHA

async def enviar_codigo_verificacion(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Generar código de 6 dígitos
    codigo = random.randint(100000, 999999)
    context.user_data['codigo_verificacion'] = codigo
    context.user_data['intentos'] = 0
    
    telefono = context.user_data.get('telefono', '')
    
    # Enviar SMS con Sofmex
    mensaje = f"Tu código de verificación de Realmente Más es: {codigo}"
    resultado = sms_client.enviar_sms(telefono, mensaje)
    
    if resultado.get('status') == 0:
        await update.message.reply_text(
            f'Por seguridad te envié un código al número de teléfono registrado terminación ****{str(telefono)[-4:] if telefono else "XXXX"}, ingrésalo:'
        )
        print(f"✅ Código {codigo} enviado a {telefono}")
    else:
        # Si falla el envío, informar al usuario pero continuar (para desarrollo)
        await update.message.reply_text(
            f'⚠️ Hubo un problema al enviar el SMS. Para continuar, ingresa el código: {codigo}\n'
            f'(Este mensaje es solo para pruebas)'
        )
        print(f"⚠️ No se pudo enviar SMS. Código: {codigo}")
    
    return VERIFICAR_CODIGO

async def verificar_codigo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    codigo_ingresado = update.message.text.strip()
    codigo_correcto = str(context.user_data.get('codigo_verificacion', ''))
    intentos = context.user_data.get('intentos', 0)
    
    if codigo_ingresado == codigo_correcto:
        # Código correcto, procesar según mop
        mop = context.user_data.get('mop', 0)
        
        if mop == 5:  # Consultar saldo
            return await mostrar_saldo(update, context)
        elif mop == 6:  # Estado de cuenta
            return await mostrar_estado_cuenta(update, context)
        elif mop == 7:  # Incremento de crédito
            return await solicitar_incremento(update, context)
        elif mop == 8:  # Estatus de solicitud
            return await mostrar_estatus_solicitud(update, context)
    else:
        intentos += 1
        context.user_data['intentos'] = intentos
        
        if intentos >= 3:
            await update.message.reply_text(
                '❌ Total de intentos excedido. Por favor, contacta a un asesor.',
                reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
            )
            return MENU
        else:
            await update.message.reply_text(
                f'❌ Código incorrecto. Intenta nuevamente. ({intentos}/3 intentos)'
            )
            return VERIFICAR_CODIGO

async def mostrar_saldo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    id_cliente = context.user_data.get('id_cliente')
    
    cursor.execute('''
        SELECT TOP(1) 
            c.nombre AS nombre_cliente, 
            c.id_cliente AS num_cliente, 
            t.folio AS tarjeta_cliente,
            CASE 
                WHEN t.cancelada = 0 THEN 'Tarjeta Activa'
                ELSE 'Cancelada'
            END AS estado_tarjeta,
            c.credito_actual AS saldo_actual,
            (c.credito_actual - c.saldo) AS saldo_disponible,
            c.saldo AS saldo_pagar
        FROM rmm.dbo.cliente AS c
        INNER JOIN rmm.dbo.tarjeta AS t ON t.id_cliente = c.id_cliente 
        WHERE c.id_cliente = ?
        ORDER BY t.fecha_activacion DESC
    ''', (id_cliente,))

    resultado = cursor.fetchone()

    if resultado:
        await update.message.reply_text(
            f'💳 Cliente: {resultado[0]}\n'
            f'Número de Cliente: {resultado[1]}\n'
            f'Tarjeta: {resultado[2]}\n'
            f'Estatus: {resultado[3]}\n'
            f'Saldo Actual: ${resultado[4]:.2f}\n'
            f'Disponible: ${resultado[5]:.2f}\n'
            f'Pago Mínimo: ${resultado[6]:.2f}',
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
        )
    else:
        await update.message.reply_text(
            '❌ No se pudo obtener la información.',
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
        )

    return MENU

async def mostrar_estado_cuenta(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        await update.message.reply_document(
            document=open('estadocuenta.pdf', 'rb'),
            filename='estadocuenta.pdf',
            caption='📄 Te comparto tu estado de cuenta.'
        )
    except:
        await update.message.reply_text('❌ No se pudo obtener el estado de cuenta.')
    
    await update.message.reply_text(
        '¿En qué más puedo ayudarte?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return MENU

async def solicitar_incremento(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        'Tu solicitud de incremento de crédito será canalizada con un asesor. 👨🏽‍💻',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return MENU

async def mostrar_estatus_solicitud(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    id_cliente = context.user_data.get('id_cliente')
    
    cursor.execute("""
        SELECT 
            es.nombre,
            c.id_cliente,
            t.folio,
            c.credito_actual,
            (c.credito_actual - c.saldo) AS disponible,
            c.saldo
        FROM rmm.dbo.cliente as c 
        LEFT JOIN rmm.dbo.solicitud as s on s.id_solicitud = c.id_solicitud
        LEFT JOIN rmm.dbo.estatus_solicitud as es on es.id_estatus_solicitud = s.id_estatus_solicitud
        LEFT JOIN rmm.dbo.tarjeta as t on t.id_cliente = c.id_cliente
        WHERE c.id_cliente = ?
    """, (id_cliente,))
    
    resultado = cursor.fetchone()

    if resultado:
        await update.message.reply_text(
            f'📋 Estatus Solicitud: {resultado[0]}\n'
            f'Número de Cliente: {resultado[1]}\n'
            f'Tarjeta: {resultado[2]}\n'
            f'Saldo Actual: ${resultado[3]:.2f}\n'
            f'Disponible: ${resultado[4]:.2f}\n'
            f'Pago Mínimo: ${resultado[5]:.2f}',
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
        )
    else:
        await update.message.reply_text(
            '❌ No encontré información.',
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
        )

    return MENU

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        '✅ Conversación finalizada. Escribe /start o "hola" para comenzar de nuevo.',
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

# ============================================================================
# INICIAR APLICACIÓN
# ============================================================================

if __name__ == '__main__':
    app = ApplicationBuilder().token(TelegramToken['token']).build()

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
            MessageHandler(filters.Regex('(?i).*\\b(hola|iniciar|buenos días|buenas tardes|buenas)\\b.*'), start)
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

    print('✅ Bot is polling...')
    app.run_polling()n un asesor'],
    ['5️⃣ Consultar saldo', '6️⃣ Estado de cuenta'],
    ['7️⃣ Incremento de crédito', '8️⃣ Estatus de solicitud'],
    ['❌ Finalizar']
]

# Función de inicio
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    print("Se inicio una conversación")
    await update.message.reply_text(
        'Hola, soy tu asistente de Realmente Más. ¿En qué puedo ayudarte hoy?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return MENU

# Menú de opciones
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    text = text.lower()
    
    if text.startswith('1️⃣') or text.startswith('1') or 'beneficios' in text:
        print('Se consultaron Beneficios - Op 1')
        await update.message.reply_text(
            '📌 Beneficios: \n- Aumenta tus ventas\n- Ahorras tiempo\n- Historial crediticio sano\n\n'
        )
        return MENU


    elif text.startswith('2️⃣') or text.startswith('2') or 'requeridos' in text or 'documentos' in text:
        print('Se consultó Documentos Requeridos - Op 2')
        await update.message.reply_text(
            '📋 Requisitos:\n- Mayor de edad\n- Socio PAKAR\n- Identificación oficial\n- Comprobante de domicilio\n- 4 referencias personales'
        )
        await update.message.reply_photo(
        photo=open('requisitos.jpg', 'rb')
        #,caption='¡Aquí tienes tu estado de cuenta!.'
        )
        return MENU
    
    elif text.startswith('3️⃣') or text.startswith('3') or 'información' in text or 'pagos' in text:
        print('Se consultó Información de Pagos - Op 3')
        await update.message.reply_text('💳 Puedes realizar tus pagos a la cuenta: XXXX-XXXX-XXXX en BBVA. Enviar comprobante al WhatsApp 2228500632.')
        return MENU
    
    elif text.startswith('4️⃣') or text.startswith('4') or 'ayuda' in text or 'asesor' in text or 'hablar' in text:
        print('Se consultó Hablar con Asesor - Op 4')
        await update.message.reply_text('👨🏽‍💻 Un asesor se pondrá en contacto contigo muy pronto.')
        return MENU
    
    elif text.startswith('5️⃣') or text.startswith('5') or 'consultar saldo' in text or 'saldo' in text:
        print('Se consultó saldo - Op 5')
        await update.message.reply_text('Por favor, envíame tu nombre completo para consultar tu saldo.')
        return CONSULTA_SALDO
    
    elif text.startswith('6️⃣') or text.startswith('6') or 'estado' in text or 'cuenta' in text or 'estado de cuenta' in text:
        print('Se consultó Estado de cuenta - Op 6')
        await update.message.reply_document(
           document=open('estadocuenta.pdf', 'rb'),
           filename='estadocuenta.pdf',
           caption='📄 ¡Aquí tienes tu estado de cuenta!' 
        )
        #return ESTADO_CUENTA
        return MENU
        
    elif text.startswith('5️⃣') or text.startswith('7') or 'incremento' in text:
        print('Se consultó Incremento Crédito - Op 7')
        await update.message.reply_text('Tu solicitud de incremento de crédito será canalizada con un asesor. 👨🏽‍💻')
        return MENU
    
    elif text.startswith('5️8️⃣') or text.startswith('8') or 'estatus' in text or 'estatus de solicitud' in text:
        print('Se consultó Estatus de solicitud - Op 8')
        await update.message.reply_text('Por favor, envíame tu nombre completo para consultar el estatus de tu solicitud.')
        return ESTATUS_SOLICITUD

    elif text.startswith('❌') or text.startswith('0') or text.find('fin') or 'finalizar' in text or 'acabar' in text or 'terminar' in text or 'adios' in text or 'bye' in text:
        print('Se Finalizó - Op 0')
        await update.message.reply_text('✅ Conversación finalizada. ¡Gracias por contactarnos!')
        return ConversationHandler.END

    else:
        await update.message.reply_text('Por favor selecciona una opción válida.')
        return MENU

# Consultar saldo
async def consultar_saldo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    nombre = update.message.text

    cursor.execute('''
        SELECT TOP(1) 
            c.nombre AS nombre_cliente, 
            c.id_cliente AS num_cliente, 
            t.folio AS tarjeta_cliente,
            CASE 
                WHEN t.cancelada = 0 THEN 'Tarjeta Activa'
                ELSE 'Cancelada'
            END AS estado_tarjeta,
            c.credito_actual AS saldo_actual,
            (c.credito_actual - c.saldo) AS saldo_disponible,
            c.saldo AS saldo_pagar,
            CASE 
                WHEN c.credito_actual >= c.saldo THEN 'OK'
                ELSE 'Saldo insuficiente'
            END AS estado_saldo
        FROM rmm.dbo.cliente AS c
        INNER JOIN rmm.dbo.tarjeta AS t ON t.id_cliente = c.id_cliente 
        WHERE c.nombre LIKE ? 
        ORDER BY t.fecha_activacion DESC
    ''', (f'%{nombre}%',))

    resultado = cursor.fetchone()

    if resultado:
        await update.message.reply_text(
            f'💳 Cliente: {resultado[0]}\n'
            f'Número de Cliente: {resultado[1]}\n'
            f'Tarjeta: {resultado[2]}\n'
            f'Estatus: {resultado[3]}\n'
            f'Saldo Actual: ${resultado[4]}\n'
            f'Disponible: ${resultado[5]}\n'
            f'Pago Mínimo: ${resultado[6]}'
        )
    else:
        await update.message.reply_text('❌ No encontré información para este nombre.')

    return MENU

# Consultar estatus de solicitud
async def estatus_solicitud(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    nombre = update.message.text
    cursor.execute("""
        SELECT es.nombre
        FROM [rmm].[dbo].[cliente] as c 
        inner join solicitud as s on s.id_solicitud = c.id_solicitud
        inner join estatus_solicitud as es on es.id_estatus_solicitud = s.id_estatus_solicitud 
        where c.nombre like ?
                   """, (f'%{nombre}%',))
    resultado = cursor.fetchone()

    if resultado:
        await update.message.reply_text(f'📝 El estatus de tu solicitud es: {resultado[0]}')
    else:
        await update.message.reply_text('❌ No encontré información para este nombre.')

    return MENU

async def estado_cuenta(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    nombre = update.message.text
    cursor.execute("SELECT EstatusSolicitud FROM Clientes WHERE NombreCompleto = ?", nombre)
    resultado = cursor.fetchone()

    if resultado:
        await update.message.reply_text(f'📝 El estatus de tu solicitud es: {resultado[0]}')
    else:
        await update.message.reply_text('❌ No encontré información para este nombre.')

    return MENU

# Finalizar conversación
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('✅ Conversación finalizada. Escribe /start o "hola" para comenzar de nuevo.')
    return ConversationHandler.END

# Iniciar la aplicación
if __name__ == '__main__':
    app = ApplicationBuilder().token(TelegramToken['token']).build()

    # Conversación completa
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
            MessageHandler(filters.Regex('(?i).*\\b(hola|iniciar|buenos días|buenas tardes|buenas)\\b.*'), start)
        ],
        states={
            MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, menu)],
            CONSULTA_SALDO: [MessageHandler(filters.TEXT & ~filters.COMMAND, consultar_saldo)],
            ESTATUS_SOLICITUD: [MessageHandler(filters.TEXT & ~filters.COMMAND, estatus_solicitud)],
            ESTADO_CUENTA: [MessageHandler(filters.TEXT & ~filters.COMMAND, estado_cuenta)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    app.add_handler(conv_handler)

    print('✅ Bot is polling...')
    app.run_polling()
