import json
import math
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from model.api import JDM_API

DATASET_PATH = Path(__file__).parent / "dataset.json"
AGENTS_PATH = Path(__file__).parent / "agents"
AGENTS_PATHS = {
    "seuil": Path(__file__).parent / "agents_seuil",
    "complet": Path(__file__).parent / "agents_complet",
}
FUSION_THRESHOLD = 0.5
VALID_STATUSES = {"valide", "corrige"}
H_SIZE = 400
TRT_SIZE = 400
INFOSEM_SIZE = 400
ANNOTATIONS_PEU_PERTINENTES = {
    "peu pertinent",
    "peu pertinente",
    "peu-pertinent",
    "peu-pertinente",
}
api = JDM_API()


def determiner_definitude(texte_complet: str, mot_b: str) -> int:
    texte = texte_complet.strip()
    if re.search(r"\b(du|de la|de l'|des)\b", texte, flags=re.IGNORECASE):
        return 1
    return 0


def regrouper_trt_par_id(relations: list[tuple[int, float]]) -> list[tuple[int, float]]:
    """Garde le poids maximal pour chaque ID de type TRT."""
    poids_par_id: dict[int, float] = {}
    for type_id, poids in relations:
        poids_par_id[type_id] = max(poids_par_id.get(type_id, poids), poids)
    return list(poids_par_id.items())


def relation_est_pertinente(relation: dict[str, Any]) -> bool:
    annotations = api.get_annotations_by_rel_id(relation["id"])
    return not any(
        annotation.strip().lower() in ANNOTATIONS_PEU_PERTINENTES
        for annotation in annotations
    )


def term2sig(
    term_id: int,
    HSize: int = H_SIZE,
    TRTSize: int = TRT_SIZE,
    SSTSize: int = INFOSEM_SIZE,
) -> dict[int, float]:
    signature: dict[int, float] = {}
    data = api.get_relations_from_by_id(term_id, types_ids=6,limit=HSize)
    relations = [
        (r["node2"], r["w"])
        for r in data.get("relations", [])
        if r["w"] > 0 and relation_est_pertinente(r)
    ]
    maximum = max((weight for _, weight in relations), default=1)
    for node_id, weight in sorted(relations, key=lambda item: item[1], reverse=True)[:HSize]:
        signature[node_id] = max(signature.get(node_id, 0), weight / maximum)
    signature[term_id] = 1.0

    data = api.get_relations_to_by_id(term_id)
    relations = [
        (r["type"], r["w"])
        for r in data.get("relations", [])
        if r["w"] > 0 and relation_est_pertinente(r)
    ]
    relations = regrouper_trt_par_id(relations)
    maximum = max((weight for _, weight in relations), default=1)
    for node_id, weight in sorted(relations, key=lambda item: item[1], reverse=True)[:TRTSize]:
        signature[node_id] = max(signature.get(node_id, 0), weight / maximum)

    data = api.get_relations_from_by_id(term_id, types_ids=36,limit=SSTSize)
    relations = [
        (r["node2"], r["w"])
        for r in data.get("relations", [])
        if r["w"] > 0 and relation_est_pertinente(r)
    ]
    maximum = max((weight for _, weight in relations), default=1)
    for node_id, weight in sorted(relations, key=lambda item: item[1], reverse=True)[:SSTSize]:
        signature[node_id] = max(signature.get(node_id, 0), weight / maximum)
    return signature


def sig2vec(signature: dict[int, float], prefix: str = "") -> dict[str, float]:
    return {f"{prefix}{node_id}": weight for node_id, weight in signature.items()}

  
def fusionner_signatures(signature_a: dict[int, float], signature_b: dict[int, float]) -> dict[str, float]:
    vector = sig2vec(signature_a, "a:")
    vector.update(sig2vec(signature_b, "b:"))
    return vector


def construire_vecteur_termes(term_id_a: int, term_id_b: int) -> dict[str, float]:
    return fusionner_signatures(term2sig(term_id_a), term2sig(term_id_b))


def fusionner_vecteurs(left: dict[str, float], right: dict[str, float]) -> dict[str, float]:
    keys = set(left) | set(right)
    return {
        key: left.get(key, 0.0) + right.get(key, 0.0)
        for key in keys
        if left.get(key, 0.0) or right.get(key, 0.0)
    }


def cosine_similarity(left: dict[str, float], right: dict[str, float]) -> float:
    dot = sum(value * right.get(key, 0.0) for key, value in left.items())
    left_norm = math.sqrt(sum(value * value for value in left.values()))
    right_norm = math.sqrt(sum(value * value for value in right.values()))
    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0
    return dot / (left_norm * right_norm)


def construire_foret(vectors: list[dict[str, float]], texts: list[str] | None = None, threshold: float | None = None) -> list[dict[str, Any]]:
    """Construit une forêt en fusionnant tant que le seuil est respecté."""
    if not vectors:
        return []
    texts = texts or [""] * len(vectors)
    clusters: list[dict[str, Any]] = [
        {"vector": vector, "samples": 1, "texte_complet": text}
        for vector, text in zip(vectors, texts)
    ]
    while len(clusters) > 1:
        best_pair = (0, 1)
        best_similarity = -1.0
        for left_index in range(len(clusters)):
            for right_index in range(left_index + 1, len(clusters)):
                similarity = cosine_similarity(
                    clusters[left_index]["vector"], clusters[right_index]["vector"]
                )
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_pair = (left_index, right_index)
        if threshold is not None and best_similarity <= threshold:
            break
        left_index, right_index = best_pair
        left, right = clusters[left_index], clusters[right_index]
        merged = {
            "vector": fusionner_vecteurs(left["vector"], right["vector"]),
            "samples": left["samples"] + right["samples"],
            "merge_similarity": best_similarity,
            "children": [left, right],
        }
        clusters = [cluster for index, cluster in enumerate(clusters) if index not in best_pair]
        clusters.append(merged)
    return clusters


def construire_arbre(vectors: list[dict[str, float]], texts: list[str] | None = None) -> dict[str, Any] | None:
    """Construit une racine unique en fusionnant sans seuil."""
    return (construire_foret(vectors, texts)[0]
            if vectors else None)


def load_examples(dataset_path: Path = DATASET_PATH) -> list[dict[str, Any]]:
    dataset = json.loads(dataset_path.read_text(encoding="utf-8"))
    if not isinstance(dataset, list):
        raise ValueError("Le dataset d'entraînement doit contenir une liste JSON d'exemples.")
    examples: list[dict[str, Any]] = []
    total = sum(
        isinstance(item, dict) and item.get("statut") in VALID_STATUSES
        for item in dataset
    )
    processed = 0
    for item in dataset:
        if not isinstance(item, dict) or item.get("statut") not in VALID_STATUSES:
            continue
        processed += 1
        print(f"[JDM] traitement {processed}/{total} : {item['texte_complet']}", flush=True)
        id_a = api.get_node_id_by_name(item["mot_a"])
        id_b = api.get_node_id_by_name(item["mot_b"])
        if id_a is None or id_b is None or not item.get("relation_humaine"):
            continue
        examples.append({
            "features": construire_vecteur_termes(id_a, id_b),
            "relation": item["relation_humaine"],
            "definitude": determiner_definitude(item["texte_complet"], item["mot_b"]),
            "texte_complet": item["texte_complet"],
        })
        if processed == 1 or processed % 10 == 0 or processed == total:
            print(f"[JDM] exemples {processed}/{total} | retenus {len(examples)}", flush=True)
    return examples


def train_model(mode: str = "seuil", dataset_path: Path = DATASET_PATH) -> dict[str, Any]:
    examples = load_examples(dataset_path)
    if not examples:
        raise ValueError("Aucun exemple annoté exploitable n'a été trouvé.")
    relations = sorted({example["relation"] for example in examples})
    agents: dict[str, dict[str, Any]] = {}
    agents_path = AGENTS_PATHS[mode]
    agents_path.mkdir(exist_ok=True)
    for old_agent in agents_path.glob("*.json"):
        old_agent.unlink()
    print(f"[ARBRE] construction de {len(relations)} agents", flush=True)
    for index, relation in enumerate(relations, start=1):
        print(f"[ARBRE] agent {index}/{len(relations)} : {relation}", flush=True)
        agents[relation] = {}
        for definitude in (0, 1):
            compatible = [example for example in examples if example["relation"] == relation and example["definitude"] == definitude]
            trees = construire_foret(
                [example["features"] for example in compatible],
                [example["texte_complet"] for example in compatible],
                FUSION_THRESHOLD if mode == "seuil" else None,
            )
            agents[relation][str(definitude)] = trees
            if trees:
                agent_model = {
                    "relation": relation,
                    "definitude": definitude,
                    "mode": mode,
                    "fusion_threshold": FUSION_THRESHOLD if mode == "seuil" else None,
                    "examples_count": len(compatible),
                    "trees": trees,
                }
                agent_path = agents_path / f"{relation}_{definitude}.json"
                agent_path.write_text(
                    json.dumps(agent_model, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
                print(f"[ARBRE] sauvegardé : {agent_path}", flush=True)
    return {"agents": agents}

def parcourir_arbre(tree: dict[str, Any], vector: dict[str, float]) -> tuple[dict[str, Any], float]:
    node = tree
    parent_similarity = cosine_similarity(vector, node["vector"])
    while node.get("children"):
        child, child_similarity = max(
            ((candidate, cosine_similarity(vector, candidate["vector"])) for candidate in node["children"]),
            key=lambda item: item[1],
        )
        if child_similarity < parent_similarity:
            break
        node = child
        parent_similarity = child_similarity
    return node, parent_similarity


def expliquer_parcours(tree: dict[str, Any], vector: dict[str, float]) -> list[dict[str, Any]]:
    """Retourne les comparaisons effectuées pendant la descente."""
    node = tree
    parent_similarity = cosine_similarity(vector, node["vector"])
    path = [{"niveau": 0, "similarite_parent": parent_similarity, "action": "racine"}]
    depth = 0
    while node.get("children"):
        scored_children = [
            (child, cosine_similarity(vector, child["vector"]))
            for child in node["children"]
        ]
        child, child_similarity = max(scored_children, key=lambda item: item[1])
        depth += 1
        decision = "descente" if child_similarity >= parent_similarity else "arret"
        path.append({
            "niveau": depth,
            "similarite_parent": parent_similarity,
            "similarite_enfant": child_similarity,
            "enfant_exemples": child["samples"],
            "action": decision,
        })
        if decision == "arret":
            break
        node = child
        parent_similarity = child_similarity
    return path


def construire_arbre_explicatif(
    tree: dict[str, Any], vector: dict[str, float], max_examples: int = 5
) -> dict[str, Any]:
    """Résume l'arbre évalué en développant le chemin suivi et ses alternatives."""
    next_id = 0

    def exemples_du_noeud(node: dict[str, Any]) -> list[str]:
        examples: list[str] = []
        pending = [node]
        while pending and len(examples) < max_examples:
            current = pending.pop()
            children = current.get("children", [])
            if children:
                pending.extend(reversed(children))
            else:
                text = current.get("texte_complet")
                if isinstance(text, str) and text:
                    examples.append(text)
        return examples

    def build_node(
        node: dict[str, Any],
        similarity: float,
        selected: bool,
        expand: bool,
        best: bool = False,
    ) -> dict[str, Any]:
        nonlocal next_id
        node_id = next_id
        next_id += 1
        children = node.get("children", [])
        scored_children = [
            (child, cosine_similarity(vector, child["vector"]))
            for child in children
        ]
        best_child, best_similarity = (
            max(scored_children, key=lambda item: item[1])
            if scored_children else (None, None)
        )
        best_similarity_value = best_similarity if best_similarity is not None else 0.0
        descend = best_child is not None and best_similarity_value >= similarity

        if not children:
            decision = "Exemple terminal retenu" if selected else "Exemple alternatif"
        elif descend:
            decision = (
                f"Descente vers le nœud suivant : similarité "
                f"{best_similarity_value:.3f} ≥ {similarity:.3f}."
                if selected else "Branche alternative"
            )
        else:
            decision = (
                f"Arrêt : aucun enfant n'améliore la similarité du nœud ({similarity:.3f})."
                if selected else "Branche alternative"
            )

        explained_children = []
        if expand:
            for child, child_similarity in scored_children:
                child_selected = selected and descend and child is best_child
                explained_children.append(
                    build_node(
                        child,
                        child_similarity,
                        child_selected,
                        child_selected,
                        child is best_child,
                    )
                )

        examples = exemples_du_noeud(node)
        return {
            "id": node_id,
            "exemples": node.get("samples", 1),
            "similarite": similarity,
            "cohesion_fusion": node.get("merge_similarity"),
            "generalisation": bool(children),
            "selectionne": selected,
            "meilleur": best,
            "decision": decision,
            "exemples_representatifs": examples,
            "exemples_masques": max(0, node.get("samples", 1) - len(examples)),
            "enfants": explained_children,
        }

    root_similarity = cosine_similarity(vector, tree["vector"])
    return build_node(tree, root_similarity, True, True)


def predict(
    model: dict[str, Any],
    features: dict[str, float],
    definitude: int,
    mode: str = "seuil",
    include_tree_explanation: bool = False,
) -> tuple[str, float, float, str, dict[str, Any]]:
    candidates = {
        relation: agent.get(str(definitude), [])
        for relation, agent in model["agents"].items()
        if agent.get(str(definitude))
    }
    if not candidates:
        raise ValueError(f"Aucun agent n'est entraîné pour la définitude {definitude}.")
    evaluated_trees = {
        relation: [
            {
                "tree": tree,
                "root_similarity": cosine_similarity(features, tree["vector"]),
                "leaf": parcourir_arbre(tree, features),
            }
            for tree in trees
        ]
        for relation, trees in candidates.items()
    }
    scored_agents = {
        relation: max(results, key=lambda result: result["leaf"][1])["leaf"][1]
        for relation, results in evaluated_trees.items()
    }
    relation = max(scored_agents.items(), key=lambda item: item[1])[0]
    result = max(
        evaluated_trees[relation],
        key=lambda item: item["leaf"][1],
    )
    root = result["tree"]
    root_similarity = result["root_similarity"]
    leaf, leaf_similarity = result["leaf"]
    explanation = {
        "agents": scored_agents,
        "arbres_evalues": {relation: len(trees) for relation, trees in candidates.items()},
        "parcours": expliquer_parcours(root, features),
        "dimensions_entree": len(features),
    }
    if include_tree_explanation:
        explanation["arbre_explicatif"] = construire_arbre_explicatif(root, features)
    return relation, root_similarity, leaf_similarity, leaf.get("texte_complet", ""), explanation


def parse_phrase(phrase: str) -> tuple[str, str]:
    underscore_marker = "\x00"
    phrase_a_parser = phrase.replace("_", underscore_marker)
    match = re.match(r"^\s*(.+?)\s+(?:de\s+la|de\s+l['’]|du|des|de|d['’])\s*(.+?)\s*$", phrase_a_parser, flags=re.IGNORECASE)
    if not match:
        raise ValueError("La phrase doit avoir la forme 'A de B'.")
    return tuple(
        groupe.replace(underscore_marker, " ").strip()
        for groupe in match.groups()
    )


def predict_relation_details(
    phrase: str, mode: str = "seuil", include_tree_explanation: bool = False
) -> tuple[str, float, float, str, dict[str, Any]]:
    mot_a, mot_b = parse_phrase(phrase)
    id_a = api.get_node_id_by_name(mot_a)
    id_b = api.get_node_id_by_name(mot_b)
    if id_a is None or id_b is None:
        raise ValueError(f"Terme JDM introuvable : {mot_a if id_a is None else mot_b}")
    model = charger_agents(mode) if any(AGENTS_PATHS[mode].glob("*.json")) else train_model(mode)
    vector = construire_vecteur_termes(id_a, id_b)
    definitude = determiner_definitude(phrase, mot_b)
    return predict(model, vector, definitude, mode, include_tree_explanation)


def predict_relation(phrase: str, mode: str = "seuil") -> str:
    relation, root_similarity, leaf_similarity, example, explanation = predict_relation_details(
        phrase, mode
    )
    _, mot_b = parse_phrase(phrase)
    definitude = determiner_definitude(phrase, mot_b)
    print(f"Définitude : {definitude}")
    print(f"Mode : {mode}")
    print(f"Dimensions non nulles : {explanation['dimensions_entree']}")
    print("Scores des agents compatibles :")
    for agent_relation, score in sorted(explanation["agents"].items(), key=lambda item: item[1], reverse=True):
        print(f"  {agent_relation:<24} {score:.3f}")
    print("Nombre d'arbres évalués par agent :")
    for agent_relation, count in explanation["arbres_evalues"].items():
        print(f"  {agent_relation:<24} {count}")
    print(f"Similarité à la racine : {root_similarity:.3f}")
    print(f"Similarité finale : {leaf_similarity:.3f}")
    print("Parcours :")
    for step in explanation["parcours"]:
        if step["action"] == "racine":
            print(f"  niveau 0 : racine = {step['similarite_parent']:.3f}")
        else:
            print(
                f"  niveau {step['niveau']} : enfant = {step['similarite_enfant']:.3f} "
                f"vs parent = {step['similarite_parent']:.3f} -> {step['action']}"
            )
    if example:
        print(f"Exemple terminal : {example}")
    return relation


def inserer_dataset(mode: str = "seuil", dataset_path: Path = DATASET_PATH) -> dict[str, Any]:
    return train_model(mode, dataset_path)


def charger_agents(mode: str = "seuil") -> dict[str, Any]:
    """Charge tous les arbres d'agents présents dans le dossier du mode."""
    agents: dict[str, dict[str, Any]] = {}
    agents_path = AGENTS_PATHS[mode]
    for path in sorted(agents_path.glob("*.json")):
        agent = json.loads(path.read_text(encoding="utf-8"))
        agents.setdefault(agent["relation"], {})[str(agent["definitude"])] = agent["trees"]
    if not agents:
        raise ValueError(f"Aucun agent trouvé dans {agents_path}.")
    return {"agents": agents}


