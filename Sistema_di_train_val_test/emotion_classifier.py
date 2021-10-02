""" Classi necessarie per la creazione/management della rete """
import json
import joblib
from sklearn.metrics import r2_score
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import plot_confusion_matrix
from sklearn.metrics import accuracy_score
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import f1_score
from numpy import ravel
import matplotlib.pyplot as plt
import settings
from Sistema_di_train_val_test import utils


class EmotionClassifierxception(Exception):
    """ Classe di Eccezioni del classificatore"""


class EmotionClassifier:
    """ Classe della rete per classificazione delle emozioni """

    def __init__(self, id_user):
        self.id_user = id_user
        self.x_train = None
        self.x_test = None
        self.y_train = None
        self.y_test = None
        self.trained_model = None
        self.labels = None

    def build(self):
        """ Funzione necessaria per il build della rete """
        try:
            config = utils.loadconfig(self.id_user)
            self.trained_model = MLPClassifier().set_params(**config)
            print("\n[" + str(self.id_user) + "]" + " Rete correttamente configurata")
        except Exception as err:
            raise EmotionClassifierxception("[" + str(self.id_user) + "] Errore nel buildind della "
                                                                      "rete: ", err) from err

    def load(self):
        """ Funzione necessaria per il caricamento all'interno della classe dei learning sets """
        try:
            self.x_train, self.y_train, self.x_test, self.y_test = utils.loadsets(self.id_user)
            if (not self.x_train.empty) and (not self.y_train.empty) and (not self.x_test.empty)\
                    and (not self.y_test.empty):
                print("\n[" + str(self.id_user) + "]" + " Learning sets correttamente caricati")
            else:
                raise EmotionClassifierxception(
                    "[" + str(self.id_user) + "]" + " Si prega di fornire "
                                                    "set di apprendimento non-nulli")
        except Exception as err:
            raise EmotionClassifierxception("[" + str(self.id_user)
                                            + "] Errore nel carricamento "
                                              "dei learning sets: ", err) from err

    def train(self):
        """ Funzione necessaria per l'addestramento della rete """
        try:
            if self.trained_model:
                self.trained_model = self.trained_model.fit(self.x_train, ravel(self.y_train))
                print("[" + str(self.id_user) + "]", self.trained_model)
            else:
                raise EmotionClassifierxception("[" + str(self.id_user)
                                                + "] Per favore eseguire il build della "
                                                + "rete prima di addestrarla")
        except Exception as err:
            raise EmotionClassifierxception("[" + str(self.id_user)
                                            + "] Errore nell'addestramento "
                                              "della rete: ", err) from err

    def classify(self, test, mode):
        """ Funzione necessaria per la classificazione di un emozione """
        # numpy.ndarray => tipo dell'argometo "test"
        try:
            if mode == "training":
                if self.trained_model:
                    self.labels = self.trained_model.predict(test)
                else:
                    raise EmotionClassifierxception(
                        "\n[" + str(self.id_user)
                        + "]" + " Per favore eseguire il build della rete prima di testarla")
            elif mode == "operative":
                if self.trained_model:
                    if test is not None:
                        # In questo caso viene fornita l'emozione classificata
                        labels = self.trained_model.predict(test)
                        emotion = settings.INDEX_TO_LABEL_DICT[labels[0]]
                        print(f'[INFO] Riproduco canzone associata all\'emozione {emotion}.')
                    else:
                        raise EmotionClassifierxception("[" + str(self.id_user)
                                                        + "] sets non riconosciuto ")
            else:
                raise EmotionClassifierxception("[" + str(self.id_user)
                                                + "]" + " mode non riconosciuta")
        except Exception as err:
            raise EmotionClassifierxception("[" + str(self.id_user)
                                            + "] Errore nella classificazione: ", err) from err

    def evaluate(self):
        """ Funzione necessaria per il calcolo dei performance indexes della rete """
        try:
            accuracy = accuracy_score(ravel(self.y_test), self.labels)
            mae = mean_absolute_error(ravel(self.y_test), self.labels)
            r2s = r2_score(ravel(self.y_test), self.labels)
            f1s = f1_score(ravel(self.y_test), self.labels, average='micro')
            outcome = {"accuracy": float(accuracy), "mean_absolute_error": float(mae),
                       "R_Squared": float(r2s), "f1_score": float(f1s)}
            with open(settings.NN_RESULTS_DIR + "/result_"
                      + str(self.id_user) + '.json', 'w') as file:
                file.write(json.dumps(outcome, indent=4))
            plot_confusion_matrix(self.trained_model, self.x_test, self.y_test)
            plt.savefig(settings.NN_RESULTS_DIR + '/confusion_matrix_' + str(self.id_user) + '.png')

        except Exception as err:
            raise EmotionClassifierxception("[" + str(self.id_user) + "] "
                                            + "Errore durante la valutazione della rete: ",
                                            err) from err

    def savemodel(self):
        """ Funzione necessaria per il salvataggio della rete deployata  """
        try:
            if self.trained_model:
                joblib.dump(self.trained_model, settings.NN_MODELS_DIR
                            + '/model_' + str(self.id_user) + '.sav')
            else:
                raise EmotionClassifierxception("[" + str(self.id_user) + "] model not found")
        except Exception as err:
            raise EmotionClassifierxception("\n[" + str(self.id_user)
                                            + "] Errore nel salvare il modello: ", err) from err
