import pandas as pd
import os
from logs import logw
from stamp import Stamp

class SpamCleaner:
    def __init__(self, input_file='clusters/spam.csv', output_file='clusters/spam_cleaned.csv'):
        self.input_file = input_file
        self.output_file = output_file
        self.df = None
        self.log_str = Stamp()

    def load_data(self):
        try:
            self.df = pd.read_csv(self.input_file)
            logw("info", f"{self.log_str} Loaded {self.input_file} successfully.")
        except Exception as e:
            logw("error", f"{self.log_str} Error loading file: {e}")
            raise

    def clean_text(self, text):
        if pd.isna(text):
            return ''
        return (
            str(text)
            .replace('\xa0', ' ')   
            .replace('\n', ' ')
            .replace('\r', ' ')
            .replace('\t', ' ')
            .strip()
        )

    def clean_data(self):
        if self.df is not None:
            for col in self.df.columns:
                self.df[col] = self.df[col].apply(self.clean_text)
            logw("info", f"{self.log_str} Data cleaned successfully.")
        else:
            logw("error", f"{self.log_str} Dataframe is empty. Load data first.")

    def save_cleaned_file(self):
        self.df.to_csv(self.output_file, index=False)
        logw("info", f"{self.log_str} Cleaned data saved to {self.output_file}")

    def delete_original_file(self):
        try:
            os.remove(self.input_file)
            logw("info", f"{self.log_str} Deleted original file: {self.input_file}")
            logw("info", f"{self.log_str} ################################ Working of SpamCleaner ends here. ###################################\n")
        except Exception as e:
            logw("error", f"{self.log_str} Failed to delete {self.input_file}: {e}")

    def process(self):
        logw("info", f"{self.log_str} ################################ Working of SpamCleaner start from here. ###################################\n")
        self.load_data()
        self.clean_data()
        self.save_cleaned_file()
        self.delete_original_file()

if __name__ == '__main__':
    cleaner = SpamCleaner()
    cleaner.process()

