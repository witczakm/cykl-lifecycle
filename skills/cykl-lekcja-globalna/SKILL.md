---
name: cykl-lekcja-globalna
description: Złap wniosek GLOBALNY — taki, który obowiązuje w KAŻDYM projekcie użytkownika, nie tylko bieżącym — i zapisz go do globalnego pliku lekcji dostępnego wszystkim projektom. Użyj gdy użytkownik pisze "/lekcja-g", "lekcja globalna", "to dotyczy wszystkich projektów", "zapisz globalnie", albo gdy nauka jest uniwersalna (sposób pracy z narzędziami, wzorzec komunikacji, zasada procesu — nie specyfika jednego projektu). Lekcja globalna ZAWSZE wymaga zgody użytkownika przed zapisem. NIE używaj gdy mowa o lekcji w sensie edukacyjnym ani gdy wniosek dotyczy tylko bieżącego projektu — wtedy użyj /lekcja.
---
<!-- cykl-lifecycle v2.3.0 -->

# /lekcja-g — wniosek globalny

## Cel

Zapisać lekcję działającą ponad pojedynczym projektem do warstwy globalnej dostępnej każdemu
projektowi użytkownika. Osobny skill, bo lekcja globalna wpływa na INNE projekty — nie wolno
zapisać automatem. Zawsze wymaga jawnej zgody.

## Najpierw potwierdź, że to naprawdę globalna

Test: "Czy ta lekcja byłaby prawdziwa i użyteczna w INNYM projekcie użytkownika?"
- TAK i jest uniwersalna → globalna, kontynuuj.
- Dotyczy tylko tego projektu → użyj /lekcja.
- Niepewne → zapytaj. Przy wątpliwości wybieraj projektową.

## Gdzie trafia lekcja globalna

Cel zależy od środowiska (numeracja zawsze GL-NNN):

| Środowisko | Plik docelowy | Zapis |
|---|---|---|
| Claude Code (CCT) | `~/.claude/context/lessons.md` | bezpośrednio |
| Codex | `~/.codex/AGENTS.md` (sekcja „cykl-lifecycle — global lessons") | bezpośrednio, za zgodą; sandbox może poprosić o zatwierdzenie zapisu poza katalogiem projektu |
| Cowork | brak zapisu do `~/.claude/` → marker [CANDIDATE GLOBAL] + gotowa komenda dla CCT | dwuetapowo |

Dlaczego `~/.codex/AGENTS.md`: to plik globalnych instrukcji, który Codex czyta na starcie KAŻDEJ sesji w każdym projekcie — więc lekcja realnie zaczyna obowiązywać. Dopisuj zwięźle (globalny limit ~32 KiB).

## Kroki

1. Sformułuj lekcję:
   - Reguła (1 zdanie) + Dlaczego (precedent) + Test operacyjny.
   - Status: PROPOSED. Owner: użytkownik. Data. Zakres. Ewentualne przeciwwskazania.

2. Pokaż użytkownikowi treść + uzasadnienie "czemu globalna" → czekaj na OK. Bez zgody nie idź dalej.

3. Po zgodzie — zapis zależnie od środowiska:
   - **Claude Code / Codex (terminal):** dopisz bezpośrednio do pliku docelowego (tabela wyżej) jako GL-NNN, pod nagłówkiem sekcji. W Codeksie zapis do ~/.codex/AGENTS.md jest poza katalogiem projektu — sandbox może poprosić o zatwierdzenie; to oczekiwane.
   - **Cowork (brak zapisu globalnego):** wstaw w docs/LESSONS_CANON.md marker [CANDIDATE GLOBAL: do zapisu przez CCT] przy lekcji i podaj gotową treść + polecenie dla CCT.

4. Po faktycznym zapisie GL-NNN (przez terminal lub CCT):
   - Podmień marker [CANDIDATE GLOBAL] na [GLOBALNA → GL-NNN].
   - Dopisz GL-NNN do GLOBAL_LESSONS_BASELINE w PROJECT_CONFIG.md.

## Siatka bezpieczeństwa

Kandydat nie zależy od ludzkiej pamięci: /start przy każdym wejściu skanuje LESSONS_CANON
pod kątem [CANDIDATE GLOBAL] i przypomina z gotowym poleceniem dla CCT.

## Zasady

- Zawsze za zgodą. Nigdy automatem.
- Cowork nie deklaruje "zapisane globalnie" — robi to i potwierdza terminal (Claude Code lub Codex).
- Marker [GLOBALNA → GL-NNN] wolno wstawić dopiero po faktycznym zapisie GL-NNN.

## Powiązane

- /lekcja — wniosek projektowy.
- /start — wykrywa wiszące kandydatury globalne.
- /zamknij — może wywołać tę logikę przy zbiorczym wyciąganiu lekcji.
