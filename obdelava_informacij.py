from branje_izdelkov import nalozi_vse_informacije

informacije = nalozi_vse_informacije()

import re
def poisci_kandidate(kljucne_besede):
    kljucne_besede_brez_koncnice = []
    for beseda in kljucne_besede:
        if beseda[-1] in "aeiou" :
            kljucne_besede_brez_koncnice.append(beseda[:-1])
        else:
            kljucne_besede_brez_koncnice.append(beseda)
    
    pari = []
    for info in informacije:
        stevilo_zadetkov=0
        
        for s in kljucne_besede_brez_koncnice:
            zadetki = re.search(s.upper(), info[0].upper())
            if zadetki is not None:
                stevilo_zadetkov+=1
        
        if stevilo_zadetkov > 0:
            pari.append([stevilo_zadetkov, info])

    pari.sort(key = lambda par : (-par[0], len(par[1][0])))

    kandidati = list(map(lambda par : par[1], pari))
    return kandidati

# Motivacija: poskusimo razbiti "mlečna čokolada 30% (sladkor, kakavovo maslo, kakavova masa, POSNETO MLEKO V PRAHU, KONCENTRIRANO MASLO, EMULGATOR: LECITINI (SOJA) VANILIN), LEŠNIKI (28,5%), sladkor, palmino olje, PŠENIČNA MOKA, SIROTKA V PRAHU (MLEKO), manj masten kakav, EMULGATOR: LECITINI (SOJA), sredstvo za vzhajanje (natrijev bikarbonat), jedilna sol, vanilin"
# na: "sladkor, kakavovo maslo, kakavova masa, POSNETO MLEKO V PRAHU, KONCENTRIRANO MASLO, EMULGATOR: LECITINI, LEŠNIKI, palmino olje, PŠENIČNA MOKA, SIROTKA V PRAHU, manj masten kakav, natrijev bikarbonat, jedilna sol, vanilin"
# pri tem smo izvzeli sestavine iz oklepajev in jih združili z ostalimi (saj je vsota hranilnih vrednosti na koncu obtežena vsota vseh), odstranili pa smo tudi ponovitve.

# pomožna funkcija, ki razcepi niz na delilnih mestih
def razcepi_niz(niz):
    stopnja = 0
    delitev = []

    trenuten_niz = ""
    for c in niz:
        if c.isalnum() or c in " ,()%":
            if c==',' and stopnja == 0 and len(trenuten_niz) > 0:
                delitev += [trenuten_niz]
                trenuten_niz = ""
            else:
                trenuten_niz += c
                if c == '(' : stopnja += 1
                elif c == ')': stopnja -= 1
    
    if len(trenuten_niz) > 0:
        delitev += [trenuten_niz]

    return delitev

def dobi_oklepaje(niz):
    stopnja = 0
    delitev = []

    trenuten_niz = ""
    for c in niz:
        if stopnja > 0:
            if c==')' and stopnja == 1 and len(trenuten_niz) > 0:
                delitev += [trenuten_niz]
                trenuten_niz = ""
            elif c.isalnum() or c in " ,()%":
                trenuten_niz +=c
        if c == ')': stopnja -= 1
        elif c == '(' : stopnja += 1
    
    if len(trenuten_niz) > 0:
        delitev += [trenuten_niz]

    return delitev

def dobi_besedilo_brez_oklepajev(niz):
    stopnja = 0
    trenuten_niz = ""
    for c in niz:
        if stopnja == 0 and (c.isalnum() or c in " ,%"):
            trenuten_niz += c
        elif c == '(' : stopnja += 1
        elif c == ')': stopnja -= 1
    return trenuten_niz

# https://prehrana.si/sestavine-zivil/alergeni

alergeni = [
    "SOJA",
    "MLEKO",
    "PŠENICA",
    "GLUTEN",
    "OREŠČKI",
    "GORČIČNO SEME",
    "JAJCA",
    "ZELENA",
    "VOLČJI BOB"
]
def oznacuje_alergen(niz):
    return niz in alergeni

def dobi_vnos(moznosti):
    while(True):
        vnos = input()
        if vnos in moznosti:
            return vnos
        else:
            print("Vnos neveljaven. Poskusite ponovno")

def odstrani_procent(niz):
    return re.sub("\(?(\s)*\d+\,?\d+(\s)*%\)?", "", niz)

def razcepi_sestavine(sestavine):
    razcep = razcepi_niz(sestavine)

    if len(razcep) == 1:
        oklepaji = dobi_oklepaje(sestavine)
        
        # predpostvka: vsaka sestavina ima največ 2 oklepaja, mogoče enega za podsestavine in mogoče enega za procent v originalnem receptu
        if len(oklepaji) == 0:
            return [sestavine]
        else:
            
            besedilo_izven_oklepaja = dobi_besedilo_brez_oklepajev(sestavine)
            koncne_sestavine = []
            for besedilo_v_oklepaju in oklepaji:
                razcepljene_podsestavine = razcepi_sestavine(besedilo_v_oklepaju)
                if oznacuje_alergen(besedilo_v_oklepaju):
                    continue
                elif len(razcepljene_podsestavine) >= 2:
                    koncne_sestavine += razcepljene_podsestavine
                else:
                    # če ni nič od tega vprašamo uporabnika
                    print("\n" * 50)
                    print(f"Pri obravnavi '{sestavine}' ne morem razbrati kaj je v oklepajih. Izberi:")
                    print("0: Ignoriraj besedilo v oklepaju.")
                    print("1: Uporabi besedilo v oklepaju.")

                    vnos = dobi_vnos(['0', '1'])
                    
                    if vnos == '0':
                        continue
                    elif vnos == '1':
                        koncne_sestavine += razcepljene_podsestavine
            if len(koncne_sestavine) == 0:
                return razcepi_sestavine(besedilo_izven_oklepaja)
            else:
                return koncne_sestavine
    else:
        koncne_sestavine = []
        for kos in razcep:
            koncne_sestavine += razcepi_sestavine(kos)
        return koncne_sestavine

def precisti(niz):
    return re.sub("\s", " ", niz).strip().upper()

def dobi_sestavine(sestavine):
    sestavine = odstrani_procent(sestavine).upper()
    nepreciscene_ponovitvami = razcepi_sestavine(sestavine)

    sestavine_s_ponovitvami = []

    for s in nepreciscene_ponovitvami:
        sestavine_s_ponovitvami += [precisti(s)]

    # odstrani ponovitve
    print(sestavine_s_ponovitvami)

    #uredimo zato ker list(set()) naključno premeče seznam
    koncne_sestavine = sorted(list(set(sestavine_s_ponovitvami)))
    
    return koncne_sestavine

NAJBOLJ_POMEMBNI_ZADETKI = 7

def obravnavaj_sestavine(sestavine):
    mozne_sestavine = dobi_sestavine(sestavine)
    print(mozne_sestavine)

    koncne_sestavine = []
    for mozna_sestavina in mozne_sestavine:
        mozni_zadetki = poisci_kandidate(mozna_sestavina.split())
        
        if len(mozni_zadetki) == 0:
            continue
        
        for zacetek in range(0, len(mozni_zadetki), NAJBOLJ_POMEMBNI_ZADETKI):
            print("\n" * 50)
            print(f"Za '{mozna_sestavina}' sem našel naslednje možne zadetke:")
            print("0: Spusti to sestavino.")

            stevilo_trenutnih_zadetkov = min(NAJBOLJ_POMEMBNI_ZADETKI, len(mozni_zadetki) - zacetek)
            trenutni_zadetki = mozni_zadetki[zacetek : zacetek + stevilo_trenutnih_zadetkov]
            for i in range(stevilo_trenutnih_zadetkov):
                print(f"{i+1}: {trenutni_zadetki[i][0]}")
            print(f"{stevilo_trenutnih_zadetkov + 1}: Izdelek ni med prikazanimi, pokaži naslednje.")

            vnos = dobi_vnos([f"{i}" for i in range(2+stevilo_trenutnih_zadetkov) ])

            if vnos == "0":
                break
            elif vnos == f"{stevilo_trenutnih_zadetkov + 1}":
                continue
            else:
                koncne_sestavine += [mozni_zadetki[int(vnos)-1]]
                break
    return koncne_sestavine


s ="sončnično olje, kisle kumarice 6,00 %, kis, voda, sladkor, koruzni škrob, GORČICA (VODA, KIS, GORČIČNA SEMENA, SOL, SLADKOR, ZAČIMBE, AROMA), začimbe, izvleček začimbe (paprika, kurkuma) sol, modificirani škrob, AROME (VSEBUJEJO ZELENO IN GORČICO)."
print(obravnavaj_sestavine(s))
#obravnavaj_sestavine(s)