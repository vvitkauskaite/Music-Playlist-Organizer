<!--
Encoding: UTF-8
Language: Lithuanian
-->

# TuneTide: Muzikos grojaraščių organizatorius
 
Autorius: Vaiva Vitkauskaitė  
Grupė: EDIf-24/2  
Vilnius Tech, 2025 



# Kursinio darbo ataskaita


## Įvadas (Introduction)


### Kas tai per programa?

„TuneTide“ – tai muzikos grojaraščių internetinė aplikacija, leidžianti vartotojams kurti ir redaguoti asmeninius grojaraščius, įkelti savo muzikos failus, klausytis jų tiesiogiai naršyklėje bei valdyti savo dainų biblioteką. 

Sistema palaiko dvi dainų kategorijas – vartotojo įkeltą (lokalią) muziką ir viešą (public) muzikos kolekciją. Vartotojai gali pervardinti grojaraščius, pridėti aprašymus ir nuotraukas, ieškoti dainų pagal pavadinimą.

Aplikacija sukurta naudojant Python (su Flask), HTML, CSS ir JavaScript, o backend’e taikomi python OOP principai, dizaino šablonai, failų skaitymas/rašymas ir testavimas.


### Kaip paleisti programą?

1. Įsitikinkite, kad kompiuteryje įdiegtas **Python 3.10+**.
2. Atsisiųskite arba nuklonuokite projektą iš GitHub į savo kompiuterį:
>    git clone https://github.com/vvitkauskaite/Music-Playlist-Organizer.git
3. Atidarykite projektą su VS Code arba kita IDE.
4. Terminale įveskite:
>    ```
>    pip install -r requirements.txt
>    ```
>    Tai įdiegs visas reikalingas bibliotekas.
5. Norėdami paleisti programą, terminale įveskite:
>    ```
>    python app.py
>    ```
6. Atidarykite naršyklę ir eikite į adresą **http://127.0.0.1:5000/**
>
> Ten galėsite registruotis, įkelti dainas, kurti grojaraščius ir naudotis visa sistema.


### Kaip naudotis programa?

Atidarius „TuneTide“ naršyklėje, naudotojas mato pradinį registracijos arba prisijungimo langą.

1. **Registracija**  
Norint naudotis sistema, reikia prisiregistruoti įvedant vartotojo vardą, el. paštą ir slaptažodį.

2. **Pagrindinis valdymo langas (Dashboard)**  
Prisijungus, vartotojas mato valdymo langą, kuriame pateikiamos šios sekcijos:
- **Local Songs** – vartotojo įkelti muzikos failai (.mp3).
- **Public Songs** – iš anksto įkelta bendroji muzikos kolekcija.
- **Playlists** – vartotojo sukurti grojaraščiai.
 
3. **Muzikos įkėlimas**  
Naudotojas gali įkelti savo .mp3 failus į „Local Songs“ biblioteką spustelėjęs „Upload“ mygtuką.

4. **Grojaraščių kūrimas ir valdymas**  
- Spustelėjęs „Create Playlist“, naudotojas gali sukurti naują grojaraštį.
- Spustelėjus grojaraštį, jis atsidaro kaip mažas „popup“ langas.
- Ten galima pervardinti grojaraštį, pridėti aprašymą ir nuotrauką.

5. **Dainų paieška**  
Yra du atskiri paieškos laukeliai:
- Vienas ieško tik tarp įkeltų (local) dainų.
- Kitas – tarp „Public Songs“ kolekcijos.

6. **Grojimas**  
Sistema turi įtaisytą muzikos grotuvą, leidžiantį klausyti bet kurią pasirinktą dainą. Rodo pavadinimą, laiko slankiklį, garso lygį.

7. **Papildomos funkcijos**  
        - Animacinės bangelės dekoratyviai puošia svetainę pagal temą.
        - Grojaraščiai numeruoja dainas ir leidžia leisti kiekvieną atskirai.


---


## Analizė/Programos paaiškinimas (Body/Analysis)

### Objektinio programavimo principai (OOP)

#### Encapsulation
Programa naudoja klases su privačiais laukais ir viešais metodais, kad paslėptų vidinę logiką ir apsaugotų duomenis. Klasė User naudoja privačius laukus su dviem pabraukimais (__) ir @property metodą, kad apsaugotų duomenis ir leistų prieigą tik per viešą metodą.

```python
class User:
    def __init__(self, u_name, gmail, password):
        self.__u_name = u_name
        self.__gmail = gmail
        self.__password = password

    @property
    def name(self):
        return self.__u_name
```


#### Inheritance
Tam tikros klasės paveldi savybes iš bendresnių klasių. Klasė PublicLibrary paveldi Library klasę ir perima jos metodus bei savybes.

```python
class Library:
    def __init__(self, name):
        self.name = name
        self.songs = []

class PublicLibrary(Library):
    def load_public_songs(self):
        pass
```


#### Abstraction
Pagrindiniai programos komponentai (pvz., daina, grojaraštis) yra atvaizduoti kaip klasės, paslepiant jų vidinę logiką. Song yra abstrakti bazinė klasė, kuri apibrėžia bendras dainos savybes, bet play() metodas paliekamas įgyvendinti paveldinčioms klasėms.

```python
from abc import ABC, abstractmethod

class Song(ABC):
    def __init__(self, s_name, artist, duration):
        self.s_name = s_name
        self.artist = artist
        self.duration = duration

    @abstractmethod
    def play(self):
        pass
```


#### Polymorphism
Įvairūs objektai gali naudoti tą patį metodą skirtingai. Abi klasės PublicSong ir LocalSong paveldi Song ir įgyvendina tą patį metodą play() skirtingai – tai polimorfizmas.

```python
class PublicSong(Song):
    def play(self):
        print(f"Playing public song: {self.s_name}")

class LocalSong(Song):
    def play(self):
        print(f"Playing local song: {self.s_name}")

```


#### Singleton
TuneTide naudoja Singleton dizaino šabloną valdyti muzikos grotuvui – kad egzistuotų tik vienas grotuvo objektas visos programos metu:

```python
class MusicPlayer(metaclass=SingletonMP):
    def __init__(self):
        self.volume = 50
        self.current_song = None
        self.is_playing = False

    def play_song(self, user: User, song: Song):
        self.current_song = song
        song.play()
        HistoryLogger.log_song(user.name, song)
        self.is_playing = True
```


#### Composition and aggregation
**Kompozicija**: Vartotojas "turi" savo biblioteką ir grojaraščius, ir kai jis pašalinamas, visi tie objektai ištrinami kartu. Tai – kompozicija, nes objektai neegzistuoja be vartotojo.

```python
class User:
    def __init__(self, ...):
        self.private_library = ...
        self.playlists = [...]
```
**Agregacija**: Grojaraščiai turi dainas, bet tos dainos (ypač viešos – PublicSong) egzistuoja nepriklausomai - jos saugomos atskirame aplanke, į playlistus tik pridėtos, bet jų neištrinsi su playlistu. Todėl čia agregacija: playlistas naudoja dainas, bet jų nekontroliuoja ir nesunaikina.

```python
class Playlist:
    def __init__(self):
        self.songs = [...]
```


#### Reading from file & writing to file
HistoryLogger klasė rašo informaciją apie paleistas dainas į failą Recently_Played.txt ir iš jo skaito. Tai leidžia naudotojui matyti savo klausytų dainų istoriją.

```python
class HistoryLogger:
    @staticmethod
    def log_song(user_name, song):
        with open("Recently_Played.txt", 'a', encoding='utf-8') as file:
            file.write(f"{user_name},{song.s_name},{datetime.date.today()}\n")

    @staticmethod
    def read_history():
        try:
            with open("Recently_Played.txt", 'r', encoding='utf-8') as file:
                return file.readlines()
        except FileNotFoundError:
            return ["No history found."]
```

---

## Rezultatai (Results)

### Ką pavyko padaryti?

- Sukurta pilnai veikianti muzikinė aplikacija su galimybe kurti, redaguoti ir valdyti grojaraščius.
- Įgyvendintas dainų įkėlimas, jų atkūrimas bei istorijos saugojimas į failą.
- Pritaikyti visi keturi objektinio programavimo principai ir vienas dizaino šablonas (Singleton).
- Įdiegta dviguba paieškos sistema: atskirai local ir public dainų paieškai.
- Sukurtas estetiškas vartotojo sąsajos dizainas su animuotomis bangelėmis, atitinkančiomis „TuneTide“ tematiką.


### Kokie iššūkiai iškilo?

- Iškilo problemų su sesijų tvarkymu, ypač registracijos kontekste.
- Failų įkėlimas reikalavo papildomo dėmesio dėl leidžiamų formatų, saugumo (`secure_filename`) ir įrašymo kelių.
- Sudėtingiau buvo įgyvendinti grojaraščių popup langų dizainą, kad jie nepažeistų kitų svetainės elementų.


### Kokios funkcijos veikia?

- Vartotojų registracija.
- Muzikos failų įkėlimas (lokali biblioteka).
- Grojaraščių kūrimas, redagavimas (pavadinimas, aprašymas, nuotrauka), dainų pridėjimas ir išimimas.
- Istorijos failo rašymas ir peržiūra.
- Paieška tarp skirtingų dainų bibliotekų.
- Muzikos grotuvas su dainos informacija, trukme, garsumu.


### Kokie buvo naudotojo testai (jei buvo)?

- Atliekant testavimą, vartotojai sėkmingai sukūrė grojaraštį, įkėlė dainą ir perklausė ją per grotuvo sąsają.
- Testuota, ar dainos perkeliamos į grojaraštį ir ar jos ten lieka net perkrovus puslapį.
- Patikrintas istorijos failas – ar daina tinkamai įrašoma po perklausos.
- Išbandytas registracijos mechanizmas: neteisingas el. paštas, užimtas vartotojo vardas ir sėkminga registracija.


### Ką galima būtų patobulinti ar pridėti ateityje?

- Pridėti galimybę vartotojams įvertinti ar komentuoti dainas.
- Sukurti filtravimo funkcijas pagal dainos ilgį, žanrą ar atlikėją.
- Pridėti galimybę dalintis grojaraščiais su kitais naudotojais.
- Įdiegti prisijungimo patvirtinimą el. paštu ir slaptažodžio keitimą.

---


## Apibendrinimas (Conclusion)

Šio kursinio darbo metu buvo sukurta pilnai veikianti internetinė muzikos grojaraščių organizavimo sistema „TuneTide“. Projektas sėkmingai pritaikė visus objektinio programavimo principus – inkapsuliaciją, paveldėjimą, abstrakciją ir polimorfizmą – bei panaudojo Singleton dizaino šabloną. 

Aplikacija leidžia vartotojams registruotis, įkelti muzikos failus, kurti ir valdyti grojaraščius, klausytis dainų, o visa vartotojo veikla (pvz. perklausytos dainos) fiksuojama istorijos faile. Taip pat išskiriamos lokali ir vieša muzikos bibliotekos, palaikomos paieškos.

Projekto rezultatas – patogi, estetiška sistema, kuri gali būti tobulinama ateityje. Galimos plėtros kryptys: pažangesnė vartotojų sąveika, bendri grojaraščiai, rekomendacijų sistema, papildomi formatai ir prisijungimo autentifikavimas per el. paštą ar socialinius tinklus.