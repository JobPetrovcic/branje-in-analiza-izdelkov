try:
    from requests_html import HTMLSession, HTML
except Exception as e:
    print("Prosim namesti knjižnico requests_html z uporabo pip-a.")

# funkcije za dobivanje strani in shranjevanje strani
def stran_v_niz(url):
    try:
        seansa = HTMLSession()
            
        odgovor = seansa.get(url)
        odgovor.html.render()

        vsebina = odgovor.html.html

        seansa.close()
    except Exception as e:
        print(f"Pri doseganju spletne strani je prišlo do naslednje napake:{e}")
    else:
        return vsebina

def shrani_niz(besedilo, pot):
    with open(pot, 'w', encoding='utf-8') as datoteka:
        datoteka.write(besedilo)

def shrani_stran(url, pot):
    shrani_niz(stran_v_niz(url), pot)


# funkcije za naložitev strani iz tekstovne datoteke
def niz_v_html_objekt(niz):
    # Vrne html objekt knjižnice requests_html
    html = HTML(html=niz)
    return html

def preberi_datoteko(pot):
    with open(pot, 'r', encoding='utf-8') as datoteka:
        return datoteka.read()

def nalozi_stran_iz_datoteke(pot):
    return niz_v_html_objekt(preberi_datoteko(pot))