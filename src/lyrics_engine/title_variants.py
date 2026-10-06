import re
import unicodedata


def generate_title_variants(title):
    """
    Genera variantes del título para aumentar
    las posibilidades de encontrar la canción.
    """

    variants = []

    # 1. Original
    variants.append(("original", title))

    # 2. Sin apóstrofes
    no_apostrophe = re.sub(r"['’‘`´]", "", title)

    if no_apostrophe != title:
        variants.append(("sin_apostrofe", no_apostrophe))

    # 3. Guiones convertidos en espacios
    dash_space = re.sub(r"[-–—]", " ", title)
    dash_space = re.sub(r"\s+", " ", dash_space).strip()

    if dash_space != title:
        variants.append(("guion_a_espacio", dash_space))

    # 4. Sin sufijo editorial
    no_editorial_suffix = re.sub(
        r"\s*\((?:\d{4}\s+)?(?:remaster(?:ed)?|bonus\s+track)\)\s*$",
        "",
        title,
        flags=re.IGNORECASE,
    )

    if no_editorial_suffix != title:
        variants.append(
            (
                "sin_sufijo_editorial",
                no_editorial_suffix,
            )
        )

    # 5. Sin paréntesis
    no_parentheses = re.sub(r"\s*\([^)]*\)", "", title)
    no_parentheses = re.sub(r"\s+", " ", no_parentheses).strip()

    if no_parentheses != title:
        variants.append(("sin_parentesis", no_parentheses))

    # 6. Sin paréntesis + sin apóstrofes
    no_parentheses_apostrophe = re.sub(
        r"['’‘`´]",
        "",
        no_parentheses,
    )

    if no_parentheses_apostrophe != title:
        variants.append(
            (
                "sin_parentesis_sin_apostrofe",
                no_parentheses_apostrophe,
            )
        )

    # 7. Normalización Unicode
    normalized = unicodedata.normalize("NFKD", title)
    normalized = "".join(
        c for c in normalized
        if not unicodedata.combining(c)
    )

    if normalized != title:
        variants.append(("unicode_normalizado", normalized))

    # 8. Unicode normalizado + sin apóstrofes
    normalized_apostrophe = re.sub(
        r"['’‘`´]",
        "",
        normalized,
    )

    if normalized_apostrophe != title:
        variants.append(
            (
                "unicode_normalizado_sin_apostrofe",
                normalized_apostrophe,
            )
        )

    # Eliminar duplicados conservando el orden
    result = []
    seen = set()

    for name, value in variants:

        key = value.strip()

        if key not in seen:
            seen.add(key)
            result.append((name, key))

    return result
