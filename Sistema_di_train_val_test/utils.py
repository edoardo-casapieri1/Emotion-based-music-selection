"""Utils necessarie per il sistema di train validazione e test della rete"""
import json
import os
import joblib
import pandas as pd
import settings
import validatore_json
from Sistema_di_train_val_test import emotion_classifier
from timer_decorator import timer as timer_test


def loadconfig(userid):
    """Funzione necessaria per il caricamento del file json di configurazione della rete"""
    homedir = settings.NN_PARAMS_CONFIG_DIR
    schema = settings.NN_PARAMS_SCHEMA
    try:
        if validatore_json.validate_json_files(homedir + "NNparams_"
                                               + str(userid) + ".json", schema):
            with open(settings.NN_PARAMS_CONFIG_DIR
                      + "NNparams_" + str(userid) + ".json", 'r') as json_file:
                data = json.load(json_file)
            # check che la dimensione dell'array contenente il numero di neuroni nascosti per layer
            # sia uguale al numero di layer nascosti
            # meno due (i livelli di input ed i livelli di output)
            if ("hidden_layer_sizes" and "n_layers") in data:
                if len(data["hidden_layer_sizes"]) != (data["n_layers"] - 2):
                    raise Exception("[" + str(userid) + "]"
                                    + " Numero errato di neuroni nascosti per strato")
                data["hidden_layer_sizes"] = tuple(data["hidden_layer_sizes"])
                data.pop("n_layers")
            data.pop("id_utente")
        else:
            raise Exception("[" + str(userid)
                            + "]" + " Il file di configurazione della rete fornito non è valido  ")
        return data
    except IOError as err:
        raise Exception("[" + str(userid) + "]" + " Errore nel caricamento "
                                                  "della configurazione della rete") from err


def loadsets(userid):
    """" Funzione per il caricamento dei learning sets di training e tests della rete """
    homedir = settings.NN_LEARNING_SETS_DIR
    try:
        training_data = pd.read_csv(homedir + "/Training_" + str(userid) + ".csv", delimiter=";",
                                    header=None)
        training_labels = pd.read_csv(homedir + "/Training_Target_" + str(userid) + ".csv",
                                      header=None)
        testing_data = pd.read_csv(homedir + "/Test_" + str(userid) + ".csv", delimiter=";",
                                   header=None)
        testing_labels = pd.read_csv(homedir + "/Test_Target_" + str(userid) + ".csv",
                                     header=None)
        return training_data, training_labels, testing_data, testing_labels
    except FileNotFoundError:
        print("\n[" + str(userid) + "]"
              + " Errore nel caricamento dei set di apprendimento: uno o più file non trovati")


def loadoperativesets(relativefilepath, userid):
    """ Funzione utilizzata per il caricamento del set da classificare durante la
    fase operativa della rete"""
    homedir = settings.NN_OPERATIVE_SETS_DIR
    try:
        operative_set = pd.read_csv(homedir + "/" + relativefilepath, delimiter=";", header=None)
        return operative_set
    except FileNotFoundError as error:
        print("\n[" + str(userid) + "]" + "Errore nel caricamento "
                                          "del set da classificare: file non trovato")
        raise emotion_classifier.EmotionClassifierxception from error


def loadmodel(userid):
    """ Funzione necessaria per il caricamento della rete deployata"""
    homedir = settings.NN_MODELS_DIR
    try:
        for file in os.listdir(homedir):
            if str(userid) in file:
                emclassifier = emotion_classifier.EmotionClassifier(userid)
                emclassifier.trained_model = joblib.load(homedir + "/" + file)
                return emclassifier
        raise FileNotFoundError("Errore nel caricamento del modello")
    except FileNotFoundError as error:
        print("\n[" + str(userid) + "]", error)
        raise emotion_classifier.EmotionClassifierxception from error


@timer_test(True)
def buildfromscratch(userid):
    """ Funzione utilizzata per costruire da zero la rete """
    try:
        emclassifier = emotion_classifier.EmotionClassifier(userid)
        while 1:
            emclassifier.build()
            emclassifier.load()
            emclassifier.train()
            emclassifier.classify(emclassifier.x_test, "training")
            emclassifier.evaluate()
            while 1:
                try:
                    choice = int(input('\n[' + str(userid) + '] Si prega di controllare se le '
                                                             'prestazioni di rete sono '
                                                             'soddisfacenti nella cartella '
                                                             '"Models", quindi scegliere cosa '
                                                             'fare:\nInserire 1 per salvare '
                                                             'il modello\nInserire 2 per '
                                                             'riaddestrare\n'))
                    if choice in (1, 2):
                        break
                    print('\n[' + str(userid) + '] Scelta non valida')
                except ValueError:
                    print('\n[' + str(userid) + '] Scelta non valida')
            if choice == 1:
                break
            continue
        emclassifier.savemodel()
        return emclassifier
    except emotion_classifier.EmotionClassifierxception as err:
        print("\n[" + str(userid) + "] Errore nella costruzione della rete da zero: ")
        print(err)
        raise emotion_classifier.EmotionClassifierxception from err
