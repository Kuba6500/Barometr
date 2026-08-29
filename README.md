# Barometr — codzienny briefing rynkowy

MVP narzędzia, które codziennie zbiera podstawowe dane z rynków (GPW, główne
indeksy światowe, waluty, złoto, bitcoin) i tłumaczy je w prostym języku —
**bez rekomendacji inwestycyjnych**, wyłącznie w formie edukacyjnej.

## Jak to działa

```
scripts/fetch_data.py       → pobiera darmowe dane EOD ze Stooq.pl (bez klucza API)
scripts/generate_summary.py → wysyła dane do Claude, dostaje gotowy briefing po polsku
site/                        → statyczna strona wyświetlająca briefing (bez frameworka, czysty HTML/CSS/JS)
.github/workflows/daily.yml → automatycznie odpala powyższe co dzień roboczy, za darmo
```

Strona już teraz działa z przykładowymi danymi w `site/summary.json` — możesz
ją od razu otworzyć i zobaczyć, jak wygląda, zanim podłączysz prawdziwe dane.

## Uruchomienie lokalne (test)

```bash
cd scripts
python fetch_data.py            # tworzy market_data.json
export ANTHROPIC_API_KEY="sk-..."
python generate_summary.py      # tworzy summary.json
cp summary.json ../site/summary.json
```

Potem otwórz `site/index.html` w przeglądarce (albo `python -m http.server`
w folderze `site/` i wejdź na `localhost:8000`).

## Darmowe wdrożenie (produkcja) — krok po kroku

1. **Załóż repozytorium na GitHubie** i wrzuć tam ten folder.
2. **Dodaj klucz API jako sekret**: w repo → Settings → Secrets and variables →
   Actions → New repository secret → nazwa `ANTHROPIC_API_KEY`, wartość: Twój
   klucz z [console.anthropic.com](https://console.anthropic.com/).
   (Płacisz tylko za realne zużycie — przy 1 podsumowaniu dziennie to grosze/miesiąc.)
3. **Włącz GitHub Pages**: Settings → Pages → Source: „Deploy from branch" →
   branch `main`, folder `/site`. Po chwili strona będzie dostępna pod
   `https://twoja-nazwa.github.io/nazwa-repo/`.
4. **Automatyzacja już działa** — `.github/workflows/daily.yml` uruchomi się
   sam każdego dnia roboczego i zaktualizuje `site/summary.json`. Możesz też
   odpalić go ręcznie od razu: zakładka *Actions* → *Codzienny briefing
   rynkowy* → *Run workflow*.

Cały ten setup (GitHub, GitHub Actions, GitHub Pages) mieści się w darmowych
limitach dla publicznego/małego prywatnego repozytorium.

## Co dalej (rozwój)

- **Więcej rynków**: dopisz kolejne symbole w `TICKERS` w `fetch_data.py`
  (pełna lista symboli Stooq: https://stooq.pl/db/h/)
- **Newsletter e-mail**: dodać krok w workflow wysyłający `summary.json` jako
  e-mail (np. przez darmowy tier Resend albo SendGrid)
- **Model monetyzacji**: na start trzymaj wszystko darmowe i zbieraj
  użytkowników; płatny plan (pełne archiwum, więcej rynków, powiadomienia)
  wprowadź dopiero gdy będziesz mieć pierwszych stałych czytelników

## Ważne zastrzeżenie

To narzędzie **opisuje kontekst rynkowy — nie doradza, co kupić**. Rekomendacje
inwestycyjne w Polsce wymagają licencji KNF. Prompt w
`scripts/generate_summary.py` celowo to wymusza — nie usuwaj tych zasad bez
konsultacji prawnej, jeśli planujesz rozwijać narzędzie w tym kierunku.
