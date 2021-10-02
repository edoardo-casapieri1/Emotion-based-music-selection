"""Utility necessarie per il sistema di monitoraggio"""
import json
from datetime import datetime
import random
import os
import validatore_json
import settings


def loadconfig(userid):
    """Funzione necessaria per il caricamento del file json di configurazione della rete"""
    conf = settings.PERF_MONITORING_CONF_DIR
    schema = settings.PERF_MONITORING_SCHEMA
    try:
        if validatore_json.validate_json_files(conf + "configurazioneID"
                                               + str(userid) + ".json", schema):
            with open(settings.PERF_MONITORING_CONF_DIR
                      + "configurazioneID" + str(userid) + ".json", 'r') as json_file:
                data = json.load(json_file)
        else:
            raise Exception("[" + str(userid)
                            + "]" + " Configurazione per il monitoraggio non valida  ")
        return data
    except IOError as err:
        raise Exception("[" + str(userid) + "]" +
                        " Errore durante il caricamento della configurazione") from err


def loadinput(userid, timestamp_min, timestamp_max):
    """Funzione necessaria per il caricamento del file json di input"""
    reports_path = settings.REPORTS_DIRECTORY_PATH
    data = reports_path + 'input_jsonID' + str(userid) + '.json'
    try:
        with open(data, 'r') as json_file:
            input_data = json.load(json_file)
            # print(input)
            new_input = {
                "messaggi_disaccordo": [],
                "canzoni_ascoltate": []
            }
            for mess in input_data["messaggi_disaccordo"]:
                if timestamp_min <= mess <= timestamp_max:
                    new_input["messaggi_disaccordo"].append(mess)

            for canz in input_data["canzoni_ascoltate"]:
                if timestamp_min <= canz <= timestamp_max:
                    new_input["canzoni_ascoltate"].append(canz)
            # print(new_input)
            if len(new_input["canzoni_ascoltate"]) == 0:  # se non ci sono canzoni ascoltate
                raise Exception("[" + str(userid)
                                + "]" + " input completamente non valido  ")
            print("Totale emozioni classificate durante il periodo: " +
                  str(len(new_input["canzoni_ascoltate"])))
            print("Emozioni classificate NON correttamente durante il periodo: " +
                  str(len(new_input["messaggi_disaccordo"]))
                  )
            return new_input
    except IOError as err:
        raise Exception("[" + str(userid) + "]" +
                        " Errore durante il caricamento di input") from err


def reset_input_file(userid):
    """Reset del file di input"""
    reports_path = settings.REPORTS_DIRECTORY_PATH
    file_path = reports_path + 'input_jsonID' + str(userid) + '.json'
    new_input = {
        "messaggi_disaccordo": [],
        "canzoni_ascoltate": []
    }

    json_file = open(file_path, 'w', encoding='utf-8')
    json_file.write(json.dumps(new_input, indent=4))
    json_file.close()


def crea_storico(userid):
    """Funzione necessaria per creare lo storico"""
    dizionario_store_performance = {
        "storico": []
    }
    jsonf = open(settings.PERF_MONITORING_HISTORICAL
                 + "storico_performanceID" + str(userid) + ".json", 'w', encoding='utf-8')
    jsonf.write(json.dumps(dizionario_store_performance, indent=4))
    jsonf.close()


def create_or_store_input(user_id):
    """Funzione che Popola il file di input"""
    reports_path = settings.REPORTS_DIRECTORY_PATH

    if os.path.exists(reports_path + '/input_jsonID' + str(user_id) + '.json'):
        with open(reports_path + '/input_jsonID' + str(user_id)
                  + '.json', encoding='utf-8') as jsonf:
            dictionary = json.load(jsonf)
    else:
        dictionary = {"messaggi_disaccordo": [],
                      "canzoni_ascoltate": []}

    now = datetime.now()
    timestamp_now = datetime.timestamp(now)

    random_int = random.randint(0, 10)

    if random_int > 7:
        dictionary["messaggi_disaccordo"].append(timestamp_now)

    dictionary["canzoni_ascoltate"].append(timestamp_now)

    with open(reports_path + '/input_jsonID' + str(user_id) +
              '.json', 'w', encoding='utf-8') as jsonf:
        jsonf.write(json.dumps(dictionary, indent=4))
