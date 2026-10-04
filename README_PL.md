# Fusion 360 Linux Arch Fixes

[English README](README.md)

Nieoficjalny zestaw poprawek dla **Autodesk Fusion 360** uruchamianego przez
[`stonegray/fusion360-linux`](https://github.com/stonegray/fusion360-linux) na
**Arch Linux i dystrybucjach opartych o Arch**, m.in. CachyOS, EndeavourOS i
Manjaro.

Projekt **nie zawiera Fusion 360, plików Autodesk, Wine ani Protona**. Modyfikuje
wyłącznie skrypty launchera/helperów w istniejącej instalacji
`fusion360-linux`.

> Testowane na Arch/CachyOS, KDE Plasma 6 / Wayland, NVIDIA, GE-Proton 10-32 i
> Fusion 360 w październiku 2026.

## Co naprawia

- zamienia błędną dla Arch nazwę zależności `python3-tk` na `tk`, jeśli plik
  zależności instalatora jest obecny;
- poprawia składanie `WINEDLLOVERRIDES` — niezależne reguły są rozdzielane `;`;
- ustawia trwały override `bcp47langs` w rejestrze prefixu Wine, co omija błąd
  `bcp47langs.dll.GetUserLanguages, aborting` w Autodesk Identity Manager;
- domyślnie wyłącza problematyczny Toolwindow Fixer;
- usuwa podwójne uruchamianie Toolwindow Fixera i sprawia, że monitor zdrowia
  respektuje ustawienie włącz/wyłącz;
- zastępuje szerokie zabijanie Wine/Proton przez `wineserver -k` ograniczony do
  prefixu Fusion, aby zamknięcie Fusion nie kończyło innych programów/gier;
- rejestruje callbacki Autodesk `adsk://` i `adskidmgr://` przez `gio`, co omija
  problemy z `xdg-mime`, np. brak `qtpaths`;
- robi backup przed modyfikacją;
- sprawdza składnię zmodyfikowanych skryptów przez `bash -n`.

## Wymagania

Musisz mieć już zainstalowany `stonegray/fusion360-linux`, standardowo w:

```text
~/.local/share/fusion360-linux
```

i konfigurację w:

```text
~/.config/fusion360-linux/config
```

Potrzebne są także Python 3, Bash, `gio` z GLib oraz działająca konfiguracja
Protona w `fusion360-linux`.

## Szybki start

```bash
git clone https://github.com/terrakot2001/fusion360-linux-arch-fixes.git
cd fusion360-linux-arch-fixes
./install.sh
```

Następnie uruchom Fusion normalnie:

```bash
~/.local/share/fusion360-linux/launch-fusion.sh
```

Patcher jest idempotentny — ponowne uruchomienie nie powinno dublować zmian.

## Sprawdzenie instalacji

```bash
./check.sh
```

albo:

```bash
python3 fusion360_arch_fix.py check
```

Najważniejsze kontrole powinny zakończyć się `[OK]`.

## Backup i przywracanie

Każde `apply` tworzy backup w:

```text
~/.local/share/fusion360-linux/backup-arch-fixes/
```

Lista backupów:

```bash
python3 fusion360_arch_fix.py backups
```

Przywrócenie najnowszego:

```bash
python3 fusion360_arch_fix.py restore
```

Przywrócenie konkretnego:

```bash
python3 fusion360_arch_fix.py restore ~/.local/share/fusion360-linux/backup-arch-fixes/YYYYMMDD-HHMMSS
```

Przywracane są pliki. Ustawienia MIME przez `gio` i wpis `bcp47langs` w rejestrze
Wine pozostają celowo bez zmian.

## Logowanie Autodesk

Typowy poprawny przebieg:

1. Fusion otwiera logowanie Autodesk.
2. Przeglądarka otwiera Autodesk Accounts.
3. Po zalogowaniu przeglądarka wywołuje `adskidmgr:/login?...`.
4. `fusion-callback-handler.sh` zapisuje żądanie callback.
5. `fusion-browser-listener.sh` przekazuje je do `AdskIdentityManager.exe`.
6. Fusion przyjmuje token i przechodzi do interfejsu programu.

W logu Neutron Platform dobrym sygnałem są m.in.:

```text
IDSDK immediatly returned success in sign-in dialog.
IDSDKAuth: idsdk_get_token returned IDSDK_E_SUCCESS
```

Więcej informacji: [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md).

## Toolwindow Fixer

Patcher pozostawia:

```text
FUSION_ENABLE_TOOLWINDOW_FIXER=0
```

To celowe. W obserwowanej wersji helper potrafił tworzyć bardzo dużą liczbę
procesów `fusion-toolwindow-fixer.exe`. Fusion działa bez niego, ale na części
konfiguracji Wine/KDE pierwsze okna samouczka mogą mieć problem z kolejnością
warstw. Wtedy pomocna jest nawigacja klawiaturą `Tab`, `Space`, `Enter`, `Esc`.

## Bezpieczeństwo i prywatność

Patcher nie wysyła logów, tokenów Autodesk, identyfikatorów konta, danych
przeglądarki ani projektów użytkownika. Nie publikuj pełnych callbacków Autodesk
w zgłoszeniach — mogą zawierać krótkotrwałe kody logowania i wartości `state`.

## Zakres projektu

To niewielka warstwa kompatybilności dla konkretnych problemów Arch/CachyOS z
`stonegray/fusion360-linux`, a nie pełny instalator Fusion. Projekt nie próbuje
obsługiwać wszystkich środowisk graficznych, sterowników GPU ani wersji Protona.

## Licencja

Skrypty i dokumentacja są udostępnione na licencji MIT. Autodesk, Fusion i
Fusion 360 są znakami towarowymi Autodesk, Inc. Projekt jest nieoficjalny i nie
jest powiązany ani wspierany przez Autodesk.
