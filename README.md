# 📧 Email Intelligence System using Machine Learning and Telegram Bot

This project is an end-to-end intelligent email processing system that integrates machine learning (unsupervised + supervised) with Telegram for real-time notifications and control over incoming emails. It fetches emails, clusters and labels them, trains a spam detection model, and lets you interact with emails directly from Telegram.

---

## 📂 Project Structure

📁 email-intelligence-system/

├── fetch_emails.py # Fetch Inbox emails and save to emails_data.csv

├── fetch_spam_emails.py # Fetch Spam emails and save to clusters/spam.csv

├── SpamCleaner.py # Clean spam emails and save cleaned CSV

├── cluster_emails.py # Apply KMeans clustering to group emails

├── config.py # Contains CLUSTER_LABEL_MAP for manual labels

├── find_label.py # Map cluster numbers to labels

├── merger_csv.py # Merge all CSVs into one final dataset

├── spam_detector.py # Train and save spam classifier

├── email_notifier_tele.py # Poll emails and send Telegram alerts

├── telegram_api.py # Handle Telegram actions

├── email_utils.py # Email action helper (archive, delete, etc.)

├── clusters/ # Contains cluster CSV files

├── emails_dataset.csv # Final labeled dataset

├── spam_model.pkl # Trained spam classifier

├── vectorizer.pkl # Fitted vectorizer

├── DOCUMENTATION.md # Feature documentation with screenshots

├── LICENSE # Open-source license

└── README.md # This file

---

## 🔄 Workflow Summary

1. **Fetch Emails**  
   - Inbox → `emails_data.csv`
   - Spam → `clusters/spam.csv`

2. **Clean Data**  
   - Spam cleaning via `SpamCleaner.py` → `clusters/spam_cleaned.csv`

3. **Unsupervised Clustering**  
   - `cluster_emails.py` clusters Inbox emails into 5 groups (0–4)

4. **Manual Labeling**  
   - Label clusters in `config.py` like:
     ```python
     CLUSTER_LABEL_MAP = {
         0: "Career Update",
         1: "Daily Updates",
         2: "Banking",
         3: "Newsletter",
         4: "Promotions"
     }
     ```

5. **Assign Labels to Emails**  
   - `find_label.py` adds a `label` column to all cluster CSVs

6. **Merge CSVs**  
   - All cleaned and labeled data → `emails_dataset.csv`

7. **Train Supervised Spam Detection Model**  
   - `spam_detector.py` trains model on final dataset
   - Saves `spam_model.pkl` and `vectorizer.pkl`

8. **Real-Time Email Notifications on Telegram**  
   - `email_notifier_tele.py` polls for new mail every minute
   - Sends a formatted message like:

     ```
     📬 New Email Received!
     Subject: [subject here]
     Label: [predicted label]
     Model Confidence: [xx%]
     Summary: [email summary]

     Choose an action below:
     ```

     With buttons: `Delete`, `Archive`, `Snooze`, `AI Reply`

9. **Telegram Interaction**  
   - Actions handled in `telegram_api.py` and `email_utils.py`
   - Example: On clicking archive → bot asks for label → moves mail

---

## 🌐 Multilingual Support

The bot supports **language switching** using the command:

/language


Options:
- 🇬🇧 English
- 🇮🇳 Hindi

(See `DOCUMENTATION.md` for screenshots.)

---

## ⚙️ Technologies Used

- Python
- IMAP/SMTP (Gmail)
- Pandas, scikit-learn
- Telegram Bot API
- Joblib, Ngrok
- Regex, Time, JSON, Logging

---

## 📍 Future Enhancements

- Implement better spam filtering using **deep learning**
- Use **OAuth-based Gmail access** instead of basic authentication
- Enable **"Email as a Database"** (advanced querying/filtering)
- Add **"Auto-Unsubscribe"** feature for newsletters
- Introduce **"Schedule Send" Reminders**
- AI-generated reply feature using GPT
- Build a user-friendly **dashboard UI**

---

## 🚀 Getting Started

1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/email-intelligence-system.git
   cd email-intelligence-system
2. Configure your Gmail and Telegram Bot credentials securely.

3. Run the files in the following sequence:

```
python fetch_emails.py
python fetch_spam_emails.py
python SpamCleaner.py
python cluster_emails.py
# Edit config.py manually to define cluster labels
python find_label.py
python merger_csv.py
python spam_detector.py
python email_notifier_tele.py
```

4. Use Telegram to receive and manage new email alerts in real-time.

📄 License
This project is licensed under the MIT License.

🙌 Acknowledgements
Thanks to the open-source community and Python libraries that made this project possible!
