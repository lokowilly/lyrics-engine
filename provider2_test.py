from pathlib import Path
from urllib.parse import quote
import requests


TESTS = [
    ("Steve Perry", "Against the Wall"),
    ("Steve Perry", "Once in a Lifetime, Girl"),
    ("Steve Perry", "I Stand Alone"),
    ("Steve Perry", "If You Need Me, Call Me"),
    ("Kenny Loggins & Steve Perry", "Don't Fight It"),
]


def test_page(url):
    try:
        response = requests.get(
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(X11; Linux x86_64) "
                    "AppleWebKit/537.36 "
                    "Chrome/130 Safari/537.36"
                )
            },
            timeout=15,
        )

        print(f"HTTP       : {response.status_code}")
        print(f"Caracteres : {len(response.text)}")

        if response.status_code == 200:
            return True

        return False

    except requests.RequestException as e:
        print(f"ERROR      : {e}")
        return False


def main():

    print("=" * 70)
    print("PROVIDER #2 — LYRICSWEB")
    print("=" * 70)
    print()
    print("Solo comprobamos las páginas.")
    print("NO descargamos ni guardamos letras.")
    print("NO modificamos MP3.")
    print()

    for artist, title in TESTS:

        print("-" * 70)
        print(f"Artista : {artist}")
        print(f"Título  : {title}")

        artist_slug = quote(
            artist.lower().replace(" ", "-")
        )

        title_slug = quote(
            title.lower()
            .replace(" ", "-")
            .replace(",", "")
            .replace("'", "")
        )

        url = (
            f"https://lyricsweb.com/song/"
            f"{artist_slug}/"
            f"{artist_slug}-{title_slug}"
        )

        print(f"URL      : {url}")

        found = test_page(url)

        print(
            "RESULTADO : "
            + ("PAGE_OK" if found else "NOT_FOUND")
        )

    print()
    print("=" * 70)
    print("FIN DEL LABORATORIO")
    print("=" * 70)


if __name__ == "__main__":
    main()
