"""file sistema di monitoraggio"""
import json
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import timer
import settings
from sistema_di_monitoraggio_delle_performance.utility import loadconfig, loadinput, \
    crea_storico, reset_input_file

class SistemaDiMonitoraggio:
    """ Classe del sistema di monitoraggio """

    def __init__(self, id_user):
        conf = loadconfig(id_user)
        crea_storico(id_user)
        self.id_utente = id_user
        self.periodo_monitoraggio = conf["periodo_monitoraggio"]
        self.numero_periodi = conf["numero_periodi"]
        self.threshold = conf["threshold"]
        self.periodi_visualizzati = 0
        self.timestamp_min = 0
        self.timestamp_max = 0
        reset_input_file(self.id_utente)

    def monitoring_loop(self, file_available_event, logger):
        """ funzione necessaria per l'elaborazione dei dati alla scadenza del timer """
        periodi_da_visualizzare = settings.VISUALIZED_PERIODS
        while True:
            # generazione_store_input(self.periodo_monitoraggio,
            #       self.numero_periodi, self.id_utente)
            self.imposta_intervallo_timestamp(logger)
            # create_or_store_input(self.id_utente)
            thread1 = timer.Timer(self.periodo_monitoraggio, self.numero_periodi)
            thread1.start()
            thread1.join()
            print('MONITORING_LOOP: fine periodo monitoraggio ' +
                   str(self.periodi_visualizzati + 1))
            file_available_event.wait()
            file_available_event.clear()
            dati_input = loadinput(self.id_utente, self.timestamp_min, self.timestamp_max)
            file_available_event.set()
            percentuale = self.calcolo_percentuale(dati_input, logger)
            self.aggiornamento_storico(percentuale, periodi_da_visualizzare)
            self.disegna_grafico(periodi_da_visualizzare)
            reset = self.controllo_cambiamento_config()
            # Se la configurazione è cambiata
            if reset:
                self.periodi_visualizzati = 0
                open(settings.PERF_MONITORING_HISTORICAL + "storico_performanceID"
                     + str(self.id_utente) + ".json",
                     'w').close()
                # Flushing dello storico
                crea_storico(self.id_utente)
            # se la percentuale di approvazione è minore della soglia riallenare la rete'''
            if percentuale < self.threshold:
                logger.print_log("Soglia di approvazione inferiore alla soglia")
                print("Retraining ...")
                break

    def calcolo_percentuale(self, dati_input, logger):
        """Funzione che calcola la percentuale di accordo"""
        num_disaccordi = len(dati_input['messaggi_disaccordo'])
        num_canzoni = len(dati_input['canzoni_ascoltate'])
        logger.print_log("Numero messaggi di disaccordo ultimo periodo: "
                         + str(num_disaccordi))
        logger.print_log("Numero canzoni ascoltate ultimo periodo: " + str(num_canzoni))
        canzoni_approvate = num_canzoni - num_disaccordi
        percentuale = int((canzoni_approvate / num_canzoni) * 100)
        logger.print_log("Percentuale approvazione: " + str(percentuale))
        return percentuale

    def aggiornamento_storico(self, percentuale, periodi_da_visualizzare):
        """Funzione che aggiunge il nuovo dato allo storico"""
        with open(settings.PERF_MONITORING_HISTORICAL + "storico_performanceID" +
                  str(self.id_utente) + ".json", 'r') as storico_fr:
            dati_storico = json.load(storico_fr, encoding='utf-8')
            storico_fr.close()
        with open(settings.PERF_MONITORING_HISTORICAL + "storico_performanceID"
                  + str(self.id_utente) + ".json",
                  'w') as storico_fw:
            dati_storico["storico"].append({"id_utente": self.id_utente,
                                            "percentuale": int(percentuale)})
            if len(dati_storico['storico']) >= periodi_da_visualizzare + 1:
                # Elimino il meno recente
                dati_storico["storico"].pop(0)
            storico_fw.write(json.dumps(dati_storico, indent=4))
            storico_fw.close()

    def imposta_intervallo_timestamp(self, logger):
        """ Funzione per IMPOSTARE i timestamp degli estremi del periodo di monitoraggio """
        now = datetime.now()
        if self.periodo_monitoraggio == "minuti":
            end_period = now + timedelta(minutes=self.numero_periodi)
        elif self.periodo_monitoraggio == "secondi":
            end_period = now + timedelta(seconds=self.numero_periodi)
        elif self.periodo_monitoraggio == "ore":
            end_period = now + timedelta(hours=self.numero_periodi)
        elif self.periodo_monitoraggio == "giorni":
            end_period = now + timedelta(days=self.numero_periodi)
        elif self.periodo_monitoraggio == "settimane":
            end_period = now + timedelta(weeks=self.numero_periodi)
        timestamp_now = datetime.timestamp(now)
        # print("timestamp =", timestamp_now)
        timestamp_end = datetime.timestamp(end_period)
        # print("timestamp =", timestamp_end)
        if self.timestamp_max == 0:
            self.timestamp_min = timestamp_now
        else:
            # Il timestamp minimo è il max timestamp del periodo precedente'''
            # Se alla fine di un periodo c'è un retraining fa la stessa cosa '''
            self.timestamp_min = self.timestamp_max
        self.timestamp_max = timestamp_end
        logger.print_log("Timestamp fine periodo monitoraggio: " + str(self.timestamp_max))
        logger.print_log("Timestamp inizio periodo monitoraggio: " + str(self.timestamp_min))

    def controllo_cambiamento_config(self):
        """ funzione  per controllare cambiamenti nella configurazione del sistema """
        with open(settings.PERF_MONITORING_CONF_DIR + "configurazioneID"
                  + str(self.id_utente) + ".json",
                  'r') as conf_f:
            dati_conf = json.load(conf_f, encoding='utf-8')
            changed = False
            if self.periodo_monitoraggio != dati_conf['periodo_monitoraggio']:
                changed = True
                self.periodo_monitoraggio = dati_conf['periodo_monitoraggio']
            if self.numero_periodi != dati_conf['numero_periodi']:
                changed = True
                self.numero_periodi = dati_conf['numero_periodi']
            if self.threshold != dati_conf['threshold']:
                changed = True
                self.threshold = dati_conf["threshold"]
            return changed

    def disegna_grafico(self, periodi_da_visualizzare):
        """ funzione per disegnare il grafico delle percentuali di approvazione """
        names = []
        values = []
        with open(settings.PERF_MONITORING_HISTORICAL + "storico_performanceID"
                  + str(self.id_utente) + ".json",
                  'r') as storico_fr:
            dati_storico = json.load(storico_fr, encoding='utf-8')
            storico_fr.close()
        num_periodi_precedenti = len(dati_storico['storico'])
        self.periodi_visualizzati = self.periodi_visualizzati + 1
        if self.periodi_visualizzati >= periodi_da_visualizzare + 1:
            j = self.periodi_visualizzati - periodi_da_visualizzare + 1
        else:
            j = 1
        for i in range(num_periodi_precedenti):
            names.append('per' + str(j))
            values.append(dati_storico["storico"][i]["percentuale"])
            j = j + 1
        fig = plt.figure()
        ax_ = fig.add_subplot(111)
        ax_.set_ylabel('Percentuale di approvazione')
        ax_.set_xlabel("Periodo di monitoraggio:" + self.periodo_monitoraggio
                   + ":" + str(self.numero_periodi))
        #fig.ylabel('Percentuale di approvazione')
        #fig.xlabel("Periodo di monitoraggio:" + self.periodo_monitoraggio
        #           + ":" + str(self.numero_periodi))
        ax_.set_ylim([1, 100])
        ax_.plot(names, values, color='green', marker="o")
        names.clear()
        values.clear()
        ax_.axhline([int(self.threshold)])
        ax_.plot(color='blue')
        fig.suptitle('Monitoraggio delle performance  Periodo corrente:'
                     + str(self.periodi_visualizzati) + '  Utente:' + str(self.id_utente))
        # plt.show()
        path = settings.PERF_MONITORING_RESULTS + 'Result_' + str(self.id_utente) + '.png'
        fig.savefig(path)
        plt.close()
