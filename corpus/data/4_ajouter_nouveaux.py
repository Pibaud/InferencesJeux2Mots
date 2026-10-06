import argparse
import json
from pathlib import Path


DOSSIER_DATA = Path(__file__).resolve().parent
FICHIER_BRUT = DOSSIER_DATA / "1_syntagmes_bruts.json"
FICHIER_NOUVEAUX = DOSSIER_DATA / "nouveaux_syntagmes.json"
RELATION_CIBLE = "r_lieu>origine"
NOMBRE_CIBLE = 160


def ajouter_syntagmes(dry_run: bool = False) -> tuple[int, int, int]:
    with FICHIER_BRUT.open(encoding="utf-8") as fichier:
        syntagmes_bruts = json.load(fichier)

    with FICHIER_NOUVEAUX.open(encoding="utf-8") as fichier:
        nouveaux_syntagmes = json.load(fichier)

    nombre_relation_cible = sum(
        item.get("relation_humaine") == RELATION_CIBLE for item in syntagmes_bruts
    )

    textes_existants = {
        item["texte_complet"].lower()
        for item in syntagmes_bruts
        if item.get("relation_humaine") == RELATION_CIBLE
    }
    syntagmes_ajoutes = []

    for item in nouveaux_syntagmes:
        if nombre_relation_cible >= NOMBRE_CIBLE:
            break
        if item.get("relation_humaine") != RELATION_CIBLE:
            continue

        texte = item["texte_complet"]
        texte_compare = texte.lower()
        if texte_compare in textes_existants:
            print(f"Le syntagme '{texte}' existe déjà dans le dataset brut.")
            continue

        syntagmes_ajoutes.append(item)
        textes_existants.add(texte_compare)
        if item.get("relation_humaine") == RELATION_CIBLE:
            nombre_relation_cible += 1

    if syntagmes_ajoutes and not dry_run:
        syntagmes_bruts.extend(syntagmes_ajoutes)
        with FICHIER_BRUT.open("w", encoding="utf-8") as fichier:
            json.dump(syntagmes_bruts, fichier, ensure_ascii=False, indent=4)
            fichier.write("\n")

    return (
        len(syntagmes_ajoutes),
        len(nouveaux_syntagmes)
        - sum(
            item.get("relation_humaine") == RELATION_CIBLE
            for item in nouveaux_syntagmes
        ),
        nombre_relation_cible,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ajoute les nouveaux syntagmes absents du dataset brut."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Compte les ajouts sans modifier le fichier brut.",
    )
    args = parser.parse_args()

    ajoutes, ignores, nombre_relation_cible = ajouter_syntagmes(dry_run=args.dry_run)
    action = "auraient ete ajoutes" if args.dry_run else "ajoutes"
    print(
        f"{ajoutes} syntagmes {action}, {ignores} ignores. "
        f"{RELATION_CIBLE}: {nombre_relation_cible}/{NOMBRE_CIBLE}."
    )


if __name__ == "__main__":
    main()