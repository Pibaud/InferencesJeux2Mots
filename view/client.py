import json
import re
import sys
import math

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

def inference_deductive(name1, name2, relation_name):
    """
    Vérifie par déduction avec gestion des raffinements et calcul de poids par moyenne géométrique.
    """
    # 1. On récupère les raffinements (le terme lui-même est inclus s'il est type 1)
    rafs1 = get_refinements(name1)
    rafs2 = get_refinements(name2)
    
    # Si get_refinements ne renvoie rien, on travaille sur les noms bruts
    if not rafs1: rafs1 = [{"name": name1, "id": api.get_node_id_by_name(name1)}]
    if not rafs2: rafs2 = [{"name": name2, "id": api.get_node_id_by_name(name2)}]

    results = []
    all_types = api.get_relation_types()
    target_rel_id = next((rt["id"] for rt in all_types if rt["name"] == relation_name), None)

    if not target_rel_id:
        return []

    # 2. On boucle sur tous les couples de raffinements possibles
    for r1 in rafs1:
        for r2 in rafs2:
            id1, n1 = r1["id"], r1["name"]
            id2, n2 = r2["id"], r2["name"]
            
            if not id1 or not id2: continue

            # Récupérer les parents de r1 (is_a = type 6)
            data = api.get_relations_from_by_id(id1, types_ids=6)
            if not data or "relations" not in data: continue

            nodes_info = {n['id']: n for n in data.get('nodes', [])}
            
            # Tri par poids de noeud cible
            sorted_rels = sorted(data["relations"], key=lambda x: nodes_info.get(x["node2"], {"w":0})["w"], reverse=True)

            for rel_isa in sorted_rels[:5]:
                parent_id = rel_isa["node2"]
                parent_name = nodes_info[parent_id]["name"]
                w1 = rel_isa["w"] # Poids de la relation r_isa

                if w1 <= 0 or parent_name.lower() in ["zoologie", "biologie", "médecine", "science"]:
                    continue

                # Chercher la relation cible entre le Parent et le raffinement de name2
                res2 = api.get_relations_from_to_by_id(parent_id, id2, types_ids=target_rel_id)
                
                if res2 and res2.get("relations"):
                    for rel_target in res2["relations"]:
                        w2 = rel_target["w"] # Poids de la deuxième relation
                        
                        if w2 > 0:
                            # CALCUL MOYENNE GÉOMÉTRIQUE
                            poids_final = math.sqrt(w1 * w2)
                            
                            annotations = get_annotations_by_rel_id(rel_target["id"])
                            
                            results.append({
                                "terme1": n1, 
                                "relation": relation_name + " (via " + parent_name + ")", 
                                "terme2": n2, 
                                "poids": poids_final, 
                                "annotations": annotations,
                                "méthode": "Inférence déductive par r_isa"
                            })
    
    return results
        
def get_annotations_by_rel_id(rel_id):
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

def getSpécifiques(node_name):
    node1 = api.get_node_id_by_name(node_name)
    relations = api.get_relations_from_by_id(node1,8,0)
    spécifiques = []
    if relations and "relations" in relations:
        for rel in relations["relations"]:
            if rel["w"]>0:
                name2 = api.get_node_by_id(rel["node2"])["name"].split(">")[0]
                if name2[0]!=":":
                    spécifiques.append({"specifique":name2,"poids":rel["w"]})
 
    spécifiques.sort(key= lambda x : x["poids"],reverse=True)
    return spécifiques

def inferences_inductives(name1,relation, name2):
    print(f"----------Spécifiques de {name1}-------------\n")
    spec = getSpécifiques(name1)[0:20]
    inferences = []
    notString = ""
    for s in spec:
        z = s["specifique"]
        poidsSpecCible = relation_weight_between_terms(z,relation,name2)
        if (poidsSpecCible!=None):
            inferences.append([
                {"terme1":name1, "relation":"r_hypo", "terme2":z, "poids":s["poids"]},
                {"terme1":z,"relation":relation,"terme2":name2,"poids":poidsSpecCible}
                ])
            
    return inferences
            
#printInferencesList(liste):


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
        
def get_annotations_between_terms(name1, rel, name2):
    relations = api.get_relations_from_to(name1, name2)
    
    if relations and "relations" in relations:
        for rel in relations["relations"]:
            rel_type_id = rel["type"]
            rel_id = rel["id"]
            rel_type_name = api.get_relation_name_by_type_id(rel_type_id)
            if rel_type_name == relation:
                return get_annotations_by_rel_id(rel_id)
            
def inference_transitive(name1, rel, name2):
    transitive_relations_ids = [6, 8, 9, 15, 41, 42, 52, 57, 61, 73, 74] # id des relations transitives (ex: r_isa)
    return

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
    
    # Inférence Directe
    for raf1 in raffinements_name1:
        for raf2 in raffinements_name2:
            weight = relation_weight_between_terms(raf1['name'], relation, raf2['name'])
            if(raf1['name']==name1 and raf2['name']==name2 and weight is None): # il est intéressant d'afficher le poids de la relation directe entre les deux termes de départ, 
                inferences.append({"terme1":raf1['name'], "relation":relation, "terme2":raf2['name'], "poids":0, "annotations":[],"méthode":"Inférence directe "}) # même si elle est nulle ou inexistante car cela dit "le sens direct n'est pas évident"
            if(weight is not None):
                annotations = get_annotations_between_terms(raf1['name'], relation, raf2['name'])
                inferences.append({"terme1":raf1['name'], "relation":relation, "terme2":raf2['name'], "poids":weight, "annotations":annotations,"méthode":"Inférence directe"})
                
    
    # INférence déductive
    inferences += inference_deductive(name1, name2, relation)           
    return inferences

if __name__ == "__main__":
    query = interface.messageDépart()
    if len(query)==1 and (query[0]=="S"):
                print(inference_inductive("chat","r_carac","tigré"))
                
    elif len(query) == 2:
            name, name2 = query
            if (name=="R"):
                print_refinements(name2)
           
            else:    
                print(inference_deductive(name, name2))
                #print_relations_between_terms(name, name2)
    elif len(query) == 3:
        name, relation, name2 = query
        inferences = infer(name,relation,name2)    
        # Ordonner les inférences par poids décroissant
        inferences.sort(key=lambda x: x["poids"], reverse=True)
        for inf in inferences:
            print(f"Poids: {inf["poids"]} : {inf["terme1"]} --({inf["relation"]})--> {inf["terme2"]} Méthode: {inf["méthode"]}, Annotations: {inf["annotations"]}")
    else:
        interface.messageErreur()