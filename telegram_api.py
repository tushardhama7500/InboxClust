from flask import Flask, request
import json
import imaplib
import email
import smtplib
from email.mime.text import MIMEText
from email.utils import parseaddr
from email_utils import EmailFeatures, USER_MAP_FILE, STAGE_FILE
from config import (
    EMAIL_USER, EMAIL_PASS,
    SIGNATURE_NAME, SIGNATURE_PHONE, SIGNATURE_EMAIL,
    LANGUAGE_FILE
)

app = Flask(__name__)


@app.route("/", methods=["POST"])
def telegram_reply():
    try:
        data = request.get_json()
        message = data.get("message") or data.get("callback_query")
        if not message:
            return "Invalid request", 400

        chat_id = str(message["from"]["id"] if "from" in message else message["message"]["chat"]["id"])
        user_input = message.get("data") if "data" in message else message.get("text", "").strip()

        # Load user state data
        try:
            with open(USER_MAP_FILE, "r") as f:
                user_map = json.load(f)
        except:
            user_map = {}

        try:
            with open(STAGE_FILE, "r") as f:
                stages = json.load(f)
        except:
            stages = {}

        # 🔄 Change language
        if user_input == "/language":
            keyboard = {
                "inline_keyboard": [[
                    {"text": "🇬🇧 English", "callback_data": "lang_en"},
                    {"text": "🇮🇳 हिन्दी", "callback_data": "lang_hi"}
                ]]
            }
            EmailFeatures.send_telegram_message(
                chat_id,
                EmailFeatures.get_translation(chat_id, "ask_language"),
                reply_markup=keyboard
            )
            return "OK", 200

        elif user_input.startswith("lang_"):
            lang_code = user_input.split("_")[1]
            try:
                with open(LANGUAGE_FILE, "r") as f:
                    lang_data = json.load(f)
            except:
                lang_data = {}
            lang_data[chat_id] = lang_code
            with open(LANGUAGE_FILE, "w") as f:
                json.dump(lang_data, f)
            EmailFeatures.send_telegram_message(
                chat_id,
                EmailFeatures.get_translation(chat_id, "language_changed", lang=lang_code)
            )
            return "OK", 200

        # ❌ Check if email is already deleted
        if chat_id not in user_map and not user_input.startswith("lang_") and not user_input == "/language":
            EmailFeatures.send_telegram_message(chat_id, EmailFeatures.get_translation(chat_id, "no_email_found"))
            return "OK", 200

        # 🗑️ Delete email
        if user_input.startswith("delete_"):
            uid = int(user_input.split("_")[1])
            folder = user_map.get(chat_id, {}).get("folder", "inbox")
            if EmailFeatures.delete_email(uid, folder):
                EmailFeatures.send_telegram_message(chat_id, EmailFeatures.get_translation(chat_id, "email_deleted"))
            else:
                EmailFeatures.send_telegram_message(chat_id, EmailFeatures.get_translation(chat_id, "delete_failed"))
            user_map.pop(chat_id, None)
            with open(USER_MAP_FILE, "w") as f:
                json.dump(user_map, f)
            return "OK", 200

        # 📂 Archive email
        elif user_input.startswith("archive_"):
            uid = int(user_input.split("_")[1])
            folder = user_map.get(chat_id, {}).get("folder", "inbox")
            stages[chat_id] = {"stage": "awaiting_custom_label", "uid": uid, "folder": folder}
            with open(STAGE_FILE, "w") as f:
                json.dump(stages, f)
            EmailFeatures.send_telegram_message(
                chat_id,
                EmailFeatures.get_translation(chat_id, "choose_label")
            )
            return "OK", 200

        # 🤖 Generate AI reply
        elif user_input.startswith("reply_"):
            uid = int(user_input.split("_")[1])
            folder = user_map.get(chat_id, {}).get("folder", "inbox")
            reply = EmailFeatures.ai_reply(chat_id, uid, folder)
            if reply:
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
                    f"🤖 AI reply:\n\n{reply}\n\n{EmailFeatures.get_translation(chat_id, 'send_ai_confirm')}",
                    reply_markup=keyboard
                )
            else:
                EmailFeatures.send_telegram_message(chat_id, EmailFeatures.get_translation(chat_id, "ai_error"))
            return "OK", 200

        # ✅ Confirm AI send
        elif user_input.startswith("sendai_"):
            uid = int(user_input.split("_")[1])
            stage_info = stages.get(chat_id, {})
            if stage_info.get("stage") == "confirm_ai_reply":
                folder = stage_info["folder"]
                reply = (
                    stage_info["reply"].strip() +
                    f"\n\nBest Regards,\n\n{SIGNATURE_NAME}\n{SIGNATURE_PHONE}\n{SIGNATURE_EMAIL}"
                )

                mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
                mail.login(EMAIL_USER, EMAIL_PASS)
                mail.select(folder)
                result, data = mail.uid("fetch", str(uid), "(RFC822)")
                original_msg = email.message_from_bytes(data[0][1])
                to_email = parseaddr(original_msg.get("Reply-To") or original_msg.get("From"))[1]
                subject = original_msg.get("Subject", "")
                msg_id = original_msg.get("Message-ID", "")

                msg = MIMEText(reply, "plain")
                msg["Subject"] = "Re: " + subject
                msg["From"] = EMAIL_USER
                msg["To"] = to_email
                if msg_id:
                    msg["In-Reply-To"] = msg_id
                    msg["References"] = msg_id

                try:
                    smtp = smtplib.SMTP_SSL("smtp.gmail.com", 465)
                    smtp.login(EMAIL_USER, EMAIL_PASS)
                    smtp.sendmail(EMAIL_USER, [to_email], msg.as_string())
                    smtp.quit()
                    EmailFeatures.send_telegram_message(chat_id, EmailFeatures.get_translation(chat_id, "ai_sent"))
                except Exception as e:
                    EmailFeatures.send_telegram_message(chat_id, f"❌ Failed to send email: {e}")

                stages.pop(chat_id, None)
                with open(STAGE_FILE, "w") as f:
                    json.dump(stages, f)
            return "OK", 200

        # ❌ Cancel AI Reply
        elif user_input == "cancelai":
            stages.pop(chat_id, None)
            with open(STAGE_FILE, "w") as f:
                json.dump(stages, f)
            EmailFeatures.send_telegram_message(chat_id, EmailFeatures.get_translation(chat_id, "cancel_reply"))
            return "OK", 200

        # 📥 Archive label reply
        elif chat_id in stages:
            stage_info = stages[chat_id]
            if stage_info["stage"] == "awaiting_custom_label":
                uid = stage_info["uid"]
                folder = stage_info["folder"]
                label_name = user_input.strip()
                if EmailFeatures.move_email(uid, folder, label_name, chat_id):
                    EmailFeatures.send_telegram_message(
                        chat_id,
                        EmailFeatures.get_translation(chat_id, "email_moved", label=label_name)
                    )
                else:
                    EmailFeatures.send_telegram_message(
                        chat_id,
                        EmailFeatures.get_translation(chat_id, "move_failed")
                    )
                stages.pop(chat_id)
                with open(STAGE_FILE, "w") as f:
                    json.dump(stages, f)
                return "OK", 200

        # ❓ Unknown command fallback
        EmailFeatures.send_telegram_message(chat_id, EmailFeatures.get_translation(chat_id, "unknown_command"))
        return "OK", 200

    except Exception as e:
        EmailFeatures.log(f"Exception in telegram_reply: {e}")
        return "Error", 500


if __name__ == "__main__":
    app.run(port=5310, debug=True)

