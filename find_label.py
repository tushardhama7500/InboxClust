import os
import pandas as pd
from config import CLUSTER_LABEL_MAP, OUTPUT_DIRECTORY
from logs import logw
from stamp import Stamp

class ClusterLabelAssigner:
    def __init__(self, label_map, input_dir):
        self.label_map = label_map
        self.input_dir = input_dir
        self.log_str = Stamp()

    def assign_labels(self):
        for cluster_id, label in self.label_map.items():
            filename = os.path.join(self.input_dir, f"cluster_{cluster_id}.csv")

            try:
                df = pd.read_csv(filename)
                df['Label'] = label
                df.to_csv(filename, index=False)
                logw("info", f"{self.log_str} [INFO] Added label '{label}' to '{filename}'")
            except FileNotFoundError:
                logw("error", f"{self.log_str} [WARNING] File '{filename}' not found. Skipping.") 
            except Exception as e:
                logw("error", f"{self.log_str} [ERROR] Failed to process '{filename}': {str(e)}")

    def run(self):
        try:
            logw("info", f"{self.log_str} ################# Working of find_label.py start from here. ########################\n")
            logw("info", f"{self.log_str} [INFO] Starting label assignment process...")
            self.assign_labels()
            logw("info", f"{self.log_str} [SUCCESS] Label assignment completed.")
            logw("info", f"{self.log_str} ################# Working of find_label.py ends here. ########################\n")
        except Exception as e:
            logw("error", f"{self.log_str} [FATAL] Unexpected error: {str(e)}")


if __name__ == "__main__":
    label_assigner = ClusterLabelAssigner(CLUSTER_LABEL_MAP, OUTPUT_DIRECTORY)
    label_assigner.run()
