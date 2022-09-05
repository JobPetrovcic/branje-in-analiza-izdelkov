import pandas as pd
import re
from branje_izdelkov import nalozi_vse_informacije_pandas

df = nalozi_vse_informacije_pandas()


def poisci_kandidate(kljucne_besede):
    """
    Vzame ključne besede nato pa jih poišče v imenih izdelkov. Vrne bazo izdelkov urejenih glede nato, koliko ključnih besed smo našli v imenu.
    """
    kljucne_besede_brez_koncnice = []
    for beseda in kljucne_besede:
        if beseda == "":
            continue
        if beseda[-1] in "aeiou":
            kljucne_besede_brez_koncnice.append(beseda[:-1])
        else:
            kljucne_besede_brez_koncnice.append(beseda)

    def oceni(niz):
        stevilo_zadetkov = 0

        for kb in kljucne_besede_brez_koncnice:
            zadetki = re.search(kb.upper(), niz.upper())
            if zadetki is not None:
                stevilo_zadetkov += 1
        return -stevilo_zadetkov

    return df.sort_values(by='ime', key=lambda col: col.apply(oceni))

# Motivacija: poskusimo razbiti "mlečna čokolada 30% (sladkor, kakavovo maslo, kakavova masa, POSNETO MLEKO V PRAHU, KONCENTRIRANO MASLO, EMULGATOR: LECITINI (SOJA) VANILIN), LEŠNIKI (28,5%), sladkor, palmino olje, PŠENIČNA MOKA, SIROTKA V PRAHU (MLEKO), manj masten kakav, EMULGATOR: LECITINI (SOJA), sredstvo za vzhajanje (natrijev bikarbonat), jedilna sol, vanilin"
# na: "sladkor, kakavovo maslo, kakavova masa, POSNETO MLEKO V PRAHU, KONCENTRIRANO MASLO, EMULGATOR: LECITINI, LEŠNIKI, palmino olje, PŠENIČNA MOKA, SIROTKA V PRAHU, manj masten kakav, natrijev bikarbonat, jedilna sol, vanilin"
# pri tem smo izvzeli sestavine iz oklepajev in jih združili z ostalimi (saj je vsota hranilnih vrednosti na koncu obtežena vsota vseh), odstranili pa smo tudi ponovitve.


def razcepi_niz(niz):
    """
    pomožna funkcija, ki razcepi niz na delilnih mestih
    """

    stopnja = 0
    delitev = []

    trenuten_niz = ""
    for c in niz:
        if c.isalnum() or c in " ,()%":
            if c == ',' and stopnja == 0 and len(trenuten_niz) > 0:
                delitev += [trenuten_niz]
                trenuten_niz = ""
            else:
                trenuten_niz += c
                if c == '(':
                    stopnja += 1
                elif c == ')':
                    stopnja -= 1

    if len(trenuten_niz) > 0:
        delitev += [trenuten_niz]

    return delitev


def dobi_oklepaje(niz):
    """
    Razcepi niz glede na oklepaje.
    """

    stopnja = 0
    delitev = []

    trenuten_niz = ""
    for c in niz:
        if stopnja > 0:
            if c == ')' and stopnja == 1 and len(trenuten_niz) > 0:
                delitev += [trenuten_niz]
                trenuten_niz = ""
            elif c.isalnum() or c in " ,()%":
                trenuten_niz += c
        if c == ')':
            stopnja -= 1
        elif c == '(':
            stopnja += 1

    if len(trenuten_niz) > 0:
        delitev += [trenuten_niz]

    return delitev


def dobi_besedilo_brez_oklepajev(niz):
    stopnja = 0
    trenuten_niz = ""
    for c in niz:
        if stopnja == 0 and (c.isalnum() or c in " ,%"):
            trenuten_niz += c
        elif c == '(':
            stopnja += 1
        elif c == ')':
            stopnja -= 1
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
    """
    Sprasuje uporabnika dokler ne poda pravilnega vnosa.
    """
    while(True):
        vnos = input()
        if vnos in moznosti:
            return vnos
        else:
            print("Vnos neveljaven. Poskusite ponovno")


def odstrani_procent(niz):
    return re.sub("\(?(\s)*\d+\,?\d+(\s)*%\)?", "", niz)


def razcepi_sestavine(sestavine):
    """
    Smiselno razcepi sestavine. Če ne ve, kaj bi naredil vpraša uporabnik. Vrne seznam nizov, za katere misli, da so imena sestavine.
    """

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
                razcepljene_podsestavine = razcepi_sestavine(
                    besedilo_v_oklepaju)
                if oznacuje_alergen(besedilo_v_oklepaju):
                    continue
                elif len(razcepljene_podsestavine) >= 2:
                    koncne_sestavine += razcepljene_podsestavine
                else:
                    # če ni nič od tega vprašamo uporabnika
                    print(
                        f"Pri obravnavi '{sestavine}' ne morem razbrati kaj je v oklepajih. Izberi:")
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
    nepreciscene_s_ponovitvami = razcepi_sestavine(sestavine)

    sestavine_s_ponovitvami = []

    for s in nepreciscene_s_ponovitvami:
        sestavine_s_ponovitvami += [precisti(s)]

    # odstrani ponovitve

    # uredimo zato ker list(set()) naključno premeče seznam
    koncne_sestavine = sorted(list(set(sestavine_s_ponovitvami)))

    return koncne_sestavine


NAJBOLJ_POMEMBNI_ZADETKI = 7


def obravnavaj_sestavino(mozna_sestavina):
    """
    Najdene sestavino prikažemo uporabniku, nato pa jih ta z vnosom izbere.
    """
    mozni_zadetki = poisci_kandidate(mozna_sestavina.split())

    if len(mozni_zadetki) == 0:
        return

    for zacetek in range(0, len(mozni_zadetki), NAJBOLJ_POMEMBNI_ZADETKI):
        print(f"Za '{mozna_sestavina}' sem našel naslednje možne zadetke:")
        print("0: Spusti to sestavino.")

        stevilo_trenutnih_zadetkov = min(
            NAJBOLJ_POMEMBNI_ZADETKI, len(mozni_zadetki) - zacetek)
        trenutni_zadetki = mozni_zadetki[zacetek: zacetek +
                                         stevilo_trenutnih_zadetkov]
        for i in range(stevilo_trenutnih_zadetkov):
            print(f"{i+1}: {trenutni_zadetki.ime.iloc[i]}")
        print(
            f"{stevilo_trenutnih_zadetkov + 1}: Izdelek ni med prikazanimi, pokaži naslednje.")

        vnos = dobi_vnos([f"{i}" for i in range(2+stevilo_trenutnih_zadetkov)])

        if vnos == "0":
            return
        elif vnos == f"{stevilo_trenutnih_zadetkov + 1}":
            continue
        else:
            return trenutni_zadetki.iloc[int(vnos)-1]


def obravnavaj_sestavine(sestavine):
    """
    Funkcijo obravnavaj_sestavino uporabimo na večjih sestavinah.
    """
    mozne_sestavine = dobi_sestavine(sestavine)
    print(mozne_sestavine)

    koncne_sestavine = []
    for mozna_sestavina in mozne_sestavine:
        dobljena_sestavina = obravnavaj_sestavino(mozna_sestavina)
        if dobljena_sestavina is not None:
            koncne_sestavine += [dobljena_sestavina]
    return koncne_sestavine


def dobi_stevilo_iz_niza(niz):
    """
    Pretvori niz v število, pri tem odstrani enoto.
    """
    stevilo_v_nizu = ""
    for c in niz:
        if c in "0123456789":
            stevilo_v_nizu += c
        elif c in ".,":
            stevilo_v_nizu += '.'
    return float(stevilo_v_nizu)
