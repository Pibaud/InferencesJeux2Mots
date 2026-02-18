import json
import re
import sys

from requests import HTTPError
import manipSyntaxe as manipSyntaxe
import interface as interface
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from viewmodel.viewmodel import VM

vm = VM()

def fetch_node_id_by_name(node_name):
    """
    retourne l'id d'un node par son nom
    """
    return vm.fetch_node_id_by_name(node_name)

def fetch_relation_by_id(node_id, node_id2):
    """
    retourne les relations entre deux nodes à partir de leur id
    """
    res =  vm.fetch_relation_by_id(node_id, node_id2)
    return res
    
def fetch_refinements_by_name(node_name):
    """
    retourne les raffinements d'un node à partir de son nom
    """
    res = vm.fetch_refinements_by_name(node_name)
    return res

if __name__ == "__main__":
    if len(sys.argv)==3:
        name2 = sys.argv[2]
        name = sys.argv[1]

    elif len(sys.argv)==2:
        name = sys.argv[1]
    else:
        name = input("Entrez le nom du nœud 1 à rechercher : ")
        name2 = input("Entrez le nom du nœud 2 à rechercher : ")

    id1 = fetch_node_id_by_name(name)
    
    refs = fetch_refinements_by_name(name)
    
    print("--- Raffinements du noeud 1 ---")
    for ref in refs:
        print(f"Raffinement ID : {ref}")
    
    id2 = fetch_node_id_by_name(name2)
    
    print("--- Relations entre les nœuds  ---")
    
    relations = fetch_relation_by_id(id1, id2)
    
    
    print("Relations trouvées : ", relations)

    for i in relations:
        try: 
            nodeRel = vm.fetch_node_by_name(":r"+str(i))
            relations_out = vm.fetch_relations_from(nodeRel["name"])
            print("Relations sortantes du nœud : ", relations_out, "\n")
        except HTTPError as e:
            continue
            #print(f"erreur HTTP pour : {i} : {e}")


            