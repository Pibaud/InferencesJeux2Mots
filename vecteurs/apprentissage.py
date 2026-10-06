import argparse
import sys
from collections.abc import Collection, Iterator, Sequence
from pathlib import Path
from typing import cast

from qdrant_client.http import models
from qdrant_client.http.models import PointIdsList, Record

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from build_vecteurs import COLLECTION_NAME, client

COLLECTION_PLUS_PROCHE = f"{COLLECTION_NAME}_plus_proche"
SEUIL_MINIMUM = 0.5

def iter_points(collection_name: str = COLLECTION_NAME) -> Iterator[Record]:
    """Parcourt tous les points de la collection avec leurs deux vecteurs."""
    offset = None
    while True:
        points, offset = client.scroll(
            collection_name=collection_name,
            limit=256,
            offset=offset,
            # On remplace is_def par traits_morpho dans le payload récupéré
            with_payload=["texte_complet", "relation", "traits_morpho", "fus", "fusion_sources"],
            with_vectors=["s_L", "s_R"],
        )
        yield from points
        if offset is None:
            break

def sparse_similarity(left: object, right: object) -> float:
    """Calcule le produit scalaire de deux vecteurs creux normalises."""
    left_indices = getattr(left, "indices", [])
    left_values = getattr(left, "values", [])
    right_values = dict(zip(
        getattr(right, "indices", []),
        getattr(right, "values", []),
    ))
    return sum(
        value * right_values.get(index, 0.0)
        for index, value in zip(left_indices, left_values)
    )

def union_sparse_vectors(left: object, right: object) -> models.SparseVector:
    """Construit l'union des signatures en conservant le poids maximal."""
    weights = {}
    for vector in (left, right):
        for index, value in zip(
            getattr(vector, "indices", []),
            getattr(vector, "values", []),
        ):
            weights[index] = max(weights.get(index, 0.0), value)

    norm = sum(value ** 2 for value in weights.values()) ** 0.5 or 1.0
    return models.SparseVector(
        indices=list(weights),
        values=[value / norm for value in weights.values()],
    )

def combined_similarity(
    point: Record | models.PointStruct,
    candidate: Record | models.PointStruct,
) -> float:
    """Agrège les similarités gauche et droite comme dans evaluation.py."""
    point_vectors = cast(dict[str, object], point.vector or {})
    candidate_vectors = cast(dict[str, object], candidate.vector or {})
    return 0.5 * (
        sparse_similarity(point_vectors["s_L"], candidate_vectors["s_L"])
        + sparse_similarity(point_vectors["s_R"], candidate_vectors["s_R"])
    )


def find_nearest_neighbor(
    point: Record | models.PointStruct,
    points: Sequence[Record | models.PointStruct],
    minimum_score: float | None = None,
) -> tuple[Record | models.PointStruct | None, float | None]:
    """Trouve le voisin compatible le plus proche, avec un seuil optionnel."""
    payload = point.payload or {}
    candidates = (
        candidate
        for candidate in points
        if candidate.id != point.id
        and (candidate.payload or {}).get("relation") == payload.get("relation")
    )
    nearest = max(
        candidates,
        key=lambda candidate: combined_similarity(point, candidate),
        default=None,
    )
    score = combined_similarity(point, nearest) if nearest else None
    if score is not None and minimum_score is not None and score < minimum_score:
        return None, score
    return nearest, score


def fuse_points(
    point: Record | models.PointStruct,
    nearest: Record | models.PointStruct,
    new_id: int,
    collection_name: str = COLLECTION_NAME,
) -> models.PointStruct:
    """Crée le point fusionné et marque ses deux sources comme fusionnées."""
    point_vectors = cast(dict[str, object], point.vector or {})
    nearest_vectors = cast(dict[str, object], nearest.vector or {})
    point_payload = point.payload or {}
    nearest_payload = nearest.payload or {}
    point_text = point_payload.get("texte_complet")
    nearest_text = nearest_payload.get("texte_complet")
    fused_text = " + ".join(
        text for text in (point_text, nearest_text) if isinstance(text, str) and text
    )

    fused_point = models.PointStruct(
        id=new_id,
        payload={
            "texte_complet": fused_text,
            "relation": point_payload.get("relation"),
            "traits_morpho": point_payload.get("traits_morpho"), # On garde pour l'affichage
            "fus": 0,
            "fusion_sources": [point.id, nearest.id],
        },
        vector={
            "s_L": union_sparse_vectors(point_vectors["s_L"], nearest_vectors["s_L"]),
            "s_R": union_sparse_vectors(point_vectors["s_R"], nearest_vectors["s_R"]),
        },
    )

    client.batch_update_points(
        collection_name=collection_name,
        update_operations=[
            models.UpsertOperation(
                upsert=models.PointsList(points=[fused_point]),
            ),
            models.SetPayloadOperation(
                set_payload=models.SetPayload(
                    payload={"fus": 1},
                    points=[point.id, nearest.id],
                ),
            ),
        ],
        wait=True,
    )
    return fused_point


def find_nearest_neighbors(
    collection_name: str = COLLECTION_NAME,
    minimum_score: float | None = None,
) -> list[dict[str, object]]:
    """Trouve le voisin le plus proche compatible pour chaque point."""
    points = list(iter_points(collection_name))
    results = []

    for point in points:
        payload = point.payload or {}
        nearest, score = find_nearest_neighbor(point, points, minimum_score)

        results.append({
            "point_id": point.id,
            "texte_complet": payload.get("texte_complet"),
            "relation": payload.get("relation"),
            "traits_morpho": payload.get("traits_morpho"),
            "nearest_point_id": nearest.id if nearest else None,
            "nearest_texte_complet": (nearest.payload or {}).get("texte_complet") if nearest else None,
            "score": score,
        })

    return results


def clone_collection(
    source_name: str,
    target_name: str,
    point_ids: Collection[int] | None = None,
) -> None:
    """Recrée une collection de travail, éventuellement limitée à certains points."""
    if client.collection_exists(collection_name=target_name):
        client.delete_collection(collection_name=target_name)

    client.create_collection(
        collection_name=target_name,
        vectors_config={},
        sparse_vectors_config={
            "s_L": models.SparseVectorParams(),
            "s_R": models.SparseVectorParams(),
        },
    )

    selected_ids = set(point_ids) if point_ids is not None else None
    source_points = (
        point for point in iter_points(source_name)
        if selected_ids is None or point.id in selected_ids
    )
    batch = list(source_points)
    while batch:
        client.upsert(
            collection_name=target_name,
            points=[
                models.PointStruct(
                    id=point.id,
                    payload=point.payload,
                    vector=point.vector,
                )
                for point in batch
            ],
            wait=True,
        )
        batch = list(source_points)


def run_learning(
    collection_name: str,
    minimum_score: float | None = None,
    limit: int | None = None,
) -> int:
    """Fusionne les points d'une collection et retourne le nombre de fusions."""
    points = list(iter_points(collection_name))
    points_a_traiter: list[Record | models.PointStruct] = [
        point for point in points
        if (point.payload or {}).get("fus") == 0
    ]
    next_id = max(
        (point.id for point in points if isinstance(point.id, int)),
        default=-1,
    ) + 1
    processed = 0

    while points_a_traiter and (limit is None or processed < limit):
        point = points_a_traiter.pop(0)
        nearest, score = find_nearest_neighbor(
            point,
            points_a_traiter,
            minimum_score,
        )

        if nearest is None or score is None:
            continue

        payload = point.payload or {}
        score_text = f"{score:.6f}"
        fused_point = fuse_points(point, nearest, next_id, collection_name)
        points_a_traiter.remove(nearest)
        point.payload = {**payload, "fus": 1}
        nearest.payload = {**(nearest.payload or {}), "fus": 1}
        points_a_traiter.append(fused_point)
        
        print(
            f"[{collection_name}] fusion {point.id} + {nearest.id} -> {fused_point.id} "
            f"score={score_text} relation={payload.get('relation')!r} "
            f"traits={payload.get('traits_morpho')}"
        )
        print(f"  {payload.get('texte_complet')}")
        print(f"  voisin: {(nearest.payload or {}).get('texte_complet')}")
        next_id += 1
        processed += 1

    return processed


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Trouve le voisin le plus proche de chaque point compatible."
    )
    parser.add_argument(
        "--limit", type=int, default=None,
        help="Limite le nombre de résultats affichés (par défaut: tous).",
    )
    args = parser.parse_args()

    clone_collection(COLLECTION_NAME, COLLECTION_PLUS_PROCHE)

    total_plus_proche = run_learning(
        COLLECTION_PLUS_PROCHE,
        limit=args.limit,
    )
    print(
        f"Fusions realisees: {COLLECTION_PLUS_PROCHE}={total_plus_proche}"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())