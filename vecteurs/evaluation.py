import argparse
import re
import sys
import time
from collections import defaultdict
from pathlib import Path

from qdrant_client.http import models

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from build_vecteurs import COLLECTION_NAME, client, sig2vec, term2sig
from model.api import JDM_API

THRESHOLD = 0.3

api = JDM_API()

def parse_phrase(phrase: str) -> tuple[str, str]:
    """Extrait les deux termes A et B d'un syntagme génitif."""
    pattern = r"^\s*(.+?)\s+(?:de\s+la|de\s+l['’]|du|des|de|d['’])\s*(.+?)\s*$"
    match = re.match(pattern, phrase.strip(), flags=re.IGNORECASE)
    
    if not match:
        raise ValueError(f"Le syntagme '{phrase}' n'a pas pu être découpé en forme 'A de B'.")
        
    return match.group(1).strip(), match.group(2).strip()

def query_sparse_neighbors(vector, vector_name: str, limit: int = 10000):
    """Recherche dans Qdrant"""
    return client.query_points(
        collection_name=COLLECTION_NAME,
        query=models.NearestQuery(nearest=vector),
        using=vector_name,
        with_payload=["relation", "texte_complet"],
        limit=limit,
    )

def aggregate_relation_scores(left_hits, right_hits, threshold: float):
    """Agrège les scores selon la Formule 3 du papier : 1/2(sim(A, sL) + sim(B, sR))."""
    rules_scores = defaultdict(lambda: {
        'score_L': 0.0,
        'score_R': 0.0,
        'relation': None,
        'texte_complet': None,
    })

    for result in left_hits.points:
        rules_scores[result.id]['score_L'] = result.score
        if result.payload:
            rules_scores[result.id]['relation'] = result.payload.get("relation")
            rules_scores[result.id]['texte_complet'] = result.payload.get("texte_complet")

    for result in right_hits.points:
        rules_scores[result.id]['score_R'] = result.score
        if result.payload:
            rules_scores[result.id]['relation'] = result.payload.get("relation")
            rules_scores[result.id]['texte_complet'] = result.payload.get("texte_complet")

    relation_aggregated = defaultdict(list)
    for rule_id, data in rules_scores.items():
        if data['relation']:
            score_formule = 0.5 * (data['score_L'] + data['score_R'])
            if score_formule >= threshold:
                relation_aggregated[data['relation']].append((score_formule, data['texte_complet']))

    result = []
    for relation, scores in relation_aggregated.items():
        score, syntagme = max(scores, key=lambda item: item[0])
        result.append((relation, score, syntagme))

    result.sort(key=lambda item: item[1], reverse=True)
    return result

def find_nearest_relation_types(phrase: str, threshold: float = THRESHOLD, limit: int = 20):
    """Retourne les types de relation les plus proches du syntagme avec le profiling."""
    timings = {}
    
    # 1. Parsing
    t0 = time.perf_counter()
    mot_a, mot_b = parse_phrase(phrase)
    t1 = time.perf_counter()
    timings["Parsing (RegEx)"] = (t1 - t0) * 1000

    # 2. Récupération des IDs JDM
    id_a = api.get_node_id_by_name(mot_a)
    id_b = api.get_node_id_by_name(mot_b)
    if id_a is None or id_b is None:
        raise ValueError(f"Impossible de trouver les termes '{mot_a}' et '{mot_b}' dans la base JDM.")
    t2 = time.perf_counter()
    timings["IDs (API JDM)"] = (t2 - t1) * 1000

    # 3. Création des signatures brutes (Appels lourds à l'API)
    sig_a = term2sig(id_a)
    sig_b = term2sig(id_b)
    t3 = time.perf_counter()
    timings["Signatures (API JDM)"] = (t3 - t2) * 1000

    # 4. Conversion et normalisation locale en vecteurs
    left_vector = sig2vec(sig_a)
    right_vector = sig2vec(sig_b)
    t4 = time.perf_counter()
    timings["Vecteurs (sig2vec)"] = (t4 - t3) * 1000

    # 5. Requêtes Qdrant
    left_hits = query_sparse_neighbors(left_vector, "s_L")
    right_hits = query_sparse_neighbors(right_vector, "s_R")
    t5 = time.perf_counter()
    timings["Recherche Qdrant"] = (t5 - t4) * 1000

    # 6. Agrégation Formule 3
    relation_scores = aggregate_relation_scores(left_hits, right_hits, threshold)
    t6 = time.perf_counter()
    timings["Agrégation"] = (t6 - t5) * 1000
    
    timings["Total global"] = (t6 - t0) * 1000

    return relation_scores[:limit], timings

def main():
    parser = argparse.ArgumentParser(
        description="Recherche les types de relations les plus proches d'un syntagme de type 'A de B'."
    )
    parser.add_argument("phrase", nargs="?", help="Syntagme de la forme 'A de B' (ex. 'chien de chasse')")
    parser.add_argument("--seuil", type=float, default=THRESHOLD, help=f"Seuil minimal de similarité (défaut: {THRESHOLD})")
    parser.add_argument("--limit", type=int, default=20, help="Nombre maximum de relations à afficher")
    args = parser.parse_args()

    phrase = args.phrase
    if not phrase:
        parser.print_help()
        return 1

    try:
        results, timings = find_nearest_relation_types(phrase, threshold=args.seuil, limit=args.limit)
    except Exception as exc:
        print(f"Erreur : {exc}", file=sys.stderr)
        return 1

    # Affichage du rapport de performance
    print(f"Recherche pour : {phrase}")
    print(f"Seuil retenu : {args.seuil}")
    print("\n--- Profiling des performances (ms) ---")
    for step, duration in timings.items():
        if step == "Total global":
            print("-" * 39)
            print(f"{step:<25}: {duration:>10.2f} ms")
        else:
            print(f"{step:<25}: {duration:>10.2f} ms")
    print("---------------------------------------")

    if not results:
        print(f"\nAucune relation ne dépasse le seuil de {args.seuil} pour '{phrase}'.")
        return 0

    rows = [
        (relation, f"{score:.4f}", syntagme or "-")
        for relation, score, syntagme in results
    ]
    headers = ("Relation", "Score", "Syntagme le plus proche")
    widths = [
        max(len(headers[index]), *(len(row[index]) for row in rows))
        for index in range(len(headers))
    ]

    print()
    print(" | ".join(
        header.ljust(width)
        for header, width in zip(headers, widths)
    ))
    print("-+-".join("-" * width for width in widths))
    for relation, score, syntagme in rows:
        print(" | ".join((
            relation.ljust(widths[0]),
            score.rjust(widths[1]),
            syntagme.ljust(widths[2]),
        )))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())