import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from config import CSV_FILENAME, OUTPUT_DIRECTORY, Cluster_Size 
from logs import logw
from stamp import Stamp

class EmailClustering:
    def __init__(self):
        self.df = None
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        self.k = Cluster_Size
        self.log_str = Stamp()

    def load_csv(self):
        try:
            #logw("info", f"{self.log_str} ################# Working of cluster_email.py start from here. ########################\n")
            self.df = pd.read_csv(CSV_FILENAME)
            assert 'Subject' in self.df.columns and 'Content' in self.df.columns, "CSV must have 'Subject' and 'Content' columns."
            logw("info", f"{self.log_str} [INFO] Loaded {len(self.df)} emails from '{CSV_FILENAME}'.")
        except FileNotFoundError:
            logw("error", f"{self.log_str} [ERROR] File '{CSV_FILENAME}' not found.")
            raise
        except AssertionError as e:
            logw("error", f"{self.log_str} [ERROR] {str(e)}")
            raise
        except Exception as e:
            logw("error", f"{self.log_str} [ERROR] Failed to read CSV: {str(e)}")
            raise

    def preprocess_text(self):
        try:
            self.df['text'] = self.df['Subject'].fillna('') + ' ' + self.df['Content'].fillna('')
            logw("info", f"{self.log_str} [INFO] Text data preprocessing complete.")
        except Exception as e:
            logw("error", f"{self.log_str} [ERROR] Failed to process text data: {str(e)}")
            raise

    def vectorize_text(self):
        try:
            X = self.vectorizer.fit_transform(self.df['text'])
            logw("info", f"{self.log_str} [INFO] Text vectorization successful.")
            return X
        except Exception as e:
            logw("error", f"{self.log_str} [ERROR] Vectorization failed: {str(e)}")
            raise

    def cluster_text(self, X):
        try:
            kmeans = KMeans(n_clusters=self.k, random_state=42)
            self.df['cluster'] = kmeans.fit_predict(X)
            logw("info", f"{self.log_str} [INFO] Clustering complete. {self.k} clusters created.")
        except Exception as e:
            logw("error", f"{self.log_str} [ERROR] Clustering failed: {str(e)}")
            raise

    def save_clusters(self):
        try:
            os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)
            for cluster_id in sorted(self.df['cluster'].unique()):
                cluster_df = self.df[self.df['cluster'] == cluster_id][['Subject', 'Content']]
                cluster_filename = os.path.join(OUTPUT_DIRECTORY, f"cluster_{cluster_id}.csv")
                cluster_df.to_csv(cluster_filename, index=False)
                logw("info", f"{self.log_str} [INFO] Saved {len(cluster_df)} emails to '{cluster_filename}'.")
        except Exception as e:
            logw("error", f"{self.log_str} [INFO] Saved {len(cluster_df)} emails to '{cluster_filename}'.")
            raise

    def run(self):
        try:
            logw("info", f"{self.log_str} ################# Working of cluster_email.py start from here. ########################\n")            
            self.load_csv()
            self.preprocess_text()
            X = self.vectorize_text()
            self.cluster_text(X)
            self.save_clusters()
            logw("info", f"{self.log_str} [SUCCESS] Clustering process completed.")
            logw("info", f"{self.log_str} ################# Working of cluster_email.py ends here. ########################\n")
        except Exception:
            logw("error", f"{self.log_str} [FAILURE] Clustering process terminated due to errors.")


if __name__ == "__main__":
    cluster_app = EmailClustering()
    cluster_app.run()

