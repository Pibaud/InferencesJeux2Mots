import json
import re
import sys

from requests import HTTPError
import manipSyntaxe as manipSyntaxe
import interface
import interface as interface
import os
import hashlib
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from model.api import JDM_API

# Créez l'instance ici
api = JDM_API()

def print_relations_between_terms(name1, name2):
    """
    Affiche toutes les relations entre deux termes avec le type de relation et le nom du node cible
    """
    node1 = api.get_node_id_by_name(name1)
    node2 = api.get_node_id_by_name(name2)
    relations = api.get_relations_from_to_by_id(node1, node2)
    if relations and "relations" in relations:
        print(f"--- Relations entre '{name1}' et '{name2}' ---")
        for rel in relations["relations"]:
            rel_type_id = rel["type"]
            rel_type_name = api.get_relation_name_by_type_id(rel_type_id)
            rel_id = rel["id"]
            print(f"{name1} --({rel_type_name})--> {name2} (relation id: {rel_id})")
            #pour cette relation, on essaie d'obtenir les annotations : ajouter ":r" avant l'id donc ":r12345"
            rel_node_name = f":r{rel_id}"
            annotations = api.get_relations_from(rel_node_name)
            print(f"Annotations pour la relation '{rel_type_name}' dont le nom du noeud qui la représente est {rel_node_name} :")
            print(annotations)
    else:
        print("Aucune relation trouvée entre les deux termes.")


def relation_weight_between_terms(name1,relation, name2):
        node1 = api.get_node_id_by_name(name1)
        node2 = api.get_node_id_by_name(name2)
        relations = api.get_relations_from_to_by_id(node1, node2)
        if relations and "relations" in relations:
            for rel in relations["relations"]:
                rel_type_id = rel["type"]
                rel_type_name = api.get_relation_name_by_type_id(rel_type_id)
                if rel_type_name == relation:
                    return rel["w"]
        return None

def inference_inductive(name1, name2):
    """
    Vérifie s'il existe une relation inductive entre name1 et name2
    """
    node1 = api.get_node_id_by_name(name1)
    node2 = api.get_node_id_by_name(name2)
    print(f"id de {name1} : {node1}, id de {name2} : {node2}")
    relations = api.get_relations_from_to_by_id(node1, node2)
    if relations and "relations" in relations:
        for rel in relations["relations"]:
            rel_type_id = rel["type"]
            rel_type_name = api.get_relation_name_by_type_id(rel_type_id)
            if rel_type_name == "transitive":
                return True
    return False


def print_relation_weight_between_terms(name1,relation,name2):
    print(f"--- Poids de la relation '{relation}' entre '{name1}' et '{name2}' ---")
    poids = relation_weight_between_terms(name1,relation,name2)
    
    if poids==None:
        print("NULL retourné : on ne sait pas")
        return
    
    print(poids)
    return

def get_refinement_names(name):
    retour = []
    ref = api.get_refinements(name)
    for raf in ref["nodes"]:
        if (raf["type"]==1):
            retour.append(raf["name"])
    return retour

def print_refinements(name):
    print(f"---Raffinements de '{name}'---")
    print(get_refinement_names(name))


def infer(name1, relation, name2):
    """
    Fait les inférences néccessaires pour affirmer ou réfuter la relation <name1> <relation> <name2>
    1. Paralléliser les étapes suivantes pour chaque raffinement

    2. Essayer directement si la relation existe
    
    3. Donner un score unique pour transitivité, déduction, induction (utiliser le poids max des relations trouvées si un poids est attribué à chaque relation)
    
    4. Faire un classement des scores pour donner la raison principale d'inférence (pour commencer. Ensuite on peut imaginer d'autres idées pour trouver la meilleure inférence que juste prendre celle de poids max)
    """

if __name__ == "__main__":
    query = interface.messageDépart()
    if len(query) == 2:
            name, name2 = query
            if (name=="R"):
                print_refinements(name2)
            else:    
                print_relations_between_terms(name, name2)
    elif len(query) == 3:
        name, relation, name2 = query
        print_relation_weight_between_terms(name,relation,name2)    

    else:
        interface.messageErreur()

