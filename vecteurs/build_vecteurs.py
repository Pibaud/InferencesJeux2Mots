from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from model.api import JDM_API

api = JDM_API()

NB_H = 20

def term2sig(term_id : int, HSize : int = 10, TRTSize : int = 5,SSTSize : int = 5) -> dict:
    """Prend un terme représenté par son id, récupère ses hyperonymes, ses relations de type et ses infosems.

    Args:
        term_id (int): id du terme

    Returns:
        dict: la si gnature du terme, sous la forme d'un dictionnaire contenant les hyperonymes, les types de relations et les infosems
    """
    sig = {'H': {}, 'TRT': {}, 'SST': {}}
    
    # ============== HYPERONYMES =============== 
    data = api.get_relations_from_by_id(term_id, types_ids=6)  # 6 = r_isa
    h_relations = [
        (rel["node2"], rel["w"])
        for rel in data.get("relations", [])
        if rel["w"] > 0
    ]
    max_h = max((weight for _, weight in h_relations), default=0)
    if max_h == 0:
        max_h = 1

    for parent_id, weight in sorted(h_relations, key=lambda x: x[1], reverse=True)[:HSize]:
        normalized_weight = weight / max_h
        sig["H"][parent_id] = max(sig["H"].get(parent_id, 0), normalized_weight)

    sig["H"][term_id] = 1.0

    # ============== TRT : cibles types de relations =============== 
    data = api.get_relations_to_by_id(term_id)
    trt_relations = [
        (rel["type"], rel["w"])
        for rel in data.get("relations", [])
        if rel["w"] > 0
    ]
    max_trt = max((weight for _, weight in trt_relations), default=0)
    if max_trt == 0:
        max_trt = 1

    for rel_type, weight in sorted(trt_relations, key=lambda x: x[1], reverse=True):
        normalized_weight = weight / max_trt
        sig["TRT"][rel_type] = max(sig["TRT"].get(rel_type, 0), normalized_weight)
        if len(sig["TRT"]) >= TRTSize:
            break

    # ============== INFOSEM: informations sémantiques supplémentaires (r_infopot) ===============
    data = api.get_relations_from_by_id(term_id, types_ids=36)  # 36 = r_infopot
    sst_relations = [
        (rel["node2"], rel["w"])
        for rel in data.get("relations", [])
        if rel["w"] > 0
    ]
    max_sst = max((weight for _, weight in sst_relations), default=0)
    if max_sst == 0:
        max_sst = 1

    for node_id, weight in sorted(sst_relations, key=lambda x: x[1], reverse=True)[:SSTSize]:
        normalized_weight = weight / max_sst
        sig["SST"][node_id] = max(sig["SST"].get(node_id, 0), normalized_weight)

    return sig


def debugVecteur(vecteur: dict, term_id: int | None = None) -> None:
    """Affiche un vecteur de manière lisible en remplaçant les ids par les noms JDM."""

    def resolve_node_name(node_id):
        try:
            node = api.get_node_by_id(int(node_id))
            return node.get("name", str(node_id))
        except Exception:
            return str(node_id)

    def resolve_relation_type(type_id):
        try:
            name = api.get_relation_name_by_type_id(int(type_id))
            return name if name is not None else str(type_id)
        except Exception:
            return str(type_id)

    if term_id is not None:
        try:
            term_name = api.get_node_by_id(term_id).get("name", str(term_id))
        except Exception:
            term_name = str(term_id)
        print(f"Vecteur pour '{term_name}' (id={term_id})")
    else:
        print("Vecteur")

    # Hyperonymes
    if "H" in vecteur and vecteur["H"]:
        print("\nH:")
        for node_id, weight in vecteur["H"].items():
            print(f"  - {resolve_node_name(node_id)} ({node_id}) : {weight}")
    else:
        print("\nH: []")

    # Types de relation
    if "TRT" in vecteur and vecteur["TRT"]:
        print("\nTRT:")
        for relation_type, weight in vecteur["TRT"].items():
            print(f"  - {resolve_relation_type(relation_type)} ({relation_type}) : {weight}")
    else:
        print("\nTRT: []")

    # Infosems
    if "SST" in vecteur and vecteur["SST"]:
        print("\nSST:")
        for node_id, weight in vecteur["SST"].items():
            print(f"  - {resolve_node_name(node_id)} ({node_id}) : {weight}")
    else:
        print("\nSST: []")


if __name__ == "__main__":
    sig = term2sig(43, 10, 10, 10)
    debugVecteur(sig, 43)

