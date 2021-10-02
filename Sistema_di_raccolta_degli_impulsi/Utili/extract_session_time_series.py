import csv
import json

# controlla se l'impulso alla colonna indicata ha abbastanza campioni per essere valutato
def check_impulse(data_list, column_index) -> bool:

    missing_values = 0
    for channel_index in range(22):
        if data_list[channel_index][column_index] == '':
            missing_values = missing_values + 1
    if missing_values >=2:
        print("L'impulso " + str(column_index - 3) + " scartato")
        return False
    return True


'''
Questa funzione prende tutti i dati delle time series della sessione indicata come parametro
e ritorna un oggetto json di questo tipo:
{
      "id_sessione": 1, <- ipotizzando che sia stato passato l'id 1
      "id_utente": 1, <- a quale utente si riferisce
      "label": "excited", <- la label riportata
      "id_applicazione": 3, <- applicazione che sta usando l'utente
      "canale_1": [3.14, 434, ecc], <- una serie di liste contenenti tutti i campioni trovati nei vari canali
      "canale_2": [3.14, 434, NaN, ecc], <- da notare che se un valore manca e l'impulso è comunque valido, allora ci metto un NaN
      ecc...
}
'''
def extract_session_time_series(csv_file_path, json_file_path, sessionId):
    # calcolo l'indice della riga base della sessione che voglio estrarre
    base_index = (sessionId * 22) + 1
    session_dict = {}
    csv_data_list = []

    try: # apro il file csv ed estraggo solo le righe della sessione che mi interessa
        with open(csv_file_path, encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file, delimiter=',')

            i = 0
            for row in reader:
                if i in range(base_index, base_index + 22): # mi segno solo le righe della sessione
                    csv_data_list.append(row)
                if i > base_index + 22: # sarebbe inutile proseguire
                    break
                i = i + 1
    except IOError as err:
        raise Exception("[ERRORE] Errore durante l'estrazione della sessione: " + str(sessionId)) from err

    # controllo se il file è finito
    if not csv_data_list:
        print("file finito")
        exit(0)

    id_app = csv_data_list[0][0]
    id_utente = csv_data_list[0][1]
    label = csv_data_list[0][2]

    # creo la l'oggetto base
    session_dict["id_applicazione"] = int(id_app)
    session_dict["id_sessione"] = sessionId
    #session_dict["id_utente"] = int(id_utente)
    session_dict["label"] = label
    for i in range(22):
        session_dict["canale_" + str(i + 1)] = []

    # da basic_info_dataset.py so che ci sono 1375 colonne di dati + 3 per id applicazione, id utente, emozione e canale
    for column_index in range(4, 1379):
        if check_impulse(csv_data_list, column_index) == False: # impulso da scartare
            continue
        for channel_index in range(22):
            value = 0
            if csv_data_list[channel_index][column_index] == '':
                value = None
            else:
                # appendo i valori corretti nelle apposite liste
                value = float(csv_data_list[channel_index][column_index])
            session_dict["canale_" + str(channel_index + 1)].append(value)

    try:
        with open(json_file_path, 'w', encoding='utf-8') as jsonf:
            jsonf.write(json.dumps(session_dict, indent=4))
    except IOError as err:
        raise Exception("[ERRORE] Errore durante la scrittura del file json per la sessione: " + str(sessionId)) from err


# codice driver

SessId = 0
csvFilePath = '../Data/shortDataset.csv'
jsonFilePath = '../Data/shortDataset3.json'

extract_session_time_series(csvFilePath, jsonFilePath, SessId)
