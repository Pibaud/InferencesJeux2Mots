import json
import re
import sys
import manipSyntaxe
import interface
from api.api import JDM_API

jdm_api = JDM_API()

def fetch_node_id_by_name(node_name):
    """
    retourne l'id d'un node par son nom
    """
    return jdm_api.get_node_by_name(node_name).get("id")

def fetch_relation_by_id(node_id, node_id2):
    """
    retourne les relations entre deux nodes à partir de leur id
    """
    res =  jdm_api.get_relations_from_to_by_id(node_id, node_id2)
    resultat = []
    if res:
        for elem in res["relations"] :
            resultat.append(elem["id"])
        return resultat
    else:
        print("Aucune relation trouvée entre les deux nœuds.")
        return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        name = sys.argv[1]
    else:
        name = input("Entrez le nom du nœud 1 à rechercher : ")
    
    id1 = fetch_node_id_by_name(name)
    
    name = input("Entrez le nom du nœud 2 à rechercher : ")
    
    id2 = fetch_node_id_by_name(name)
    
    print("--- Relations entre les nœuds  ---")
    
    relations = fetch_relation_by_id(id1, id2)
    
    print("Relations trouvées : ", relations)