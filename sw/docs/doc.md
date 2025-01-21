# <p style="text-align: center;">Dokumentace k semestrální práci z předmětu KIV/UPS <br><br>Téma práce: Hra Inverzní lodě</p>

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
- [7. Popis implementace](#7-popis-implementace)
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

> Příkazy jsou pro Unix OS, pro Windows OS je nutné je přizpůsobit.

```bash
./server/bin/server -a "127.0.0.1:8080"
```

> Při volbě IP adresy a portu je vhodné zjistit, zda je adresa a port dostupný a nejsou blokovány firewallem apod.

## 6. Struktura projektu

Projekt je rozdělen následovně:

- *Kořenová složka* &mdash; Obsahuje soubory pro sestavení projektu, složky *client* a *server*, složku *docs* s dokumentací a soubor *requirements.txt* s definicemi Python závislostí.
  - *client/* &mdash; Obsahuje celou klientskou část projektu včetně konfiguračních souborů, použitých textových a obrazových zdrojů a programátorské referenční dokumentace.
  - *server/* &mdash; Obsahuje celou serverovou část projektu včetně konfiguračních souborů a programátorské referenční dokumentace.

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
  - *docs/doc.md* a *docs/doc.pdf* &mdash; Tento dokument ve formátu Markdown a PDF.
  - *docs/client_ref.html* &mdash; Odkaz na dokumentaci klientské části.
  - *docs/server_ref.html* &mdash; Odkaz na dokumentaci serverové části.

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

## 7. Popis implementace

### 7.1 Klientská část

Klientská část aplikace byla implementována v jazyce Python s využití knihovny **pygame** pro grafické rozhraní. Hlavní součásti klienta jsou rozděleny do modulů podle jejich funkce.

> Veškerý kód se nachází pod složkou *client/src/*.

Při běhu programu pracuje vždy jedno hlavní vlákno, které se stará o logiku hry, zpracovávání vstupů a vykreslování grafického rozhraní. Pro správu asynchronní komunikace se serverem je vždy vytvořeno vlastní vlákno, které

#### Moduly klientské části

1. **game**
   - *connection_manager.py*: Spravuje připojení klienta k serveru pomocí socketů.
   - *ib_game.py*: Obsahuje hlavní logiku hry, jako je zpracování tahů a synchronizace herního stavu se serverem.
   - *ib_game_state.py*: Reprezentuje stav hry a poskytuje API pro manipulaci s herními daty.

2. **graphics**
   - *game_session.py*: Zajišťuje vykreslování herního prostředí a interakci uživatele s hrou.
   - *menus*: Obsahuje moduly pro tvorbu a správu herních menu, jako jsou vstupní obrazovky, lobby nebo nastavení.

3. **util**
   - *assets_loader.py*: Zajišťuje načítání grafických a zvukových souborů.
   - *loggers.py*: Implementuje vlastní logování pro snadněší diagnostiku a ladění.
   - *init_setup.py*: Zajišťuje inicializaci klientské aplikace.

#### Rozvrstvení klientské aplikace

Klientská část je navržena jako modulární aplikace s jasným rozdělením na:

- **Prezentaci (UI)**: Moduly v *graphics*.
- **Logiku hry**: Moduly v *game*.
- **Podpůrné funkce**: Moduly v *util*.

#### Použité knihovny klientské části

- **pygame 2.6.0**: Pro vykreslování grafického rozhraní.
- **pydantic 2.8.2**: Pro validaci dat.
- **termcolor 2.5.0**: Pro barevné logování v terminálu.
- **pyinstaller 6.11.1**: Pro sestavení spustitelných souborů.

#### Paralelizace klienta

Klientská část využívá moduly knihovny **asyncio** pro správu asynchronní komunikace se serverem, což umožňuje zpracovávat zprávy od serveru souběžně s vykreslováním a zpracováním vstupů uživatele.

### 7.2 Serverová část

Serverová část byla implementována v jazyce Go pro svou rychlost a efektivní práci s paralelizací. Server je navržen jako modulární aplikace s těmito hlavními komponentami:

#### Moduly serverové části

1. **server**
   - *connection_manager.go*: Spravuje připojení klientů a jejich komunikaci se serverem.
   - *client_manager.go*: Uchovává informace o připojených klientech a jejich stavech.

2. **util**
   - *arg_parser.go*: Zajišťuje parsování argumentů při spouštění serveru.
   - *cmd_validator.go*: Validuje příkazy přijaté od klientů.
   - *msg_parser.go*: Zajišťuje správné formátování zpráv při odesílání a příjmu.

3. **const**
   - *protocol/server_communication.go*: Obsahuje definice protokolu a formátu zpráv mezi klientem a serverem.

#### Rozvrstvení serverové aplikace

Server je rozdělen do těchto vrstev:

- **Komunikační vrstva**: Moduly *connection_manager* a *client_manager*.
- **Aplikační logika**: Validace a zpracování příkazů v *util*.
- **Konfigurace**: Moduly v *const*.

#### Použité knihovny serverové části

- **Go 1.23**: Základní runtime.
- Standardní knihovna Go pro práci s net (TCP komunikace).

#### Paralelizace

Server využívá **gorutiny** pro souběžné zpracování klientských požadavků. Pro synchronizaci dat jsou používány **mutexy** a kanály (*channels*).

---

Tento popis poskytuje přehled o implementaci obou částí aplikace a může být dle potřeby rozšířen o další detaily.




## 8. Závěr

