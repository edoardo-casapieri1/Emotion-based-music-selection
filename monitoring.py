from sistema_di_monitoraggio_delle_performance import monitoraggio_performance
from logger import Logger
import settings


def monitoring_phase(userid, training_finished_event, retrain_event, file_available_event):
    print("\n####### Sistema di monitoraggio delle performance ###########\n")

    monitor = monitoraggio_performance.SistemaDiMonitoraggio(userid)
    logger = Logger(settings.PERF_MONITORING_LOGFILE)

    while 1:
        training_finished_event.wait()
        training_finished_event.clear()

        monitor.monitoring_loop(file_available_event, logger)

        retrain_event.set()

