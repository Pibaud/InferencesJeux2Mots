import argparse
import json
import re
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import TypedDict, cast

from qdrant_client.http import models

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apprentissage import COLLECTION_PLUS_PROCHE, COLLECTION_SEUIL_05
from build_vecteurs import COLLECTION_NAME, client, sig2vec, term2sig
from model.api import JDM_API

THRESHOLD = 0.3

api = JDM_API()


class EvaluationRow(TypedDict):
    index: int
    phrase: str
    expected: str
    prediction: str | None
    score: float
    top3: list[str]
    correct: bool
    reciprocal_rank: float
    error: str | None


class ClassMetrics(TypedDict):
    support: int
    predicted: int
    precision: float
    recall: float
    f1: float


class EvaluationMetrics(TypedDict):
    total: int
    evaluated: int
    errors: int
    correct: int
    accuracy: float
    coverage: float
    top3_accuracy: float
    mrr: float
    average_score: float
    per_class: dict[str, ClassMetrics]
    confusion: Counter[tuple[str, str]]

def parse_phrase(phrase: str) -> tuple[str, str]:
    """Extrait les deux termes A et B d'un syntagme génitif."""
    pattern = r"^\s*(.+?)\s+(?:de\s+la|de\s+l['’]|du|des|de|d['’])\s*(.+?)\s*$"
    match = re.match(pattern, phrase.strip(), flags=re.IGNORECASE)
    
    if not match:
        raise ValueError(f"Le syntagme '{phrase}' n'a pas pu être découpé en forme 'A de B'.")
        
    return match.group(1).strip(), match.group(2).strip()

def query_sparse_neighbors(
    vector,
    vector_name: str,
    collection_name: str = COLLECTION_NAME,
    limit: int = 10000,
):
    """Recherche dans Qdrant"""
    return client.query_points(
        collection_name=collection_name,
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

def find_nearest_relation_types(
    phrase: str,
    threshold: float = THRESHOLD,
    limit: int = 20,
    collection_name: str = COLLECTION_NAME,
):
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
    left_hits = query_sparse_neighbors(left_vector, "s_L", collection_name)
    right_hits = query_sparse_neighbors(right_vector, "s_R", collection_name)
    t5 = time.perf_counter()
    timings["Recherche Qdrant"] = (t5 - t4) * 1000

    # 6. Agrégation Formule 3
    relation_scores = aggregate_relation_scores(left_hits, right_hits, threshold)
    t6 = time.perf_counter()
    timings["Agrégation"] = (t6 - t5) * 1000
    
    timings["Total global"] = (t6 - t0) * 1000

    return relation_scores[:limit], timings


def compute_metrics(rows: list[EvaluationRow], total: int) -> EvaluationMetrics:
    """Calcule les métriques globales et par classe du jeu évalué."""
    predictions = [row for row in rows if row["prediction"] is not None]
    correct = sum(row["correct"] for row in predictions)
    reciprocal_rank = sum(row["reciprocal_rank"] for row in rows)
    average_score = sum(row["score"] for row in predictions) / len(predictions) if predictions else 0.0

    actual_counts = Counter(row["expected"] for row in rows)
    predicted_counts = Counter(cast(str, row["prediction"]) for row in predictions)
    correct_counts = Counter(row["expected"] for row in predictions if row["correct"])
    classes = sorted(set(actual_counts) | set(predicted_counts))
    per_class: dict[str, ClassMetrics] = {}
    for relation in classes:
        support = actual_counts[relation]
        predicted = predicted_counts[relation]
        true_positive = correct_counts[relation]
        precision = true_positive / predicted if predicted else 0.0
        recall = true_positive / support if support else 0.0
        f1 = (2 * precision * recall / (precision + recall)) if precision + recall else 0.0
        per_class[relation] = {
            "support": support,
            "predicted": predicted,
            "precision": precision,
            "recall": recall,
            "f1": f1,
        }

    confusion = Counter(
        (row["expected"], cast(str, row["prediction"]))
        for row in predictions
        if not row["correct"]
    )
    return {
        "total": total,
        "evaluated": len(predictions),
        "errors": total - len(predictions),
        "correct": correct,
        "accuracy": correct / total if total else 0.0,
        "coverage": len(predictions) / total if total else 0.0,
        "top3_accuracy": sum(row["expected"] in row["top3"] for row in rows) / total if total else 0.0,
        "mrr": reciprocal_rank / total if total else 0.0,
        "average_score": average_score,
        "per_class": per_class,
        "confusion": confusion,
    }


def evaluate_dataset(
    dataset_path: Path,
    collection_name: str,
    threshold: float = THRESHOLD,
    limit: int = 20,
) -> tuple[list[EvaluationRow], EvaluationMetrics]:
    """Évalue chaque syntagme annoté contre une collection apprise."""
    with dataset_path.open(encoding="utf-8") as file:
        dataset = json.load(file)

    rows: list[EvaluationRow] = []
    for index, item in enumerate(dataset, start=1):
        expected = item["relation_humaine"]
        phrase = item["texte_complet"]
        try:
            results, _ = find_nearest_relation_types(
                phrase,
                threshold=threshold,
                limit=limit,
                collection_name=collection_name,
            )
            ranked_relations = [relation for relation, _, _ in results]
            prediction = ranked_relations[0] if ranked_relations else None
            score = results[0][1] if results else 0.0
            top3 = ranked_relations[:3]
            rank = ranked_relations.index(expected) + 1 if expected in ranked_relations else 0
            row: EvaluationRow = {
                "index": index,
                "phrase": phrase,
                "expected": expected,
                "prediction": prediction,
                "score": score,
                "top3": top3,
                "correct": prediction == expected,
                "reciprocal_rank": 1 / rank if rank else 0.0,
                "error": None,
            }
        except Exception as exc:
            row = {
                "index": index,
                "phrase": phrase,
                "expected": expected,
                "prediction": None,
                "score": 0.0,
                "top3": [],
                "correct": False,
                "reciprocal_rank": 0.0,
                "error": str(exc),
            }
        rows.append(row)
        prediction_text = row["prediction"] or "Aucune"
        status = "OK" if row["correct"] else "ERREUR"
        print(
            f"[{index:>3}/{len(dataset)}] {status:<6} {phrase:<40} "
            f"attendu={expected:<24} predit={prediction_text:<24} "
            f"score={row['score']:.4f}"
        )
        if row["error"]:
            print(f"      erreur: {row['error']}")

    return rows, compute_metrics(rows, len(dataset))


def print_dataset_report(collection_name: str, metrics: EvaluationMetrics) -> None:
    """Affiche le rapport synthétique d'une évaluation batch."""
    per_class = metrics["per_class"]
    macro = {
        metric: sum(values[metric] for values in per_class.values()) / len(per_class)
        if per_class else 0.0
        for metric in ("precision", "recall", "f1")
    }
    print(f"\n=== Résultats pour {collection_name} ===")
    print(f"Exemples : {metrics['total']} | évalués : {metrics['evaluated']} | sans prédiction : {metrics['errors']}")
    print(f"Exactitude top-1 : {metrics['accuracy']:.2%}")
    print(f"Couverture       : {metrics['coverage']:.2%}")
    print(f"Exactitude top-3 : {metrics['top3_accuracy']:.2%}")
    print(f"MRR              : {metrics['mrr']:.4f}")
    print(f"Score moyen      : {metrics['average_score']:.4f}")
    print(f"Macro précision/rappel/F1 : {macro['precision']:.2%} / {macro['recall']:.2%} / {macro['f1']:.2%}")

    ranked_classes = sorted(per_class.items(), key=lambda item: item[1]["f1"], reverse=True)
    print("\nClasses les mieux prédites (F1) :")
    for relation, values in ranked_classes[:5]:
        print(f"  {relation:<24} F1={values['f1']:.2%} rappel={values['recall']:.2%} support={values['support']}")
    print("Classes les moins bien prédites (F1) :")
    for relation, values in ranked_classes[-5:]:
        print(f"  {relation:<24} F1={values['f1']:.2%} rappel={values['recall']:.2%} support={values['support']}")

    if metrics["confusion"]:
        print("\nConfusions top-1 les plus fréquentes :")
        for (expected, prediction), count in metrics["confusion"].most_common(10):
            print(f"  {expected} -> {prediction}: {count}")

def main():
    parser = argparse.ArgumentParser(
        description="Recherche les types de relations les plus proches d'un syntagme de type 'A de B'."
    )
    parser.add_argument("phrase", nargs="?", help="Syntagme de la forme 'A de B' (ex. 'chien de chasse')")
    parser.add_argument(
        "--jeu-test",
        type=Path,
        help="Évalue tous les syntagmes annotés du fichier JSON indiqué.",
    )
    parser.add_argument("--seuil", type=float, default=THRESHOLD, help=f"Seuil minimal de similarité (défaut: {THRESHOLD})")
    parser.add_argument("--limit", type=int, default=20, help="Nombre maximum de relations à afficher")
    parser.add_argument(
        "--collection",
        choices=("principale", "plus_proche", "seuil_05", "toutes"),
        default="toutes",
        help="Collection à évaluer (défaut: toutes en mode jeu de test).",
    )
    args = parser.parse_args()

    collections = {
        "principale": COLLECTION_NAME,
        "plus_proche": COLLECTION_PLUS_PROCHE,
        "seuil_05": COLLECTION_SEUIL_05,
    }

    if args.jeu_test:
        selected_collections = (
            [COLLECTION_PLUS_PROCHE, COLLECTION_SEUIL_05]
            if args.collection == "toutes"
            else [collections[args.collection]]
        )
        if not args.jeu_test.is_file():
            print(f"Erreur : fichier de test introuvable : {args.jeu_test}", file=sys.stderr)
            return 1

        for collection_name in selected_collections:
            if not client.collection_exists(collection_name=collection_name):
                print(
                    f"Erreur : collection Qdrant absente : {collection_name}. "
                    "Lancez d'abord l'apprentissage.",
                    file=sys.stderr,
                )
                return 1
            print(f"\n### Évaluation du jeu de test avec {collection_name} ###")
            _, metrics = evaluate_dataset(
                args.jeu_test,
                collection_name,
                threshold=args.seuil,
                limit=args.limit,
            )
            print_dataset_report(collection_name, metrics)
        return 0

    phrase = args.phrase
    if not phrase:
        parser.print_help()
        return 1
    if args.collection == "toutes":
        collection_name = COLLECTION_NAME
    else:
        collection_name = collections[args.collection]

    try:
        results, timings = find_nearest_relation_types(
            phrase,
            threshold=args.seuil,
            limit=args.limit,
            collection_name=collection_name,
        )
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