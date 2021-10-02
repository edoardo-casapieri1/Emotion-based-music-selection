from Sistema_di_raccolta_degli_impulsi.raccolta_impulsi import SistemaDiRaccoltaDati
from Sistema_di_elaborazione_degli_impulsi.elaborazione_impulsi import ElaborazioneImpulsi
from Generatore_degli_insiemi_di_learning import quality_check
from Generatore_degli_insiemi_di_learning import generazione_insiemi
from Sistema_di_train_val_test import utils
from timer_decorator import timer as timer_test


@timer_test(True)
def quality_check_wrapper():
    qc = quality_check.QualityCheck()
    qc.class_quality_for_all_user()


def training_phase():
    sis_racc = SistemaDiRaccoltaDati()
    id_user = -1

    while 1:
        print("Inizio Fase di raccolta dei dati per il training")
        id_user = sis_racc.get_training_data()
        print("Fine raccolta dati per il training")
        print("Inizio Fase di elaborazione dei dati")
        el = ElaborazioneImpulsi(id_user)
        el.start_training()
        print("Fine elaborazione dati")
        quality_check_wrapper()

        while 1:
            try:
                option = int(
                    input('Le classi sono distribuite correttamente?\n'
                          '1 = Sì , 2 = No\n'))
                if option in (1, 2):
                    break
            except ValueError:
                print('opzione non valida')

        if option == 1:
            break  # procedo con la creazione della rete

    generazione_insiemi.GeneratoreInsiemiDiLearning().generate_learning_sets()

    emotionclassifier = utils.buildfromscratch(id_user)
    print("\n[" + str(id_user) + "] model correctly built and saved")
    return id_user
