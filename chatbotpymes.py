import pyodbc
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from config_db import *


# Conectar a la base de datos SQL Server
def conectar_db():
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={DB_CONFIG['server']};"
        f"DATABASE={DB_CONFIG['database']};"
        f"UID={DB_CONFIG['username']};"
        f"PWD={DB_CONFIG['password']}"
    )
    return pyodbc.connect(conn_str)

conn = conectar_db()
cursor = conn.cursor()

# Estados de la conversación
MENU, CONSULTA_SALDO, ESTATUS_SOLICITUD, ESTADO_CUENTA = range(4)

# Teclado de opciones
reply_keyboard = [
    ['1️⃣ ️Ubicación del consultorio', '2️⃣ ️Servicios disponible'],
    ['3️⃣ Costo de servicios', '4️⃣ Redes sociales o contacto'],
    ['❌ Finalizar']
]

# Función de inicio
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    print("Se inicio una conversación")
    await update.message.reply_text(
        '¡Hola! Soy Montoya_bot asistente virtual de Consultorio Montoya ¿Cómo puedo ayudarte hoy?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return MENU

# Menú de opciones
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    text = text.lower()
    
    if text.startswith('1️⃣') or text.startswith('1') or 'Ubicación' in text or 'Ubicacion' in text:
        print('Se consultó Ubicación - Op 1')
        await update.message.reply_text(
            '📌 Ubicación: \n- C. 4 Sur 502, Chachapa Centro, 72990 Amozoc de Mota, Pue \n- O bien ubicanos en maps:\n- https://maps.app.goo.gl/nUyezczDLVCiuDJU9 \n\n'
        )
        return MENU

    elif text.startswith('2️⃣') or text.startswith('2') or ('servicios' in text and 'costo' not in text):
        print('Se consultó Servicios - Op 2')
        await update.message.reply_text(
            '📋 Servicios:\n- Consulta médica general\n- Consulta pediatríca\n- Aplicación de inyecciones\n- Revisiones médicas\n- Terapias \n- Farmacia'
        )

    elif text.startswith('3️⃣') or text.startswith('3') or 'costo' in text:
        print('Se consultó Costos - Op 3')
        await update.message.reply_text(
            '💳\n -Consulta General: $40 pesos\n -Consulta pediatrica: $60 pesos\n -Aplicación de inyecciones: $25 pesos\n -Terapias: $150 pesos\n Revisiones gratuitas' 
        )
    
    elif text.startswith('4️⃣') or text.startswith('4') or 'contacto' in text or 'numero' in text or 'redes' in text:
        print('Se consultó Contacto - Op 4')
        await update.message.reply_text('👨🏽‍💻 -Puedes marcar al: 2211664671\n -o siguenos en Facebook:\n https://www.facebook.com/dr.montoya2020')
        return MENU
    
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
    cursor.execute("SELECT NumeroCliente, NumeroTarjeta, EstatusTarjeta, SaldoActual, Disponible, PagoMinimo FROM Clientes WHERE NombreCompleto = ?", nombre)
    resultado = cursor.fetchone()

    if resultado:
        await update.message.reply_text(
            f'💳 Cliente: {nombre}\n'
            f'Número de Cliente: {resultado[0]}\n'
            f'Tarjeta: {resultado[1]}\n'
            f'Estatus: {resultado[2]}\n'
            f'Saldo Actual: ${resultado[3]}\n'
            f'Disponible: ${resultado[4]}\n'
            f'Pago Mínimo: ${resultado[5]}'
        )
    else:
        await update.message.reply_text('❌ No encontré información para este nombre.')

    return MENU

# Consultar estatus de solicitud
async def estatus_solicitud(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    nombre = update.message.text
    cursor.execute("SELECT EstatusSolicitud FROM Clientes WHERE NombreCompleto = ?", nombre)
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
    app = ApplicationBuilder().token(TelegramTokenpymes['token']).build()

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
