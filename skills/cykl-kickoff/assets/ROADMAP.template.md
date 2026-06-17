# ROADMAP — {PROJECT_NAME} (SSOT „co po kolei" + postępu)

**Wersja:** 1.0.0
**Utworzono:** {YYYY-MM-DD HH:MM CEST}
**Ostatnia aktualizacja:** {YYYY-MM-DD HH:MM CEST}
**Autor:** {autor}
**Status:** LIVING DOCUMENT — **jedyne** źródło prawdy o kolejności prac i pozycji w sekwencji.

> **Po co ten plik:** żeby każda sesja wiedziała dwie rzeczy naraz — na którym **etapie projektu**
> jesteśmy i w którym **kroku tego etapu**. Bez tego praca wielosesyjna gubi pozycję.
> **Relacja do innych źródeł (linkuje, nie powiela):** live-state (commity/testy/daty) → `PROJECT_CONFIG.md`;
> jak budujemy → `CLAUDE.md`; czego nie powtarzać → `docs/LESSONS_CANON.md`; przejście między wątkami → `docs/HANDOFF.md`.
>
> **Reguła edycji (ważna):** statusy zmieniaj swobodnie (`/handoff`, `/zamknij`, `/roadmap update`),
> ale treści etapów i kroków **NIE usuwaj i NIE przeredagowuj** przy okazji zmiany statusu.
> Usunięty krok to praca, która znika bezgłośnie — nikt nie zauważy braku. Zmiana zakresu
> wymaga jawnej decyzji użytkownika + powodu w changelogu.

---

## 0. W skrócie, po ludzku

{1-2 zdania: co budujemy i w jakim porządku.}

---

## 1. Pozycja (aktualizowana co sesję — to czyta `/start`)

**Etap {X}/{N}: {nazwa etapu}** · **krok {Y}/{M}: {nazwa kroku}** · status kroku: {IN_PROGRESS}

---

## 2. Etapy (poziom 1 — cały projekt)

Statusy: `TODO` / `IN_PROGRESS` / `DONE` / `BLOCKED`.

| # | Etap | Status | Bramka wyjścia (co musi być prawdą, żeby uznać etap za DONE) |
|---|---|---|---|
| 1 | {etap 1} | IN_PROGRESS | {...} |
| 2 | {etap 2} | TODO | {...} |
| 3 | {etap 3} | TODO | {...} |

---

## 3. Rozbicie bieżącego etapu (poziom 2 — kroki)

> Rozbity jest TYLKO bieżący etap (F6 — anti-overengineering). Następny etap rozbijasz przy
> `/zamknij`, gdy bieżący przejdzie na DONE. Kolumna „Weryfikacja" to warunek flipu na DONE —
> krok bez spełnionej weryfikacji nie jest zrobiony, niezależnie od wrażenia.

**Etap {X}: {nazwa}**

| # | Krok | Status | Weryfikacja (jak sprawdzimy, że zrobione) |
|---|---|---|---|
| {X}.1 | {krok} | IN_PROGRESS | {np. test przechodzi / plik istnieje i ma sekcję Y / smoke-test OK} |
| {X}.2 | {krok} | TODO | {...} |
| {X}.3 | {krok} | TODO | {...} |

---

## 4. Następny ruch (jeden krok naraz)

- **CO:** {jeden krok z tabeli wyżej}
- **PO CO:** {...}
- **Bramka:** {jakie decyzje/akceptacje przed startem}.

---

## 5. Otwarte decyzje strategiczne (należą do właściciela)

| # | Decyzja | Status |
|---|---|---|
| S1 | {...} | OTWARTE |

---

## Changelog

| Wersja | Data | Zmiana |
|---|---|---|
| 1.0.0 | {YYYY-MM-DD} | Initial — etapy z wywiadu /kickoff, rozbity etap 1, Pozycja = 1/{N} · 1/{M}. |
