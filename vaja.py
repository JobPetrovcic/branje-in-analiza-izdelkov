from requests_html import HTMLSession

url='https://www.spar.si/online/kamniski-odscipanci-s-slanino-anton-400g/p/529123'

seansa = HTMLSession()
odgovor = seansa.get(url)
odgovor.html.render()

print(odgovor.html)

from branje_izdelkov import poberi_hranilne_vrednosti, poberi_ime, poberi_kolicino, poberi_sestavine, poberi_vse_informacije

from branje_izdelkov import nalozi_stran_iz_datoteke
neki = nalozi_stran_iz_datoteke("izdelki/529123.html")

print(poberi_ime(neki))
print(poberi_kolicino(neki))
print(poberi_hranilne_vrednosti(neki))
print(poberi_sestavine(neki))
#from branje_izdelkov import poberi_vse_informacije
#print(poberi_vse_informacije(odgovor))

"""import os

print(os.listdir("izdelki"))"""