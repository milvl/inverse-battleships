# <p style="text-align: center;">Dokumentace k semestrální práci z předmětu KIV/UPS <br><br> Inverzní lodě</p>

> Autor: Milan Vlachovský

## Obsah

- [1. Úvod](#1-úvod)
- [2. Popis hry](#2-popis-hry)
- [3. Popis síťového protokolu](#3-popis-síťového-protokolu)
- [4. Architektura systému](#4-architektura-systému)
- [5. Návod na zprovoznění](#5-návod-na-zprovoznění)
  - [5.1 Klientská část](#51-klientská-část)
  - [5.2 Serverová část](#52-serverová-část)
- [6. Struktura projektu](#6-struktura-projektu)
- [7. Algoritmické a implementační detaily](#7-algoritmické-a-implementační-detaily)
- [8. Závěr](#8-závěr)

## 1. Úvod

Cílem tohoto projektu bylo vytvořit elementární hru pro více hráčů používající síťovou komunikaci se serverovou částí v nízkoúrovňovém programovacím jazyce a klientskou částí v programovacím libovolném jazyce. Autor projektu zvolil vlastní variantu hry Lodě s upravenými pravidly nazvanou *&bdquo;Inverse Battleships&ldquo;*. Stejně jako její předloha je hra určena pro 2 hráče, přičemž se hráčí střídají v tazích.<p style="text-indent: 12pt;">Byl zvolen protokol na bázi TCP. Jako programovací jazyk serveru byl zvolen jazyk Go, díky své rychlosti a nízkoúrovňovému přístupu k síťové komunikaci. Klientská část byla implementována v jazyce Python s využitím knihovny [pygame](https://www.pygame.org/news) pro správu vykreslování grafického prostředí hry.</p>

## 2. Popis hry

Hra *Inverse Battleships* je variantou klasické hry Lodě, ve které se hráči snaží najít a zničit všechny lodě protivníka. V této variantě hráči sdílí jedno pole 9x9 a každý dostane na začátku přiřazenou jednu loď. Následně se hráči střídají v tazích, kdy každý hráč se může pokusit vykonat akci na prázdné políčko. Mohou nastat tři situace:

- Hráč zkusí akci na prázdné políčko, ve kterém se nachází nikým nezískaná loď. V tomto případě hráč loď získává a získává body.  

- Hráč zkusí akci na prázdné políčko, ve kterém se nachází protivníkova loď. V tomto případě protivník o loď přichází, je zničena, hráč získává body a protivník ztrácí body.

- Hráč zkusí akci na políčko, na kterém se nic nenachází. V tomto případě hráč nezískává nic.

Hra končí, když jeden z hráčů ztratí všechny lodě. Vítězem je přeživší hráč. Body jsou pouze pro statistické účely a nemají vliv na průběh hry.

## 3. Popis síťového protokolu

## 4. Architektura systému

### Požadavky

Projekt byl vyvíjen s použitím následujících technologií:

- Python 3.12
  - pygame 2.6.0
  - pydantic 2.8.2
  - typing-extensions 4.12.2
  - termcolor 2.5.0
  - pyinstaller 6.11.1
- Go 1.23

> Za použití zmiňovaných technologií by měl být projekt bez problémů spustitelný. Spouštění na starších verzích nebylo testováno a nemusí fungovat správně.

## 5. Návod na zprovoznění

Pro sestavení celého projektu byly vytvořeny soubory *Makefile* a *Makefile.win*, které obsahují instrukce pro sestavení projektu na Unixových a Windows OS. Pro sestavení projektu na Unixových OS stačí spustit příkaz:

```bash
make
```

a pro Windows OS stačí spustit příkaz:

```cmd
make -f Makefile.win
```

Předpokládá se, že je nainstalován program `make`; na Windows je možné použít například [make z chocolatey](https://community.chocolatey.org/packages/make), či jiné alternativy.<p style="text-indent: 12pt;">Skript sestaví spustitelné soubory ve složce *client/bin/* pro klientskou část projektu a ve složce *server/bin/* pro serverovou část projektu. Spustitelné soubory jsou pojmenovány *client* a *server*, případně na Windows *client.exe* a *server.exe*. Stačí pouze z kořenové složky projektu na Unix OS spustit příkaz:</p>

```bash
make
```

Nebo na Windows OS:

```cmd
make -f Makefile.win
```

> Jelikož je klientská část implementována v jazyce Python, je možné ji spustit i bez sestavení. Stačí spustit soubor *client/src/main.py* v Python virtuálním prostředí s nainstalovanými závislostmi ze souboru *requirements.txt*. Spustitelné soubory pro klientskou část byly vytvořeny pomocí knihovny *[pyinstaller](https://pyinstaller.org/en/stable/)* a jejich úspěšnost překladu bývá závislá na operačním systému a verzi Pythonu.

> Na základě standardu [PEP 394](https://peps.python.org/pep-0394/) počítají soubory *Makefile* a *Makefile.win* s tím, že Python rozkaz pod Unixem je `python3` a pod Windows je `python`. V případě odlišného nastavení je nutné soubory upravit.

### 5.1 Klientská část

Klientská část je napsaná v jazyce Python, tedy kód je standardně interpretován řádku po řádce pomocí Python interpreteru. Pro spuštění klientské části je tedy nutné mít nainstalovaný Python 3.12 a nainstalované závislosti ze souboru *requirements.txt*.

#### Spuštění krok za krokem

Autor dopořučuje vytvořit si virtuální prostředí a nainstalovat závislosti pomocí následujících příkazů:

> Příkazy jsou pro Unix OS, pro Windows OS je nutné je přizpůsobit.

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd client/
```

Následně je možné spustit klienta pomocí příkazu:

```bash
python ./src/main.py
```

Je také možné spustit klienta se specifickým nastavením a nastavením logování pomocí:

```bash
python ./src/main.py -c ./cfg/debug_cfg.json -l ./cfg/debug_loggers_cfg.json
```

> Standardně se předpokládá spouštění ze složky *client/*

#### Sestavení spustitelného souboru

Kvůli charakteru jazyka není možné bez externích knihoven vytvořit spustitelný soubor. Autor proto zvolil cestu sestavení pomocí knihovny *pyinstaller*. Pro sestavení spustitelného souboru je nutné mít nainstalovaný *pyinstaller*.<p style="text-indent: 12pt;">Pro sestavení spustitelného souboru stačí pouze spustit z kořenové složky na Unix OS příkaz:</p>

```bash
make client
```

Nebo na Windows OS:

```cmd
make -f Makefile.win client
```

Pro manuální sestavení lze použít kód z Makefile souborů.

### 5.2 Serverová část

Serverová část je napsaná v jazyce Go. Pro sestavení serverové části je nutné mít nainstalovaný Go 1.23 či novější. Sestavení opět probíhá za pomocí souborů *Makefile* a *Makefile.win*. Na Unix OS stačí spustit příkaz:

```bash
make server
```

Na Windows OS:

```cmd
make -f Makefile.win server
```

Make sestaví spustilený soubor ve složce *server/bin/* s názvem *server*.

#### Spuštění serveru

Pro spuštění serveru je nutné zadat jako parametr buď IP adresu, na které bude server naslouchat (parametr *-a*), nebo specifikovat konfigurační soubor (parametr *-c*). Pro spuštění serveru na 127.0.0.1 a na portu 8080 stačí zadat: 

```bash
./server/bin/server -a "127.0.0.1:8080"
```

> Při volbě IP adresy a portu je vhodné zjistit, zda je adresa a port dostupný a nejsou blokovány firewallem apod.

## 6. Struktura projektu

### Kořenová složka

<!-- strom: -->
<!-- .
├── ./Makefile
├── ./Makefile.win
├── ./client/
│   ├── ./client/Doxyfile
│   ├── ./client/cfg/
│   │   ├── ./client/cfg/debug_cfg.json
│   │   ├── ./client/cfg/debug_loggers_cfg.json
│   │   ├── ./client/cfg/debug_loggers_cfg_win.json
│   │   ├── ./client/cfg/default_config.json
│   │   ├── ./client/cfg/default_user_config.json
│   │   ├── ./client/cfg/loggers_config.json
│   │   └── ./client/cfg/users/
│   ├── ./client/docs/
│   ├── ./client/res/
│   │   ├── ./client/res/colors.json
│   │   ├── ./client/res/img
│   │   └── ./client/res/strings.json
│   └── ./client/src/
│       ├── ./client/src/const/
│       │   ├── ./client/src/const/exit_codes.py
│       │   ├── ./client/src/const/loggers.py
│       │   ├── ./client/src/const/paths.py
│       │   └── ./client/src/const/typedefs.py
│       ├── ./client/src/game/
│       │   ├── ./client/src/game/connection_manager.py
│       │   ├── ./client/src/game/ib_game.py
│       │   └── ./client/src/game/ib_game_state.py
│       ├── ./client/src/graphics/
│       │   ├── ./client/src/graphics/game_session.py
│       │   ├── ./client/src/graphics/menus
│       │   │   ├── ./client/src/graphics/menus/info_screen.py
│       │   │   ├── ./client/src/graphics/menus/input_menu.py
│       │   │   ├── ./client/src/graphics/menus/lobby_select.py
│       │   │   ├── ./client/src/graphics/menus/primitives.py
│       │   │   ├── ./client/src/graphics/menus/select_menu.py
│       │   │   └── ./client/src/graphics/menus/settings_menu.py
│       │   └── ./client/src/graphics/viewport.py
│       ├── ./client/src/main.py
│       └── ./client/src/util/
│           ├── ./client/src/util/assets_loader.py
│           ├── ./client/src/util/etc.py
│           ├── ./client/src/util/file.py
│           ├── ./client/src/util/generic_client.py
│           ├── ./client/src/util/graphics.py
│           ├── ./client/src/util/init_setup.py
│           ├── ./client/src/util/input_validators.py
│           ├── ./client/src/util/loggers.py
│           └── ./client/src/util/path.py
├── ./docs/
├── ./requirements.txt
└── ./server/
    ├── ./server/cfg/
    ├── ./server/docs/
    └── ./server/src/
        ├── ./server/src/const
        │   ├── ./server/src/const/const_file/
        │   │   └── ./server/src/const/const_file/const_file.go
        │   ├── ./server/src/const/custom_errors/
        │   │   └── ./server/src/const/custom_errors/custom_errors.go
        │   ├── ./server/src/const/exit_codes/
        │   │   └── ./server/src/const/exit_codes/exit_codes.go
        │   ├── ./server/src/const/msg/
        │   │   └── ./server/src/const/msg/msg.go
        │   └── ./server/src/const/protocol/
        │       └── ./server/src/const/protocol/server_communication.go
        ├── ./server/src/go.mod
        ├── ./server/src/logging/
        │   └── ./server/src/logging/logging.go
        ├── ./server/src/main.go
        ├── ./server/src/server/
        │   ├── ./server/src/server/connection_manager.go
        │   └── ./server/src/server/client_manager.go
        └── ./server/src/util/
            ├── ./server/src/util/arg_parser/
            │   └── ./server/src/util/arg_parser/arg_parser.go
            ├── ./server/src/util/cmd_validator/
            │   └── ./server/src/util/cmd_validator/cmd_validator.go
            ├── ./server/src/util/msg_parser/
            │   └── ./server/src/util/msg_parser/msg_parser.go
            └── ./server/src/util/util.go -->

- *Makefile* &mdash; Soubor pro sestavení projektu na Unix OS.

- *Makefile.win* &mdash; Soubor pro sestavení projektu na Windows OS.

- *client/* &mdash; Složka obsahující kód s klientskou částí aplikace.

  - *client/Doxyfile* &mdash; Soubor s konfigurací pro Doxygen.

  - *client/cfg/* &mdash; Složka obsahující konfigurační soubory klientské části.
    - *client/cfg/debug_cfg.json* &mdash; Soubor s konfigurací pro debugování.
    - *client/cfg/debug_loggers_cfg.json* &mdash; Soubo s konfigurací logování pro debugování.
    - *client/cfg/debug_loggers_cfg_win.json* &mdash; Soubor s konfigurací logování pro debugování na Windows.
    - *client/cfg/default_config.json* &mdash; Soubor s výchozí konfigurací.
    - *client/cfg/default_user_config.json* &mdash; Soubor s výchozí konfigurací nového uživatele.
    - *client/cfg/loggers_config.json* &mdash; Soubor s konfigurací logování.
    - *client/cfg/users/* &mdash; Složka obsahující konfigurace uživatelů.

  - *client/docs/* &mdash; Složka obsahující dokumentaci kódu klientské části.

  - *client/res/* &mdash; Složka obsahující zdroje pro klientskou část.
    - *client/res/colors.json* &mdash; Soubor s definicemi barev použitých v GUI klienta.
    - *client/res/img/* &mdash; Složka obsahující obrázky použité ve GUI klienta.
    - *client/res/strings.json* &mdash; Soubor s definicemi textoých řetězců použitých v GUI klienta.

  - *client/src/* &mdash; Složka obsahující zdrojové kódy klientské části.

    - *client/src/const/* &mdash; Složka obsahující konstanty.
      - *client/src/const/exit_codes.py* &mdash; Soubor s konstantami pro návratové kódy.
      - *client/src/const/loggers.py* &mdash; Soubor s konstantami pro logování.
      - *client/src/const/paths.py* &mdash; Soubor s cestovými konstantami.
      - *client/src/const/typedefs.py* &mdash; Soubo s definicemi požívaných objektů v kódu klienta.

    - *client/src/game/* &mdash; Složka zastřešující kód pro správu hry.
      - *client/src/game/connection_manager.py* &mdash; Soubor s kódem pro správu spojení se serverem.
      - *client/src/game/ib_game.py* &mdash; Soubor s kódem spravujícím hru.
      - *client/src/game/ib_game_state.py* &mdash; Soubor s kódem pro stav hry.

    - *client/src/graphics/* &mdash; Složka obsahující kód GUI klienta.
      - *client/src/graphics/game_session.py* &mdash; Soubor s kódem pro GUI herní session.
      - *client/src/graphics/menus/* &mdash; Složka obsahující kód GUI menu.
        - *client/src/graphics/menus/info_screen.py* &mdash; Soubor s kódem GUI informační obrazovku.
        - *client/src/graphics/menus/input_menu.py* &mdash; Soubor s kódem GUI vstupní menu.
        - *client/src/graphics/menus/lobby_select.py* &mdash; Soubor s kódem GUI výběr lobby.
        - *client/src/graphics/menus/primitives.py* &mdash; Soubor s kódem pro primitiva GUI.
        - *client/src/graphics/menus/select_menu.py* &mdash; Soubor s kódem pro výběrové menu.
        - *client/src/graphics/menus/settings_menu.py* &mdash; Soubor s kódem pro nastavení.

      - *client/src/graphics/viewport.py* &mdash; Soubor s kódem představujícím viewport pro zobrazování libovolného GUI.

    - *client/src/main.py* &mdash; Soubor s kódem pro spuštění klienta.

    - *client/src/util/* &mdash; Složka obsahující pomocné metody.
      - *client/src/util/assets_loader.py* &mdash; Soubor s kódem pro načítání zdrojů (obrázky, zvuky, ...).
      - *client/src/util/etc.py* &mdash; Soubor s vedlejšími pomocnými metodami.
      - *client/src/util/file.py* &mdash; Soubor s pomocnými metodami pro práci se soubory.
      - *client/src/util/generic_client.py* &mdash; Soubor s kódem představující generického klienta (založeném na socketech).
      - *client/src/util/graphics.py* &mdash; Soubor s pomocnými metodami pro práci s grafikou.
      - *client/src/util/init_setup.py* &mdash; Soubor s kódem pro inicializaci klienta.
      - *client/src/util/input_validators.py* &mdash; Soubor s validátory vstupu.
      - *client/src/util/loggers.py* &mdash; Soubor s kódem pro příspůsobené logování.
      - *client/src/util/path.py* &mdash; Soubor s pomocnými metodami pro práci s cestami.

- *docs/* &mdash; Složka obsahující dokumentaci.

- *requirements.txt* &mdash; Soubor s definicemi Python závislostí.

- *server/* &mdash; Složka obsahující kód s serverovou částí aplikace.

  - *server/cfg/* &mdash; Složka obsahující konfigurační soubory serverové části.

  - *server/docs/* &mdash; Složka obsahující dokumentaci kódu serverové části.

  - *server/src/* &mdash; Složka obsahující zdrojové kódy serverové části.

    - *server/src/const/* &mdash; Složka obsahující konstanty.
      - *server/src/const/const_file/* &mdash; Složka obsahující konstanty pro práci se soubory.
        - *server/src/const/const_file/const_file.go* &mdash; Soubor s konstantami pro práci se soubory.
      - *server/src/const/custom_errors/* &mdash; Složka obsahující definice chyb.
        - *server/src/const/custom_errors/custom_errors.go* &mdash; Soubor s definicemi chyb.
      - *server/src/const/exit_codes/* &mdash; Složka obsahující konstanty pro návratové kódy.
        - *server/src/const/exit_codes/exit_codes.go* &mdash; Soubor s konstantami pro návratové kódy.
      - *server/src/const/msg/* &mdash; Složka obsahující definice uživatelských zpráv.
        - *server/src/const/msg/msg.go* &mdash; Soubor s definicemi uživatelských zpráv.
      - *server/src/const/protocol/* &mdash; Složka obsahující definice síťového protokolu.
        - *server/src/const/protocol/server_communication.go* &mdash; Soubor s definicemi síťového protokolu.

    - *server/src/go.mod* &mdash; Soubor s definicí modulů Go.

    - *server/src/logging/* &mdash; Složka obsahující kód pro logování.
      - *server/src/logging/logging.go* &mdash; Soubor s kódem pro logování.

    - *server/src/main.go* &mdash; Soubor s kódem pro spuštění serveru.

    - *server/src/server/* &mdash; Složka obsahující kód pro správu serveru.
      - *server/src/server/connection_manager.go* &mdash; Soubor s kódem pro správu spojení.
      - *server/src/server/client_manager.go* &mdash; Soubor s kódem pro správu klientů.

    - *server/src/util/* &mdash; Složka obsahující pomocné funkce.
      - *server/src/util/arg_parser/* &mdash; Složka obsahující kód pro parsování argumentů.
        - *server/src/util/arg_parser/arg_parser.go* &mdash; Soubor s kódem pro parsování argumentů.
      - *server/src/util/cmd_validator/* &mdash; Složka obsahující kód pro validaci síťových příkazů.
        - *server/src/util/cmd_validator/cmd_validator.go* &mdash; Soubor s kódem pro validaci síťových příkazů.
      - *server/src/util/msg_parser/* &mdash; Složka obsahující kód pro parsování zpráv.
        - *server/src/util/msg_parser/msg_parser.go* &mdash; Soubor s kódem pro parsování zpráv.
      - *server/src/util/util.go* &mdash; Soubor s pomocnými funkcemi.


<!-- ### Backend (složka *backend/* )

- `db.json`: JSON soubor pro inicializaci databáze pro správný běh hry při prvním spuštění.
- `db_init.py`: Pythonovský skript pro inicializaci databáze.
- `ajax_handler.py`: Pythonovský skript pro zpracování AJAX požadavků s využitím Flask.
- `requirements.txt`: Závislosti pro Python.

### Frontend (složka *js/* )

> Soubory jsou řazeny podle jejich přednosti ve spouštění. Jsou ukázány pouze hlavní soubory, ze kterých je evidentní struktura and fungování hry. Podrobnější popis jednotlivých metod a tříd je uveden v dokumentaci kódu či v souboru **jsdoc.html**. Všechny metody jsou podrobně zdokumentovány pomocí JSDoc.

- **app.js**: Vstupní bod pro hru.
  - Zde dochází k inicializaci hry.
  - Dojde k vytvoření instance PIXI aplikace.
  - Dojde k napojení metod zajistujících škálování a přizpůsobení velikosti okna a pro ovládání klávesnicí.
  - Dojde k načtení všech potřebných assetů (obrázky, zvuky, ...).
  - Vznikne instance hry, kterou reprezentuje třída `Game` z modulu `game.js`.
  - K metodě `update(delta)` z modulu **game.js** je připojen ticker poskytovaný PIXI.js, který zajišťuje pravidelné volání metody `update(delta)` s aktuálním časovým rozdílem mezi jednotlivými vykreslenými snímky.
    - Metoda `update(delta)` zajišťuje aktualizaci stavu hry a jedná se o hlavní smyčku hry.

- **loader.js**: Modul, který zajišťuje načítání assetů.

- **sound_manager.js**: Modul, který zajišťuje používání zvuků ve hře.
  - Obsahuje třídu `SoundManager`, která si drží informace o zvucích ve hře.
  - Každý zvuk se spoustí pomocí metody `playNázevZvuku()`.
  - Instanci třídy `SoundManager` používá třída `Game` a `GameSession` pro spouštění zvuků ve hře.

- **game.js**: Modul obsahující třídu `Game`, která reprezentuje hru.
  - Třída `Game` si drží informaci o stavu ve kterém se hra nachází pomocí proměnné `gameState` (jedná se o instanci třídy `GameState`, která je definována v modulu `game_state.js`).
  - Hlavní metodou je `update(delta)`, která zajišťuje aktualizaci stavu hry.
  - Metoda `update(delta)` je volána z `app.js` a zajišťuje pravidelné volání metody `update(delta)` s aktuálním časovým rozdílem mezi jednotlivými vykreslenými snímky.
  - Funguje na pricipu stavového automatu, kde se v závislosti na stavu hry provádí jiné aktualizace (pro rozhnodování byl použit switch case).
  - V závislosti na stavu hry se volají metody pro aktualizaci jednotlivých částí hry:
    - `handleMainMenuUpdate()`: Aktualizace hlavního menu na základě stisknutých kláves a vybraných možností.
    - `handleGameSessionUpdate(delta)`: Inicializace/aktualizace probíhající herní session.
    - `handleSettingsUpdate()`: Aktualizace nastavení hry na základě stisknutých kláves a vybraných možností.
    - `handleLeaderboardUpdate()`: Aktualizace pohledu žebříčku nejlepších hráčů.
    - `handleGameEndScreen()`: Aktualizace obrazovky po skončení hry.
  - Ve všech těchto metodách se pracuje se dvěma hlavními objekty:
    - `screenContent`: Obsahuje všechny logické objekty, které se mají vykreslit na obrazovku (v případě menu tedy jednotlivé možnosti, v případě herní session tedy herní pole, hráče, nepřátele, ...).
    - `drawingManager`: Jedná se jednu z instancí modulu `drawing_manager_menus.js` pokud se jedná o vykreslování určitého menu, nebo `game_session.js` pokud se jedná o vykreslování herní session.
      - Pokud se jedná o menu, tak se přímo volají metody pro vykreslení celého pohledu na základě aktualizace uživatelského vstupu. Překreslování se děje vždy, když je změněn stav menu nebo z důvodu změny velikosti okna.
      - Pokud se jedná o herní session, tak se neustále volá metoda pro aktualizaci herní session, která si sama spravuje vykreslování herního pole, hráče, nepřátel, ... a zajišťuje interakci mezi nimi včetně kolizí a zpracování vstupu od uživatele. Překresoloání se děje na úrovni herních objektů, které jsou vytvořeny pomocí PIXI.js nikoli na úrovni celého pohledu (z důvodu optimalizace a svižnosti překreslování).
      - > Autorova původní myšlenka byla, že by se instance z modulu drawing_manager používaly pouze pro vykreslování na obrazovku, ale nakonec se ukázalo, že v případě herní session (kvůli složitosti implementace detekce kolizí bez přístupu k hernímu kanvasu atd.) bylo rozumnější nechat si spravovat vykreslování a interakce přímo herní session, neboť detekce a pohyb byl úzce spjat PIXI objekty a bylo by nepřehledné posílat aktualizace mezi různými moduly.
      - JavaScript sice nativně nepodporuje rozhraní, ale na základě autorem vytvořené struktury se očekává, že instance proměnné `drawingManager` bude vždy obsahovat metody:
        - `redraw()` pro překreslení herního pole po změně velikosti okna.
        - `cleanUp()` pro vyčištění kreslící plochy po přechodu na jiný pohled.
      - Všechny stavy zobrazující menu používají metodu `draw()`, která vykresluje `screenContent` na obrazovku.
      - Stav herní session používá metodu `update(delta)`, která zajišťuje aktualizaci herní session a v případě potřeby i překreslení herního pole.

- **game_session.js**: Modul obsahující třídu `GameSession`, která reprezentuje herní session.
  - Třída `GameSession` si drží informaci o stavu ve kterém se herní session nachází pomocí proměnné `gameSessionState` (jedná se o instanci třídy `GameSessionState`, která je definována v modulu `game_session_state.js`).
  - Jako první je nutné zavolat metodu `start()` pro inicializaci herní session.
  - Hlavní metodou je `update(delta)`, která zajišťuje aktualizaci stavu herní session.
  - Metoda `update(delta)` je volána z **game.js** a zajišťuje pravidelné překreslování a aktualizace herní logiky s aktuálním časovým rozdílem mezi jednotlivými vykreslenými snímky.
  - Funguje na pricipu stavového automatu, kde se v závislosti na stavu herní session provádí jiné aktualizace (pro rozhnodování byl použit switch case).
  - V závislosti na stavu herní session se volají metody pro aktualizaci jednotlivých částí hry:
    - `handleGameSessionInProgressUpdate(delta)`: Aktualizace probíhající herní session. Posloupnost aktualizací je následující:
      1) Aktualizace času hry.
      2) Aktualizace HUD pomocí metody `updateStats(delta)`.
      3) Aktualizace herních entit pomocí metody `updateEntities(delta)`. Tato metoda vrací informaci o případném zisku skóre, které je potřeba zpracovat.
         1) Nejprve se získají informace o všech entitách na herním poli (hráč, nepřátelé, bomby, bonusy, ...).
         2) Poté se aktualizuje entita hráče (kolize s entitami a poté pohyb).
         3) Poté se aktualizují nepřátelé (kolize s entitami a poté pohyb).
         4) Poté se aktualizují ničitelné zdi (kolize s entitami).
         5) Poté se aktualizují bomby (pokládání bomb, časovač výbuchu).
         6) Poté se aktualizují výbuchy bomb (vytvoření explozí, časovač trvání explozí).
         7) Nakonec se kontroluje, zda se můžou objevit únikové dveře (pokud jsou splněny podmínky).
      - > K aktualizacím dochází pouze pokud mometálně nedochází ke škálování herního pole (kvůli změně velikosti okna).
    - `handleGameSessionPlayerHitUpdate(delta)`: Aktualizace herní session po zásahu hráče nepřítelem.
      - Zajišťuje problikávání hráče při zásahu nepřítelem a aktualizaci životů hráče.
      - Pokud hráč ztratí všechny životy, tak se stav herní session změní na `GAME_SESSION_STATE_GAME_END`.
      - Pokud hráč má ještě životy, tak se stav herní session změní na `GAME_SESSION_STATE_LEVEL_INFO_SCREEN`.
    - `handleGameSessionLevelInfoScreen(delta)`: Aktualizace obrazovky s informacemi o levelu.
    - `handleGameSessionPausedUpdate()`: Aktualizace obrazovky po pozastavení hry.
    - `handleGameSessionLeavePromptUpdate(delta)`: Aktualizace obrazovky s výzvou k opuštění hry.
    - `handleGameSessionGameEndUpdate(delta)`: Metoda zajišťující správné ukončení herní session.
    - Většina těchto metod pracuje s proměnnou `screenContent`, která obsahuje všechny logické objekty, které se mají vykreslit na obrazovku (v případě herní session tedy herní pole, hráče, nepřátele, HUD, prompty, ...).

- **arena.js**: Modul obsahující třídu `Arena`, která reprezentuje herní pole.
  - Třída `Arena` si drží informace o herním poli (reprezentované 2D polem) vzhledem k obrazovce.
  - Obsahuje metody pro vykreslení a překreslení herního pole.
  - Obsahuje metody pro získání informací o herním poli (získání 2D indexu pole na základě souřadnic, získání souřadnic pole na základě 2D indexu, ...).
  - Obsahuje metodu pro ověření kolize s herním polem (metoda pro výpočet je předávána jako parametr).
  - Také obsahuje metody
    - `draw()`: Metoda pro vykreslení herního pole.
    - `redraw()`: Metoda pro překreslení herního pole.
    - `cleanUp()`: Metoda pro vyčištění herního pole.

- **entity.js**: Modul obsahující třídu `Entity`, která reprezentuje herní entitu.
  - Třída `Entity` si drží informace o herní entitě vzhledem k hernímu poli.
  - Obsahuje metody pro vykreslení entity při jejím vytvoření a aktualizaci entity (detekce kolize a pohyb).
  - Všechny herní entity (hráč, nepřátelé, bomby, exploze, ...) dědí od třídy `Entity` a přepisují metodu `update(delta)` na základě svých potřeb.
  - Obsahuje metody:
    - `spawn(x, y)`: Metoda pro vytvoření entity na herním poli na základě souřadnic.
    - `update(delta)`: Metoda pro aktualizaci entity.
    - `redraw()`: Metoda pro překreslení entity (při změně velikosti okna).
    - `moveToTop()`: Metoda pro přesunutí entity do popředí.
    - `remove()`: Metoda pro odstranění entity z herního pole.

- **levels_config.js**: Modul obsahující konfiguraci levelů pro *normal* mód.
  
> Většina elementů je pozicováná/škálována na základě předem specifikovaných poměrových konstant (vzhledem k šířce/výšce obrazovky/určité entity). Všechny tyto konstanty jsou buď definovány na začátku modulu, na začátku třídy nebo jsou předávány jako parametry metodám. -->

## 7. Algoritmické a implementační detaily

<!-- Způsob kreslení herních elementů v game session prošel v průběhu vývoje velkými změnami. V původní verzi bylo vykreslování a pohybování entit řešeno zvenčí. V průběhu vývoje se ukázalo, že je lepší nechat si spravovat vykreslování a pohybování entit přímo v jejich vlastních instancích, neboť jednotlivé odchylky způsobů aktualizací, založené na typu entity, se daly řešit děděním od nadřazeného, implicitního objektu `Entity`. Před posláním verze testerům tedy došlo k větším změnám v kódu.\
\
Jinak je kód dle autorova úsudku napsaný se standardními postupy pokud se jedná o problematiku jako jsou stavové automaty, zobrazování grafických primitiv na plátně, preškálování, řešení hit testů, pohyb na základě delta času, atd. Úsek kódu, který stojí za zmínku, neboť se jedná o vlastní verzi algoritmu je pohyb nepřátel z modulu **enemy.js**. Způsob jakým se nepřítel pohybuje je následující:

```pseudocode
1. Nepřítel si zkontroluje, zda má nastavený cíl.
2. Pokud nemá cíl, tak se pokusí najít cíl následujícím způsobem:
   1. S určitou pravděpodobností (na základě obtížnosti nepřítele) si vybere pokud jeho cíl bude hráč nebo náhodný bod na herním poli.
   2. S určitou pravděpodobností (na základě obtížnosti nepřítele) si vybere jakým způsobem vypočítá cestu k cíli.
       - Při vyšší obtížnosti se spíše použije BFS algoritmus pro nalezení nejkratší cesty k cíli.
       - Při nižší obtížnosti se spíše použije DFS algoritmus pro nalezení nejkratší cesty k cíli (varianta s náhodným výběrem větve).
   3. Vypočítaná cesta k cíly je tvořena seznamem 2D indexů herního pole.
3. Pokud má cíl, tak se pokouší jednoduchým přičítáním a odečítáním od souřadnic dostat na následující bod v cestě k cíli (vzdálenost je vypočítána v souladu s rychlostí hráče)
4. Takto se pokouší dostat na cíl, dokud není v dosahu cíle.
5. Pokud je v dosahu cíle, tak se cesta k cíli zahodí a algoritmus se opakuje od bodu 1.
``` -->

## 8. Závěr

<!-- Aplikace byla úspěšně dokončena a splnila všechny povinné požadavky ze zadání. Během vývoje projektu si autor rozšířil znalosti v oblasti JavaScriptu, práce s knihovnou PIXI.js a backendového vývoje v Pythonu s Flaskem. Hra byla otestována třemi nezávislými testery a získaná zpětná vazba byla zohledněna při dalším vývoji, což vedlo k vylepšení uživatelského rozhraní a herní logiky.\
\
Autor reflektuje na tento projekt jako na významný krok ve svém studiu, který mu umožnil propojit teoretické znalosti s praktickou realizací software. Cenné bylo zejména řešení reálných programátorských výzev, jako je optimalizace výkonu hry a zajištění plynulého uživatelského zážitku.\
\
Aplikace by dále mohla být rozvíjena přidáním dalších herních módu, vylepšením AI nepřátel pro zvýšení obtížnosti, přidáním power-upů a bonusů a implementací mobilní verze hry, aby byla přístupná širšímu spektru hráčů. Tento projekt posílil autorovy schopnosti jako vývojáře software a ukázal důležitost základů uživatelského rozhraní a herní logiky pro vytvoření kvalitního produktu. -->
