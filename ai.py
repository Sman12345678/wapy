import logging
import threading
import time
from datetime import datetime
from wapy import get_unread_msgs, send_msg, is_authenticated, main

# Set up logging with emojis
class EmojiFormatter(logging.Formatter):
    EMOJI_MAP = {
        'DEBUG': '🔍',
        'INFO': '✨',
        'WARNING': '⚠️',
        'ERROR': '❌',
        'CRITICAL': '🚨'
    }

    def format(self, record):
        record.levelname = f"{self.EMOJI_MAP.get(record.levelname, '')} {record.levelname}"
        return super().format(record)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setFormatter(EmojiFormatter('%(asctime)s [%(levelname)s] %(message)s'))
logger.handlers = [handler]

class AIAutoReplyBot(threading.Thread):
    def __init__(self, driver, check_interval=5):
        super().__init__()
        self.driver = driver
        self.check_interval = check_interval
        self.running = True
        self._lock = threading.Lock()
        self.processed_msgs = set()
        
        self.reply_rules = {
            'greeting': {
                'patterns': ['hello', 'hi', 'hey', 'good morning', 'good afternoon'],
                'response': 'Hello! 👋 This is an automated response. How can I help you today?'
            },
            'help': {
                'patterns': ['help', 'support', 'assist', 'how to'],
                'response': 'I understand you need help. Please provide more details about your query, and I\'ll assist you. 🤝'
            },
            'thanks': {
                'patterns': ['thank', 'thanks', 'appreciate'],
                'response': 'You\'re welcome! Feel free to reach out if you need anything else. 😊'
            },
            'goodbye': {
                'patterns': ['bye', 'goodbye', 'see you'],
                'response': 'Goodbye! Have a great day! 👋'
            }
        }

    def generate_response(self, message):
        """Generate appropriate response based on message content"""
        message_lower = message.lower()
        
        for category, rule in self.reply_rules.items():
            if any(pattern in message_lower for pattern in rule['patterns']):
                logger.info(f"🎯 Matched category: {category}")
                return rule['response']
        
        return "Thank you for your message. I'll process this and get back to you soon. 🤖"

    def process_message(self, message):
        """Process a single message and generate reply"""
        try:
            msg_id = f"{message.get('info', '')}-{message.get('text', '')}"
            
            if msg_id not in self.processed_msgs:
                logger.info(f"📝 Processing message: {message.get('text', '')[:50]}...")
                
                reply = self.generate_response(message.get('text', ''))
                
                if reply and send_msg(self.driver, reply):
                    logger.info(f"✅ Sent reply: {reply[:50]}...")
                    self.processed_msgs.add(msg_id)
                    
                    if len(self.processed_msgs) > 1000:
                        self.processed_msgs = set(list(self.processed_msgs)[-500:])
                
                time.sleep(1)
                
        except Exception as e:
            logger.error(f"❌ Error processing message: {e}")

    def run(self):
        """Main bot loop"""
        logger.info("🚀 Starting AI Auto-Reply Bot")
        
        while self.running:
            try:
                if is_authenticated(self.driver):
                    new_messages = get_unread_msgs(self.driver)
                    
                    if new_messages:
                        logger.info(f"📥 Received {len(new_messages)} new messages")
                        for msg in new_messages:
                            self.process_message(msg)
                            
                time.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"❌ Error in bot main loop: {e}")
                time.sleep(self.check_interval * 2)

    def stop(self):
        """Stop the bot gracefully"""
        logger.info("🛑 Stopping AI Auto-Reply Bot")
        self.running = False

def start_bot():
    """Initialize and start the bot"""
    try:
        logger.info(f"Current Date and Time (UTC): {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("Current User's Login: Sman12345678")
        
        driver = main()
        if not driver:
            logger.error("❌ Failed to initialize driver")
            return None
            
        logger.info("✨ Driver initialized successfully")
        bot = AIAutoReplyBot(driver)
        bot.start()
        logger.info("🤖 AI Auto-Reply Bot started successfully")
        return bot, driver
        
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")
        return None

if __name__ == "__main__":
    result = start_bot()
    if result:
        bot, driver = result
        try:
            # Keep the main thread running
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("👋 Stopping bot...")
            bot.stop()
            bot.join()
            driver.quit()
            logger.info("✅ Bot stopped successfully")
