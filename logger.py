from datetime import datetime


class Logger:

    def __init__(self, path):
        self.path = path

    def print_log(self, message):
        with open(self.path, 'a') as log_file:
            log_message = f'[INFO] {datetime.now().strftime("%d/%m/%Y %H:%M:%S")} : {message}'
            log_file.write(log_message + '\n')
