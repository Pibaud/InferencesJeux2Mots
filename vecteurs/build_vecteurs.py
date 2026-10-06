import json
import math
import re
import sys
from statistics import mean
from pathlib import Path
from qdrant_client import QdrantClient
from qdrant_client.http import models

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from model.api import JDM_API

api = JDM_API()
client = QdrantClient(url="http://localhost:6333")
COLLECTION_NAME = "syntagmes_grasp_it"

def init_qdrant():
    """Vide la collection existante ou la crée avec ses vecteurs creux."""
    if client.collection_exists(collection_name=COLLECTION_NAME):
        client.delete(
            collection_name=COLLECTION_NAME,
            points_selector=models.FilterSelector(filter=models.Filter()),
            wait=True,
        )
        print(f"Collection '{COLLECTION_NAME}' vidée.")
        return

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config={},
        sparse_vectors_config={
            "s_L": models.SparseVectorParams(),
            "s_R": models.SparseVectorParams(),
        },
    )
    print(f"Collection '{COLLECTION_NAME}' créée.")


def regrouper_trt_par_type(
    relations: list[tuple[int, float]], aggregation: str
) -> list[tuple[int, float]]:
    """Regroupe les poids TRT par type avec une agrégation configurable."""
    if aggregation not in {"max", "mean"}:
        raise ValueError("aggregation doit valoir 'max' ou 'mean'")

    poids_par_type: dict[int, list[float]] = {}
    for type_id, poids in relations:
        poids_par_type.setdefault(type_id, []).append(poids)

    relations_groupees = []
    for type_id, poids in poids_par_type.items():
        poids_agreges = max(poids) if aggregation == "max" else mean(poids)
        relations_groupees.append((type_id, poids_agreges))
    return relations_groupees


def term2sig(
    term_id: int,
    stats: dict | None = None,
    trt_aggregation: str = "max",
) -> dict:
    """Génère la signature pondérée d'un terme."""
    sig = {}
    
    # Hyperonymes
    data = api.get_relations_from_by_id(term_id, types_ids=6)
    h_relations = [(rel["node2"], rel["w"]) for rel in data.get("relations", []) if rel["w"] > 0]
    max_h = max((w for _, w in h_relations), default=1)
    for parent_id, weight in sorted(h_relations, key=lambda x: x[1], reverse=True):
        sig[parent_id] = max(sig.get(parent_id, 0), weight / max_h)
    sig[term_id] = 1.0

    # Cibles TRT
    data = api.get_relations_to_by_id(term_id)
    trt_relations = [(rel["type"], rel["w"]) for rel in data.get("relations", []) if rel["w"] > 0]
    if stats is not None:
        stats["avant"].append(len(trt_relations))
    trt_relations = regrouper_trt_par_type(trt_relations, trt_aggregation)
    max_trt = max((w for _, w in trt_relations), default=1)
    if stats is not None:
        stats["apres"].append(len(trt_relations))
    for rel_type, weight in sorted(trt_relations, key=lambda x: x[1], reverse=True):
        sig[rel_type] = max(sig.get(rel_type, 0), weight / max_trt)

    # InfoSem (SST)
    data = api.get_relations_from_by_id(term_id, types_ids=36)
    sst_relations = [(rel["node2"], rel["w"]) for rel in data.get("relations", []) if rel["w"] > 0]
    max_sst = max((w for _, w in sst_relations), default=1)
    for node_id, weight in sorted(sst_relations, key=lambda x: x[1], reverse=True):
        sig[node_id] = max(sig.get(node_id, 0), weight / max_sst)

    return sig

def sig2vec(sig_dict: dict) -> models.SparseVector:
    """Transforme le dictionnaire en SparseVector Qdrant après Normalisation L2."""
    if not sig_dict:
        return models.SparseVector(indices=[], values=[])

    somme_carres = sum(poids ** 2 for poids in sig_dict.values())
    norme = math.sqrt(somme_carres) if somme_carres > 0 else 1.0

    indices = []
    valeurs_normalisees = []
    
    for idx, poids in sig_dict.items():
        indices.append(idx)
        valeurs_normalisees.append(poids / norme)

    return models.SparseVector(indices=indices, values=valeurs_normalisees)


def determiner_traits_morpho(texte_complet: str, mot_b: str) -> tuple[str, str]:
    """
    Extrait les deux symboles (Det/NoDet et Def/NoDef) du complément de nom B.
    """
    texte = texte_complet.strip()

    # 1. Présence d'un déterminant défini (du, des, de la, de l')
    if re.search(r"\b(du|de la|de l'|des)\b", texte, flags=re.IGNORECASE):
        return "Det", "Def"

    # 2. Présence d'un déterminant indéfini (d'un, d'une)
    if re.search(r"\b(d'un|d'une)\b", texte, flags=re.IGNORECASE):
        return "Det", "NoDef"

    # 3. Absence de déterminant (de, d')
    # Cas particulier : l'attribut Def est forcé pour les entités nommées
    if mot_b and mot_b[0].isupper():
        return "NoDet", "Def"
        
    # Cas par défaut : nom commun sans déterminant
    return "NoDet", "NoDef"


def inserer_dataset(trt_aggregation: str = "max"):
    chemin_dataset = Path(__file__).parent / "dataset.json"
    
    with open(chemin_dataset, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    points_a_inserer = []
    tailles = {"avant": [], "apres": []}
    
    TRAITS_MAP = { # Indices positifs reserves aux traits, hors des ID JDM.
        "Det": 4_000_000_001,
        "NoDet": 4_000_000_002,
        "Def": 4_000_000_003,
        "NoDef": 4_000_000_004,
    }

    for i, item in enumerate(dataset):
        if item.get("statut") not in ["valide", "corrige"]:
            continue
            
        mot_a = item["mot_a"]
        mot_b = item["mot_b"]
        texte_complet = item["texte_complet"]
        relation = item["relation_humaine"]

        print(f"[{i+1}/{len(dataset)}] Traitement de : '{texte_complet}' ...")

        id_a = api.get_node_id_by_name(mot_a)
        id_b = api.get_node_id_by_name(mot_b)

        if not id_a or not id_b:
            print(f"  -> Ignoré : ID introuvable pour {mot_a} ou {mot_b}")
            continue

        sig_a = term2sig(id_a, stats=tailles, trt_aggregation=trt_aggregation)
        sig_b = term2sig(id_b, stats=tailles, trt_aggregation=trt_aggregation)

        trait_det, trait_def = determiner_traits_morpho(texte_complet, mot_b)
        
        sig_b[TRAITS_MAP[trait_det]] = 1.0
        sig_b[TRAITS_MAP[trait_def]] = 1.0

        point = models.PointStruct(
            id=i,
            payload={
                "texte_complet": texte_complet,
                "mot_a": mot_a,
                "mot_b": mot_b,
                "relation": relation,
                "traits_morpho": [trait_det, trait_def],
                "fus": 0,
            },
            vector={
                "s_L": sig2vec(sig_a),
                "s_R": sig2vec(sig_b)
            }
        )
        points_a_inserer.append(point)

    if points_a_inserer:
        print(f"\nInsertion de {len(points_a_inserer)} points dans Qdrant...")
        operation_info = client.upsert(
            collection_name=COLLECTION_NAME,
            wait=True,
            points=points_a_inserer
        )
        print("Statut de l'opération :", operation_info.status)

if __name__ == "__main__":
    init_qdrant()
    inserer_dataset()