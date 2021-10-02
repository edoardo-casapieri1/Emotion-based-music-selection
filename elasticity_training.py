import json
import csv
import os
from math import ceil
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import gridspec
import settings
from training import training_phase


def create_or_insert_in_list(building_dict, key, value):
    if key not in building_dict:
        building_dict[key] = list()
    building_dict[key].append(value)


class TrainingElasticity:

    def __init__(self, n_sessions_list):

        if isinstance(n_sessions_list, str):
            with open(n_sessions_list, 'r') as f:
                self.__n_sessions_list = json.load(f)['numero_sessioni']
        elif isinstance(n_sessions_list, list):
            self.__n_sessions_list = n_sessions_list
        else:
            raise Exception('n_sessions_list deve essere un path a un JSON o una lista.')

    @staticmethod
    def clean_csv_file():
        if os.path.isfile(settings.TIMER_CSV_PATH):
            os.remove(settings.TIMER_CSV_PATH)

    def start(self):
        self.clean_csv_file()

        for n_sessions in self.__n_sessions_list:
            print(f'[INFO] Avviato test con {n_sessions} sessioni.')
            self.rewrite_data_ingestion_config(n_sessions)
            training_phase()

        return self.__create_dataframe()

    def __create_dataframe(self):
        with open(settings.TIMER_CSV_PATH, 'r') as csv_f:
            df_in = pd.read_csv(csv_f)
            columns = ['num_sessioni', 'raccolta', 'elaborazione',
                       'generatore_insiemi', 'train_val_test', 'totale']
            data = []

            for i in range(len(self.__n_sessions_list)):
                temp = [self.__n_sessions_list[i]]

                for j in range(5):
                    if j != 3:
                        temp.append(df_in.iloc[i * 5 + j]['time'])
                    else:
                        temp[2] += df_in.iloc[i * 5 + j]['time']

                temp.append(sum(temp[1:]))
                data.append(temp)

            df_out = pd.DataFrame(data=data, columns=columns)
            return df_out

    def generate_plots(self):
        df = self.__create_dataframe()
        self.__generate_pie_charts(df)
        self.__generate_elasticity_diagram(df)

    @staticmethod
    def __generate_elasticity_diagram(dataframe):
        plt.rcParams.update({'font.size': 10})
        x = dataframe['num_sessioni'].to_numpy()
        y = dataframe['totale'].tolist()
        m, b = np.polyfit(x, y, 1)
        _, ax = plt.subplots(1)
        ax.plot(x, y, '-o', label='Tempi registrati')
        ax.plot(x, m * x + b, '--', label=f'Linea di regressione: {round(m, 2)}x - {abs(round(b, 2))}')
        ax.set_ylim(ymin=0)
        ax.set_xlim(xmin=0)
        ax.set_xlabel('Numero di sessioni')
        ax.set_ylabel('Tempo (s)')
        ax.set_title('Diagramma di elasticità')
        ax.legend(loc='upper left')
        path = os.path.join(settings.TEST_RESULTS, 'elasticity_diagram.svg')
        plt.savefig(path)
        plt.clf()

    @staticmethod
    def __generate_pie_charts(dataframe):
        plt.rcParams.update({'font.size': 6})

        n_charts = len(dataframe.index)
        cols = 2
        rows = int(ceil(n_charts / cols))

        gs = gridspec.GridSpec(rows, cols)
        fig = plt.figure()
        labels = dataframe.columns.tolist()[1:5]
        for n in range(n_charts):
            ax = fig.add_subplot(gs[n])
            values = dataframe.iloc[n].tolist()[1:5]
            total = dataframe.iloc[n]['totale']
            explode = (0.2, 0.2, 0.2, 0.2)
            wedges, texts = ax.pie(values, explode=explode,
                                   shadow=True, startangle=90)
            ax.axis('equal')
            ax.set_title(f'{int(dataframe.iloc[n]["num_sessioni"])} sessioni')
            pcts = [round(value / total * 100, 2) for value in values]
            legend_labels = [f'{labels[i]}: {pcts[i]}%' for i in range(len(labels))]
            ax.legend(wedges, legend_labels,
                      loc="upper center",
                      bbox_to_anchor=(0, 1))

        path = os.path.join(settings.TEST_RESULTS, 'pie_charts.svg')
        plt.savefig(path)

    @staticmethod
    def create_dataframe_from_csv(num_session):
        df_dict = dict()

        df_dict['num_session_training'] = num_session #list(num_session)

        with open(settings.TIMER_CSV_PATH, 'r') as csv_f:
            reader = csv.reader(csv_f, delimiter=',')

            skip_first = True
            for row in reader:
                if skip_first:
                    skip_first = False
                    continue

                create_or_insert_in_list(df_dict, row[0], row[1])

        df = pd.DataFrame(df_dict)

        df.to_csv("final_time_summary.csv", sep=";")

    @staticmethod
    def rewrite_data_ingestion_config(n_sessions):
        with open(settings.RACC_CONFIG_FILE, 'r') as conf_f:
            config = json.load(conf_f)

        config['numero_sessioni_training'] = n_sessions

        with open(settings.RACC_CONFIG_FILE, 'w') as conf_f:
            json.dump(config, conf_f)


if __name__ == '__main__':
    TrainingElasticity([25, 50, 100, 150, 200, 250]).generate_plots()
