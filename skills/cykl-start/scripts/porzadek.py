#!/usr/bin/env python3
"""porzadek.py — bramka i porządek dokumentów stanu cykl-lifecycle.

Bez argumentu tylko SPRAWDZA (read-only, kod wyjścia 1 przy FAIL).
Z --wykonaj PORZĄDKUJE: przenosi historię do docs/archive/, zostawia jeden
blok bieżący, wraca do sprawdzenia. Nic nie usuwa — wszystko przeniesione
ląduje w archiwum. Idempotentny: drugi przebieg nic nie przenosi.

Użycie:  python3 porzadek.py [--wykonaj] [--prog 40000] [--zostaw 5] [KATALOG_PROJEKTU]

Reguły porządku (deterministyczne, bez AI):
  1. Nagłówek: zostaje pierwsza linia `**Wersja` i pierwsza `**Ostatnia aktualizacja`;
     kolejne (stos historycznych nagłówków) → archiwum. „bieżąca" znika z etykiet.
  2. Bloki <details> z „histori" w <summary> → archiwum.
  3. Sekcje `##`/`###` z „histori"/„archiw" w tytule → archiwum.
  4. W sekcji „Snapshot": zostaje pierwszy fragment (do pierwszego `---`), reszta → archiwum.
  5. Bloki cytatu `> **STAN POPRZEDNI…` / `> **AKTUALIZACJA…` / `> **Aktualizacja <data>…` /
     `> **AKTUALNY STAN…`: w każdej sekcji zostaje pierwszy, kolejne → archiwum. Linia
     „Aktualizacja <data>" wewnątrz dłuższego cytatu zaczyna nowy blok (łańcuchy dopisków).
  6. Tabela Changelog: zostaje N najnowszych wierszy (--zostaw), reszta → archiwum.
  7. LESSONS: lekcje `### W<n>` za `## Changelog` wracają do Części II, posortowane.
  Po każdym przebiegu z przeniesieniami: linia `> **Archiwum:** …` pod nagłówkiem dokumentu
  (nadpisywana) i `docs/archive/README.md` (raz) — porządek dokumentuje się sam.
  Test (bez porządku): pola stanowe PROJECT_CONFIG (`CURRENT_SPRINT_STATUS`, `_BRANCH`,
  `_NEXT_DECISION`, `_OPEN_RISKS`, `REPO_STATE`) mają `[zmierzone RRRR-MM-DD …]` nie starszy
  niż data nagłówka, albo `<mierzone przez STATE_PROBE>` / `[DO SPRAWDZENIA]`. Pole bez pomiaru
  = stara wartość przepisana z pliku — to drift, który przez 4 sesje nikt nie naprawił.
"""
import argparse
import datetime as dt
import os
import re
import shutil
import sys

DOKUMENTY = ["PROJECT_CONFIG.md", "docs/HANDOFF.md", "docs/ROADMAP.md", "docs/LESSONS_CANON.md"]
RE_H2 = re.compile(r"^## ")
RE_H3 = re.compile(r"^### ")
RE_HIST = re.compile(r"histor|archiw", re.I)          # luźne — tylko <summary> w <details>
RE_TYTUL_HIST = re.compile(r"^#{2,3}\s*(snapshot\w*\s+)?(histor|archiw)", re.I)  # tytuł sekcji
RE_WERSJA = re.compile(r"^\*\*Wersja")
RE_OSTATNIA = re.compile(r"^\*\*Ostatnia aktualizacja")
RE_STAN = re.compile(r"^> \*\*(STAN POPRZEDNI|POPRZEDNI STAN|(?i:aktualizacja)\s+\d|AKTUALIZACJA|AKTUALNY STAN)")
RE_STAN_STARY = re.compile(r"^> \*\*(STAN POPRZEDNI|POPRZEDNI STAN)")
RE_DATA = re.compile(r"\d{4}-\d{2}-\d{2}")
RE_W = re.compile(r"^### W(\d+)\b")
RE_POLE = re.compile(r"^(CURRENT_SPRINT_STATUS|CURRENT_SPRINT_BRANCH|CURRENT_SPRINT_NEXT_DECISION|CURRENT_SPRINT_OPEN_RISKS|REPO_STATE)=")
RE_ZMIERZONE = re.compile(r"\[zmierzone (\d{4}-\d{2}-\d{2})")
RE_ODSYLACZ = re.compile(r"^> \*\*Archiwum:\*\* ")


def sekcje(lines):
    """[(naglowek_h2 | None, [linie])] — pierwszy element to nagłówek pliku."""
    out, cur = [], (None, [])
    for ln in lines:
        if RE_H2.match(ln):
            out.append(cur)
            cur = (ln, [])
        else:
            cur[1].append(ln)
    out.append(cur)
    return out


def zloz(secs):
    out = []
    for h, body in secs:
        if h is not None:
            out.append(h)
        out.extend(body)
    return out


class Porzadek:
    def __init__(self, sciezka):
        self.sciezka = sciezka
        self.nazwa = os.path.basename(sciezka)
        self.przeniesione = []  # (opis, [linie])

    def _arch(self, opis, linie):
        if linie:
            self.przeniesione.append((opis, linie))

    # --- 1. nagłówek ---
    def naglowek(self, body):
        out, w, o = [], 0, 0
        for ln in body:
            if RE_WERSJA.match(ln):
                w += 1
                if w > 1:
                    self._arch("nagłówek historyczny", [ln])
                    continue
                ln = ln.replace("**Wersja bieżąca:**", "**Wersja:**").replace(
                    "**Ostatnia aktualizacja bieżąca:**", "**Ostatnia aktualizacja:**")
            elif RE_OSTATNIA.match(ln):
                o += 1
                if o > 1:
                    self._arch("nagłówek historyczny", [ln])
                    continue
                ln = ln.replace("**Ostatnia aktualizacja bieżąca:**", "**Ostatnia aktualizacja:**")
            out.append(ln)
        return out

    # --- 2. <details> z historią ---
    def details(self, body):
        out, i = [], 0
        while i < len(body):
            ln = body[i]
            if ln.startswith("<details") and RE_HIST.search(ln):
                j = i
                while j < len(body) and "</details>" not in body[j]:
                    j += 1
                self._arch("blok <details> z historią", body[i:j + 1])
                i = j + 1
                continue
            out.append(ln)
            i += 1
        return out

    # --- 3b. podsekcje ### z historią ---
    def h3_hist(self, body):
        out, i = [], 0
        while i < len(body):
            ln = body[i]
            if RE_TYTUL_HIST.match(ln):
                j = i + 1
                while j < len(body) and not RE_H3.match(body[j]):
                    j += 1
                self._arch(f"podsekcja {ln.strip('# ').strip()}", body[i:j])
                i = j
                continue
            out.append(ln)
            i += 1
        return out

    # --- 4. Snapshot: pierwszy fragment ---
    def snapshot(self, body):
        try:
            k = body.index("---")
        except ValueError:
            return body
        # zostaw treść przed pierwszym --- (plus ewentualny pusty ogon)
        self._arch("snapshoty historyczne", body[k + 1:])
        return body[:k]

    # --- 5. bloki STAN ---
    def bloki_stanu(self, body):
        out, i, n = [], 0, 0
        while i < len(body):
            ln = body[i]
            if RE_STAN.match(ln):
                j = i + 1
                while j < len(body) and body[j].startswith(">") and not RE_STAN.match(body[j]):
                    j += 1
                n += 1
                if n == 1:
                    k = next((m for m in range(i + 1, j) if RE_STAN_STARY.match(body[m])), None)
                    if k is not None:
                        self._arch("blok stanu zastąpiony (ogon bieżącego cytatu)", body[k:j])
                        out.extend(body[i:k])
                        i = j
                        continue
                if n > 1:
                    self._arch("blok stanu zastąpiony", body[i:j])
                    # zjedz pustą linię po bloku
                    if j < len(body) and body[j].strip() == "":
                        j += 1
                    i = j
                    continue
            out.append(ln)
            i += 1
        return out

    # --- 6. changelog ---
    def changelog(self, body, zostaw):
        out, rows, i = [], 0, 0
        while i < len(body):
            ln = body[i]
            if ln.startswith("|") and not re.match(r"^\|\s*-", ln) and "Wersja" not in ln.split("|")[1]:
                rows += 1
                if rows > zostaw:
                    j = i
                    while j < len(body) and body[j].startswith("|"):
                        j += 1
                    self._arch("changelog — starsze wpisy", body[i:j])
                    out.append(f"\n_Starsze wpisy: `docs/archive/{self.arch_nazwa()}`._")
                    i = j
                    continue
            out.append(ln)
            i += 1
        return out

    # --- 7. LESSONS ---
    def lekcje(self, secs):
        idx_ii = next((k for k, (h, _) in enumerate(secs) if h and "Część II" in h), None)
        idx_cl = next((k for k, (h, _) in enumerate(secs) if h and "Changelog" in h), None)
        if idx_ii is None or idx_cl is None:
            return secs
        # zbierz bloki ### W<n> ze WSZYSTKICH sekcji za Częścią II (w tym Changelog)
        zebrane, naprawiono = [], 0
        for k in range(idx_ii, len(secs)):
            h, body = secs[k]
            reszta, i = [], 0
            while i < len(body):
                m = RE_W.match(body[i])
                if m:
                    j = i + 1
                    while j < len(body) and not RE_H3.match(body[j]):
                        j += 1
                    zebrane.append((int(m.group(1)), body[i:j]))
                    if k != idx_ii:
                        naprawiono += 1
                    i = j
                    continue
                reszta.append(body[i])
                i += 1
            secs[k] = (h, reszta)
        zebrane.sort(key=lambda t: t[0])
        h, body = secs[idx_ii]
        while body and body[-1].strip() == "":
            body.pop()
        for _, blok in zebrane:
            while blok and blok[-1].strip() == "":
                blok.pop()
            body.append("")
            body.extend(blok)
        body.append("")
        secs[idx_ii] = (h, body)
        if naprawiono:
            self.przeniesione.append((f"{naprawiono} lekcji przeniesionych z Changelogu do Części II (bez archiwum)", []))
        return secs

    def arch_nazwa(self):
        d = dt.date.today()
        return f"{self.nazwa[:-3]}-{d.year}-Q{(d.month - 1) // 3 + 1}.md"

    def uporzadkuj(self, zostaw):
        with open(self.sciezka, encoding="utf-8") as f:
            lines = f.read().split("\n")
        secs = sekcje(lines)
        nowe = []
        for h, body in secs:
            if h is None:
                body = self.details(self.naglowek(body))
            elif RE_TYTUL_HIST.match(h):
                self._arch(f"sekcja {h.strip('# ').strip()}", [h] + body)
                continue
            else:
                body = self.details(body)
                body = self.h3_hist(body)
                if h.lstrip("# ").lower().startswith("snapshot"):
                    body = self.snapshot(body)
                body = self.bloki_stanu(body)
                if "changelog" in h.lower():
                    body = self.changelog(body, zostaw)
            nowe.append((h, body))
        if "LESSONS" in self.nazwa:
            nowe = self.lekcje(nowe)
        return re.sub(r"\n{3,}", "\n\n", "\n".join(zloz(nowe)))

    def odsylacz(self, tekst, arch_rel, n_linii):
        """Jedna linia pod nagłówkiem: dokąd poszła historia. Nadpisywana, nie dopisywana."""
        stamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
        nowa = f"> **Archiwum:** historia tego dokumentu (ostatni porządek {stamp}, {n_linii} linii) jest w `{arch_rel}` — porzadek.py, cykl-lifecycle."
        lines = tekst.split("\n")
        for i, l in enumerate(lines):
            if RE_ODSYLACZ.match(l):
                lines[i] = nowa
                return "\n".join(lines)
        # wstaw po pierwszej linii **Wersja (i ewentualnej **Ostatnia aktualizacja tuż pod nią)
        for i, l in enumerate(lines):
            if RE_WERSJA.match(l):
                j = i + 1
                while j < len(lines) and RE_OSTATNIA.match(lines[j]):
                    j += 1
                lines[j:j] = ["", nowa]
                return "\n".join(lines)
        return tekst

    def zapisz_archiwum(self, root):
        real = [p for p in self.przeniesione if p[1]]
        if not real:
            return None
        arch_dir = os.path.join(root, "docs", "archive")
        os.makedirs(arch_dir, exist_ok=True)
        return self._zapisz(root, arch_dir, real)

    def readme_archiwum(self, root):
        arch_dir = os.path.join(root, "docs", "archive")
        os.makedirs(arch_dir, exist_ok=True)
        readme = os.path.join(arch_dir, "README.md")
        if not os.path.exists(readme):
            with open(readme, "w", encoding="utf-8") as f:
                f.write("# docs/archive — historia dokumentów stanu\n\n"
                        "Tu trafia to, co `porzadek.py` (cykl-lifecycle, uruchamiany przez `/start`, `/zamknij`, `/migawka`) "
                        "przeniósł z dokumentów stanu, żeby zostały cienkie i miały jeden blok bieżący: stare nagłówki wersji, "
                        "zastąpione bloki `STAN POPRZEDNI` / `AKTUALIZACJA`, snapshoty poza pierwszym, sekcje „Historia…”, "
                        "wiersze changelogu poza 5 najnowszymi.\n\n"
                        "Jeden plik na dokument i kwartał: `<NAZWA>-RRRR-Qn.md`. Każdy przebieg dopisuje sekcję "
                        "`# Przeniesione <data> z <plik>` z podsekcjami wg rodzaju. Nic nie jest kasowane; kolejność = kolejność w źródle.\n\n"
                        "Odsyłacz do właściwego pliku stoi pod nagłówkiem każdego dokumentu stanu (`> **Archiwum:** …`). "
                        "Szukasz starego stanu z konkretnej daty → `grep -n \"RRRR-MM-DD\" docs/archive/*.md`.\n")

    def _zapisz(self, root, arch_dir, real):
        path = os.path.join(arch_dir, self.arch_nazwa())
        stamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"\n\n# Przeniesione {stamp} z `{self.nazwa}` (porzadek.py)\n")
            for opis, linie in real:
                f.write(f"\n## {opis}\n\n")
                f.write("\n".join(linie).rstrip("\n") + "\n")
        return path


def sprawdz(root, prog, zostaw):
    """Zwraca listę (dokument, test, PASS/FAIL/INFO, szczegół)."""
    wyniki = []
    for rel in DOKUMENTY:
        p = os.path.join(root, rel)
        if not os.path.exists(p):
            continue
        with open(p, encoding="utf-8") as f:
            txt = f.read()
        lines = txt.split("\n")
        size = len(txt.encode("utf-8"))
        secs = sekcje(lines)
        nazwa = os.path.basename(rel)

        # rozmiar + największa sekcja
        big = max(secs, key=lambda s: len("\n".join(s[1])))
        big_h = (big[0] or "nagłówek").strip("# ").strip()[:40]
        kanon = "LESSONS" in nazwa  # kanon lekcji rośnie z wiedzą, nie z driftem — rozmiar to informacja
        wyniki.append((nazwa, "rozmiar ≤ próg", "PASS" if size <= prog else ("INFO" if kanon else "FAIL"),
                       f"{size:,} B / {prog:,} B; największa sekcja: „{big_h}” {len(chr(10).join(big[1]).encode()):,} B"))
        # jeden nagłówek wersji
        nw = sum(1 for l in secs[0][1] if RE_WERSJA.match(l))
        wyniki.append((nazwa, "1 linia Wersja w nagłówku", "PASS" if nw == 1 else "FAIL", f"{nw} linii"))
        # bloki stanu / details / sekcje historyczne / snapshoty
        stan = sum(1 for l in lines if RE_STAN_STARY.match(l))
        det = sum(1 for l in lines if l.startswith("<details") and RE_HIST.search(l))
        hist = sum(1 for h, _ in secs if h and RE_TYTUL_HIST.match(h)) + sum(
            1 for _, b in secs for l in b if RE_TYTUL_HIST.match(l))
        snap = 0
        for h, b in secs:
            if h and h.lstrip("# ").lower().startswith("snapshot"):
                snap = b.count("---")
        multi = []
        for h, b in secs:
            k = sum(1 for l in b if RE_STAN.match(l))
            if k > 1:
                multi.append(f"{(h or '').strip('# ').strip()[:25]}×{k}")
        problemy = stan + det + hist + snap + len(multi)
        wyniki.append((nazwa, "jeden blok bieżący", "PASS" if problemy == 0 else "FAIL",
                       f"STAN POPRZEDNI {stan}, <details> hist. {det}, sekcje hist. {hist}, snapshoty ponad 1: {snap}, "
                       f"wiele bloków stanu: {', '.join(multi) or 0}"))
        # changelog: liczba wierszy + data nagłówka == data 1. wiersza
        cl = next((b for h, b in secs if h and "changelog" in h.lower()), None)
        if cl is not None:
            rows = [l for l in cl if l.startswith("|") and not re.match(r"^\|\s*-", l) and "Wersja" not in l.split("|")[1]]
            wyniki.append((nazwa, f"changelog ≤ {zostaw} wierszy", "PASS" if len(rows) <= zostaw else "FAIL", f"{len(rows)} wierszy"))
            d_head = next((RE_DATA.search(l).group() for l in secs[0][1] if RE_OSTATNIA.match(l) or RE_WERSJA.match(l)
                           if RE_DATA.search(l)), None)
            d_row = RE_DATA.search(rows[0]).group() if rows and RE_DATA.search(rows[0]) else None
            if d_head and d_row:
                wyniki.append((nazwa, "data nagłówka = 1. wiersz changelogu", "PASS" if d_head == d_row else "FAIL",
                               f"nagłówek {d_head}, changelog {d_row}"))
        # PROJECT_CONFIG: pola stanowe ze znacznikiem pomiaru, nie starszym niż nagłówek
        if "PROJECT_CONFIG" in nazwa:
            d_head = next((RE_DATA.search(l).group() for l in secs[0][1] if RE_WERSJA.match(l) and RE_DATA.search(l)), None)
            zle = []
            for l in lines:
                m = RE_POLE.match(l)
                if not m:
                    continue
                if "<mierzone przez STATE_PROBE>" in l or "[DO SPRAWDZENIA]" in l:
                    continue
                z = RE_ZMIERZONE.search(l)
                if not z:
                    zle.append(f"{m.group(1)}: brak `[zmierzone RRRR-MM-DD …]`")
                elif d_head and z.group(1) < d_head:
                    zle.append(f"{m.group(1)}: zmierzone {z.group(1)} < nagłówek {d_head}")
            wyniki.append((nazwa, "pola stanowe zmierzone", "PASS" if not zle else "FAIL",
                           "; ".join(zle) or "wszystkie ze znacznikiem nie starszym niż nagłówek"))
        # LESSONS: nic za Changelogiem
        if "LESSONS" in nazwa and cl is not None:
            po = sum(1 for l in cl if RE_H3.match(l))
            wyniki.append((nazwa, "brak lekcji za Changelogiem", "PASS" if po == 0 else "FAIL", f"{po} sekcji ###"))
        # wiek pliku (informacja o równoległej sesji)
        wiek = (dt.datetime.now() - dt.datetime.fromtimestamp(os.path.getmtime(p))).total_seconds() / 60
        wyniki.append((nazwa, "ostatnia modyfikacja", "INFO", f"{wiek:.0f} min temu" + (" — możliwa inna żywa sesja" if wiek < 30 else "")))
    return wyniki


def drukuj(wyniki):
    print(f"\nporzadek.py · {dt.datetime.now().strftime('%Y-%m-%d %H:%M %Z').strip()} · zegar systemowy\n")
    print("| Dokument | Test | Wynik | Szczegół |\n|---|---|---|---|")
    for d, t, w, s in wyniki:
        print(f"| {d} | {t} | {w} | {s} |")
    fails = sum(1 for w in wyniki if w[2] == "FAIL")
    print(f"\n**{'FAIL' if fails else 'PASS'}** — {fails} testów FAIL")
    return fails


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--wykonaj", action="store_true", help="porządkuj (domyślnie tylko sprawdzenie)")
    ap.add_argument("--prog", type=int, default=40_000, help="próg rozmiaru w bajtach (40000)")
    ap.add_argument("--zostaw", type=int, default=5, help="ile wierszy changelogu zostaje (5)")
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    if not os.path.exists(os.path.join(root, "PROJECT_CONFIG.md")):
        print(f"Brak PROJECT_CONFIG.md w {root} — to nie jest projekt cykl-lifecycle.")
        return 2

    if a.wykonaj:
        print("## Porządek — co przeniesiono\n")
        for rel in DOKUMENTY:
            p = os.path.join(root, rel)
            if not os.path.exists(p):
                continue
            przed = os.path.getsize(p)
            po = Porzadek(p)
            nowy = po.uporzadkuj(a.zostaw)
            arch = po.zapisz_archiwum(root)
            istniejace = os.path.join(root, "docs", "archive", po.arch_nazwa())
            if arch or os.path.exists(istniejace):
                po.readme_archiwum(root)
                nowy = po.odsylacz(nowy, os.path.relpath(arch or istniejace, root), sum(len(l) for _, l in po.przeniesione))
            if nowy != open(p, encoding="utf-8").read():
                with open(p, "w", encoding="utf-8") as f:
                    f.write(nowy)
            print(f"- `{rel}`: {przed:,} → {os.path.getsize(p):,} B" + (f"; archiwum `{os.path.relpath(arch, root)}`" if arch else ""))
            grupy = {}
            for opis, linie in po.przeniesione:
                g = grupy.setdefault(opis, [0, 0]); g[0] += 1; g[1] += len(linie)
            for opis, (n, k) in grupy.items():
                print(f"    - {opis}" + (f" ×{n}" if n > 1 else "") + (f" ({k} linii)" if k else ""))
        print()

    fails = drukuj(sprawdz(root, a.prog, a.zostaw))
    if fails and not a.wykonaj:
        print("\nNapraw: `python3 porzadek.py --wykonaj <katalog>` (historia → docs/archive/), potem ręcznie to, co zostało FAIL.")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
