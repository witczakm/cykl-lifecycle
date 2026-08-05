# Przewodnik komend — zestaw cykl-lifecycle

**Wersja:** 2.7.0  
**Dla kogo:** każda osoba używająca zestawu skilli do prowadzenia projektów wielosesyjnych

---

## Idea w jednym akapicie

Projekt trwający kilkanaście-kilkadziesiąt sesji ma jeden główny problem: każda nowa sesja
zaczyna się bez pamięci o poprzednich. Ten zestaw rozwiązuje to przez 7 komend, które razem
tworzą pętlę: **wejdź → pracuj → zapisz stan → wyjdź → wejdź następnym razem**. Model zawsze
wie, na którym etapie projektu jesteśmy (np. "Etap 2/5") i w którym kroku tego etapu
(np. "krok 3/6"). Nie trzeba niczego "tłumaczyć od początku" przy każdej sesji.

---

## Pętla (jak to wygląda w praktyce)

```
Pierwsza sesja:
  /kickoff  →  wywiad + struktura + pierwszy /start

Każda kolejna sesja:
  /start  →  pracuj  →  (opcjonalnie /migawka lub /lekcja w trakcie)  →  /zamknij

Gdy chcesz sprawdzić postęp:
  /roadmap

Gdy pojawi się wniosek z pracy:
  /lekcja  (dla tego projektu)
  /lekcja-g  (dla wszystkich projektów)
```

---

## /kickoff — założenie projektu

**Kiedy używać:** raz, na samym początku nowego projektu, który będzie trwał wiele sesji.

**Co robi:**
1. Pyta o nazwę, cel i etapy projektu (zwięźle — maks 5-7 pytań)
2. Tworzy strukturę katalogów i pliki dokumentów
3. Wypełnia ROADMAP etapami i rozbija pierwszy etap na kroki
4. Odpala pierwszy `/start`

**Przykładowe użycie:**
```
/kickoff
```
Model zapyta: "Jak ma się nazywać projekt? Jakie są główne etapy (3-7 haseł)?"

**Ważne:**
- Jeśli projekt już istnieje — powiedz "adopt", żeby dołożyć brakujące elementy bez nadpisywania
- Profil struktury: `lite` (mały projekt/PoC), `standard` (typowy), `regulated` (produkcja/audyt)

---

## /start — wejście w sesję

**Kiedy używać:** na początku KAŻDEJ sesji. Najlepiej jako pierwsza komenda po otwarciu czatu.

**Co robi:**
1. Czyta PROJECT_CONFIG, HANDOFF, ROADMAP, LESSONS_CANON
2. **Mierzy stan poza dokumentami** — wykonuje `STATE_PROBE` z PROJECT_CONFIG i porównuje z zapisaną wartością
3. Sprawdza, czy dokumenty są spójne między sobą (drift-check)
4. Referuje: **Pozycja** (Etap X/N · krok Y/M), co ostatnio zamknięte, następny ruch (JEDEN krok)
5. Zgłasza wykryte niespójności + wiszące lekcje globalne do zapisu

> **Dlaczego krok 2 jest przed krokiem 3.** Trzy dokumenty potrafią zgodnie powtarzać tę samą nieaktualną informację i przejść drift-check bez zarzutu — spójność wewnętrzna to nie prawdziwość. Sonda daje jedyny punkt oparcia, który nie pochodzi z dokumentów. Jeśli nie odpowie po trzech próbach, `/start` wpisuje `[DO SPRAWDZENIA]` i **nie blokuje** wejścia w sesję.

**Przykładowe użycie:**
```
/start
```
Oczekiwany output:
```
Pozycja: Etap 2/5 "Implementacja API" · krok 3/7 "Endpoint autoryzacji"
Ostatnio zamknięte: endpoint rejestracji (krok 2) — testy przeszły.
Następny ruch: zaimplementować endpoint /auth/login (krok 3).
Drift: brak. Wiszące lekcje globalne: brak.
```

**Nie odpala się gdy:** wpisujesz "zacznij pisać funkcję", "uruchom npm start", "start serwera"

---

## /zamknij — koniec sesji

**Kiedy używać:** na końcu każdej sesji, przed zamknięciem czatu. Zawsze po realnej pracy.

**Co robi:**
1. Zbiera co się wydarzyło w sesji
2. Aktualizuje HANDOFF (nadpisuje snapshot), ROADMAP (statusy kroków, Pozycja), PROJECT_CONFIG
3. Wyciąga wnioski (opcjonalnie /lekcja lub /lekcja-g)
4. Pokazuje diff + gotowy blok komend git

**Przykładowe użycie:**
```
/zamknij
```
Oczekiwany output:
```
Sesja: zaimplementowano endpoint /auth/login (krok 3) — testy przeszły.
Nowa Pozycja: Etap 2/5 · krok 4/7 "Middleware JWT"
Zaktualizowane: docs/HANDOFF.md v1.4.0, docs/ROADMAP.md v1.3.0
Commit:
  set -euo pipefail
  grep -n "Ostatnia aktualizacja" docs/HANDOFF.md docs/ROADMAP.md PROJECT_CONFIG.md \
    | grep -q "$(date +%Y-%m-%d)" \
    && git add docs/HANDOFF.md docs/ROADMAP.md PROJECT_CONFIG.md \
    && git commit -m "sesja: endpoint login, krok 3/7 DONE"
```

> **Dlaczego blok wygląda tak, a nie prościej.** Warunek „commituj tylko, jeśli daty w plikach są dzisiejsze" musi być **składnią**, nie komentarzem. Wcześniejsze wersje miały `# jeśli data nie jest dzisiejsza — nie commituj` jako adnotację — a człowiek wkleja cały blok naraz, więc `git commit` wykonywał się niezależnie od wyniku sprawdzenia. `set -o pipefail` jest tu obowiązkowe: bez niego `cmd | grep` zwraca kod wyjścia ostatniego elementu potoku i bramka przepuszcza błąd.

**Nie używaj gdy:** sesja była tylko rozmową bez decyzji/zmian — wtedy tylko podsumuj słownie.

---

## /migawka — snapshot w środku sesji

**Kiedy używać:** po ważnej decyzji lub domkniętym kroku roadmapy, gdy nie chcesz czekać do końca sesji.

**Co robi:**
1. Nadpisuje sekcję Snapshot w HANDOFF
2. Jeśli krok się domknął — flipuje jego status i przesuwa Pozycję w ROADMAP
3. Aktualizuje PROJECT_CONFIG jeśli zmienił się live-state

**Przykładowe użycie:**
```
/migawka
```
lub przy długiej sesji po konkretnej decyzji:
```
Zdecydowałem: używamy Redis zamiast Memcached. /migawka
```

**Różnica /migawka vs /zamknij:**
| | /migawka | /zamknij |
|---|---|---|
| Kiedy | W trakcie sesji | Na koniec sesji |
| Lekcje | Nie | Tak |
| Commit | Nie (zbiorczo potem) | Tak |
| Zakres | HANDOFF + CONFIG + krok w ROADMAP | Wszystko |

**Nie odpala się przy:** snapshotach testów (Jest/Vitest), VM snapshots, backupach baz danych

---

## /roadmap — przegląd postępu

**Kiedy używać:** gdy chcesz zobaczyć "z lotu ptaka" — gdzie jesteśmy w całym projekcie i co zostało.

**Co robi:**
1. Pokazuje Pozycję (Etap X/N · krok Y/M)
2. Statusy kroków bieżącego etapu (DONE/IN_PROGRESS/TODO)
3. Sekwencję pozostałych etapów

**Przykładowe użycie:**
```
/roadmap
```
Oczekiwany output:
```
Pozycja: Etap 2/5 "Implementacja API" · krok 3/7 "Endpoint autoryzacji"

Etap 2 — kroki:
[DONE] 2.1 Konfiguracja routera
[DONE] 2.2 Endpoint rejestracji  
[IN_PROGRESS] 2.3 Endpoint autoryzacji
[TODO] 2.4 Middleware JWT
[TODO] 2.5 Refresh token
[TODO] 2.6 Wylogowanie
[TODO] 2.7 Testy integracyjne

Dalsze etapy: 3-Frontend (TODO) · 4-Testy E2E (TODO) · 5-Deploy (TODO)
```

**Aktualizacja roadmapy:**
```
/roadmap update zmieniamy kolejność: 2.5 (refresh token) przed 2.4 (middleware)
```

**Nie używaj dla:** roadmapy produktu klienta, strategii firmy zewnętrznej

---

## /lekcja — zapis wniosku projektowego

**Kiedy używać:** gdy pojawi się nauka specyficzna dla tego projektu — "żeby nie wrócić do tego błędu".

**Co robi:**
1. Pyta: czy ta lekcja dotyczy TYLKO tego projektu czy wszystkich? (routing zasięgu)
2. Formułuje w formacie: **Reguła** + **Dlaczego** + **Test operacyjny**
3. Dopisuje do docs/LESSONS_CANON.md

**Przykładowe użycie:**
```
/lekcja
Straciłem godzinę bo nie sprawdziłem czy Redis jest uruchomiony przed testem.
```
Model zapisze:
```
### W7 — Weryfikacja zależności przed testem
Reguła: Przed uruchomieniem testów integracyjnych sprawdź czy zewnętrzne usługi (Redis, DB) są active.
Dlaczego: Stracone 1h na diagnozowanie testu, który failował bo Redis był zatrzymany.
Test: `docker ps | grep redis` przed `npm test` lub guard w setup.ts.
```

**Różnica /lekcja vs /lekcja-g:**
- `/lekcja` → "ten konkretny projekt", zapis bez pytania
- `/lekcja-g` → "każdy projekt", zawsze pyta o zgodę

---

## /lekcja-g — zapis wniosku globalnego

**Kiedy używać:** gdy wniosek jest tak ogólny, że będzie przydatny we WSZYSTKICH Twoich projektach.

**Co robi:**
1. Sprawdza: czy to naprawdę globalna? (test: "prawdziwa w innym projekcie?")
2. Formułuje lekcję
3. Pyta o zgodę (zawsze — bez zgody nie zapisuje)
4. W Cowork: wstawia marker `[CANDIDATE GLOBAL]` i podaje polecenie dla CCT
5. W CCT: zapisuje do `~/.claude/context/lessons.md` jako GL-NNN

**Przykładowe użycie:**
```
/lekcja-g
Zawsze sprawdzaj wersję API w dokumentacji przed implementacją — minęło 6 miesięcy i endpoint się zmienił.
```

**Ważne:**
- W Cowork: musisz potem odpalić polecenie w CCT, żeby lekcja faktycznie trafiła do warstwy globalnej
- `/start` przy następnym wejściu przypomni o wiszących kandydatach jeśli zapomnisz

---

## Reguły, które warto znać

**1. Jeden krok naraz**  
`/start` zawsze podaje JEDEN następny krok. Nie próbuj planować 5 kroków do przodu w jednej sesji — to prowadzi do połowicznie zrobionej pracy i nieudokumentowanego stanu.

**2. DONE tylko z dowodem**  
Krok w ROADMAP dostaje status DONE tylko gdy kolumna "Weryfikacja" jest spełniona (test przeszedł, plik istnieje, smoke-test OK). "Wydaje się działać" to nie DONE.

**3. Changelog przy każdym bumpie wersji**  
Gdy model aktualizuje nagłówek dokumentu (Wersja + data), zawsze dopisuje też wiersz w changelogu. Bez tego `/start` zgłosi drift. Jeśli widzisz dziwny "drift alarm" — sprawdź czy changelog zgadza się z nagłówkiem.

**4. Nie musisz nic pamiętać między sesjami**  
To jest cały sens systemu. `/start` odczyta aktualny stan. Pisz komendy, rób pracę, `/zamknij` — i zapomnij do następnej sesji.

**5. Pola dziennikowe rosną, pola stanowe są nadpisywane**  
Changelog i nagłówek dokumentu są **przyrostowe** — dopisujesz warstwę, poprzednia zostaje. Pola opisujące stan (stan repo, następna otwarta decyzja, publiczny adres, hash wdrożonego artefaktu) mają **jedną** prawdziwą wartość i są **nadpisywane w całości po pomiarze**, ze znacznikiem `[zmierzone RRRR-MM-DD HH:MM UTC]`. Dopisanie do pola stanowego robi z niego listę sprzecznych stanów, w której czytający bierze pierwszy — czyli najstarszy. Jeśli w takim polu siedzi też trwała wiedza (obejścia, ograniczenia narzędzi), rozszczep je na dwa: `REPO_STATE` nadpisywane i `REPO_NOTES` przyrostowe.

**6. Bramka jest składnią, nie komentarzem**  
Wszędzie, gdzie warunek decyduje o wykonaniu (commit po sprawdzeniu, etap na DONE po bramce wyjścia), warunek musi być egzekwowalny. Komentarz „zrób Y tylko gdy X" nie zatrzyma niczego.

**7. Pomiar ma datę ważności**  
„Dziś zero zmian" zmierzone o 18:00 bywa nieprawdą o 21:00. Dlatego znacznik pomiaru zawiera godzinę, a nie samą datę — i dlatego zamykanie dnia przed jego końcem jest pomiarem przedwczesnym.

---

## Typowy dzień pracy

```
# Poranek — wejście
/start
→ "Pozycja: Etap 2/5 · krok 3/7. Następny ruch: endpoint autoryzacji."

# Praca (normalna rozmowa z Claude)
...implementacja...

# W połowie — ważna decyzja architektoniczna
/migawka

# Koniec dnia
/zamknij
→ diff + blok git add/commit (wklejam do terminala)
```

---

## Pytania i odpowiedzi

**Q: Muszę wpisywać /start ręcznie?**  
A: Nie. Skill cykl-start odpala się automatycznie gdy Claude wykryje, że zaczynasz sesję w projekcie (wrócenie po przerwie, "gdzie byliśmy"). Ale wpisanie /start jest zawsze bezpieczne.

**Q: Co jeśli nie commituję przez kilka sesji?**  
A: Nic się nie gubi — dokumenty są na dysku, a commit możesz zebrać zbiorczo z ostatniego `/zamknij`. Od 2.6.0 `/start` to jednak **zauważy i powie**: `STATE_PROBE` porówna żywy stan repo z tym, co zapisano w PROJECT_CONFIG, więc zaległe commity albo rozjazd z remote wyjdą na wejściu w sesję, a nie po tygodniu. Wcześniej praca niezacommitowana wyglądała identycznie jak zacommitowana, bo `/start` czytał wyłącznie pliki.

**Q: Czy skille działają z GitHubem/Jirą/Notion?**  
A: Te skille zarządzają wyłącznie lokalnymi dokumentami projektu (Markdown w repo). Integracja z zewnętrznymi narzędziami to osobny temat.

**Q: Mogę używać /start bez /zamknij z poprzedniej sesji?**  
A: Tak, ale dostaniesz drift-alarm jeśli dokumenty są nieaktualne. Model powie "HANDOFF jest z 3 dni temu" — potraktuj to jako sygnał do ręcznego /migawka przed pracą.

**Q: Czy te skille działają w Claude API (bez Cowork/CCT)?**  
A: Działają, ale musisz zainstalować je lokalnie w projekcie (Opcja C w instrukcji instalacji) i upewnić się, że masz włączone narzędzie do odczytu/zapisu plików (computer_use lub bash_tool).
