from Sistema_di_raccolta_degli_impulsi.raccolta_impulsi import SistemaDiRaccoltaDati
import validatore_json
import settings
from Sistema_di_elaborazione_degli_impulsi.elaborazione_impulsi import ElaborazioneImpulsi
from Sistema_di_train_val_test import emotion_classifier
from Sistema_di_train_val_test import utils
from sistema_di_monitoraggio_delle_performance import utility


def operative_phase(file_available_event):
    sis_racc = SistemaDiRaccoltaDati()

    session_dict, id_user = sis_racc.get_session_to_classify()
    session_id = session_dict["id_sessione"]

    if not validatore_json.validate_json_with_schema_path(session_dict, settings.SESSIONE_DA_CLASSIFICARE_SCHEMA):
        raise Exception("Errore la sessione non rispetta lo schema")

    el = ElaborazioneImpulsi(id_user)
    el.start(session_dict)

    try:
        emotionclassifier = utils.loadmodel(id_user)
        print("\n[" + str(id_user) + "] model correctly loaded")
        tobeclassified = utils.loadoperativesets(str(id_user) + "_" + str(session_id) + ".csv", id_user)
        print("\n####### Classifico ###########\n")
        emotionclassifier.classify(tobeclassified, "operative")

    except emotion_classifier.EmotionClassifierxception as error:
        print(error)

    file_available_event.wait()
    file_available_event.clear()
    utility.create_or_store_input(id_user)
    file_available_event.set()
