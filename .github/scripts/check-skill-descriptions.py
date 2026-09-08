#!/usr/bin/env python3
"""El `description` de cada SKILL.md no puede pasar los 1024 caracteres.

El importador de git acepta descripciones mas largas, pero el uploader de plugins
las rechaza con "field 'description' in SKILL.md must be at most 1024 characters".
Sin esta barrera el error recien aparece al subir el zip, con el plugin ya publicado.
"""
import glob
import re
import sys

LIMITE = 1024


def descripcion(texto):
    m = re.match(r"^---\n(.*?)\n---\n", texto, re.S)
    if not m:
        return None
    fm = m.group(1)
    dm = re.search(r"^description:[ \t]*(.*)$", fm, re.M)
    if not dm:
        return None
    primera = dm.group(1).strip()
    if primera not in (">", ">-", "|", "|-"):
        return primera.strip("\"'")
    lineas, empezo = [], False
    for linea in fm[dm.end():].split("\n"):
        if linea.startswith((" ", "\t")) or linea.strip() == "":
            lineas.append(linea.strip())
            empezo = True
        elif empezo:
            break
        else:
            break
    return " ".join(x for x in lineas if x)


def main():
    malas = []
    for f in sorted(glob.glob("plugins/*/skills/*/SKILL.md")):
        d = descripcion(open(f, encoding="utf-8").read())
        if d is None:
            print(f"::error file={f}::SKILL.md sin frontmatter o sin campo description")
            malas.append(f)
            continue
        n = len(d)
        print(f"{n:6d}  {'EXCEDE' if n > LIMITE else '  ok  '}  {f}")
        if n > LIMITE:
            print(f"::error file={f}::description de {n} caracteres, el maximo es {LIMITE}")
            malas.append(f)
    return 1 if malas else 0


if __name__ == "__main__":
    sys.exit(main())
