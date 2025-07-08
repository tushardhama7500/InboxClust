# fetch_spam_emails.py

import imaplib
import email
from email.header import decode_header
from bs4 import BeautifulSoup
import pandas as pd
import os
from config import EMAIL_HOST, EMAIL_PORT, EMAIL_USER, EMAIL_PASS
from logs import logw
from stamp import Stamp

class SpamEmailFetcher:
    def __init__(self, host, port, user, password):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.connection = None
        self.log_str = Stamp()

    def connect(self):
        try:
            ##############################
            logw("info", f"\n{self.log_str} ############################## Working of fetch_spam_emails.py start from here. ###########################\n ")
            logw("info", f"{self.log_str} Connecting to email server...")
            self.connection = imaplib.IMAP4_SSL(self.host, self.port)
            self.connection.login(self.user, self.password)
            logw("info", f"{self.log_str} Connected and logged in successfully.")
        except Exception as e:
            logw("error", f"{self.log_str} Connection or login failed: {e}")
            raise

    def disconnect(self):
        if self.connection:
            try:
                self.connection.logout()
                logw("info", f"{self.log_str} Disconnected from email server.")
            except Exception as e:
                logw("error", f"{self.log_str} Error during logout: {e}")

    def clean_text(self, text):
        return "".join(c if c.isalnum() or c.isspace() else " " for c in text).strip()

    def fetch_spam_emails(self):
        emails_data = []

        try:
            logw("info", f"{self.log_str} Selecting Spam folder..." ) 
            status, _ = self.connection.select('"[Gmail]/Spam"')
            if status != "OK":
                logw("info", f"{self.log_str} Could not open spam folder.")
                return emails_data

            result, data = self.connection.search(None, "ALL")
            if result != "OK":
                logw("info", f"{self.log_str} Failed to search spam emails.")
                return emails_data

            email_ids = data[0].split()
            logw("info", f"{self.log_str} Total spam emails in inbox: {len(email_ids)}")

            for i, eid in enumerate(email_ids, 1):
                try:
                    result, msg_data = self.connection.fetch(eid, "(RFC822)")
                    if result != "OK":
                        logw("info", f"{self.log_str} Failed to fetch email ID {eid}.")
                        continue

                    msg = email.message_from_bytes(msg_data[0][1])

                    # Decode subject
                    subject, encoding = decode_header(msg.get("Subject"))[0]
                    if isinstance(subject, bytes):
                        try:
                            subject = subject.decode(encoding if encoding else "utf-8", errors="ignore")
                        except Exception:
                            subject = "Undecodable Subject"
                    subject = self.clean_text(subject)

                    # Extract body
                    content = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            if content_type == "text/plain":
                                try:
                                    content = part.get_payload(decode=True).decode(errors="ignore")
                                    break
                                except Exception as e:
                                    logw("error", f"{self.log_str} Error decoding text part: {e}")
                                    continue
                            elif content_type == "text/html":
                                try:
                                    html = part.get_payload(decode=True).decode(errors="ignore")
                                    soup = BeautifulSoup(html, "html.parser")
                                    content = soup.get_text()
                                    break
                                except Exception as e:
                                    logw("error", f"{self.log_str} Error decoding HTML part: {e}") 
                                    continue
                    else:
                        try:
                            content = msg.get_payload(decode=True).decode(errors="ignore")
                        except Exception as e:
                            logw("error", f"{self.log_str} Error decoding singlepart email: {e}")
                            content = ""

                    content = self.clean_text(content)

                    emails_data.append({
                        "Subject": subject,
                        "Content": content,
                        "Label": "Spam"
                    })

                    if i % 200 == 0:
                        logw("info", f"{self.log_str} Fetched {i} spam emails...")

                except Exception as e:
                    logw("error", f"{self.log_str} Error processing email {i}: {e}")

        except Exception as e:
            logw("error", f"{self.log_str} Error fetching spam emails: {e}")

        return emails_data

    def save_to_csv(self, emails, filename):
        try:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            df = pd.DataFrame(emails)
            df.to_csv(filename, index=False)
            logw("info", f"{self.log_str} Saved {len(df)} spam emails to '{filename}'")
            logw("info", f"{self.log_str} ############################## Working of fetch_spam_emails.py ends here. ######################\n")
        except Exception as e:
            logw("error", f"{self.log_str} Failed to save CSV: {e}")


if __name__ == "__main__":
    fetcher = SpamEmailFetcher(host=EMAIL_HOST,port=EMAIL_PORT, user=EMAIL_USER, password=EMAIL_PASS)

    try:
        fetcher.connect()
        spam_emails = fetcher.fetch_spam_emails()
        fetcher.save_to_csv(spam_emails, "clusters/spam.csv")
    finally:
        fetcher.disconnect()

