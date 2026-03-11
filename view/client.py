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

def print_relations_between_terms(name1, name2):
    """
    Affiche toutes les relations entre deux termes avec le type de relation et le nom du node cible
    """
    node1 = vm.fetch_node_id_by_name(name1)
    node2 = vm.fetch_node_id_by_name(name2)
    relations = vm.jdm_api.get_relations_from_to_by_id(node1, node2)
    if relations and "relations" in relations:
        print(f"--- Relations entre '{name1}' et '{name2}' ---")
        for rel in relations["relations"]:
            rel_type_id = rel["type"]
            rel_type_name = vm.fetch_relation_name_by_type_id(rel_type_id)
            rel_id = rel["id"]
            print(f"{name1} --({rel_type_name})--> {name2} (relation id: {rel_id})")
    else:
        print("Aucune relation trouvée entre les deux termes.")
        
def infer(name1, relation, name2):
    """
    Fait les inférences néccessaires pour affirmer ou réfuter la relation <name1> <relation> <name2>
    1. Paralléliser les étapes suivantes pour chaque raffinement

    2. Essayer directement si la relation existe
    
    3. Donner un score unique pour transitivité, déduction, induction (utiliser le poids max des relations trouvées si un poids est attribué à chaque relation)
    
    4. Faire un classement des scores pour donner la raison principale d'inférence (pour commencer. Ensuite on peut imaginer d'autres idées pour trouver la meilleure inférence que juste prendre celle de poids max)
    """
    

if __name__ == "__main__":
    print("\n Mises en forme possible:")
    print("\n- Chercher relations entre 2 termes: <terme1> <terme2>")
    print('\n   Par exemple : "quelles sont les relations entre chat et griffer ?" écrivez : "chat griffer"')
    print("\n- Chercher si une relation existe entre deux termes: <terme1> <relation> <terme2>")
    print('\n   Par exemple : "un chat peut-il griffer ?" écrivez : "chat griffer"')
    query = input("\nVotre requête : ").strip().split()
    if len(query) == 2:
            name, name2 = query
            print_relations_between_terms(name, name2)
    elif len(query) == 3:
        name, relation, name2 = query
        pass
    else:
        print("Format de requête invalide. Veuillez écrire :<mode> <terme1> <relation> <terme2>")

        