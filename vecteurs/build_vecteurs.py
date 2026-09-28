import json
import math
import re
import sys
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
    """Crée la collection avec la configuration pour vecteurs creux."""
    if client.collection_exists(collection_name=COLLECTION_NAME):
        client.delete_collection(collection_name=COLLECTION_NAME)
        
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config={},
        sparse_vectors_config={
            "s_L": models.SparseVectorParams(),
            "s_R": models.SparseVectorParams(),
        }
    )
    print(f"Collection '{COLLECTION_NAME}' créée.")


def term2sig(term_id: int, HSize: int = 10, TRTSize: int = 5, SSTSize: int = 5) -> dict:
    """Génère la signature pondérée d'un terme."""
    sig = {}
    
    # Hyperonymes
    data = api.get_relations_from_by_id(term_id, types_ids=6)
    h_relations = [(rel["node2"], rel["w"]) for rel in data.get("relations", []) if rel["w"] > 0]
    max_h = max((w for _, w in h_relations), default=1)
    for parent_id, weight in sorted(h_relations, key=lambda x: x[1], reverse=True)[:HSize]:
        sig[parent_id] = max(sig.get(parent_id, 0), weight / max_h)
    sig[term_id] = 1.0

    # Cibles TRT
    data = api.get_relations_to_by_id(term_id)
    trt_relations = [(rel["type"], rel["w"]) for rel in data.get("relations", []) if rel["w"] > 0]
    max_trt = max((w for _, w in trt_relations), default=1)
    for i, (rel_type, weight) in enumerate(sorted(trt_relations, key=lambda x: x[1], reverse=True)):
        if i >= TRTSize: break
        sig[rel_type] = max(sig.get(rel_type, 0), weight / max_trt)

    # InfoSem (SST)
    data = api.get_relations_from_by_id(term_id, types_ids=36)
    sst_relations = [(rel["node2"], rel["w"]) for rel in data.get("relations", []) if rel["w"] > 0]
    max_sst = max((w for _, w in sst_relations), default=1)
    for node_id, weight in sorted(sst_relations, key=lambda x: x[1], reverse=True)[:SSTSize]:
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


def determiner_definitude(texte_complet: str, mot_b: str) -> int:
    """
    Détermine si le complément B est défini (1) ou non défini (0),
    """
    texte = texte_complet.strip()

    if re.search(r"\b(du|de la|de l'|des)\b", texte, flags=re.IGNORECASE):
        return 1

    if mot_b and mot_b[0].isupper():
        return 1

    # Par défaut (" de ", " d' " devant nom commun sans déterminant) -> Non défini
    return 0


def inserer_dataset():
    chemin_dataset = Path(__file__).parent / "dataset.json"
    
    with open(chemin_dataset, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    points_a_inserer = []
    
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

        sig_a = term2sig(id_a)
        sig_b = term2sig(id_b)

        # Calcul correct de la définitude
        is_def = determiner_definitude(texte_complet, mot_b)

        point = models.PointStruct(
            id=i,
            payload={
                "texte_complet": texte_complet,
                "mot_a": mot_a,
                "mot_b": mot_b,
                "relation": relation,
                "is_def": is_def
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