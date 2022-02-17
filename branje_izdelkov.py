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
    # zagotovimo, da ne bo računalnik se izklopil
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


glava_csv=['ime',
'sestavine',
'kolicina',
'kcal',
'Maščobe',
'od tega nasičene maščobe',
'Ogljikovi hidrati',
'od tega sladkorji',
'Prehranske vlaknine',
'Beljakovine',
'Sol']
def dobi_vrstico_csv(slovar):
    # ali je mogoča uporaba dictwriterja?

    vrstica=[]

    for indeks_stolpca in range(0, 3):
        if glava_csv[indeks_stolpca] in slovar:
            vrstica += [slovar[glava_csv[indeks_stolpca]]]
        else:
            vrstica += ['']
    
    for indeks_stolpca in range(3, len(glava_csv)):
        if glava_csv[indeks_stolpca] in slovar['hranilne_vrednosti']:
            vrstica += [slovar['hranilne_vrednosti'][glava_csv[indeks_stolpca]]]
        else:
            vrstica +=['0,0 g']

    return vrstica
    


# Zaradi kolicine podatkov in pomanjkanja RAMa je ta funkcija ni razbita na več funkcij, saj je potrebno vse narediti v enem koraku .

MAPA_IZDELKOV = "izdelki"
DATOTEKA_INFORMACIJ_IZDELKOV = 'informacije.csv'

def obdelaj_strani_izdelkov():
    with open(DATOTEKA_INFORMACIJ_IZDELKOV, 'w', newline='', encoding='utf-8') as datoteka:
        zapis = csv.writer(datoteka, delimiter='|')

        zapis.writerow(glava_csv)

        for stevilka_izdelka in listdir(MAPA_IZDELKOV):
            try:
                stran = nalozi_stran_iz_datoteke(dobi_ime_datoteke(stevilka_izdelka.strip(".html")))

                informacije = poberi_vse_informacije(stran)
            except:
                pass

            if informacije is not None:
                    vrstica = dobi_vrstico_csv(informacije)
                    zapis.writerow(vrstica)

def nalozi_vse_informacije():
    print("Odpiram informacije o izdelkih...")
    with open(DATOTEKA_INFORMACIJ_IZDELKOV, 'r', newline='', encoding='utf-8') as datoteka:
        zapis = csvreader = csv.reader(datoteka, delimiter='|')
        glava = next(csvreader)
        #print(glava)
        vrstice = []
        for vrstica in csvreader:
            vrstice.append(vrstica)
        return vrstice

if __name__ == '__main__':
    #shrani_strani_izdelkov(0.5)
    #obdelaj_strani_izdelkov()
    pass