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
            
            # --- GESTION DES ANNOTATIONS ---
            rel_node_name = f":r{rel_id}"
            try:
                # 1. On tente de récupérer l'ID du noeud réifié
                # Si le noeud n'existe pas, cela lèvera une HTTPError (404 ou 500)
                reified_node_id = api.get_node_id_by_name(rel_node_name)
                
                if reified_node_id:
                    # 2. On récupère les relations sortantes VIA L'ID
                    out_relations = api.get_relations_from_by_id(reified_node_id)
                    
                    annotations_trouvees = False
                    print(f"  ↳ Annotations trouvées pour cette relation :")
                    
                    # 3. On filtre pour ne garder que le type 998 (r_annotation)
                    for r_ann in out_relations.get("relations", []):
                        if r_ann["type"] == 998:
                            annotations_trouvees = True
                            
                            # On récupère les infos du noeud de l'annotation
                            id_annotation = r_ann['node2']
                            poids_annotation = r_ann['w']
                            
                            try:
                                noeud_annotation = api.get_node_by_id(id_annotation)
                                # On extrait le nom (ex: "pertinent")
                                nom_annotation = noeud_annotation.get("name", "Nom inconnu")
                                
                                print(f"    - [{nom_annotation}] (Poids: {poids_annotation})")
                            except HTTPError:
                                print(f"    - [ID {id_annotation} introuvable] (Poids: {poids_annotation})")
                            
                    if not annotations_trouvees:
                        print("    - Aucune annotation de type 998.")
                        
            except HTTPError:
                # Si le noeud :rXXX n'existe pas, ça plantera ici. On l'ignore silencieusement.
                print("  ↳ [Aucune annotation existante pour cette relation]")
            except Exception as e:
                print(f"  ↳ [Erreur lors de la recherche d'annotation : {e}]")
                
    else:
        print("Aucune relation trouvée entre les deux termes.")
        
def get_annotations(rel_id):
    rel_node_name = f":r{rel_id}"
    try:
        reified_node_id = api.get_node_id_by_name(rel_node_name)
        if reified_node_id:
            out_relations = api.get_relations_from_by_id(reified_node_id)
            annotations = []
            for r_ann in out_relations.get("relations", []):
                if r_ann["type"] == 998:
                    id_annotation = r_ann['node2']
                    poids_annotation = r_ann['w']
                    try:
                        noeud_annotation = api.get_node_by_id(id_annotation)
                        nom_annotation = noeud_annotation.get("name", "Nom inconnu")
                        annotations.append((nom_annotation, poids_annotation))
                    except HTTPError:
                        annotations.append((f"ID {id_annotation} introuvable", poids_annotation))
            return annotations
    except HTTPError:
        return []
    except Exception as e:
        print(f"Erreur lors de la recherche d'annotation : {e}")
        return []

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

def get_refinements(name):
    retour = []
    ref = api.get_refinements(name)
    for raf in ref.get("nodes", []):
        if (raf["type"]==1):
            retour.append(raf)
    return retour

def print_refinements(name):
    print(f"---Raffinements de '{name}'---")
    refinements = get_refinements(name)
    if refinements:
        for raf in refinements:
            print(f"- {raf['name']} (id: {raf['id']})")
    else:
        print("Aucun raffinement trouvé pour ce terme.")

def infer(name1, relation, name2):
    """
    Fait les inférences néccessaires pour affirmer ou réfuter la relation <name1> <relation> <name2>
    1. Paralléliser les étapes suivantes pour chaque raffinement (ne pas oublier qu'un terme raffiné peut lui-même être raffiné 
       et que le premier raffinement d'un terme est le terme lui-même)
    
    2. Donner un score unique pour transitivité, déduction, induction (utiliser le poids max des relations trouvées si un poids est attribué à chaque relation)
    
    3. Faire un classement des scores pour donner la raison principale d'inférence (pour commencer. Ensuite on peut imaginer d'autres idées pour trouver la meilleure inférence que juste prendre celle de poids max)
    """
    
    inferences = []
    
    print(f"--- Inférence pour la relation '{relation}' entre '{name1}' et '{name2}' ---")
    
    print("1. Parallélisation des raffinements de name1 et name2")
    raffinements_name1 = get_refinements(name1)
    raffinements_name2 = get_refinements(name2)
    
    for raf1 in raffinements_name1:
        for raf2 in raffinements_name2:
            weight = relation_weight_between_terms(raf1['name'], relation, raf2['name'])
            if(weight is not None and weight > 0):
                annotations = []
                # les annotations s'obtiennent à partir d'un id de relation
                # obtenir l'id de la relation raf1 --(relation)--> raf2 avec getrelationfromto, 
                relations = api.get_relations_from_to(raf1['name'], raf2['name'])
    
                if relations and "relations" in relations:
                    for rel in relations["relations"]:
                        # vérifier que le type de la relation correspond à celle qu'on cherche à inférer
                        rel_type_id = rel["type"]
                        rel_id = rel["id"]
                        rel_type_name = api.get_relation_name_by_type_id(rel_type_id)
                        if rel_type_name == relation:
                            # appeler get_annotations sur cet id pour obtenir les annotations de cette relation
                            annotations = get_annotations(rel_id)
                inferences.append((raf1['name'], relation, raf2['name'], "par inférence directe", weight, annotations))
                
    return inferences

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
        inferences = infer(name,relation,name2)    
        # Ordonner les inférences par poids décroissant
        inferences.sort(key=lambda x: x[4], reverse=True)
        for inf in inferences:
            print(f"Poids: {inf[4]} : {inf[0]} --({inf[1]})--> {inf[2]} Méthode: {inf[3]}, Annotations: {inf[5]}")
    else:
        interface.messageErreur()