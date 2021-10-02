# pylint: disable=too-many-instance-attributes,invalid-name,import-error
"""Modulo contenente la classe ElaborazioneImpulsi."""
import os
import json
from time import sleep
import csv
import pickle
import pathlib
import numpy as np
from scipy.integrate import simps
from mne.time_frequency import psd_array_multitaper
from Sistema_di_elaborazione_degli_impulsi import exceptions
from Sistema_di_elaborazione_degli_impulsi.config import load_config
from logger import Logger
import validatore_json
import settings
from timer_decorator import timer


class ElaborazioneImpulsi:
    """"Classe che implementa il sistema di elaborazione degli impulsi."""

    def __init__(self, user_id):

        self.__user_id = user_id
        self.__config = load_config()

        self.__samples = {}

        # Utilizzati in fase di training
        self.__X = None
        self.__y = None

        # Utilizzati in fase operativa
        self.__sample_to_classify = None
        self.__sample_label = None
        self.__session = None
        self.__sess_id = None

        self.__logger = Logger(settings.DATA_PREP_LOG_FILE)

    @timer(settings.DEBUG)
    def start_training(self, daemon=False):
        """Avvia il sistema di elaborazione degli impulsi come daemon. Trascorso un intervallo
        di tempo pari al tempo di polling specificato nel file JSON, verifica la presenza
        di nuovi dati da elaborare della fase di training, ed avvia l'elaborazione.
        """

        config_file_path = settings.DATA_PREP_POLLING_CONFIG
        self.__session = None
        if not os.path.exists(settings.DATA_PREP_PROCESSED_TIMESTAMPS):
            os.makedirs(settings.DATA_PREP_PROCESSED_TIMESTAMPS)
        pickle_file = os.path.join(settings.DATA_PREP_PROCESSED_TIMESTAMPS,
                                   f'processed_{self.__user_id}.dat')

        # default value
        polling_time = 3600
        if os.path.isfile(config_file_path):
            with open(config_file_path, 'r') as polling_file:
                polling_time = json.load(polling_file)['polling_timeout']

        while True:
            processed_timestamps = []

            if os.path.isfile(pickle_file):
                with open(pickle_file, 'rb') as file:
                    processed_timestamps = pickle.load(file)

            data_path = os.path.join(settings.DATA_PREP_INPUT_PATH,
                                     f'{settings.DATA_PREP_INPUT_BASENAME}{self.__user_id}.json')

            if os.path.isfile(data_path):
                last_modified = pathlib.Path(data_path).stat().st_mtime
                if not processed_timestamps or last_modified > processed_timestamps[-1]:
                    if settings.DEBUG:
                        self.__logger.print_log('Elaborazione dati avviata.')
                    self.__load_data(data_path)
                    self.__split_data()
                    self.__impute()
                    self.__extract_band_power()
                    self.__dump_data()
                    processed_timestamps.append(last_modified)
                    if settings.DEBUG:
                        self.__logger.print_log('Elaborazione dati completata.')
                else:
                    if settings.DEBUG:
                        self.__logger.print_log('Dati già elaborati.')

            with open(pickle_file, 'wb') as file:
                pickle.dump(processed_timestamps, file)
            if not daemon:
                break
            sleep(polling_time)

    def start(self, session):
        """Avvia la pipeline di operazioni di data preparation sul singolo campione
        (fase operativa).

        Lancia:
            SessionNotFoundException: se non viene passata alcuna sessione da elaborare.
        """

        self.__session = session
        if self.__session is None:
            raise exceptions.SessionNotFoundException('[ERRORE] Nessuna sessione fornita.')
        self.__split_data()
        self.__impute()
        self.__extract_band_power()
        self.__dump_data()

    def __load_data(self, data_path):
        """Legge il file JSON contenente le sessioni di un utente e ne valida lo schema.

        Parametri:
            Path del file da caricare.

        Lancia:
            JSONSchemaViolationException: se il JSON in input non soddisfa lo schema di validazione.
        """

        schema_path = settings.DATA_PREP_INPUT_SCHEMA

        if validatore_json.validate_json_files(data_path, schema_path):
            self.__samples = json.loads(open(data_path, 'r').read())
        else:
            raise exceptions.JSONSchemaValidationException('[ERRORE] JSON in input errato.')

    def __split_data(self):
        """Divide i dati in inpulsi relativi a una sessione e corrispondente label.
        Se ci si trova in fase operativa, recupera i dati relativi alla sessione specificata;
        in fase di training, recupera i dati di tutte le sessioni per un dato utente.

        """

        # Se siamo in fase operativa: sample passato come parametro
        if self.__session is not None:
            channels = []
            sample_to_classify = self.__session
            for i in range(self.__config['n_channels']):
                channels.append(sample_to_classify[f'canale_{i + 1}'])
            self.__sample_to_classify = np.array(channels, dtype=np.dtype(float))
            self.__sample_label = sample_to_classify['label']
            self.__sess_id = sample_to_classify['id_sessione']

        # Se siamo in fase di training: carica tutte le sessioni
        else:
            x_matrix = []
            y_vec = []
            discarded_samples = 0
            for sample in self.__samples['sessioni']:
                channels = []
                if sample['label'] is not None:
                    y_vec.append([sample['label']])
                    for i in range(self.__config['n_channels']):
                        channels.append(sample[f'canale_{i + 1}'])
                    x_matrix.append(channels)
                else:
                    discarded_samples += 1
            self.__X = np.array(x_matrix, dtype=np.dtype(float))
            self.__y = y_vec

            if settings.DEBUG and discarded_samples > 0:
                self.__logger.print_log(f'split_data: scartati {discarded_samples} campioni.')

    def __impute(self):
        """Imputa i dati mancanti della serie temporale tramite interpolazione.

        Lancia:
            ImputationErrorException: se il numero di impulsi mancanti nella time series
                                      di un canale eccede la soglia specificata nel JSON.
        """

        def nan_helper(y):
            return np.isnan(y), lambda z: z.nonzero()[0]

        tot_nan_count = 0

        # Fase operativa
        if self.__session is not None:
            int_sample = []
            for i, channel in enumerate(self.__sample_to_classify):
                nans, x = nan_helper(channel)
                channel_nan_count = np.sum(nans)
                if channel_nan_count > self.__config['nan_threshold']:
                    raise exceptions.TooManyNaNsException(
                        f'[ERRORE] impute: il numero di valori mancanti nel canale '
                        f'{i + 1} eccede la soglia di {self.__config["nan_threshold"]}.')
                channel[nans] = np.interp(x(nans), x(~nans), channel[~nans])
                int_sample.append(channel)
                tot_nan_count += channel_nan_count
            self.__sample_to_classify = np.array(int_sample, dtype=np.dtype(float))

        # Fase di training
        else:
            x_ = []
            for i, sample in enumerate(self.__X):
                sample_ = []
                for j, channel in enumerate(sample):
                    nans, x = nan_helper(channel)
                    channel_nan_count = np.sum(nans)
                    if channel_nan_count > self.__config['nan_threshold']:
                        raise exceptions.TooManyNaNsException(
                            f'[ERRORE] impute: il numero di valori mancanti nel canale {i + 1} '
                            f'del campione {j + 1} eccede la soglia di '
                            f'{self.__config["nan_threshold"]}.')
                    channel[nans] = np.interp(x(nans), x(~nans), channel[~nans])
                    sample_.append(channel)
                    tot_nan_count += channel_nan_count
                x_.append(sample_)
            self.__X = np.array(x_, dtype=np.dtype(float))

        if settings.DEBUG:
            self.__logger.print_log(f'impute: rimossi {tot_nan_count} valori NaN.')

    def __extract_band_power(self):
        """"Porta le serie temporali dal dominio del tempo a quello della frequenza,
        e per ciascun canale dell'EEG estrae la banda di potenza.
        """

        def compute_band_power(time_series, band_):
            """Calcola la potenza di banda media per la time series e la banda specificati."""

            sampling_freq = self.__config['sampling_frequency']
            b_low = band_['low']
            b_high = band_['high']
            psd, freqs = psd_array_multitaper(time_series, sampling_freq, adaptive=True,
                                              normalization='full', verbose='CRITICAL')
            freq_res = freqs[1] - freqs[0]
            idx_band = np.logical_and(freqs >= b_low, freqs <= b_high)
            bp_ = simps(psd[idx_band], dx=freq_res) / simps(psd, dx=freq_res)
            return bp_

        bands = self.__config['bands']

        # Fase operativa
        if self.__session is not None:
            bp_sample = []
            for i, channel in enumerate(self.__sample_to_classify):
                for key, band in bands.items():
                    bp = compute_band_power(channel, band)
                    bp_sample.append(bp)
            self.__sample_to_classify = bp_sample

        # Fase di training
        else:
            bp_samples = []
            for sample in self.__X:
                bp_sample = {}
                for i, channel in enumerate(sample):
                    bp_bands = {}
                    for key, band in bands.items():
                        bp = compute_band_power(channel, band)
                        bp_bands[f'{key}'] = bp
                    bp_sample[f'canale{i + 1}'] = bp_bands
                bp_samples.append(bp_sample)
            self.__X = bp_samples

    def __dump_data(self):
        """Scrive i dati elaborati su un file. Il tipo di file generato dipende
        da se ci si trova in fase operativa o di training.
        Ciascun utente possiede la propria cartella identificata dall'id utente.
        """

        # Fase operativa
        if self.__session is not None:
            out_path = settings.DATA_PREP_OPERATIVE_OUTPUT_PATH
            if not os.path.exists(out_path):
                os.makedirs(out_path)
            file_name = os.path.join(out_path, f'{self.__user_id}_{self.__sess_id}.csv')

            with open(file_name, "w", newline="") as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerow(self.__sample_to_classify)

        # Fase di training
        else:
            out_path = os.path.join(settings.DATA_PREP_TRAINING_OUTPUT_PATH, self.__user_id)
            if not os.path.exists(out_path):
                os.makedirs(out_path)
            file_name = os.path.join(out_path, 'processed_data.json')
            output = [{'label': self.__y[i][0], 'features': self.__X[i]}
                      for i in range(len(self.__y))]
            json_out = {'impulsi': output}
            with open(file_name, 'w') as file:
                json.dump(json_out, file)
