import os
import logging
from flask import Flask, render_template
from threading import Thread
import bot

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

def run_flask():
    """Run the Flask app on a separate thread"""
    app.run(host='0.0.0.0', port=5000)

if __name__ == "__main__":
    # Start the Flask server in a separate thread
    logger.info("Starting Flask server")
    server_thread = Thread(target=run_flask)
    server_thread.daemon = True
    server_thread.start()
    
    # Start the bot
    logger.info("Starting Telegram bot")
    bot.run_bot()
