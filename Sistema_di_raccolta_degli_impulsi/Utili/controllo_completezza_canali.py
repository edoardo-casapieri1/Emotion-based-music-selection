import csv

raw_list = []

with open("../Data/DatasetCompleto.csv", encoding='utf-8') as csv_file:
    reader = csv.reader(csv_file, delimiter=',')

    for row in reader:
        if row[2] == "LABELS":
            continue
        raw_list.append(row)

for i in range(len(raw_list)//22):
    base = i * 22
    for j in range(22):
        if raw_list[base + j][3] != str(j + 1):
            print("Errore alla riga:", base + j + 1, "Il canale doveva essere:", j + 1, "e invece era:", raw_list[base + j][3])
            quit()

print("Tutti gli impulsi possiedono tutti i canali in ordine")