"""
generate_summary.py
Bierze surowe dane z market_data.json i prosi Claude o wygenerowanie
codziennego podsumowania rynkowego po polsku - w formie edukacyjnej,
BEZ rekomendacji inwestycyjnych typu "kup X" / "sprzedaj Y".

WAŻNE (kwestia prawna): to narzędzie ma WYJAŚNIAĆ kontekst rynkowy,
nie doradzać, co kupić. Prompt poniżej celowo to wymusza - nie usuwaj
tych instrukcji, nawet jeśli chcesz rozszerzyć narzędzie w przyszłości,
bez konsultacji prawnej.

Wymaga zmiennej środowiskowej ANTHROPIC_API_KEY.
(Darmowy start: https://console.anthropic.com/ - płacisz tylko za realne
zużycie, przy 1 podsumowaniu dziennie to rzędu pojedynczych groszy/dnia.)

Uruchomienie:
    export ANTHROPIC_API_KEY="twoj-klucz"
    python generate_summary.py
"""

import json
import os
import sys
import urllib.request

API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-sonnet-4-6"

SYSTEM_PROMPT = """Jesteś redaktorem codziennego, spokojnego briefingu rynkowego dla osób,
które chcą ROZUMIEĆ rynki finansowe, ale są zmęczone hype'em i sprzedawaniem kursów.

ZASADY (bezwzględne):
- NIGDY nie rekomendujesz konkretnych zakupów/sprzedaży ("kup X", "warto zainwestować w Y").
- Opisujesz TYLKO to, co się wydarzyło i jaki może mieć to kontekst/znaczenie - edukacyjnie.
- Piszesz prostym, konkretnym językiem - bez żargonu bez wyjaśnienia, bez sensacji.
- Jeśli dane są niejednoznaczne lub niepełne, mówisz to wprost zamiast zgadywać.
- Zawsze kończysz krótkim zastrzeżeniem, że to materiał edukacyjny, nie porada inwestycyjna.

Zwróć WYŁĄCZNIE poprawny JSON (bez markdown, bez ```), w formacie:
{
  "sentiment_score": <liczba od -1.0 (poważne obawy/spadki) do 1.0 (wyraźnie pozytywnie), 0 = neutralnie>,
  "sentiment_label": "<jedno-dwa słowa po polsku, np. 'Niepewność', 'Spokojnie', 'Napięcie'>",
  "headline": "<jedno zdanie - najważniejsza rzecz dnia>",
  "overview": "<2-3 zdania ogólnego kontekstu dnia>",
  "assets": [
    {"symbol": "...", "comment": "<1-2 zdania kontekstu dla TEGO aktywa>"}
  ],
  "disclaimer": "<krótkie zastrzeżenie edukacyjne>"
}
"""


def call_claude(market_data: dict) -> dict:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        sys.exit("Brak ANTHROPIC_API_KEY w zmiennych środowiskowych.")

    user_prompt = (
        "Oto dzisiejsze dane rynkowe (zamknięcia i zmiana % dzień do dnia):\n\n"
        + json.dumps(market_data, ensure_ascii=False, indent=2)
        + "\n\nWygeneruj podsumowanie dnia zgodnie z zasadami z instrukcji systemowej."
    )

    payload = {
        "model": MODEL,
        "max_tokens": 1500,
        "system": SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": user_prompt}],
    }

    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=60) as resp:
        result = json.loads(resp.read().decode("utf-8"))

    text = "".join(
        block["text"] for block in result["content"] if block.get("type") == "text"
    )
    text = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(text)


def main():
    with open("market_data.json", "r", encoding="utf-8") as f:
        market_data = json.load(f)

    summary = call_claude(market_data)
    summary["date"] = market_data["date"]
    summary["raw_assets"] = market_data["assets"]

    with open("summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print("Zapisano summary.json")


if __name__ == "__main__":
    main()
