# fetch_emails.py

import imaplib
import email
from email.header import decode_header
import pandas as pd
from config import EMAIL_HOST, EMAIL_PORT, EMAIL_USER, EMAIL_PASS, CSV_FILENAME, LIMIT
from logs import logw
from stamp import Stamp

class EmailFetcher:
    def __init__(self, host, port, user, password, limit):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.limit = limit
        self.connection = None
        self.log_str = Stamp()

    def connect(self):
        try:
            logw("info", f"{self.log_str} ############################## Working of fetch_emails.py start from here. ##############################\n")
            logw("info", f"{self.log_str} Connecting to the email server...")
            self.connection = imaplib.IMAP4_SSL(self.host, self.port)
            self.connection.login(self.user, self.password)
            self.connection.select("inbox")
            logw("info", f"{self.log_str} Connected and logged in successfully.")
        except Exception as e:
            logw("error", f"{self.log_str} Failed to connect or login: {e}")
            raise

    def clean_text(self, text):
        return ''.join(c if c.isprintable() else ' ' for c in text).strip()

    def fetch_emails(self):
        emails = []

        try:
            result, data = self.connection.search(None, "ALL")
            if result != "OK":
                logw("info", f"{self.log_str} Error fetching email IDs.)")
                return emails

            email_ids = data[0].split()
            total_available = len(email_ids)
            logw("info", f"{self.log_str} Total emails in inbox: {total_available}")

            email_ids = email_ids[-self.limit:] 
            logw("info", f"{self.log_str} Emails to be fetched (as per limit {self.limit}): {len(email_ids)}")

            for i, eid in enumerate(reversed(email_ids), 1):
                try:
                    result, msg_data = self.connection.fetch(eid, "(RFC822)")
                    if result != "OK":
                        logw("info", f"{self.log_str} Skipping email {i}, fetch failed.")
                        continue

                    msg = email.message_from_bytes(msg_data[0][1])

                    # Decode subject
                    subject, encoding = decode_header(msg.get("Subject"))[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding or "utf-8", errors="ignore")
                    subject = self.clean_text(subject)

                    # Decode body
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            content_disposition = str(part.get("Content-Disposition"))

                            if content_type == "text/plain" and "attachment" not in content_disposition:
                                try:
                                    body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                                except Exception as e:
                                    logw("info", f"{self.log_str} Error decoding multipart body: {e}")
                                    body = ""
                                break
                    else:
                        try:
                            body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
                        except Exception as e:
                            logw("error", f"{self.log_str} Error decoding body: {e}")
                            body = ""

                    body = self.clean_text(body)
                    emails.append({"Subject": subject, "Content": body})

                    if i % 500 == 0:
                        logw("info", f"{self.log_str} Fetched {i} emails...)")

                except Exception as e:
                    logw("info", f"{self.log_str} Error processing email {i}: {e}")

        except Exception as e:
            logw("error", f"{self.log_str} Failed to fetch emails: {e}")

        return emails

    def disconnect(self):
        if self.connection:
            try:
                self.connection.logout()
                logw("info", f"{self.log_str} Disconnected from the server.")
            except Exception as e:
                logw("error", f"{self.log_str} Error during disconnect: {e}")


def save_to_csv(emails, filename):
    try:
        self.log_str = Stamp()
        df = pd.DataFrame(emails)
        df.to_csv(filename, index=False)
        logw("info", f"{self.log_str} Saved {len(emails)} emails to '{filename}'\n")
        logw("info", f"{self.log_str} ############################## Working of fetch_emails.py ends here. ##############################\n")
    except Exception as e:
        logw("error", f"{self.log_str} Failed to save emails to CSV: {e}\n")


if __name__ == "__main__":
    fetcher = EmailFetcher(
        host=EMAIL_HOST,
        port=EMAIL_PORT,
        user=EMAIL_USER,
        password=EMAIL_PASS,
        limit=LIMIT
    )

    try:
        fetcher.connect()
        emails = fetcher.fetch_emails()
        save_to_csv(emails, CSV_FILENAME)
    finally:
        fetcher.disconnect()

