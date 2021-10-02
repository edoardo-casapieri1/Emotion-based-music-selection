"""file contenente l'implementazione del sistema di raccorda degli impulsi """
import csv
import json
import random
from Sistema_di_raccolta_degli_impulsi.parametri_raccolta import ParametriConfigurazioneRaccolta
import settings
from validatore_json import validate_json_files
import timer
from logger import Logger
from timer_decorator import timer as timer_test


class SistemaDiRaccoltaDati:
    """classe che offre metodi per ottenere i dati aggregati delle sessioni"""
    _config_path = settings.RACC_CONFIG_FILE
    _config_schema_path = settings.RACC_CONFIG_SCEMA
    _dataset_path = settings.RACC_DATASET_INPUT
    _output_base_path = settings.RACC_OUTPUT_BASE_PATH

    def __init__(self):
        # controllo validità del file di configurazione
        if not validate_json_files(self._config_path, self._config_schema_path):
            raise Exception("[ERRORE] Il file di configurazione del sistema di raccolta"
                            " degli impulsi non è corretto")

        # recupera la configurazione dell'ingegnere dei dati sotto forma di oggetto Parametri
        try:
            with open(self._config_path, 'r') as input_file:
                parameters = json.load(input_file)
            self.params = ParametriConfigurazioneRaccolta(**parameters)
        except IOError as err:
            raise Exception("[ERRORE] Errore durante il caricamento dei parametri"
                            " nella configurazione") from err
        self.logger = Logger(settings.RACC_LOG_FILE)

        # recupero il numero di sessioni nel dataset di ingresso (utile per get_session_to_classify)
        self._numero_sessioni = self._get_number_sessions()

    @timer_test(True)
    def get_training_data(self):
        """
        utilizza la classe timer per impostare il recupero dei dati delle sessioni
        dal dataset d'ingresso scrive il file json risultante nella cartella di
        Output indicando l'id dell'utente che ha effettuato la fase di training
        nel nome del file
        """
        sessions = {"sessioni": []}
        # -1 significa che non è stato ancora ricevuto l'id dell'utente che sta facendo il training
        id_user = -1
        i = 0
        while True:
            time_thread = timer.Timer(self.params.periodo_pooling, self.params.numero_periodi)
            time_thread.start()
            session_dict, id_user_session = self._extract_session_time_series(i)

            if not session_dict:
                self.logger.print_log("Sessioni di training finite")
                break

            sessions["sessioni"].append(session_dict)
            id_user = id_user_session if id_user == -1 else id_user

            self.logger.print_log("fine recupero sessione : " + str(i))
            if i == self.params.numero_sessioni_training:
                break
            time_thread.join()
            i = i + 1
        self._write_json_output(sessions, id_user)
        return id_user

    def get_session_to_classify(self):
        """
        estraggo un indice di sessione casuale tra 0 e self.numero_sessioni
        e ne richiedo l'estrazione chiamando la self._extract_session_time_series
        """
        # extract a random session index
        random_session_index = random.randint(0, self._numero_sessioni)

        # retrieve the dictionary of the session to be classified
        session_dict, id_user = self._extract_session_time_series(random_session_index)
        return session_dict, id_user

    # INIZIO METODI PRIVATI

    def _extract_session_time_series(self, session_id):
        # calcolo l'indice della riga base della sessione che voglio estrarre
        base_index = (session_id * 22) + 1
        csv_data_list = self._get_csv_session_rows(base_index)

        # controllo se il file è finito
        if not csv_data_list:
            return {}, 0

        session_dict = self._create_session_dict(csv_data_list, session_id)
        id_utente = csv_data_list[0][1]

        return session_dict, id_utente

    # ritorna tutte le righe, in formato csv, delle time series appartenenti ad una sessione
    def _get_csv_session_rows(self, base_index) -> list:
        csv_rows = []
        # apro il file csv ed estraggo solo le righe della sessione che mi interessa
        try:
            with open(self._dataset_path, encoding='utf-8') as csv_file:
                reader = csv.reader(csv_file, delimiter=',')

                i = 0
                for row in reader:
                    if i in range(base_index, base_index + self.params.numero_canali_elmetto):
                        # mi segno solo le righe della sessione
                        csv_rows.append(row)
                    if i > base_index + self.params.numero_canali_elmetto:  # inutile proseguire
                        break
                    i = i + 1
        except IOError as err:
            raise Exception("[ERRORE] Errore durante l'estrazione "
                            "delle righe a partire da: " + str(base_index)) from err
        return csv_rows

    def _create_session_dict(self, csv_list, session_id) -> dict:
        session_dict = {}
        id_app = csv_list[0][0]
        label = csv_list[0][2]

        # creo la l'oggetto base
        session_dict["id_applicazione"] = int(id_app)
        session_dict["id_sessione"] = session_id
        session_dict["label"] = label
        for i in range(self.params.numero_canali_elmetto):
            session_dict["canale_" + str(i + 1)] = []

        # so che ci sono 1375 colonne di dati + 4 per id applicazione, id utente, emozione e canale
        for column_index in range(4, self.params.numero_impulsi_sessione + 4):
            if not self._check_impulse(csv_list, column_index):  # impulso da scartare
                for channel_index in range(self.params.numero_canali_elmetto):
                    session_dict["canale_" + str(channel_index + 1)].append(None)  # scartato
                continue
            for channel_index in range(self.params.numero_canali_elmetto):
                if csv_list[channel_index][column_index] == '':
                    value = None
                else:
                    # appendo i valori corretti nelle apposite liste
                    value = float(csv_list[channel_index][column_index])
                session_dict["canale_" + str(channel_index + 1)].append(value)
        return session_dict

    # controlla se l'impulso alla colonna indicata ha abbastanza campioni per essere valutato
    def _check_impulse(self, data_list, column_index) -> bool:

        missing_values = 0
        for channel_index in range(self.params.numero_canali_elmetto):
            if data_list[channel_index][column_index] == '':
                missing_values = missing_values + 1
        if missing_values >= self.params.max_campioni_mancanti:
            self.logger.print_log("L'impulso " + str(column_index - 3) + " scartato")
            return False
        return True

    def _write_json_output(self, dictionary, id_user):
        try:
            with open(self._output_base_path + id_user + ".json", 'w', encoding='utf-8') as jsonf:
                jsonf.write(json.dumps(dictionary, indent=4))
        except IOError as err:
            raise Exception(
                "[ERRORE] Errore durante la scrittura del file"
                " json per l'utente: " + str(id_user)) from err

    def _get_number_sessions(self):
        tot_sessions = 0
        try:
            with open(self._dataset_path, encoding='utf-8') as csv_file:
                reader = csv.reader(csv_file, delimiter=',')

                for row in reader:
                    if row[3] == str(self.params.numero_canali_elmetto):
                        tot_sessions = tot_sessions + 1
        except IOError as err:
            raise Exception("[ERRORE] Errore durante l'estrazione sel numero delle righe") from err
        return tot_sessions
