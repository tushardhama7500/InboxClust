import os

# Email Credentials and Settings
EMAIL_HOST = "imap.gmail.com"
EMAIL_PORT = 993
EMAIL_USER = os.getenv("EMAIL_USER", "your_email@gmail.com")
EMAIL_PASS = os.getenv("EMAIL_PASS", "your_password")
LIMIT = 13000

# Clustering Config
CLUSTER_LABEL_MAP = {
    0: "Career Update",
    1: "Daily Updates",
    2: "Banking",
    3: "Newsletter",
    4: "Promotions"
}
Cluster_Size = 5

# Signature Config
SIGNATURE_NAME = os.getenv("SIGNATURE_NAME", "Your Name")
SIGNATURE_PHONE = os.getenv("SIGNATURE_PHONE", "Your Phone")
SIGNATURE_EMAIL = os.getenv("SIGNATURE_EMAIL", "your_email@example.com")
SIGNATURE_POSITION = os.getenv("SIGNATURE_POSITION", "Your Position")

# CSV Paths
CSV_FILENAME = "emails_data.csv"
FINAL_DATASET_PATH = "emails_dataset.csv"
OUTPUT_DIRECTORY = "clusters"

# Twilio / WhatsApp Credentials
TWILIO_SID = os.getenv("TWILIO_SID", "your_twilio_sid")
TWILIO_AUTH = os.getenv("TWILIO_AUTH", "your_twilio_auth")
FROM_WHATSAPP = os.getenv("FROM_WHATSAPP", "whatsapp:+14155238886")
TO_WHATSAPP = os.getenv("TO_WHATSAPP", "whatsapp:+91XXXXXXXXXX")

# Telegram Bot Credentials
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "your_bot_token")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "your_chat_id")

# OpenAI Credentials
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your_openai_api_key")
Open_router_key = os.getenv("OPEN_ROUTER_KEY", "your_openrouter_key")

# Model Paths
MODEL_PATH = "spam_model.pkl"
VECTORIZER_PATH = "vectorizer.pkl"

# Language Support
LANGUAGE_FILE = "user_language.json"
LANG_DIR = "lang"

