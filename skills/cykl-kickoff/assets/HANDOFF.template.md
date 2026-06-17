# HANDOFF — przejście między wątkami {PROJECT_NAME}

**Wersja:** 1.0.0
**Utworzono:** {YYYY-MM-DD HH:MM CEST}
**Ostatnia aktualizacja:** {YYYY-MM-DD HH:MM CEST}
**Autor:** {autor}
**Status:** LIVING DOCUMENT — snapshot stanu między sesjami. Każdy nowy wątek czyta to po `PROJECT_CONFIG.md`.

> **Po co ten plik:** żeby nowy wątek wszedł w pracę bez gubienia kontekstu. To **cienki** snapshot —
> NIE powiela live-state z `PROJECT_CONFIG.md` (commity, testy, daty). Dodaje to, czego config nie ma:
> „dlaczego tu jesteśmy" i „jaki jest następny ruch".

---

## Start każdego nowego wątku — kolejność czytania

1. `PROJECT_CONFIG.md` → `Current Sprint` — gdzie dokładnie jesteśmy (live, autorytatywne).
2. `docs/HANDOFF.md` (ten plik, sekcja „Snapshot") — dlaczego tu jesteśmy + następny ruch.
3. `docs/ROADMAP.md` — co po kolei.
4. `docs/LESSONS_CANON.md` — czego nie powtarzać.

---

## Snapshot stanu (aktualizuj na końcu każdego dłuższego wątku)

**Data snapshotu:** {YYYY-MM-DD}

**Gdzie jesteśmy (jednym zdaniem):**
{...}

**Ostatnio zamknięte:**
{...}

**Następny ruch + dlaczego:**
{...}

---

<!-- INSTRUKCJA DLA MODELU AI — możesz tę sekcję pominąć czytając plik ręcznie -->

## Jak zaktualizować ten snapshot (na końcu wątku)

Nadpisz sekcję „Snapshot" czterema rzeczami: **data** · **gdzie jesteśmy** · **ostatnio zamknięte** ·
**następny ruch + dlaczego**. Zawsze NADPISUJ (snapshot = stan „teraz"), nie dopisuj kolejnych linii —
ślad zmian zostaje w changelogu. Nie kopiuj tu commitów/testów — to robi `PROJECT_CONFIG`.
W tym samym ruchu: bump wersji + „Ostatnia aktualizacja" w nagłówku **+ wiersz changelogu** —
drift-check w `/start` porównuje nagłówek z changelogiem, bump bez wiersza to fałszywy alarm.

---

## Changelog

| Wersja | Data | Zmiana |
|---|---|---|
| 1.0.0 | {YYYY-MM-DD} | Initial — szablon handoff z /kickoff. |
