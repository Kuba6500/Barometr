"""
fetch_data.py
Pobiera darmowe dane rynkowe (dzienne zamknięcia) ze Stooq.pl - nie wymaga klucza API.

Stooq udostępnia dane historyczne/EOD (end-of-day) w formacie CSV pod adresem:
https://stooq.pl/q/d/l/?s=<symbol>&i=d

To NIE są dane w czasie rzeczywistym (opóźnienie do końca dnia sesyjnego) -
co jest zgodne z założeniem MVP: "co się wydarzyło i dlaczego to ważne" (nie real-time).

Uruchomienie:
    python fetch_data.py

Wynik:
    zapisuje market_data.json w tym samym folderze, np.:
    {
      "date": "2026-08-28",
      "assets": [
        {"symbol": "WIG", "name": "WIG (GPW)", "close": 91234.5, "change_pct": 1.23},
        ...
      ]
    }
"""

import csv
import io
import json
import urllib.request
from datetime import datetime, timedelta

# Symbole Stooq -> czytelna nazwa po polsku.
# Możesz dowolnie rozszerzać tę listę o kolejne rynki/aktywa.
TICKERS = {
    "wig": "WIG (GPW, Polska)",
    "wig20": "WIG20 (GPW, Polska)",
    "^spx": "S&P 500 (USA)",
    "^dax": "DAX (Niemcy)",
    "^ftm": "FTSE 100 (Wielka Brytania)",
    "^nkx": "Nikkei 225 (Japonia)",
    "usdpln": "USD/PLN",
    "eurpln": "EUR/PLN",
    "xauusd": "Złoto (USD/uncja)",
    "btcusd": "Bitcoin (USD)",
}

STOOQ_URL = "https://stooq.pl/q/d/l/?s={symbol}&i=d"


def fetch_symbol(symbol: str):
    """Pobiera ostatnie ~5 dni danych dla symbolu i zwraca (data, zamknięcie, zmiana_%)."""
    url = STOOQ_URL.format(symbol=symbol)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        raw_bytes = resp.read()

    # Stooq bywa niekonsekwentne z kodowaniem nagłówków (polskie znaki jak "ę").
    # Zamiast polegać na nazwach kolumn, czytamy po POZYCJI - odporne na to,
    # jak dokładnie nazywa się kolumna czy jakie ma kodowanie.
    # Format Stooq to zawsze: Data,Otwarcie,Najwyzszy,Najnizszy,Zamkniecie,Wolumen
    raw = raw_bytes.decode("utf-8", errors="replace")
    rows = list(csv.reader(io.StringIO(raw)))

    data_rows = rows[1:] if len(rows) > 1 else []  # pomiń nagłówek
    if len(data_rows) < 2:
        print(f"  [debug {symbol}] surowa odpowiedź (pierwsze 200 znaków): {raw[:200]!r}")
        return None  # brak wystarczających danych (np. zły symbol, święto, błąd zapytania)

    last = data_rows[-1]
    prev = data_rows[-2]

    # Kolumna 0 = Data, kolumna 4 = Zamkniecie (indeksy liczone od 0)
    if len(last) < 5 or len(prev) < 5:
        return None

    close = float(last[4])
    prev_close = float(prev[4])
    change_pct = ((close - prev_close) / prev_close) * 100 if prev_close else 0.0

    return {
        "date": last[0],
        "close": round(close, 4),
        "change_pct": round(change_pct, 2),
    }


def main():
    assets = []
    for symbol, name in TICKERS.items():
        try:
            data = fetch_symbol(symbol)
            if data:
                assets.append(
                    {
                        "symbol": symbol.upper(),
                        "name": name,
                        "close": data["close"],
                        "change_pct": data["change_pct"],
                    }
                )
            else:
                print(f"[UWAGA] Brak danych dla {symbol}")
        except Exception as e:
            print(f"[BŁĄD] Nie udało się pobrać {symbol}: {e}")

    output = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "assets": assets,
    }

    with open("market_data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"Zapisano market_data.json ({len(assets)} aktywów)")


if __name__ == "__main__":
    main()