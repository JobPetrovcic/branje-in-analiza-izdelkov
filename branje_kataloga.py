from branje_strani import shrani_stran, nalozi_stran_iz_datoteke

MAPA_KATALOGA = 'katalog'
def dobi_ime_strani_indeks(indeks):
    return f'{MAPA_KATALOGA}\stran_{indeks}.html'

# v vzorec strani vstavimo indeks nato pa shranimo stran s tem url-jem
OSNOVA_SPAR_STRANI = 'https://www.spar.si'
VZOREC_STRANI = OSNOVA_SPAR_STRANI + '/online/c/root/?_=1635264522253&callback=parseResponse&category=root&i=1&m_sortProdResults_egisp=a&page={stevilka_strani}&pos=81701&q=*&sort=product-ecr-sortlev&sp_cs=UTF-8&sp_q_12=81701&sp_q_exact_14=root&sp_x_12=product-visible-pos'
def shrani_stran_indeks(indeks):
    shrani_stran(VZOREC_STRANI.format(stevilka_strani=indeks), dobi_ime_strani_indeks(indeks))

# pobere in shrani vseh 255 strani (toliko jih je v času programiranja te naloge).
STEVILO_VSEH_STRANI_SPAR=255
def shrani_vse_strani_kataloga(stevilo_strani=STEVILO_VSEH_STRANI_SPAR):
    for i in range(1, stevilo_strani + 1):
        shrani_stran_indeks(i)

def nalozi_vse_strani_kataloga(stevilo_strani=STEVILO_VSEH_STRANI_SPAR):
    vse_strani = []
    for i in range(1, stevilo_strani+1):
        vse_strani += [nalozi_stran_iz_datoteke(dobi_ime_strani_indeks(i))]
    return vse_strani

# preveri ali je povezava res povezava do produkta (link se loči po tem da vsebuje: /p/)
import re
def je_povezava_do_produkta(povezava):
    return re.search('\/online\/[\w\-]+\/p[\/|$]', povezava) is not None

# iz objekta HTML knjižnice requests_html prebere vse povezave na strani, ki predstavljajo posamezen izdelek
def poberi_povezave_do_produkta(html_objekt):
    vse_povezave = html_objekt.links
    povezave_do_produkta = []

    for povezava in vse_povezave:
        if je_povezava_do_produkta(povezava):
            povezave_do_produkta+=[OSNOVA_SPAR_STRANI + povezava]

    return povezave_do_produkta

def zdruzi_sezname(seznami):
    zdruzen = []
    for seznam in seznami:
        for element in seznam:
            zdruzen += [element]

    return list(set(zdruzen))

def poberi_povezave_seznam(seznam_html_objektov):
    seznam_seznamov = []
    for html_objekt in seznam_html_objektov:
        seznam_seznamov += [poberi_povezave_do_produkta(html_objekt)]
    
    return zdruzi_sezname(seznam_seznamov)

# iz shranjenih datotek v mapi katalog prebere vse povezave in jih nato združi brez ponavljanja, 
def obdelaj_vse_strani_kataloga():
    vse_strani = nalozi_vse_strani_kataloga()
    return poberi_povezave_seznam(vse_strani)

import csv
DATOTEKA_VSEH_POVEZAV_KATALOGA = 'vse_povezave_do_produkta.csv'
def shrani_povezave_kataloga(nalozi_strani_iz_interneta=False):
    if nalozi_strani_iz_interneta:
        shrani_vse_strani_kataloga()

    vse_povezave = obdelaj_vse_strani_kataloga()

    with open(DATOTEKA_VSEH_POVEZAV_KATALOGA, 'w') as datoteka:
        zapis = csv.writer(datoteka, delimiter='\n')
        zapis.writerow(vse_povezave)
        