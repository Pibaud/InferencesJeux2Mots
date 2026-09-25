"""Utilitaires pour interroger l'API Jeux de Mots."""

import argparse
import sys

from model.api import JDM_API


api = JDM_API()


def get_term_id(term_name: str) -> int | None:
    """Retourne l'identifiant JDM correspondant au nom d'un terme."""
    term_name = term_name.strip()
    if not term_name:
        raise ValueError("Le nom du terme ne peut pas être vide.")

    term_id = api.get_node_id_by_name(term_name)
    return int(term_id) if term_id is not None else None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Affiche l'identifiant JDM correspondant à un terme."
    )
    parser.add_argument("term", nargs="+", help="Nom du terme, éventuellement composé")
    args = parser.parse_args()

    term_name = " ".join(args.term)
    try:
        term_id = get_term_id(term_name)
    except Exception as error:
        print(f"Erreur lors de la recherche de '{term_name}': {error}", file=sys.stderr)
        return 1

    if term_id is None:
        print(f"Terme introuvable : {term_name}", file=sys.stderr)
        return 1

    print(term_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
