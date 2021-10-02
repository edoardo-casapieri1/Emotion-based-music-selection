"""
file contenente le funzioni di utilità per convertire i file json in dataframe
"""
import json
import pandas as pd


def create_or_return_dictionary(building_dict, key):
    """
    Crea il dizionario  lo ritorna
    :param building_dict: dizionario in costruzione
    :param key: Chiave sotto la quale salvare il dizionario
    :return: il dizionario appena creato o quello esistente
    """
    if key not in building_dict:
        building_dict[key] = dict()
    return building_dict[key]


def create_or_insert_in_list(building_dict, key, value):
    """
    Crea la lista o lo ritorna
    :param building_dict: dizionario in costruzione
    :param key: Chiave sotto la quale salvare la lista
    :param value: valore da aggiungere alla lista
    :return: void
    """
    if key not in building_dict:
        building_dict[key] = list()
    building_dict[key].append(value)


def create_or_add_to_value_in_dictionary(building_dict, key, value=1):
    """
    Crea un intero a zero nel dizionario, o aggiunge all'intero
    :param building_dict: dizionario in costruzione
    :param key: Chiave sotto la quale salvare l'intero
    :param value: valore da aggiungere
    :return: void
    """
    if key not in building_dict:
        building_dict[key] = 0
    building_dict[key] += value


def json_to_dataframe(filename, traslation_dict):
    """
    Genera il dataframe a partire dal json delle features
    :param filename: Json delle features
    :param traslation_dict: Abbina le label con un intero
    :return: dataframe finale
    """
    with open(filename) as json_file:
        data = json.load(json_file)

    df_dict = dict()
    for impulse in data['impulsi']:
        create_or_insert_in_list(df_dict, 'label', traslation_dict[impulse['label']])

        channels = impulse['features']
        for channel in channels:
            channel_features = channels[channel]
            for feature in channel_features:
                feature_key = channel + feature
                create_or_insert_in_list(df_dict, feature_key, channel_features[feature])

    return pd.DataFrame(df_dict)


def json_to_dict_of_dataframe(filename):
    """
    Genera un dizionario di dataframe a partire dal json delle features
    :param filename: Json delle features
    :return: il dizionario con i dataframe
    """
    with open(filename) as json_file:
        data = json.load(json_file)

    df_dict = dict()
    for impulse in data['impulsi']:
        label = impulse['label']
        label_dict = create_or_return_dictionary(df_dict, label)
        create_or_add_to_value_in_dictionary(label_dict, 'total_sample')

        channels = impulse['features']
        for channel in channels:
            channel_features = channels[channel]

            channel_dict = create_or_return_dictionary(label_dict, channel)
            for feature in channel_features:
                create_or_insert_in_list(channel_dict, feature, channel_features[feature])

    for label in df_dict:
        channels = df_dict[label]
        for channel in channels:
            if channel == 'total_sample':
                continue
            df_dict[label][channel] = pd.DataFrame(channels[channel])

    return df_dict
