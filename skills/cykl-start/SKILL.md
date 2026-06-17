---
name: cykl-start
description: Wejście w sesję projektu wielosesyjnego — wczytaj stan z dokumentów i zreferuj "gdzie jesteśmy + następny ruch". Użyj na początku KAŻDEJ sesji projektu, gdy użytkownik pisze "/start", "zacznijmy sesję", "gdzie jesteśmy w projekcie", "co było ostatnio w projekcie", "wróćmy do projektu", albo wraca do pracy po przerwie. Uruchom też zanim zaczniesz jakąkolwiek pracę nad projektem wielosesyjnym, nawet bez prośby. NIE używaj, gdy "start/zacznij" dotyczy uruchamiania programu, serwera, kontenera, skryptu (npm start, docker start, cargo run) albo pisania kodu — to praca techniczna, nie wejście w sesję projektu.
---
<!-- cykl-lifecycle v2.3.0 -->

# /start — wejście w sesję

## Cel

Zacząć sesję od faktów, nie od pamięci. Wczytujesz stan projektu z dokumentów i mówisz
użytkownikowi jednym akapitem: gdzie jesteśmy, co ostatnio zamknięte, jaki jest następny ruch.
To read-only. Powód: praca bez wczytania stanu prowadzi do decyzji opartych na nieaktualnej
pamięci, a dokumenty bywają rozjechane z rzeczywistością (drift).

## Kroki

0. **Sprawdź, czy to projekt cykl-lifecycle.** Jeśli w katalogu projektu NIE ma PROJECT_CONFIG.md
   ani docs/HANDOFF.md — to nie jest projekt prowadzony tym systemem. Powiedz to wprost
   i zaproponuj /kickoff (tryb adopt). Nie wymyślaj stanu i nie szukaj plików poza katalogiem.

1. **Wczytaj dokumenty w tej kolejności** (po jednym, gdy potrzebne — nie wszystkie hurtem):
   - PROJECT_CONFIG.md — sekcja Current Sprint (live-state: branch, status, ryzyka).
   - docs/HANDOFF.md — sekcja "Snapshot" (gdzie jesteśmy + następny ruch).
   - docs/ROADMAP.md — Pozycja (etap X/N · krok Y/M) + rozbicie bieżącego etapu.
   - docs/LESSONS_CANON.md — czego nie powtarzać.

2. **Zrób lekki drift-check** (przez czytanie plików, nie git):
   - Czy nagłówek HANDOFF/ROADMAP (Wersja + Ostatnia aktualizacja) zgadza się z ostatnim wpisem changelogu? Rozjazd = drift.
   - Czy CURRENT_SPRINT/CURRENT_MILESTONE w PROJECT_CONFIG jest spójny z HANDOFF i Pozycją w ROADMAP?
   - Czy linia Pozycja zgadza się ze statusami kroków w rozbiciu?
   - Wiszące lekcje globalne: przeskanuj docs/LESSONS_CANON.md pod kątem [CANDIDATE GLOBAL]. Jeśli są — zgłoś z gotowym poleceniem zapisu globalnego dla Twojego środowiska (Claude Code lub Codex).
   - Jeśli coś się rozjeżdża — powiedz wprost. Fałszywe "wszystko gra" jest gorsze niż uczciwe "te dokumenty się nie zgadzają".

3. **Zreferuj** (zwięźle, maks 1 strona):
   - Pozycja: Etap X/N "nazwa" · krok Y/M "nazwa".
   - Gdzie jesteśmy (1 zdanie).
   - Co ostatnio zamknięte.
   - Następny ruch = JEDEN krok + dlaczego (nie planuj kilku kroków naraz).
   - Wykryty drift / wiszące kandydatury globalne + propozycja naprawy.

## Zasady

- Działaj na faktach. Brak informacji = [BRAK INFORMACJI], nie domyślaj się.
- Nic nie zapisuj. Drift napraw przez /migawka albo /zamknij.
- Nie wykonuj git.

## Powiązane

- /migawka — zapisz stan po decyzji w środku sesji.
- /zamknij — domknij sesję na końcu.
- /roadmap — pokaż pozycję i sekwencję prac.
