"""classe usata come formato standard per i parametri di configurazione"""


class ParametriConfigurazioneRaccolta:
    """metodo init usato per inizializzare le variabili lette dal file di configurazione"""

    def __init__(self, max_campioni_mancanti,
                 numero_canali_elmetto,
                 numero_impulsi_sessione,
                 periodo_pooling,
                 numero_periodi,
                 numero_sessioni_training):
        self.max_campioni_mancanti = max_campioni_mancanti
        self.numero_canali_elmetto = numero_canali_elmetto
        self.numero_impulsi_sessione = numero_impulsi_sessione
        self.periodo_pooling = periodo_pooling
        self.numero_periodi = numero_periodi
        self.numero_sessioni_training = numero_sessioni_training
