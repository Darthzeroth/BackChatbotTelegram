import pyodbc
import random
import requests
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from telegram.request import HTTPXRequest
from config_db import *

# ============================================================================
# CLASE SOFMEX SMS (ADAPTADA A TU CURL v3)
# ============================================================================
class SofmexSMS:
    def __init__(self, token):
        self.token = token
        # URL confirmada por tu CURL
        self.base_url = "https://sofmex.com/api/sms/v3/asignacion"
    
    def enviar_sms(self, numero, mensaje):
        if not self.token:
            print("❌ Error: Token Sofmex vacío.")
            return {"status": -1, "message": "Token no configurado"}
        
        try:
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
                "accept": "application/json"
            }
            
            # ESTRUCTURA EXACTA DEL CURL
            payload = {
                "registros": [
                    {
                        "telefono": str(numero),  # El API acepta texto o número
                        "mensaje": mensaje
                    }
                ]
            }

            print(f"DEBUG: Enviando a {self.base_url}")
            print(f"DEBUG PAYLOAD: {payload}")
            
            # Timeout de 20s
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=20)
            
            # Debug de respuesta
            print(f"DEBUG RESPONSE CODE: {response.status_code}")
            print(f"DEBUG RESPONSE BODY: {response.text}")

            if response.status_code in [200, 201]:
                data = response.json()
                # Ajustamos la validación de éxito según lo que devuelva v3
                # A veces devuelve data['status'] == 1 o 'success': true
                return {"status": 0, "message": "Enviado exitosamente"}
            else:
                return {"status": response.status_code, "message": response.text}
                
        except Exception as e:
            print(f"❌ Excepción SMS: {str(e)}")
            return {"status": -1, "message": str(e)}

# ============================================================================
# CONEXIÓN BASE DE DATOS
# ============================================================================
def conectar_db():
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

conn = conectar_db()
cursor = conn.cursor() if conn else None
sms_client = SofmexSMS(token=SofmexConfig['token'])

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
# LÓGICA DEL CHATBOT
# ============================================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text(
        f'Hola, soy tu asistente de Realmente Más. ¿En qué puedo ayudarte hoy?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return MENU

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.lower()
    
    if any(x in text for x in ['1️⃣', 'beneficios']):
        await update.message.reply_text('📌 Beneficios:\n- Aumenta tus ventas\n- Ahorras tiempo')
        return MENU
    elif any(x in text for x in ['2️⃣', 'documentos']):
        await update.message.reply_text('📋 Requisitos:\n- INE\n- Comp. Domicilio\n- 4 referencias')
        return MENU
    elif any(x in text for x in ['3️⃣', 'pagos']):
        await update.message.reply_text('💳 Cuenta BBVA: XXXX-XXXX-XXXX.')
        return MENU
    elif any(x in text for x in ['4️⃣', 'asesor']):
        await update.message.reply_text('👨🏽‍💻 Un asesor te contactará pronto.')
        return MENU
    elif any(x in text for x in ['5️⃣', 'saldo']):
        context.user_data['mop'] = 5
        await update.message.reply_text('Ingresa tu nombre completo:')
        return VERIFICAR_NOMBRE
    elif any(x in text for x in ['6️⃣', 'estado']):
        context.user_data['mop'] = 6
        await update.message.reply_text('Ingresa tu nombre completo:')
        return VERIFICAR_NOMBRE
    elif any(x in text for x in ['7️⃣', 'incremento']):
        context.user_data['mop'] = 7
        await update.message.reply_text('Ingresa tu nombre completo:')
        return VERIFICAR_NOMBRE
    elif any(x in text for x in ['8️⃣', 'estatus']):
        context.user_data['mop'] = 8
        await update.message.reply_text('Ingresa tu nombre completo:')
        return VERIFICAR_NOMBRE
    elif any(x in text for x in ['❌', 'finalizar']):
        await update.message.reply_text('✅ Adiós.', reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    else:
        await update.message.reply_text('Opción no válida.', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
        return MENU

async def verificar_nombre(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    nombre_input = update.message.text.strip()
    context.user_data['nombre_busqueda'] = nombre_input
    
    try:
        # Concatenación de nombre completo
        sql_nombre = "(ISNULL(nombre, '') + ' ' + ISNULL(apellido_paterno, '') + ' ' + ISNULL(apellido_materno, ''))"
        
        # 1. Contar (Manejo robusto de respuesta SQL)
        cursor.execute(f"SELECT COUNT(*) FROM [rmm].[dbo].[dato] WHERE {sql_nombre} LIKE ?", (f'%{nombre_input}%',))
        row_count = cursor.fetchone()
        
        if isinstance(row_count, (tuple, list, pyodbc.Row)):
            count = row_count[0]
        else:
            count = int(row_count)
            
        if count == 0:
            await update.message.reply_text('❌ No encontré ese nombre. Intenta de nuevo:', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
            return MENU
        
        elif count == 1:
            # Caso único
            cursor.execute(f"SELECT socio, telefono_celular FROM [rmm].[dbo].[dato] WHERE {sql_nombre} LIKE ?", (f'%{nombre_input}%',))
            row = cursor.fetchone()
            
            context.user_data['id_cliente'] = row[0]
            context.user_data['telefono'] = row[1]
            return await enviar_codigo_verificacion(update, context)
        
        else:
            # Homónimos
            await update.message.reply_text('⚠️ Hay homónimos. Ingresa tu fecha de nacimiento (dd/mm/aaaa):')
            return SOLICITAR_FECHA
            
    except Exception as e:
        print(f"❌ Error SQL: {e}")
        await update.message.reply_text("Error de sistema.")
        return MENU

async def solicitar_fecha(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    fecha_txt = update.message.text.strip()
    nombre_input = context.user_data.get('nombre_busqueda')
    
    try:
        fecha_obj = datetime.strptime(fecha_txt, '%d/%m/%Y').date()
        sql_nombre = "(ISNULL(nombre, '') + ' ' + ISNULL(apellido_paterno, '') + ' ' + ISNULL(apellido_materno, ''))"
        
        cursor.execute(f'''
            SELECT socio, telefono_celular 
            FROM [rmm].[dbo].[dato] 
            WHERE {sql_nombre} LIKE ? AND fecha_nacimiento = ?
        ''', (f'%{nombre_input}%', fecha_obj))
        
        row = cursor.fetchone()
        if row:
            context.user_data['id_cliente'] = row[0]
            context.user_data['telefono'] = row[1]
            return await enviar_codigo_verificacion(update, context)
        else:
            await update.message.reply_text('❌ Datos no coinciden.')
            return MENU
    except ValueError:
        await update.message.reply_text('Formato inválido. Usa dd/mm/aaaa')
        return SOLICITAR_FECHA

async def enviar_codigo_verificacion(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    raw_telefono = str(context.user_data.get('telefono', ''))
    
    # 1. Limpiar (dejar solo números)
    solo_numeros = ''.join(filter(str.isdigit, raw_telefono))
    
    # 2. Validar longitud mínima
    if len(solo_numeros) < 10:
        await update.message.reply_text(f"❌ El teléfono registrado ({raw_telefono}) no es válido.")
        return MENU

    # 3. Formatear: 52 + últimos 10 dígitos
    diez_digitos = solo_numeros[-10:]
    telefono_final = f"52{diez_digitos}"
    print("Cambiamos de: ")
    print(telefono_final)
    print("a: ")
    telefono_final = 522211664671
    print(telefono_final)
    # Generar código
    codigo = random.randint(100000, 999999)
    context.user_data['codigo_verificacion'] = str(codigo)
    context.user_data['intentos'] = 0
    
    print(f"DEBUG: Enviando código {codigo} a {telefono_final}")
   
    # ENVIAR
    resultado = sms_client.enviar_sms(telefono_final, f"Tu codigo RM es: {codigo}")
    
    # Si el resultado es éxito (status 0) o si Sofmex devuelve algo aceptable
    # NOTA: Ajustar validación según lo que imprimas en consola del response body
    if resultado['status'] == 0 or resultado.get('code') == 200:
        mask_phone = diez_digitos[-4:]
        await update.message.reply_text(f'🔒 Código enviado al ****{mask_phone}. Ingrésalo:')
        return VERIFICAR_CODIGO
    else:
        # Fallo
        msg_error = resultado.get('message', 'Error desconocido')
        await update.message.reply_text(f"⚠️ Error enviando SMS: {msg_error}")
        return MENU

async def verificar_codigo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text.strip() == context.user_data.get('codigo_verificacion'):
        mop = context.user_data.get('mop')
        if mop == 5: await mostrar_saldo(update, context)
        elif mop == 6: await update.message.reply_text("📄 Estado de cuenta simulado.")
        elif mop == 7: await update.message.reply_text("👨🏽‍💻 Solicitud enviada.")
        elif mop == 8: await update.message.reply_text("📄 Sin solicitud activa.")
        
        await update.message.reply_text('¿Algo más?', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
        return MENU
    else:
        context.user_data['intentos'] += 1
        if context.user_data['intentos'] >= 3:
            await update.message.reply_text('❌ Demasiados intentos.')
            return MENU
        await update.message.reply_text('❌ Código incorrecto. Intenta de nuevo:')
        return VERIFICAR_CODIGO

async def mostrar_saldo(update, context):
    try:
        # Ajustar a tu tabla real
        cursor.execute('SELECT TOP(1) credito_actual, saldo FROM rmm.dbo.cliente WHERE id_cliente = ?', (context.user_data['id_cliente'],))
        row = cursor.fetchone()
        if row:
            await update.message.reply_text(f'💰 Saldo: ${row[1]:.2f}')
        else:
            await update.message.reply_text("No hay datos financieros.")
    except Exception as e:
        print(f"Error Saldo: {e}")
        await update.message.reply_text("Error consultando saldo.")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Cancelado.', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# ============================================================================
# MAIN
# ============================================================================
if __name__ == '__main__':
    request = HTTPXRequest(connection_pool_size=10, read_timeout=30.0, write_timeout=30.0, connect_timeout=30.0)
    app = ApplicationBuilder().token(TelegramToken['token']).request(request).build()
    
    print("🧹 Limpiando webhooks...")
    app.bot.delete_webhook(drop_pending_updates=True)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start), MessageHandler(filters.Regex('(?i)^(hola|inicio)$'), start)],
        states={
            MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, menu)],
            VERIFICAR_NOMBRE: [MessageHandler(filters.TEXT & ~filters.COMMAND, verificar_nombre)],
            SOLICITAR_FECHA: [MessageHandler(filters.TEXT & ~filters.COMMAND, solicitar_fecha)],
            VERIFICAR_CODIGO: [MessageHandler(filters.TEXT & ~filters.COMMAND, verificar_codigo)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    app.add_handler(conv_handler)
    print('✅ Bot iniciado (Versión Final CURL). Presiona Ctrl+C para detener.')
    app.run_polling(allowed_updates=Update.ALL_TYPES)