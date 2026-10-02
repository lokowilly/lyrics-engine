#!/usr/bin/env python3

import re
import requests


URL = "https://lyricsweb.com/song/steve-perry/steve-perry-against-the-wall"

SEARCH_TERMS = [
    "Against the Wall",
    "All of my life",
    "Steve Perry",
]


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/130.0 Safari/537.36"
    )
}


response = requests.get(
    URL,
    headers=HEADERS,
    timeout=20,
)

print("=" * 70)
print("HTTP:", response.status_code)
print("HTML:", len(response.text), "caracteres")
print("=" * 70)

html = response.text


for term in SEARCH_TERMS:

    print()
    print("=" * 70)
    print("BUSCANDO:", term)
    print("=" * 70)

    matches = list(
        re.finditer(
            re.escape(term),
            html,
            re.IGNORECASE,
        )
    )

    print("Coincidencias:", len(matches))

    for i, match in enumerate(matches[:5], 1):

        inicio = max(0, match.start() - 500)
        fin = min(len(html), match.end() + 1500)

        fragmento = html[inicio:fin]

        print()
        print("-" * 70)
        print(f"COINCIDENCIA #{i}")
        print("-" * 70)
        print(fragmento)


# ---------------------------------------------------------
# Buscar posibles bloques de datos de Next.js
# ---------------------------------------------------------

print()
print("=" * 70)
print("BUSCANDO BLOQUES NEXT.JS")
print("=" * 70)

patterns = [
    r'<script[^>]+type="application/ld\+json"[^>]*>',
    r'<script[^>]+id="__NEXT_DATA__"[^>]*>',
    r'<script[^>]*>',
]

for pattern in patterns:

    matches = list(
        re.finditer(
            pattern,
            html,
            re.IGNORECASE,
        )
    )

    print(
        f"{pattern} -> {len(matches)} coincidencias"
    )


# ---------------------------------------------------------
# Guardar HTML
# ---------------------------------------------------------

with open(
    "lyricsweb_against_wall.html",
    "w",
    encoding="utf-8",
) as f:
    f.write(html)

print()
print("=" * 70)
print("HTML guardado en:")
print("lyricsweb_against_wall.html")
print("=" * 70)
