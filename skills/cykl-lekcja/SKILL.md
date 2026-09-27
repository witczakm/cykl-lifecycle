---
name: cykl-lekcja
description: Złap wniosek dotyczący TEGO projektu i dopisz go do LESSONS_CANON projektu (lekcja wykonawcza W lub fundamentalna F). Użyj gdy użytkownik pisze "/lekcja", "zapisz lekcję", "to na przyszłość", "wniosek z tego", "następnym razem inaczej", albo gdy w trakcie pracy pojawi się powtarzalna nauka specyficzna dla tego projektu. Jeśli wniosek dotyczy KAŻDEGO projektu użytkownika — użyj zamiast tego /lekcja-g. NIE używaj gdy mowa o lekcji w sensie edukacyjnym (plan lekcji, kurs, nauka języka, lekcja muzyki) — skill zapisuje wnioski projektowe, nie materiały edukacyjne.
---
<!-- cykl-lifecycle v2.8.0 -->

# /lekcja — wniosek projektowy

## Cel

Złapać wniosek od razu, gdy się pojawi, i dopisać go do docs/LESSONS_CANON.md tego projektu —
żeby nauka nie zginęła do końca sesji i żeby błąd nie wrócił.

## Najpierw rozstrzygnij zasięg

Zanim zapiszesz: "Czy ta lekcja byłaby prawdziwa w INNYM projekcie użytkownika?"

- TAK → globalna → przerwij i użyj /lekcja-g.
- NIE, ale obowiązuje w przyszłych sprintach → projektowa → zapisz (kroki niżej).
- NIE, dotyczy tylko bieżącego zadania → lokalna → nie zapisuj do kanonu, wystarczy notatka. Kanon to rzeczy trwałe.
- Granica niepewna → zapytaj użytkownika.

## Kroki (lekcja projektowa)

1. Sformułuj w formacie kanonu:
   - Reguła — 1 zdanie, co robić.
   - Dlaczego — precedent: co się stało, że ta lekcja powstała.
   - Test operacyjny — jak sprawdzić, że ją stosuję.

2. Zapisz do docs/LESSONS_CANON.md:
   - Nowy wpis W{kolejny numer} (wykonawcza — typowe) lub F{kolejny od F10} (fundamentalna — rzadkie). F1-F6 to baseline z /kickoff; projektowe F numeruj od F10 (F7-F9 = bufor i wizualna granica).
   - Numer ustal sprawdzając najwyższy istniejący. Przy równoległej sesji — potwierdź numer z użytkownikiem.
   - **Miejsce wstawki: koniec Części II, PRZED `## Changelog`** — nigdy koniec pliku. Lekcja za
     changelogiem to lekcja, której `/start` nie czyta (zdarzyło się 32 razy w jednym projekcie).
   - Dopisz wiersz changelogu + zsynchronizuj nagłówek (Wersja + Ostatnia aktualizacja).
   - Uruchom `python3 <katalog skilla cykl-start>/scripts/porzadek.py <katalog projektu>` — test
     „brak lekcji za Changelogiem" musi być PASS.

3. Pokaż użytkownikowi, co dopisałeś (informacyjnie — nie wymaga zgody).

## Zasady

- Lokalna lekcja nie idzie do kanonu — nie zaśmiecaj go jednorazówkami.
- Format Reguła/Dlaczego/Test jest obowiązkowy — bez "dlaczego" i "testu" lekcja staje się martwa.
- Precedens w "Dlaczego" podawaj liczbą z pomiaru, nie przymiotnikiem ("0 z 131 rekordów", nie "prawie żadne").
- Nie wykonuj git. Commit zbiorczo przy /zamknij.

## Powiązane

- /lekcja-g — wniosek globalny (poza projekt, zawsze za zgodą).
- /zamknij — używa tej samej logiki przy zbiorczym wyciąganiu lekcji.
