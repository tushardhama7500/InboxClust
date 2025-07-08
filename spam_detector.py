import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score
import joblib
from config import FINAL_DATASET_PATH, MODEL_PATH, VECTORIZER_PATH
from logs import logw
from stamp import Stamp

class SpamClassifierTrainer:
    def __init__(self, dataset_path, model_path, vectorizer_path):
        self.dataset_path = dataset_path
        self.model_path = model_path
        self.vectorizer_path = vectorizer_path
        self.df = None
        self.vectorizer = TfidfVectorizer()
        self.model = MultinomialNB()
        self.log_str = Stamp()

    def load_data(self):
        try:
            self.df = pd.read_csv(self.dataset_path)
            logw("info", f"{self.log_str} [INFO] Loaded dataset from '{self.dataset_path}' with {len(self.df)} rows.")
        except FileNotFoundError:
            logw("error", f"{self.log_str} [ERROR] File '{self.dataset_path}' not found.")
            raise
        except Exception as e:
            logw("error", f"{self.log_str} [ERROR] Failed to load dataset: {str(e)}")
            raise

    def preprocess(self):
        try:
            self.df = self.df.dropna(subset=["text", "label"]).copy()
            self.df["text"] = self.df["text"].astype(str)
            logw("info", f"{self.log_str} [INFO] Preprocessing complete. Cleaned missing values.")
        except Exception as e:
            logw("error", f"{self.log_str} [ERROR] Preprocessing failed: {str(e)}")
            raise

    def vectorize_text(self):
        try:
            X = self.df["text"]
            y = self.df["label"]
            X_vec = self.vectorizer.fit_transform(X)
            logw("info", f"{self.log_str} [INFO] Text vectorization complete.")
            return X_vec, y
        except Exception as e:
            logw("error", f"{self.log_str} [ERROR] Vectorization failed: {str(e)}")
            raise

    def train_and_evaluate(self, X_vec, y):
        try:
            X_train, X_test, y_train, y_test = train_test_split(X_vec, y, test_size=0.2, random_state=42)
            self.model.fit(X_train, y_train)
            y_pred = self.model.predict(X_test)
            acc = accuracy_score(y_test, y_pred)
            logw("info", f"{self.log_str} [INFO] Model trained. Accuracy: {acc:.4f}")
        except Exception as e:
            logw("error", f"{self.log_str} [ERROR] Model training or evaluation failed: {str(e)}")
            raise

    def save_artifacts(self):
        try:
            joblib.dump(self.model, self.model_path)
            joblib.dump(self.vectorizer, self.vectorizer_path)
            logw("info", f"{self.log_str} [INFO] Model saved to '{self.model_path}'")
            logw("info", f"{self.log_str} [INFO] Vectorizer saved to '{self.vectorizer_path}'")
        except Exception as e:
            logw("error", f"{self.log_str} [ERROR] Failed to save model/vectorizer: {str(e)}")
            raise

    def run(self):
        try:
            logw("info", f"{self.log_str} ##################################### Working of spam_detector.py start from here. ###################################\n")
            logw("info", f"{self.log_str} [INFO] Starting training pipeline...")
            self.load_data()
            self.preprocess()
            X_vec, y = self.vectorize_text()
            self.train_and_evaluate(X_vec, y)
            self.save_artifacts()
            logw("info", f"{self.log_str} [SUCCESS] Training pipeline completed successfully.")
            logw("info", f"{self.log_str} ##################################### Working of spam_detector.py ends here. ###################################\n")
        except Exception as e:
            logw("error", f"{self.log_str} [FATAL] Pipeline terminated with error: {str(e)}")


if __name__ == "__main__":
    trainer = SpamClassifierTrainer(
        dataset_path=FINAL_DATASET_PATH,
        model_path=MODEL_PATH,
        vectorizer_path=VECTORIZER_PATH
    )
    trainer.run()

