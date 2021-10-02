"""Il file contiene la classe che genera gli insiemi di learning"""

import json
import os
from sklearn.model_selection import train_test_split
import settings
from validatore_json import validate_json_files
from Generatore_degli_insiemi_di_learning.json_to_dataframe import json_to_dataframe
from timer_decorator import timer as timer_test


class GeneratoreInsiemiDiLearning:
    """
    Classe Che implementa la generazione degli insiemi di learning
    """

    def __init__(self):
        conf_path = settings.GEN_INSIEMI_LEARNING_CONFIG_PATH_GEN
        schema_path = settings.GEN_INSIEMI_LEARNING_SCHEMA_PATH_GEN
        if not validate_json_files(conf_path, schema_path):
            raise Exception("[ERRORE] Il file di configurazione del Sistema di generazione"
                            "di learning non è corretto")

        with open(conf_path) as conf_file:
            data = json.load(conf_file)

        self.train_size = data['train_size']
        self.test_size = data['test_size']
        self.output_path = settings.NN_LEARNING_SETS_DIR
        self.input_file_path = data['input_file_path']

    @timer_test(True)
    def generate_learning_sets(self):
        """
        Funzione che genera gli insiemi di learning per tutti gli utenti,
         dal file contenente le feature, generato dal sistema di elaborazione degli impulsi.

        Il file di input viene specificato nel file JSON di configurazione
        Il percorso ed il formato di output diviene specificato nel file JSON di configurazione
        Il file di configurazione viene letto nel costruttore della classe
        """

        directory = self.input_file_path

        for id_user in os.listdir(directory):
            self.generate_learning_sets_for_a_specific_user(id_user)

    @timer_test(True)
    def generate_learning_sets_for_a_specific_user(self, id_user):
        """
        Funzione che genera gli insiemi di learning per un utente specifico,
         dal file contenente le feature, generato dal sistema di elaborazione degli impulsi.

        Il file di input viene specificato nel file JSON di configurazione
        Il percorso ed il formato di output diviene specificato nel file JSON di configurazione
        Il file di configurazione viene letto nel costruttore della classe
        """
        schema_path = settings.GEN_INSIEMI_LEARNING_SCHEMA_PATH_INPUT
        id_user = str(id_user)
        json_path = self.input_file_path + id_user + '/processed_data.json'
        if not validate_json_files(json_path, schema_path):
            raise Exception("[ERRORE] Il file contenente le features "
                            "non è corretto")

        data = json_to_dataframe(json_path, settings.LABEL_TO_INDEX_DICT)

        training_data, testing_data, training_labels, testing_labels = \
            train_test_split(data.iloc[:, 1:len(data.columns)], data.iloc[:, 0],
                             train_size=self.train_size, test_size=self.test_size)

        training_data.to_csv(self.output_path + '/Training_' + id_user + '.csv',
                             sep=';', header=False, index=False)
        testing_data.to_csv(self.output_path + '/Test_' + id_user + '.csv',
                            sep=';', header=False, index=False)
        training_labels.to_csv(self.output_path + '/Training_Target_' + id_user + '.csv',
                               sep=';', header=False, index=False)
        testing_labels.to_csv(self.output_path + '/Test_Target_' + id_user + '.csv',
                              sep=';', header=False, index=False)
