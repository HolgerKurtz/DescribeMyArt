"""
Scrpt, um 
1. API von Museum anzuzapfen
2. Daten herunterzuladen
3. Formatieren
--> Title(später Tweet ohne Hashtag): Beschreibung
3. --> museum.txt erstellen, für training
"""

# Informationen zur API unter
# https://data.rijksmuseum.nl/object-metadata/api/#collection-image-api

import json
import requests
import time
from os import system



twitter_credential_path = 'rijksmuseum_creds.json'
with open(twitter_credential_path, "r") as json_file:
    museum_creds = json.load(json_file)

# Daten aus der JSON Datei
ACCESS_KEY = museum_creds["Key"]

# URL Struktur für API GET 
url_raw = 'https://www.rijksmuseum.nl/api/en/collection'
key = '?key=' + ACCESS_KEY
# art = '&type=painting'
# art = '&type=drawing'
# art = '&type=photograph'
# art = '&type=print'
results_per_page = '&ps=100' # 100 maximal anzahl
top_pieces = '&toppieces=True'
s = '&s=chronologic'

# paginierung


urls_liste = []
for i in range(1,36): # nach 35 gab es eine Fehlermeldung. Denke, weil es keine neuen Einträge gibt
    seite = i  # Seiten paginierung
    p = '&p=' + str(seite)
    url_gesamt = url_raw + key + p + results_per_page + top_pieces # Reihenfolge ist wohl wichtig: erst p dann ps
    urls_liste.append(url_gesamt)
    i += 1

print(6*'=')
print (*urls_liste)

anzahl = 0
objectNumber_liste = []
for url in urls_liste:
    print(6*'=')
    print ('Durchlauf Nr.:', anzahl + 1, 'läuft jetzt')
    print ('url:', urls_liste[anzahl])
    try:
        r = requests.get(urls_liste[anzahl]).content # GET
        # print ('sleeping')
        # time.sleep(5)
        data = json.loads(r)
    except:
        print('Seite kann nicht geladen werden. Abbruch')
        break

# Teildaten aus der JSON 
    for artwork in data['artObjects']:
        objectNumber = artwork['objectNumber']
        objectNumber_liste.append(objectNumber)

    print ('Anzahl in Liste:', len(objectNumber_liste))
    print ('Anzahl in Set:', len(set(objectNumber_liste)))
    anzahl += 1

with open('art_url_log.txt', "w") as art_url_log:
    for objekt_nummer in objectNumber_liste:
        art_url_log.write(str(objekt_nummer) + '\n')

# Überblick
print(6*'=')
print ('Durchläufe komplett!')
print(6*'=')
print ('Anzahl an objekt_nummern in der Liste', len(objectNumber_liste))
print(6*'=')
print ('Anzahl in Set:', len(set(objectNumber_liste)))
print(6*'=')
print('objekt_nummer in art_url_log.txt gespeichert')


# Nun muss für jedes objekt eine url erstellt werden
# Ab hier kann von txt gearbeitet werden
id_liste = []
with open('art_url_log.txt', "r") as art_url_log:
    for objekt_nummer in art_url_log:
        objekt_ohne_leerzeichen = objekt_nummer.replace('\n', '')
        id_liste.append(objekt_ohne_leerzeichen)

 
url_collection_liste = []
for i in id_liste:
    url_neu = url_raw + '/' + str(i) + key
    url_collection_liste.append(url_neu)

# Jetzt wird jede url geöffnet und titel & BEschreibung in .txt gespeichert

objekt_titel_liste = []
objekt_beschreibung_liste = []
objekt_maler_liste = []
number = 0

for uri in url_collection_liste:
    print (url_collection_liste[number])
    # print ('sleeping')
    # time.sleep(10)
    try:
        r = requests.get(url_collection_liste[number]).content # GET
        data = json.loads(r)

        # Teildaten aus der JSON 
        object_titel = data['artObject']['title']
        objekt_titel_liste.append(object_titel)

        object_beschreibung = data['artObject']['plaqueDescriptionEnglish']
        objekt_beschreibung_liste.append(object_beschreibung)

        object_maler = data['artObject']['principalMaker']
        objekt_maler_liste.append(object_maler)

        print (object_titel) 
        print (object_maler)
        print (object_beschreibung)

    except: 
        print (url_collection_liste[number], '--> Fehler')
        pass
    print (number + 1, 'von', len(url_collection_liste), '=', (number // len(url_collection_liste)) * 100, '%' )
    number += 1

with open('training_museum_drawing.txt', "a") as training_text:
    n = 0
    for k in range(len(objekt_beschreibung_liste)):
        if objekt_beschreibung_liste[n] == None:
            pass
        else:
            training_text.write('=== ')
            training_text.write(objekt_titel_liste[n])
            training_text.write(' ===')
            training_text.write(' by ')
            training_text.write(objekt_maler_liste[n])
            training_text.write('\n')
            training_text.write(objekt_beschreibung_liste[n])
            training_text.write('\n')
            training_text.write('\n')
        n += 1
        
        
print ('Done!')
system("say Holger, du altes Coder Genie. Du hast es mal wieder geschafft! ")