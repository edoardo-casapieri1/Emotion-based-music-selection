import csv
import os
from time import process_time
import settings


def timer(debug=False):
    """Decoratore per misurare il CPU time dei metodi; scrive il risultato su un file CSV.
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            t_start = process_time()
            result = func(*args, **kwargs)
            t_end = process_time()
            delta = t_end - t_start
            if debug:
                csv_file = settings.TIMER_CSV_PATH
                file_exists = os.path.isfile(csv_file)

                with open(csv_file, 'a', newline='') as csv_f:
                    header = ['function_name', 'time']
                    writer = csv.writer(csv_f, dialect='excel')
                    if not file_exists:
                        writer.writerow(header)
                    writer.writerow([func.__name__, delta])

            return result
        return wrapper
    return decorator
