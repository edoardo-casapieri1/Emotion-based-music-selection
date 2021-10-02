"""Driver che lancia i thread di training, di fase operativa e di monitoraggio"""
from monitoring import monitoring_phase
from operativa import operative_phase
from training import training_phase
import threading
import time

if __name__ == '__main__':
    time_to_sleep = 2

    training_finished_event = threading.Event()
    retrain_event = threading.Event()
    file_available_event = threading.Event()

    userid = training_phase()
    training_finished_event.set()
    file_available_event.set()  # all'avvio è disponibile

    monitoring_thread = threading.Thread(name='Monitoring', target=monitoring_phase,
                                         args=(userid, training_finished_event, retrain_event, file_available_event))
    monitoring_thread.start()

    while True:
        if retrain_event.isSet():
            training_phase()
            training_finished_event.set()
            retrain_event.clear()

        operative_phase(file_available_event)
        time.sleep(time_to_sleep)
