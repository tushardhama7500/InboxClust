import imaplib
import email
import os
import json
import time
import joblib
import re
from bs4 import BeautifulSoup
from email.header import decode_header
import requests
from config import (
    EMAIL_HOST, EMAIL_PORT, EMAIL_USER, EMAIL_PASS,
    TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID,
    MODEL_PATH, VECTORIZER_PATH
)
from sklearn.metrics import accuracy_score
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import TfidfVectorizer
from logs import logw
from stamp import Stamp

class EmailNotifier:
    def __init__(self):
        self.log_str = Stamp()
        self.model = joblib.load(MODEL_PATH)
        self.vectorizer = joblib.load(VECTORIZER_PATH)

        self.uid_file = "last_uid.json"
        self.user_map_file = "user_mail_map.json"

        os.makedirs("logs", exist_ok=True)

        for file in [self.uid_file, self.user_map_file]:
            if not os.path.exists(file):
                with open(file, "w") as f:
                    json.dump({}, f)

    def get_last_uid(self, folder):
        with open(self.uid_file, "r") as f:
            return json.load(f).get(folder, 0)

    def set_last_uid(self, folder, uid):
        with open(self.uid_file, "r") as f:
            data = json.load(f)
        data[folder] = uid
        with open(self.uid_file, "w") as f:
            json.dump(data, f)

    def clean(self, text):
        return ' '.join(text.replace('\n', ' ').replace('\r', ' ').split())

    def summarize(self, text, limit=500):
        return (text[:limit] + "...") if len(text) > limit else text

    def predict_label_with_accuracy(self, text):
        try:
            vec = self.vectorizer.transform([text])
            label = self.model.predict(vec)[0]
            prob = max(self.model.predict_proba(vec)[0])
            accuracy_percent = f"{prob * 100:.2f}%"
            return label, accuracy_percent
        except Exception as e:
            logw("error", f"{self.log_str} [ERROR] Prediction failed: {str(e)}")
            return "Unknown", "0%"

    def escape_markdown(self, text):
        escape_chars = r'\_*[]()~`>#+-=|{}.!'
        return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)

    def send_telegram(self, subject, summary, label, accuracy, uid, folder):
        subject = self.escape_markdown(subject)
        summary = self.escape_markdown(summary)
        label = self.escape_markdown(label)
        accuracy = self.escape_markdown(accuracy)

        body = (
            f"📬 *New Email Received\!*\n\n"
            f"*Subject:* _{subject}_\n"
            f"*Label:* *{label}*\n"
            f"*Model Confidence:* `{accuracy}`\n"
            f"*Summary:* {summary}\n\n"
            f"✨ *Choose an action below\:*"
        )

        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": body,
            "parse_mode": "MarkdownV2",
            "reply_markup": {
                "inline_keyboard": [
                    [
                        {"text": "🗑️ Delete", "callback_data": f"delete_{uid}"},
                        {"text": "📁 Archive", "callback_data": f"archive_{uid}"},
                    ],
                    [
                        {"text": "⏰ Snooze", "callback_data": f"snooze_{uid}"},
                        {"text": "🤖 AI Reply", "callback_data": f"reply_{uid}"}
                    ]
                ]
            }
        }

        try:
            response = requests.post(url, json=payload)
            result = response.json()
            if response.status_code == 200 and result.get("ok"):
                logw("info", f"{self.log_str} Telegram message sent with buttons!\n")
            else:
                logw("error", f"{self.log_str} Failed to send Telegram message.")
        except Exception as e:
            logw("error", f"{self.log_str} Telegram API call error:", str(e))

        try:
            with open(self.user_map_file, "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {}

        data[str(TELEGRAM_CHAT_ID)] = {"uid": uid, "folder": folder}
        with open(self.user_map_file, "w") as f:
            json.dump(data, f)

    def fetch_and_send(self, folder, only_latest=False):
        try:
            mail = imaplib.IMAP4_SSL(EMAIL_HOST, EMAIL_PORT)
            mail.login(EMAIL_USER, EMAIL_PASS)
            mail.select(folder)

            last_uid = self.get_last_uid(folder)
            result, data = mail.uid("search", None, "ALL")
            if result != "OK":
                logw("error", f"{self.log_str} Failed to fetch emails from {folder}")
                mail.logout()
                return

            uids = list(map(int, data[0].split()))
            new_uids = sorted(uid for uid in uids if uid > last_uid)

            if only_latest and new_uids:
                new_uids = [new_uids[-1]]

            for uid in new_uids:
                res, msg_data = mail.uid("fetch", str(uid), "(RFC822)")
                if res != "OK":
                    continue

                msg = email.message_from_bytes(msg_data[0][1])
                subject, enc = decode_header(msg["Subject"])[0]
                subject = subject.decode(enc or "utf-8", errors="ignore") if isinstance(subject, bytes) else subject
                subject = self.clean(subject)

                content = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        ctype = part.get_content_type()
                        if ctype in ["text/plain", "text/html"]:
                            payload = part.get_payload(decode=True)
                            if payload:
                                decoded = payload.decode(errors="ignore")
                                content = BeautifulSoup(decoded, "html.parser").get_text() if "html" in ctype else decoded
                            break
                else:
                    content = msg.get_payload(decode=True).decode(errors="ignore")

                full_text = self.clean(subject + " " + content)
                summary = self.summarize(content)
                label, accuracy = self.predict_label_with_accuracy(full_text)

                self.send_telegram(subject, summary, label, accuracy, uid, folder)
                self.set_last_uid(folder, uid)

            mail.logout()

        except Exception as e:
            logw("error", f"{self.log_str} [ERROR] Fetch and send failed for folder '{folder}': {str(e)}")

    def run(self):
        logw("info", f"{self.log_str} ######################## Working of email_notifier_tele.py start from here. #####################\n")
        logw("info", f"{self.log_str} Initial scan: fetching latest from inbox and spam\n")
        self.fetch_and_send("inbox", only_latest=True)
        self.fetch_and_send("[Gmail]/Spam", only_latest=True)

        while True:
            self.log_str = Stamp()
            logw("info", f"{self.log_str} Checking for new emails...\n")
            self.fetch_and_send("inbox")
            self.fetch_and_send("[Gmail]/Spam")
            time.sleep(30)


if __name__ == "__main__":
    notifier = EmailNotifier()
    notifier.run()

