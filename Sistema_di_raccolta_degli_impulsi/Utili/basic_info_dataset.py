import csv

tot_impulsi_relaxed = 0
tot_impulsi_focused = 0
tot_impulsi_excited = 0
tot_colonne = 0

with open("../Data/DatasetCompleto.csv", encoding='utf-8') as csv_file:
    reader = csv.reader(csv_file, delimiter=',')

    for row in reader:
        tot_colonne = max(len(row) - 4, tot_colonne)
        if row[2] == "relaxed":
            if row[3] == "22":
                tot_impulsi_relaxed = tot_impulsi_relaxed + 1
        if row[2] == "focused":
            if row[3] == "22":
                tot_impulsi_focused = tot_impulsi_focused + 1
        if row[2] == "excited":
            if row[3] == "22":
                tot_impulsi_excited = tot_impulsi_excited + 1

print("\nResoconto:\n")
print("Ogni riga del dataset iniziale contiene un numero di colonne pari a:", tot_colonne)
print("Il numero di impulsi nervosi di tipo relaxed è pari a:", tot_impulsi_relaxed * tot_colonne)
print("Il numero di singoli campioni di tipo relaxed è pari a:", tot_impulsi_relaxed * 22 * tot_colonne, "\n")
print("Il numero di impulsi nervosi di tipo focused è pari a:", tot_impulsi_focused * tot_colonne)
print("Il numero di singoli campioni di tipo focused è pari a:", tot_impulsi_focused * 22 * tot_colonne, "\n")
print("Il numero di impulsi nervosi di tipo excited è pari a:", tot_impulsi_excited * tot_colonne)
print("Il numero di singoli campioni di tipo excited è pari a:", tot_impulsi_excited * 22 * tot_colonne, "\n")

