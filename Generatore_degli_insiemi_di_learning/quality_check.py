"""
Il file contiene la classe che genera i radar plot,
 con cui l'ingegnere dei dati può controllare la compatezza delle classi
"""

import os
from pathlib import Path
import json
# import matplotlib.cm as cm
from matplotlib import cm
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import numpy as np
import settings
from validatore_json import validate_json_files
from Generatore_degli_insiemi_di_learning.json_to_dataframe import json_to_dict_of_dataframe


def get_plot_colors(how_many):
    """
    Crea una lista contenente i colori, per differenziare i sample sul grafico
    :param how_many: numero di colori diversi desiderati
    :return: lista di colori
    """
    # colormap = cm.viridis
    # color_list = [colors.rgb2hex(colormap(i)) for i in np.linspace(0, 0.9, how_many)]

    colormap = cm.get_cmap('viridis', how_many)
    color_list = [colors.rgb2hex(colormap(i)) for i in np.linspace(0, 1, how_many)]
    return color_list


class QualityCheck:
    """
    Classe che genera i radar plot,
     con cui l'ingegnere dei dati può controllare la compatezza delle classi
    """

    def __init__(self):
        conf_path = settings.GEN_INSIEMI_LEARNING_CONFIG_PATH_QC
        schema_path = settings.GEN_INSIEMI_LEARNING_SCHEMA_PATH_QC
        if not validate_json_files(conf_path, schema_path):
            raise Exception("[ERRORE] Il file di configurazione del Quality Check "
                            "non è corretto")

        with open(settings.GEN_INSIEMI_LEARNING_CONFIG_PATH_QC) as conf_file:
            data = json.load(conf_file)

        self.save_path = data['save_path']
        self.save_format = data['save_format']
        self.max_number_of_sample = data['max_number_of_sample']

        self.colors = get_plot_colors(self.max_number_of_sample)

        self.input_file_path = data['input_file_path']

    def __plot_radar_diagram(self, title, dataframe, num_sample, id_user):
        fig = plt.figure()
        fig.suptitle(title)

        axes = fig.add_subplot(111, projection="polar")

        theta = np.arange(len(list(dataframe)) + 1) / \
            float(len(list(dataframe))) * 2 * np.pi

        for j in range(num_sample):
            values = dataframe.iloc[[j]].values[0]
            values = np.append(values, values[0])

            # draw the polygon and the mark the points for each angle/value combination
            axes.plot(theta, values, color=self.colors[j], marker="o")
            plt.xticks(theta[:-1], list(dataframe), color='grey')
            axes.tick_params(pad=10)  # to increase the distance of the labels to the plot

            # fill the area of the polygon with green and some transparency
            axes.fill(theta, values, color=self.colors[j], alpha=0.1)

        save_path = os.path.abspath(self.save_path + id_user)
        save_file = title + '.' + self.save_format

        Path(save_path).mkdir(parents=True, exist_ok=True)

        fig.savefig(os.path.join(save_path, save_file))
        plt.close()

    def class_quality_for_all_user(self):
        """
        Genera il radar plot per tutti gli utenti
        :return: void
        """
        for id_user in os.listdir(self.input_file_path):
            self.class_quality_for_a_specific_user(id_user)

    def class_quality_for_a_specific_user(self, id_user):
        """
        Genera il radar plot per uno spcifico utente
        :return: void
        """
        schema_path = settings.GEN_INSIEMI_LEARNING_SCHEMA_PATH_INPUT
        id_user = str(id_user)
        json_path = self.input_file_path + id_user + '/processed_data.json'
        if not validate_json_files(json_path, schema_path):
            raise Exception("[ERRORE] Il file contenente le features "
                            "non è corretto")

        label_dict = json_to_dict_of_dataframe(json_path)

        for label in label_dict:
            channels = label_dict[label]

            num_sample = self.max_number_of_sample \
                if self.max_number_of_sample < channels['total_sample'] else \
                channels['total_sample']

            for channel in channels:
                if channel == 'total_sample':
                    continue

                title = label + '-' + channel
                dataframe = channels[channel]
                self.__plot_radar_diagram(title, dataframe, num_sample, id_user)
