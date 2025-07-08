import logging
import os
from datetime import date
current_date = date.today()


def file_creator(filename):
    handler = logging.FileHandler(filename)
    logger = logging.getLogger(filename)

    if not logger.handlers:  # Avoid adding multiple handlers
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
    return logger
log_file_mapping = {
    'info': f"/Czentrix/apps/Tushar/Machine_Learning/Supervised/SPAM_DET/logs/spam_detector_logs.log-{current_date}",
    'error': f"/Czentrix/apps/Tushar/Machine_Learning/Supervised/SPAM_DET/logs/spam_detector_logs.log-{current_date}"
}

loggers = {log_type: file_creator(file_path) for log_type, file_path in log_file_mapping.items()}

def logw(logtype, message):

    if logtype not in loggers:
        return  # Log type not configured

    logger = loggers[logtype]

    if logtype == 'info':
        logger.info(message)
    elif logtype == 'error':
        logger.error(message, exc_info=True)
