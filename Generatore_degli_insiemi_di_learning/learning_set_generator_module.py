"""
file che contiene L'intero sistema di generazione degli insiemi di learining
pronto per girare separatamente
"""

import json
import threading
from polling import poll
import settings
from validatore_json import validate_json_files
from Generatore_degli_insiemi_di_learning.quality_check import QualityCheck
from Generatore_degli_insiemi_di_learning.generazione_insiemi import GeneratoreInsiemiDiLearning


def _ready_check(polling_file):
    with open(polling_file) as polling_file_open:
        data = json.load(polling_file_open)
    return data['data_ready'] == 1


def _write_data(polling_file, data):
    with open(polling_file, "w") as polling_file_open:
        json.dump(data, polling_file_open)


def generatore_dgli_insiemi_di_learning_phase(polling_file, polling_time):
    """
    Funzione che esegue l'intera fase di generazione degli insiemi di learning
    :param polling_file: file su cui controllare se i dati sono pronti
    :param polling_time: Ogni quando controllare se i dati sono pronti
    :return: void
    """
    data = {
        "data_ready": 0,
        "is_needed_other_data": 0
    }

    while True:
        print("[INFO] Waiting for data")
        poll(
            lambda: _ready_check(polling_file),
            step=polling_time,
            poll_forever=True
        )

        data['data_ready'] = 0

        print("[INFO] Data ready, plotting radar diagram")
        quality_check = QualityCheck()
        quality_check.class_quality_for_all_user()

        while True:
            quality_input = int(input("Is the quality of file good enough? [SI:1, NO:2]\n"))

            if quality_input in (1, 2):
                data['is_needed_other_data'] = (quality_input - 1)
                _write_data(polling_file, data)
                break

            print("invalid input...")

        if quality_input == 2:
            continue

        print("[INFO] Generating learning sets")
        generatore_insiemi_di_learning = GeneratoreInsiemiDiLearning()
        generatore_insiemi_di_learning.generate_learning_sets()

        print("[INFO] Learning sets generated")
        print("[INFO] Restating a new Cycle")


def start(polling_file, polling_time):
    """
    Esegue il Generatore di insiemi di leaning in un altro thread
    :param polling_file: file su cui controllare se i dati sono pronti
    :param polling_time: Ogni quando controllare se i dati sono pronti
    :return: void
    """
    learning_set_thread = threading.Thread(target=generatore_dgli_insiemi_di_learning_phase,
                                           args=(polling_file, polling_time))
    learning_set_thread.start()


def main():
    """
    Funzione main
    :return: void
    """
    conf_path = settings.GEN_INSIEMI_LEARNING_CONFIG_PATH_MOD
    schema_path = settings.GEN_INSIEMI_LEARNING_SCHEMA_PATH_MOD
    if not validate_json_files(conf_path, schema_path):
        raise Exception("[ERRORE] Il file di configurazione del Module stand alone "
                        "non è corretto")

    with open(conf_path) as conf_file:
        conf = json.load(conf_file)

    run_in_separate_thread = conf['thread_mode']

    conf_polling_file = conf['polling_file']
    conf_polling_time = conf['polling_time']

    if run_in_separate_thread:
        start(conf_polling_file, conf_polling_time)
    else:
        generatore_dgli_insiemi_di_learning_phase(conf_polling_file, conf_polling_time)


if __name__ == '__main__':
    main()
