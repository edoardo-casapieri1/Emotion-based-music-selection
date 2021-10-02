"""Modulo necessario per l'implementazione del timer"""
from threading import Thread
import time


class Timer(Thread):
    """classe per il timer"""
    secondi = 0

    def __init__(self, periodo, numero):
        self.periodo = periodo
        self.numero = numero
        Thread.__init__(self)

    def run(self, verbose=False):
        if verbose:
            print("TIMER:Timer avviato")
        if self.periodo == "minuti":
            self.secondi = int(self.numero) * 60
        elif self.periodo == "ore":
            self.secondi = int(self.numero) * 3600
        elif self.periodo == "giorni":
            self.secondi = int(self.numero) * 86400
        elif self.periodo == "settimane":
            self.secondi = int(self.numero) * 604800
        elif self.periodo == "secondi":
            self.secondi = int(self.numero)
        time.sleep(self.secondi)
        if verbose:
            print("TIMER:Timer scaduto")
