import json
import imaplib
import smtplib
import email
import requests
import re
import time
from bs4 import BeautifulSoup
from email.mime.text import MIMEText
from email.utils import formataddr, parseaddr
from config import (
    EMAIL_HOST, EMAIL_PORT, EMAIL_USER, EMAIL_PASS,
    TELEGRAM_BOT_TOKEN, Open_router_key,
    SIGNATURE_NAME, SIGNATURE_POSITION,
    SIGNATURE_PHONE, SIGNATURE_EMAIL
)
from logs import logw
from stamp import Stamp


USER_MAP_FILE = "user_mail_map.json"
STAGE_FILE = "user_stage.json"
THEME_FILE = "user_theme.json"
SNOOZE_FILE = "snoozed_emails.json"
LANG_PREF_FILE = "user_lang.json"

class EmailFeatures:
    def __init__(self):
        self.log_str = Stamp() 

    @staticmethod
    def get_translation(chat_id, key, **kwargs):
        try:
            with open(LANG_PREF_FILE, "r") as f:
                lang_pref = json.load(f)
        except:
            lang_pref = {}

        lang_code = lang_pref.get(str(chat_id), "en")

        try:
            with open(f"lang/{lang_code}.json", "r", encoding="utf-8") as f:
                translations = json.load(f)
        except:
            with open("lang/en.json", "r", encoding="utf-8") as f:
                translations = json.load(f)

        msg = translations.get(key, key)
        if kwargs:
            return msg.format(**kwargs)
        return msg

    @staticmethod
    def send_telegram_message(chat_id, message, reply_markup=None):
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        if reply_markup:
            payload["reply_markup"] = json.dumps(reply_markup)
        requests.post(url, json=payload)

    @staticmethod
    def delete_email(uid, folder):
        try:
            mail = imaplib.IMAP4_SSL(EMAIL_HOST, EMAIL_PORT)
            mail.login(EMAIL_USER, EMAIL_PASS)
            mail.select(folder)
            mail.uid("STORE", str(uid), '+FLAGS', '(\\Deleted)')
            mail.expunge()
            return True
        except Exception as e:
            logw("error", f"{self.log_str} [LOG] ❌ Error deleting email: {e}")
            return False
        finally:
            try:
                mail.logout()
            except:
                pass

    @staticmethod
    def move_email(uid, current_folder, target_label, chat_id):
        mail = imaplib.IMAP4_SSL(EMAIL_HOST, EMAIL_PORT)
        mail.login(EMAIL_USER, EMAIL_PASS)
        try:
            mail.select(current_folder)
            try:
                mail.create(f'"{target_label}"')
            except:
                pass

            result = mail.uid('COPY', str(uid), f'"{target_label}"')
            if result[0] != 'OK':
                return False

            mail.uid('STORE', str(uid), '+FLAGS', '(\\Deleted)')
            mail.expunge()

            # Update user map with new folder
            try:
                with open(USER_MAP_FILE, "r") as f:
                    user_map = json.load(f)
            except:
                user_map = {}

            user_map[str(chat_id)] = {"uid": uid, "folder": target_label}
            with open(USER_MAP_FILE, "w") as f:
                json.dump(user_map, f)

            return True

        except Exception as e:
            logw("error", f"{self.log_str} Error moving email: {e}")
            return False
        finally:
            mail.logout()

    @staticmethod
    def snooze_message(chat_id):
        EmailFeatures.send_telegram_message(chat_id, EmailFeatures.get_translation(chat_id, "snooze_prompt"))
        try:
            with open(STAGE_FILE, "r") as f:
                stages = json.load(f)
        except:
            stages = {}
        stages[chat_id] = {"stage": "awaiting_snooze_duration"}
        with open(STAGE_FILE, "w") as f:
            json.dump(stages, f)

    @staticmethod
    def toggle_theme(chat_id):
        try:
            with open(THEME_FILE, "r") as f:
                themes = json.load(f)
        except:
            themes = {}

        current = themes.get(chat_id, "light")
        new_theme = "dark" if current == "light" else "light"
        themes[chat_id] = new_theme

        with open(THEME_FILE, "w") as f:
            json.dump(themes, f)

        return new_theme

    @staticmethod
    def ai_reply(chat_id):
        try:
            with open(USER_MAP_FILE, "r") as f:
                user_map = json.load(f)
            uid_info = user_map.get(chat_id)
            if not uid_info:
                EmailFeatures.send_telegram_message(chat_id, EmailFeatures.get_translation(chat_id, "no_email_found"))
                return

            uid = uid_info["uid"]
            folder = uid_info["folder"]

            mail = imaplib.IMAP4_SSL(EMAIL_HOST, EMAIL_PORT)
            mail.login(EMAIL_USER, EMAIL_PASS)
            mail.select(folder)
            result, data = mail.uid("fetch", str(uid), "(RFC822)")
            if result != "OK":
                EmailFeatures.send_telegram_message(chat_id, EmailFeatures.get_translation(chat_id, "ai_error"))
                return

            msg = email.message_from_bytes(data[0][1])
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode(errors="ignore")
                        break
            else:
                body = msg.get_payload(decode=True).decode(errors="ignore")

            # Clean the body
            body = BeautifulSoup(body, "html.parser").get_text()
            body = re.sub(r'\n\s*\n+', '\n\n', body)
            body = re.sub(r'[ \t]+', ' ', body)
            body = body.strip()
            body = body[:2000] + "..." if len(body) > 2000 else body

            prompt = f"Generate a professional reply to the following email:\n\n{body}"

            headers = {
                "Authorization": f"Bearer {Open_router_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "mistralai/mistral-7b-instruct",
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }

            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
            data = response.json()

            if 'choices' in data:
                reply = data['choices'][0]['message']['content'].strip()
                # Add signature
                reply += f"\n\nBest Regards,\n\n{SIGNATURE_NAME}\n{SIGNATURE_POSITION}\n{SIGNATURE_PHONE}\n{SIGNATURE_EMAIL}"

                with open(STAGE_FILE, "r") as f:
                    stages = json.load(f)
                stages[chat_id] = {"stage": "confirm_ai_reply", "reply": reply, "uid": uid, "folder": folder}
                with open(STAGE_FILE, "w") as f:
                    json.dump(stages, f)

                keyboard = {
                    "inline_keyboard": [[
                        {"text": "✅ Yes", "callback_data": f"sendai_{uid}"},
                        {"text": "❌ No", "callback_data": "cancelai"}
                    ]]
                }

                EmailFeatures.send_telegram_message(
                    chat_id,
                    f"🤖 *AI reply:*\n\n{reply}\n\n{EmailFeatures.get_translation(chat_id, 'send_ai_confirm')}",
                    reply_markup=keyboard
                )
            else:
                EmailFeatures.send_telegram_message(chat_id, f"❌ {data}")

        except Exception as e:
            EmailFeatures.send_telegram_message(chat_id, f"{EmailFeatures.get_translation(chat_id, 'ai_error')} {e}")

