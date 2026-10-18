"""Découpe un dataset annoté en sous-ensembles d'entraînement et de test."""

import argparse
import json
import random
from collections import defaultdict
from pathlib import Path
from typing import Any


LABEL_KEY = "relation_humaine"


def empreinte(exemple: dict[str, Any]) -> str:
    """Retourne une représentation stable d'un exemple pour détecter les doublons."""
    return json.dumps(exemple, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def charger_dataset(chemin: Path) -> list[dict[str, Any]]:
    with chemin.open(encoding="utf-8") as fichier:
        dataset = json.load(fichier)

    if not isinstance(dataset, list) or not all(isinstance(item, dict) for item in dataset):
        raise ValueError("Le dataset doit être une liste d'objets JSON.")

    doublons = len(dataset) - len({empreinte(item) for item in dataset})
    if doublons:
        raise ValueError(
            f"Le dataset contient {doublons} doublon(s) exact(s) ; "
            "supprimez-les avant la découpe."
        )

    classes_invalides = [
        index
        for index, item in enumerate(dataset)
        if not isinstance(item.get(LABEL_KEY), str) or not item[LABEL_KEY].strip()
    ]
    if classes_invalides:
        raise ValueError(
            f"Chaque exemple doit avoir une classe non vide dans '{LABEL_KEY}' "
            f"(exemples invalides : {classes_invalides[:5]})."
        )
    return dataset


def decouper_dataset(
    dataset: list[dict[str, Any]], proportion_entrainement: float, seed: int
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if not 0 < proportion_entrainement < 1:
        raise ValueError("La proportion d'entraînement doit être strictement entre 0 et 1.")

    par_classe: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for exemple in dataset:
        par_classe[exemple[LABEL_KEY]].append(exemple)

    classes_trop_petites = sorted(
        classe for classe, exemples in par_classe.items() if len(exemples) < 2
    )
    if classes_trop_petites:
        raise ValueError(
            "Impossible de représenter ces classes dans les deux datasets "
            f"(moins de 2 exemples) : {', '.join(classes_trop_petites)}"
        )

    generateur = random.Random(seed)
    entrainement: list[dict[str, Any]] = []
    test: list[dict[str, Any]] = []
    for exemples in par_classe.values():
        exemples = exemples.copy()
        generateur.shuffle(exemples)
        nombre_entrainement = round(len(exemples) * proportion_entrainement)
        nombre_entrainement = max(1, min(len(exemples) - 1, nombre_entrainement))
        entrainement.extend(exemples[:nombre_entrainement])
        test.extend(exemples[nombre_entrainement:])

    generateur.shuffle(entrainement)
    generateur.shuffle(test)
    return entrainement, test


def ecrire_dataset(chemin: Path, dataset: list[dict[str, Any]]) -> None:
    chemin.parent.mkdir(parents=True, exist_ok=True)
    with chemin.open("w", encoding="utf-8") as fichier:
        json.dump(dataset, fichier, ensure_ascii=False, indent=2)
        fichier.write("\n")


def construire_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Découpe un dataset JSON en datasets stratifiés d'entraînement et de test."
    )
    parser.add_argument("source", type=Path, help="Dataset JSON source")
    parser.add_argument("entrainement", type=Path, help="Fichier JSON de sortie pour l'entraînement")
    parser.add_argument("test", type=Path, help="Fichier JSON de sortie pour le test")
    parser.add_argument(
        "--train-ratio",
        type=float,
        default=0.8,
        help="Proportion de chaque classe placée dans l'entraînement (défaut : 0.8)",
    )
    parser.add_argument("--seed", type=int, default=42, help="Graine du mélange (défaut : 42)")
    return parser


def main() -> int:
    parser = construire_parser()
    arguments = parser.parse_args()
    try:
        dataset = charger_dataset(arguments.source)
        entrainement, test = decouper_dataset(dataset, arguments.train_ratio, arguments.seed)
        empreintes_entrainement = {empreinte(item) for item in entrainement}
        empreintes_test = {empreinte(item) for item in test}
        if empreintes_entrainement & empreintes_test:
            raise ValueError("La découpe contient des éléments communs entre les deux sorties.")
        ecrire_dataset(arguments.entrainement, entrainement)
        ecrire_dataset(arguments.test, test)
    except (OSError, json.JSONDecodeError, ValueError) as erreur:
        parser.error(str(erreur))

    print(f"{len(dataset)} exemples découpés")
    print(f"Entraînement : {len(entrainement)} exemples -> {arguments.entrainement}")
    print(f"Test : {len(test)} exemples -> {arguments.test}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
