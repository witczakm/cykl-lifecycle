# Ochrona scalania (edycje GitHub i GitHub + wiele agentów)
[English](MERGE-PROTECTION.md) · **Polski**

[Przykładowy hook](../hooks/pre-commit.sample) (skrypt, który git uruchamia automatycznie przed zapisaniem commita) sprawdza całe drzewo przygotowane do commita (staged tree), a nie katalog roboczy (worktree).
Da się go obejść i nie zastępuje on [lifecycle-integrity](../.github/workflows/lifecycle-integrity.yml).
Action (automatyczne zadanie GitHub Actions) korzysta z zaufanego walidatora (programu sprawdzającego poprawność plików) i sprawdza próbne scalenie względem **obu rodziców oraz
merge-base (wspólnego przodka obu gałęzi)**, w tym decyzje, zobowiązania, jawne zamknięcia i niezmienne archiwa.
Action używa `--merge-result`: sprawdza sumę zawartości obu rodziców i merge-base,
nie wymagając, by NOW wymieniał sztuczne commity-rodziców, które GitHub tworzy na potrzeby próbnego scalenia. Każdy identyfikator O/A/D/L
obecny w którymkolwiek z rodziców albo w merge-base musi pozostać w work/DECISIONS albo mieć jawną linię zamykającą
w scalonym NOW (identyfikator, akcja close/supersede, czyli zamknięcie lub zastąpienie, oraz powód). Treść wpisów, metadane,
kolejność, znaczniki czasu, rozliczone wiersze i historyczne skróty (hashe) źródeł nie są porównywane.
Zmiany po jednej stronie i zmiany po obu stronach przechodzą, gdy suma identyfikatorów zostaje zachowana albo zamknięta;
to samo dotyczy późniejszego PR po rozliczonej aktualizacji. Ciche usunięcie zobowiązania z drugiej strony kończy się błędem.
Bez `--merge-result` nadal dostępne są jawne sprawdzenia UUID rodziców i bazy dla
osobno przygotowanego checkpointu uzgadniającego (zapisu stanu po pogodzeniu gałęzi) względem jego migawek źródłowych.

W każdym repozytorium, które to wdraża: zainstaluj walidator pod tą samą ścieżką, przygotuj na start przejrzaną
zaufaną wersję (opcjonalnie przez zmienną repozytorium `LIFECYCLE_VALIDATOR_REF`), ustaw kontrolę
`lifecycle-integrity` jako required check (kontrolę, bez której GitHub nie pozwoli scalić PR), zabroń zwykłego omijania zabezpieczeń i bezpośrednich pushy (wysyłania zmian prosto do gałęzi z pominięciem PR), wymagaj aktualnych PR
albo merge queue (kolejki scalania, która testuje każdy PR na najnowszym stanie gałęzi). `--trusted-root` porównuje skrót SHA-256 (odcisk zawartości pliku) workflow z kandydata z
zaufaną kopią i odrzuca podmianę lub usunięcie przy sprawdzaniu projektu i pakietu.
Workflow i walidator wdrażaj na start razem; aktualizacja workflow wymaga autoryzowanej
aktualizacji zaufanej wersji, a nie oczekiwanego skrótu podanego w samym PR.

**Wymagane jest egzekwowanie z zewnątrz:** skonfiguruj wymagany workflow, którego definicja
i wersja są kontrolowane poza PR. Jeśli taka polityka jest niedostępna, wymagaj
zatwierdzenia przez CODEOWNERS (wyznaczonych właścicieli plików) dla `.github/workflows/**`, `.github/CODEOWNERS` i ścieżki zaufanego
walidatora, unieważniaj nieaktualne zatwierdzenia po nowych commitach i zabroń zwykłego omijania zabezpieczeń.
Chroń także zmiany `LIFECYCLE_VALIDATOR_REF`. Zadanie o tej samej nazwie, które nic nie robi, może usunąć
własne sprawdzenie skrótu; samo porównanie skrótów nie zapobiegnie takiemu atakowi.
Przetestuj canary PR (celowo zepsute próbne PR, które powinny zostać zablokowane), które podmieniają lub usuwają workflow oraz przywracają HANDOFF większy niż 512 bajtów;
sprawdź, że osoba bez uprawnień administratora nie może ich scalić. Zapisz identyfikator zestawu reguł (ruleset) i dowody z testów canary w
PROJECT_CONFIG. Do tego czasu zgłaszaj **ochrona scalania niezweryfikowana**. To wydanie offline
nie skonfigurowało żadnego zdalnego repozytorium ani nie testowało wykonywania zdarzeń GitHub.

Lokalne sprawdzenie drzew nie wymaga gita wewnątrz Pythona:

```sh
python3 "$LIFECYCLE" check --merge-result --root result --parent left --parent right --base merge-base
```

Aby przygotować tożsamość rodziców i bazy oraz wpisy zamykające dla brakujących identyfikatorów, zamień
`--merge-result` na `--reconcile-template`. Scal wynikowy JSON z roboczą wersją checkpointu;
przywróć każdy brakujący identyfikator albo zastąp jego powód REVIEW REQUIRED powodem zamknięcia.
Skróty źródeł nie są potrzebne. Istniejące listy skrótów są akceptowane bez porównywania.
Zakończone próby mogą opuścić NOW dopiero po uzyskaniu statusu integrated/abandoned (włączone/porzucone) i jawnym zamknięciu.

Wywołujący musi wyeksportować prawdziwe, przetestowane drzewa; dowolne katalogi nie są dowodem pochodzenia.
