from branje_kataloga import DATOTEKA_VSEH_POVEZAV_KATALOGA
from branje_strani import shrani_stran, nalozi_stran_iz_datoteke
import csv, re, time
from os import listdir, path

# funkcije za pobiranje informacij iz strani
def poberi_ime(div_informacij):
    div_imena = div_informacij.find('div', containing='Tehnično ime izdelka')

    if len(div_imena) >= 1:
        spana = div_imena[0].find('span')
        if len(spana) == 2:
            return spana[1].text

def poberi_sestavine(div_informacij):
    najdeni_divi = div_informacij.find('div.ingredient-information', containing='Sestavine')

    if len(najdeni_divi) == 1:
        ustrezen_div = najdeni_divi[0]
        najden_span = ustrezen_div.find('span.detail__content')

        if len(najden_span) == 1:
            return najden_span[0].text

def poberi_hranilne_vrednosti(div_informacij):
    dlji = div_informacij.find('dl.detail__container__table')

    vrednosti = {}
    for dl in dlji:
        dtji=dl.find('dt')
        if len(dtji) == 2:
            vrednost = dtji[0].text
            stevilka = dtji[1].text
            vrednosti[vrednost] = stevilka
        else:
            return

    return vrednosti

def poberi_kolicino(div_informacij):
    div_neto_kolicine = div_informacij.find('div.product-net-cont')
    if len(div_neto_kolicine) == 1:
        neto_kolicina = div_neto_kolicine[0].find('span.detail__content')
        if len(neto_kolicina) == 1:
            return neto_kolicina[0].text

def poberi_vse_informacije(html_objekt):
    div_informacij = html_objekt.find('div#productDetailsTabs')[0]
    #print(div_informacij)

    informacije = {}
    informacije['ime'] = poberi_ime(div_informacij)
    informacije['sestavine'] = poberi_sestavine(div_informacij)
    informacije['hranilne_vrednosti'] = poberi_hranilne_vrednosti(div_informacij)
    informacije['kolicina'] = poberi_kolicino(div_informacij)

    if informacije['sestavine'] is None:
        return 
    if informacije['ime'] is None:
        return 
    if informacije['hranilne_vrednosti'] is None:
        return 
    if informacije['kolicina'] is None:
        return 

    return informacije


#funkcije za pobiranje strani
def preberi_urlje():
    urlji = []
    with open(DATOTEKA_VSEH_POVEZAV_KATALOGA, 'r') as datoteka:
        csvzapis = csv.reader(datoteka, delimiter='\n')
        for url in csvzapis:
            # zakaj so vmes tudi prazne vrstice?
            if url != '':
                urlji += url
    return urlji

MAPA_IZDELKOV = "izdelki"
def dobi_ime_datoteke(stevilka_izdelka):
    return f'{MAPA_IZDELKOV}/{stevilka_izdelka}.html'

def najdi_stevilko_izdelka(url):
    najdeno = re.search('\/p\/(\d+)', url)
    if najdeno is not None:
        return najdeno.groups()[0]
    else:
        raise ValueError(f'Url {url} ne ustreza vzorcu za url produkta.')

from wakepy import set_keepawake, unset_keepawake
def shrani_strani_izdelkov(zamik=5):
    set_keepawake(keep_screen_awake=False)

    urlji = preberi_urlje()
    for url in urlji:
        pot = dobi_ime_datoteke(najdi_stevilko_izdelka(url))
        if not path.exists(pot):
            try:
                print(f'Shranjujem {url} ...')
                shrani_stran(url, pot)
                time.sleep(zamik)
            except:
                print(f'Ni mi uspelo shraniti {url}.')

    unset_keepawake()


def nalozi_strani_izdelkov():
    vse_strani = []
    for stevilka_izdelka in listdir(MAPA_IZDELKOV):
        vse_strani += [nalozi_stran_iz_datoteke(dobi_ime_datoteke(stevilka_izdelka.strip(".html")))]
    return vse_strani

"""glava_csv=['ime', 'sestavine', 'kolicina', ]
def shrani_informacije_cvs(seznam):
    with open('eggs.csv', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        for row in spamreader:
            print(', '.join(row))"""

def obdelaj_strani_izdelkov():
    vse_strani = nalozi_strani_izdelkov()

    seznam = []
    for stran in vse_strani:
        informacije = poberi_vse_informacije(stran)
        if informacije is not None:
            seznam += [informacije]
    
    return seznam
    #shrani_informacije_cvs(seznam)

if __name__ == '__main__':
    shrani_strani_izdelkov(0.5)