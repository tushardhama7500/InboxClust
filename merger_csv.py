import os
import glob
import pandas as pd
from config import OUTPUT_DIRECTORY, FINAL_DATASET_PATH
from logs import logw
from stamp import Stamp

class DatasetPreparer:
    def __init__(self, input_dir, output_file):
        self.input_dir = input_dir
        self.output_file = output_file
        self.dataframes = []
        self.log_str = Stamp()

    def load_cluster_files(self):
        try:
            all_files = glob.glob(os.path.join(self.input_dir, "*.csv"))
            if not all_files:
                logw("error", f"{self.log_str} [WARNING] No CSV files found in '{self.input_dir}'.") 
                return

            for filename in all_files:
                try:
                    temp_df = pd.read_csv(filename)
                    if 'Label' not in temp_df.columns:
                        logw("info", f"{self.log_str} [SKIP] 'Label' column not found in '{filename}'. Skipping.")
                        continue

                    temp_df["text"] = temp_df["Subject"].fillna("") + " " + temp_df["Content"].fillna("")
                    temp_df = temp_df[["text", "Label"]].rename(columns={"Label": "label"})
                    self.dataframes.append(temp_df)
                    logw("info", f"{self.log_str} [INFO] Processed '{filename}'")

                except Exception as e:
                    logw("error", f"{self.log_str} [ERROR] Failed to process '{filename}': {str(e)}")
        except Exception as e:
            logw("error", f"{self.log_str} [ERROR] Could not read files from '{self.input_dir}': {str(e)}")
            raise

    def save_combined_dataset(self):
        try:
            if not self.dataframes:
                logw("error", f"{self.log_str} [ERROR] No valid data to save.")
                return

            combined_df = pd.concat(self.dataframes, ignore_index=True)
            combined_df.to_csv(self.output_file, index=False)
            logw("info", f"{self.log_str} [SUCCESS] Final dataset saved to '{self.output_file}'")
        except Exception as e:
            logw("error", f" {self.log_str} [ERROR] Failed to save final dataset: {str(e)}")
            raise

    def run(self):
        try:
            logw("info", f"{self.log_str} ################# Working of merger_csv.py start from here. ########################\n") 
            logw("info", f"{self.log_str} [INFO] Starting dataset preparation...")
            self.load_cluster_files()
            self.save_combined_dataset()
            logw("info", f"{self.log_str} ################# Working of merger_csv.py ends here. ########################\n")
        except Exception as e:
            logw("error", f" {self.log_str} [FATAL] Dataset preparation failed: {str(e)}")


if __name__ == "__main__":
    preparer = DatasetPreparer(OUTPUT_DIRECTORY, FINAL_DATASET_PATH)
    preparer.run()

