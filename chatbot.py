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
    ['3️⃣ Información para pagos', '4️⃣ Hablar con un asesor'],
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
