"""Modulo che contiene la funzione per loggare i messaggi."""

from datetime import datetime
import settings


def logger(message):
    """Logga i messaggi prodotti dal sistema di elaborazione degli impulsi
    su un file di testo esterno.
    """
    with open(settings.DATA_PREP_LOG_FILE, 'a') as log_file:
        log_message = f'[INFO] {datetime.now().strftime("%d/%m/%Y %H:%M:%S")} : {message}'
        log_file.write(log_message + '\n')
