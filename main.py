import os
import logging
from flask import Flask, render_template
from threading import Thread
import bot
from models import create_tables

# Configure logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key")

@app.route('/')
def home():
    """Render the home page"""
    return render_template('index.html')

# Estado del bot
bot_running = False

@app.route('/start-bot')
def start_bot():
    """Iniciar el bot manualmente desde la web"""
    global bot_running
    if not bot_running:
        logger.info("Iniciando el bot desde la interfaz web")
        bot_thread = Thread(target=bot.run_bot)
        bot_thread.daemon = True
        bot_thread.start()
        bot_running = True
        return "Bot iniciado correctamente"
    return "El bot ya está en ejecución"

@app.route('/status')
def status():
    """Check the status of the bot"""
    global bot_running
    return {"status": "running" if bot_running else "stopped"}

# Asegurarse de que las tablas de la base de datos estén creadas
create_tables()

# Iniciar el bot automáticamente al arrancar la aplicación si hay token
if os.environ.get("BOT_TOKEN") and not bot_running:
    logger.info("Iniciando el bot automáticamente")
    bot_thread = Thread(target=bot.run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    bot_running = True

# Aplicación para gunicorn
app.logger.info("Aplicación web lista")
