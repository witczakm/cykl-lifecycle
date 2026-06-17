# LESSONS_CANON — kanon lekcji {PROJECT_NAME}

**Wersja:** 1.0.0
**Utworzono:** {YYYY-MM-DD HH:MM CEST}
**Ostatnia aktualizacja:** {YYYY-MM-DD HH:MM CEST}
**Autor:** {autor}
**Status:** LIVING DOCUMENT — kanon zasad pracy. Każda sesja czyta to na starcie, przed pracą.

> **Po co ten plik:** żeby błędy, które kosztowały czas, **nie wracały**. Jedno miejsce prawdy o tym, jak pracujemy.
> **Jak czytać:** każda zasada ma **Regułę** (1 zdanie), **Dlaczego** (precedent), **Test operacyjny** (jak sprawdzić, że ją stosuję).
> F = fundamentalne (CO budować i w jakiej kolejności). W = wykonawcze (JAK pracujemy w praktyce).

---

## Część I — Zasady fundamentalne (F)

> **Nota:** F1–F6 to universalne fundamenty pre-ładowane w każdym nowym projekcie.
> Projektowe lekcje dodawaj od W1 (wykonawcze) lub F10 (fundamentalne projektowe).

### F1 — Buy-before-build
**Reguła:** Zanim zbudujesz: sprawdź, czy istnieje gotowe narzędzie, biblioteka lub usługa, która robi to czego potrzebujesz. Godzina researchu > tydzień implementacji.
**Dlaczego:** Budowa własnego rozwiązania, gdy istniał gotowy open-source — stracone dni pracy.
**Test operacyjny:** Czy przed implementacją sprawdziłeś, że nie istnieje gotowiec? Jeśli nie — STOP, zrób research.

### F2 — Brief przed implementacją
**Reguła:** Przed napisaniem kodu: jedno zdanie CO budujesz + jedno zdanie PO CO. Brak briefu = implementacja założeń, które mogą być błędne.
**Dlaczego:** Brief daje moment na wychwycenie alternatywy lub błędnego założenia, zanim włożysz pracę.
**Test operacyjny:** Czy potrafisz w dwóch zdaniach powiedzieć CO i PO CO, zanim powstanie pierwsza linia kodu?

### F3 — Fundament first
**Reguła:** Buduj od warstwy najniżej w stosie. Nie buduj UI zanim masz działające API. Nie pisz testów zanim masz działający kod.
**Dlaczego:** Budowanie nadbudowy zanim istnieje fundament = praca włożona w komponent na nieistniejącej podstawie.
**Test operacyjny:** Czy warstwa, na której się opieram, już istnieje i działa?

### F4 — Fakty nie założenia
**Reguła:** Weryfikuj w kodzie i danych, nie z pamięci. Oddzielaj: fakty | założenia | ryzyka | rekomendacje. Nie uspokajaj bez dowodu.
**Dlaczego:** Błędne założenie o danych albo status „działa" zależny od środowiska wykonawcy daje fałszywe poczucie gotowości.
**Test operacyjny:** Czy każde twierdzenie o kodzie ma `plik:linia`? Czy „zielony" status pochodzi z niezależnego re-runu w czystym środowisku?

### F5 — Nazwane wzorce
**Reguła:** Używaj sprawdzonych, nazwanych wzorców (Repository, Strategy, Circuit Breaker...) zamiast wymyślać własne. Nazwy pozwalają komunikować architekturę.
**Dlaczego:** Wymyślone od zera rozwiązania niosą nieprzewidziane ryzyka, których sprawdzone wzorce już nie mają.
**Test operacyjny:** Czy potrafię nazwać wzorzec, który implementuję, i wskazać gdzie jest stosowany?

### F6 — Anti-overengineering
**Reguła:** Nie buduj ciężkich komponentów przed potrzebą. Slot na przyszłość (interfejs, pusta metoda) zamiast implementacji. Uprość zanim rozbudujesz.
**Dlaczego:** Przedwczesna złożoność = koszt utrzymania bez wartości tu i teraz.
**Test operacyjny:** Czy to, co buduję, ma realnego konsumenta TERAZ?

---

## Część II — Zasady wykonawcze (W) — z praktyki tego projektu

> Tu dopisujesz lekcje przez `/lekcja`. Pierwsza pojawi się jako W1.

{brak — dopisuj przez /lekcja}

---

## Changelog

| Wersja | Data | Zmiana |
|---|---|---|
| 1.0.0 | {YYYY-MM-DD} | Initial — F1-F6 (fundament uniwersalny) + pusta sekcja W. Szablon z /kickoff. |
