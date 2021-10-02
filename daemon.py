""""Daemon per i sistemi che devono fare polling periodico da file."""
from threading import Thread
from Sistema_di_elaborazione_degli_impulsi.elaborazione_impulsi import ElaborazioneImpulsi

if __name__ == '__main__':
    elab = ElaborazioneImpulsi(1)
    elab_thread = Thread(target=elab.start_training(True))
    elab_thread.daemon = True
    elab_thread.start()
    elab_thread.join()
