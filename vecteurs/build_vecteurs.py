from model.api import JDM_API
api = JDM_API()

NB_H = 20

def term2sig(term_id : int) -> list:
    """Prend un terme représenté par son id, récupère ses Hyperonymes (H), ses SRT et STT

    Args:
        term_id (int): id du terme

    Returns:
        dict: la signature du terme, sous la forme d'un dictionnaire contenant les hyperonymes, SRT et STT
    """
    
    sig = {'H':{}, 'SRT':[], 'STT':[]}
    
    # ============== HYPERONYMES =============== 
    
    data = api.get_relations_from_by_id(term_id, types_ids=6)
    nodes_info = {n['id']: n for n in data.get('nodes', [])}
    
    # Tri par poids de noeud cible
    sorted_rels = sorted(data["relations"], key=lambda x: nodes_info.get(x["node2"], {"w":0})["w"], reverse=True)

    for rel_isa in sorted_rels[:NB_H]:
        parent_id = rel_isa["node2"]
        w1 = rel_isa["w"] # Poids de la relation r_isa
        sig["H"][parent_id] = w1
        
    # ============== TRT : cibles types de relations =============== 
    
    data = api.get_relations_to_by_id(term_id)
    print(data)
    
    return []
if __name__ == "__main__":
    term2sig(6)