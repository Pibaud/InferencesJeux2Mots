import argparse
import json
from collections import Counter
from pathlib import Path


STATUTS_UTILISES = {"valide", "corrige"}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Affiche la repartition des classes relation_humaine."
    )
    parser.add_argument(
        "--tous",
        action="store_true",
        help="Inclure tous les statuts du dataset.",
    )
    args = parser.parse_args()

    chemin_dataset = Path(__file__).parent / "dataset.json"
    with chemin_dataset.open("r", encoding="utf-8") as fichier:
        dataset = json.load(fichier)

    if args.tous:
        exemples = dataset
    else:
        exemples = [
            item for item in dataset
            if item.get("statut") in STATUTS_UTILISES
        ]

    compteurs = Counter(item["relation_humaine"] for item in exemples)
    total = sum(compteurs.values())

    textes = Counter(item["texte_complet"] for item in exemples)
    doublons = {
        texte: nombre for texte, nombre in textes.items() if nombre > 1
    }

    print(f"Textes complets dupliques : {len(doublons)}")
    if doublons:
        print("\nDoublons exacts de texte_complet :")
        for texte, nombre in sorted(doublons.items(), key=lambda item: (-item[1], item[0])):
            print(f"  {nombre} occurrences : {texte}")

    print(f"Exemples analyses : {total}")
    if not total:
        return

    print("\nRelation humaine                         Nombre    Pourcentage")
    print("-" * 65)
    for relation, nombre in compteurs.most_common():
        pourcentage = 100 * nombre / total
        print(f"{relation:<40} {nombre:>7}    {pourcentage:>8.2f} %")


if __name__ == "__main__":
    main()
