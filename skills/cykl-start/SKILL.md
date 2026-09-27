---
name: cykl-start
description: Wejście w sesję projektu wielosesyjnego — wczytaj stan z dokumentów i zreferuj "gdzie jesteśmy + następny ruch". Użyj na początku KAŻDEJ sesji projektu, gdy użytkownik pisze "/start", "zacznijmy sesję", "gdzie jesteśmy w projekcie", "co było ostatnio w projekcie", "wróćmy do projektu", albo wraca do pracy po przerwie. Uruchom też zanim zaczniesz jakąkolwiek pracę nad projektem wielosesyjnym, nawet bez prośby. NIE używaj, gdy "start/zacznij" dotyczy uruchamiania programu, serwera, kontenera, skryptu (npm start, docker start, cargo run) albo pisania kodu — to praca techniczna, nie wejście w sesję projektu.
---
<!-- cykl-lifecycle v2.8.0 -->

# /start — wejście w sesję

## Cel

Zacząć sesję od faktów, nie od pamięci. Wczytujesz stan projektu z dokumentów i mówisz
użytkownikowi jednym akapitem: gdzie jesteśmy, co ostatnio zamknięte, jaki jest następny ruch.
Jedyny zapis, jaki `/start` wykonuje, to mechaniczny porządek (krok 0.5) — historia idzie do
`docs/archive/`, treść bieżąca się nie zmienia. Powód: praca bez wczytania stanu prowadzi do decyzji
opartych na nieaktualnej pamięci, a dokumenty bywają rozjechane z rzeczywistością (drift).

## Kroki

0. **Sprawdź, czy to projekt cykl-lifecycle.** Jeśli w katalogu projektu NIE ma PROJECT_CONFIG.md
   ani docs/HANDOFF.md — to nie jest projekt prowadzony tym systemem. Powiedz to wprost
   i zaproponuj /kickoff (tryb adopt). Nie wymyślaj stanu i nie szukaj plików poza katalogiem.

0.5. **Porządek automatyczny — ZANIM cokolwiek przeczytasz.** Uruchom skrypt leżący obok tego pliku:
   `python3 <katalog tego skilla>/scripts/porzadek.py --wykonaj <katalog projektu>`
   Skrypt przenosi historię (stos nagłówków wersji, bloki `STAN POPRZEDNI`/`AKTUALIZACJA` poza pierwszym,
   stare snapshoty, sekcje „Historia…", starsze wiersze changelogu) do `docs/archive/<NAZWA>-RRRR-Qn.md`,
   wraca lekcje zabłąkane za `## Changelog` na miejsce i drukuje tabelę PASS/FAIL. Nic nie kasuje.
   Do referatu (krok 3) wklej: listę „co przeniesiono" + wiersze FAIL (nie całą tabelę). FAIL po
   porządku = zadanie dla `/zamknij` tej sesji: rozmiar przez prozę w jednej sekcji (skrypt wskazuje
   największą — od niej zaczynasz) albo pole stanowe bez znacznika pomiaru (naprawia `/migawka`, nigdy
   przepisanie starej wartości). Rozmiar LESSONS_CANON to INFO, nie FAIL — kanon rośnie z wiedzą.
   INFO „możliwa inna żywa sesja" (plik zmieniony < 30 min temu) + niezacommitowane dokumenty stanu
   = odnotuj w referacie i nie ruszaj cudzych zmian; to nie jest drift do naprawy przez Ciebie.
   Powód: przez cztery kolejne sesje drift był ZGŁASZANY i nie naprawiany; reguła w tekście nie działa,
   skrypt działa. Bez `python3` → zgłoś to i czytaj dalej (nie blokuj wejścia).

1. **Wczytaj dokumenty w tej kolejności** (po jednym, gdy potrzebne — nie wszystkie hurtem):
   - PROJECT_CONFIG.md — `STATE_PROBE` + sekcja Current Sprint (live-state: stan repo, status, ryzyka).
   - docs/HANDOFF.md — sekcja "Snapshot" (gdzie jesteśmy + następny ruch).
   - docs/ROADMAP.md — Pozycja (etap X/N · krok Y/M) + rozbicie bieżącego etapu.
   - docs/LESSONS_CANON.md — czego nie powtarzać.

2. **Zrób lekki drift-check.**
   - **Najpierw pomiar zewnętrzny.** Jeśli PROJECT_CONFIG ma `STATE_PROBE=`, wykonaj tę komendę i porównaj
     wynik z polem stanowym. Dokumenty zgodne ze sobą bywają zgodnie nieaktualne — spójność wewnętrzna
     to nie prawdziwość. Maks. 3 próby; brak odpowiedzi = `[DO SPRAWDZENIA]`, nie blokuj wejścia w sesję.
     Brak pola `STATE_PROBE=` → zmierz ręcznie (`git rev-parse --short HEAD`, `git log --oneline -3`)
     i zgłoś w referacie: „brak STATE_PROBE — dopisać przy /zamknij".
   - Czy nagłówek HANDOFF/ROADMAP (Wersja + Ostatnia aktualizacja) zgadza się z ostatnim wpisem changelogu? Rozjazd = drift.
   - Czy CURRENT_SPRINT/CURRENT_MILESTONE w PROJECT_CONFIG jest spójny z HANDOFF i Pozycją w ROADMAP?
   - Czy linia Pozycja zgadza się ze statusami kroków w rozbiciu?
   - **Czytaj CAŁE pole stanowe, nie jego początek.** Pola w PROJECT_CONFIG bywają bardzo długie
     (>1000 znaków); obcięcie do pierwszych N znaków pokazuje najstarszą wartość jako bieżącą.
   - **Kilka stanów w jednym polu = drift**, nawet jeśli najnowsza wartość w nim jest. Sygnał: więcej niż
     jedna data albo więcej niż jedno „Stan (…)" w tej samej linii. Zgłoś to jako drift do naprawy przez
     `/migawka`, wskazując, która wartość jest bieżąca.
   - **Ucięty odczyt nie jest dowodem nieobecności** — listing obcięty limitem albo `head` mówi „nie widzę", nie „nie ma".
   - **Rozmiar i jeden blok bieżący** mierzy `porzadek.py` (krok 0.5) — nie powtarzaj tego ręcznie;
     cytuj jego tabelę.
   - Wiszące lekcje globalne: przeskanuj docs/LESSONS_CANON.md pod kątem [CANDIDATE GLOBAL]. Jeśli są — zgłoś z gotowym poleceniem zapisu globalnego dla Twojego środowiska (Claude Code lub Codex).
   - Jeśli coś się rozjeżdża — powiedz wprost. Fałszywe "wszystko gra" jest gorsze niż uczciwe "te dokumenty się nie zgadzają".

3. **Zreferuj** (zwięźle, maks 1 strona):
   - Pozycja: Etap X/N "nazwa" · krok Y/M "nazwa".
   - Gdzie jesteśmy (1 zdanie).
   - Co ostatnio zamknięte.
   - Następny ruch = JEDEN krok + dlaczego (nie planuj kilku kroków naraz).
   - Tabela `porzadek.py` (co przeniesiono + FAIL, które zostały) — FAIL zostaje zadaniem `/zamknij`.
   - Wykryty drift / wiszące kandydatury globalne + propozycja naprawy.

## Zasady

- Działaj na faktach. Brak informacji = [BRAK INFORMACJI], nie domyślaj się.
- **Pomiar przeczy dokumentowi? Najpierw sprawdź, czy mierzysz właściwy obiekt** — ten, którego używa
  bieżący krok, nie ten o podobnej nazwie. Dopiero potem podejrzewaj dokument.
- Poza `porzadek.py` nic nie zapisuj. Drift treści napraw przez /migawka albo /zamknij.
- Nie wykonuj git mutującego. `STATE_PROBE` musi być read-only — obowiązuje zakaz z kroku 2 `/zamknij`.

## Powiązane

- /migawka — zapisz stan po decyzji w środku sesji.
- /zamknij — domknij sesję na końcu.
- /roadmap — pokaż pozycję i sekwencję prac.
