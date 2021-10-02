import csv

'''
Questo script converte il dataset csv nella versione tsv (che è decisamente più leggibile con excel)
'''

with open('../Data/shortDataset.csv', encoding="utf-8") as csv_file:
    reader = csv.reader(csv_file, delimiter=',')
    lista = []

    for row in reader:
        lista.append(row)

with open('../Data/shortDataset.tsv', mode='w', newline='', encoding="utf8") as tsv_file:
    TSVWriter = csv.writer(tsv_file, dialect='excel-tab')
    TSVWriter.writerows(lista)
