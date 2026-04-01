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

def inference_deductive(name1, name2, relation_name, relation_id, rafs1=None, rafs2=None, res_inf_directe=None):
    """
    Vérifie par déduction avec gestion des raffinements et calcul de poids par moyenne géométrique.
    """
    
    print(f"----------Inférences déductives de {name1} --({relation_name})--> {name2}----------en sachant que c'est {res_inf_directe}\n")
    
    # Si get_refinements ne renvoie rien, on travaille sur les noms bruts
    if not rafs1: rafs1 = [{"name": name1, "id": api.get_node_id_by_name(name1)}]
    if not rafs2: rafs2 = [{"name": name2, "id": api.get_node_id_by_name(name2)}]

    results = []

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
                res2 = api.get_relations_from_to_by_id(parent_id, id2, types_ids=relation_id)
                
                if res2 and res2.get("relations"):
                    for rel_target in res2["relations"]:
                        w2 = rel_target["w"]
                        
                        if (w2 > 0 and res_inf_directe) or (w2 < 0 and res_inf_directe == False) or (res_inf_directe is None):
                            # CALCUL MOYENNE GÉOMÉTRIQUE
                            if res_inf_directe is not None:
                                poids_final = math.sqrt(w1 * abs(w2))
                            elif w2 > 0:
                                poids_final = math.sqrt(w1 * w2)
                            else:
                                poids_final = -math.sqrt(w1 * abs(w2))
                            
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
        #print(f"ID de '{name1}': {node1}, ID de '{name2}': {node2}")
        relations = api.get_relations_from_to_by_id(node1, node2)
        if relations and "relations" in relations:
            for rel in relations["relations"]:
                rel_type_id = rel["type"]
                rel_type_name = api.get_relation_name_by_type_id(rel_type_id)
                if rel_type_name == relation:
                    return rel["w"]
        return None

def getSpécifiques(node_name):
    maxSpes = 20
    node1 = api.get_node_id_by_name(node_name)
    relations = api.get_relations_from_by_id(node1,8,0,maxSpes)
    spécifiques = []
    if relations and "relations" in relations:
        for rel in relations["relations"]:
            if rel["w"]>0:
                name2 = api.get_node_by_id(rel["node2"])["name"].split(">")[0]
                if name2[0]!=":":
                    spécifiques.append({"specifique":name2,"poids":rel["w"]})
 
    spécifiques.sort(key= lambda x : x["poids"],reverse=True)
    return spécifiques

def inference_inductive(name1,relation, name2, reponse):

    nbInferencesInductives = 3
    
    print(f"----------Inférences inductives de {name1} --({relation})--> {name2}-------------\n")
    spec = getSpécifiques(name1)


    raw_spec = getSpécifiques(name1)
    if raw_spec is None:
        return None

    # --- Nettoyage des doublons ---
    unique_specs = {}
    for item in raw_spec:
        term_lower = item["specifique"].lower()
        weight = item["poids"]
        valence = 1 if weight >= 0 else -1
        key = (term_lower, valence)
        
        if key not in unique_specs:
            unique_specs[key] = item
        else:
            if abs(weight) > abs(unique_specs[key]["poids"]):
                unique_specs[key] = item

    # On récupère les 20 premiers après filtrage
    spec = list(unique_specs.values())[0:20]
    # ------------------------------


    inferences = []
    if (spec==None):
        return None
    if (reponse!=None):    


        

        for s in spec:

            z = s["specifique"]
            poidsSpecCible = relation_weight_between_terms(z,relation,name2)
            if (poidsSpecCible!=None):
                if (reponse==True and poidsSpecCible>0):
                    inferences.append({"réponse":reponse,"inférences": [
                        {"terme1":name1, "relation":"r_hypo", "terme2":z, "poids":s["poids"]},
                        {"terme1":z,"relation":relation,"terme2":name2,"poids":poidsSpecCible}
                        ]})
                if  (reponse==False and poidsSpecCible<0):
                    inferences.append({"réponse":reponse,"inférences": [
                        {"terme1":name1, "relation":"r_hypo", "terme2":z, "poids":s["poids"]},
                        {"terme1":z,"relation":"not "+relation,"terme2":name2,"poids":poidsSpecCible}
                        ]})
            if len(inferences)>=nbInferencesInductives: return inferences
        return inferences
    else:
        print("---------------------Détermination de la réponse probable via induction----------------------------")
        total = 0
        for s in spec:
            z = s["specifique"]
            poidsSpecCible = relation_weight_between_terms(z,relation,name2)
            if (poidsSpecCible!=None):
                if (poidsSpecCible>0):
                    total +=1
                    inferences.append({"réponse":reponse,"inférences": [
                        {"terme1":name1, "relation":"r_hypo", "terme2":z, "poids":s["poids"]},
                        {"terme1":z,"relation":relation,"terme2":name2,"poids":poidsSpecCible}
                        ]})
                else:
                    inferences.append({"réponse":reponse,"inférences": [
                        {"terme1":name1, "relation":"r_hypo", "terme2":z, "poids":s["poids"]},
                        {"terme1":z,"relation":"not "+relation,"terme2":name2,"poids":poidsSpecCible}
                        ]})
                
        decision = False if (total<len(spec)) else True
        infDécidées = []
        for z in inferences:
            z["réponse"] = decision
   
            if (decision and z["inférences"][-1]["poids"]>0) or (decision==False and z["inférences"][-1]["poids"]<0):
                infDécidées.append(z)
            if len(infDécidées)>=nbInferencesInductives: return infDécidées


        return infDécidées

def resultatInferenceDirecte(name1,relation,name2):
    poidsTest = relation_weight_between_terms(name1,relation,name2)
    reponseTest = None
    if (poidsTest!=None):
            reponseTest = poidsTest>0
    return reponseTest
    
def inference_inductive_lemma(name1,relation,name2,reponse):
    infBase = inference_inductive(name1,relation,name2,reponse)
    if (len(infBase)>0): return infBase

    lemmaName1 = get_lemmas(name1)  
    lemmaName2 = get_lemmas(name2)

    for z in lemmaName1:            
        for zz in lemmaName2:
            reponseLem = resultatInferenceDirecte(z["lemma"],relation,zz["lemma"])

            inflem = inference_inductive(z["lemma"],relation,zz["lemma"],reponseLem)
            if len(inflem)>0:
                for zzz in inflem:

                    if name1!=z["lemma"]: zzz["inférences"].insert(0,{"terme1":name1,"relation":"r_lemma","terme2":z["lemma"],"poids":z["poids"]})
                    if name2!=zz["lemma"]: zzz["inférences"].append({"terme1":name2,"relation":"r_lemma","terme2":zz["lemma"],"poids":zz["poids"]})
                return inflem
    
    


def printInferencesList(retourInf):
    listeInf = retourInf["inférences"]
    reponseBool = retourInf["réponse"]
    i=1
    lastElem = listeInf[-1]
    if (lastElem["relation"]=="r_lemma"):lastElem = listeInf[-2]

    stri = f"{listeInf[0]["terme1"]} ({lastElem["relation"]}) {lastElem["terme2"]}" if reponseBool else f"{listeInf[0]["terme1"]} ({lastElem["relation"].replace("not ","")}) {lastElem["terme2"]}"
    
    if reponseBool==True :stri+=  " oui | " 
    else: stri+=  " non | "
    for inf in listeInf:
        stri += (inf["terme1"]+" "+inf["relation"]+" "+inf["terme2"])
        if i!=len(listeInf):
            stri+=("  &  ")
        i+=1
    print(stri)


def print_relation_weight_between_terms(name1,relation,name2):
    print(f"--- Poids de la relation '{relation}' entre '{name1}' et '{name2}' ---")
    poids = relation_weight_between_terms(name1,relation,name2)
    
    if poids==None:
        print("NULL retourné : on ne sait pas")
        return
    
    print(poids)
    return

def get_refinements(name):
    print( f"--- Récupération des raffinements de '{name}' ---")
    retour = []
    ref = api.get_refinements(name)
    for raf in ref.get("nodes", []):
        if (raf["type"]==1):
            retour.append(raf)
    print(f"{len(retour)} raffinements trouvés pour '{name}'")
    return retour

def print_refinements(name):
    refinements = get_refinements(name)
    if refinements:
        for raf in refinements:
            print(f"- {raf['name']} (id: {raf['id']})")
    else:
        print("Aucun raffinement trouvé pour ce terme.")

def get_lemmas(name):
    node1 = api.get_node_id_by_name(name)
    relations = api.get_relations_from_by_id(node1,19,0)
    lemmas = []
    if relations and "relations" in relations:
        for rel in relations["relations"]:
            if rel["w"]>0:
                name2 = api.get_node_by_id(rel["node2"])["name"].split(">")[0]
                if name2[0]!=":":
                    lemmas.append({"lemma":name2,"poids":rel["w"]})
 
    lemmas.sort(key= lambda x : x["poids"],reverse=True)
    return lemmas
    



def print_lemmas(name):
    print(f"----------------lématisés de {name}------------------ ")
    lemmas = get_lemmas(name)
    for z in lemmas:
        print(f"{z["lemma"]}")
    pass



def get_annotations_between_terms(name1, rel, name2):
    relations = api.get_relations_from_to(name1, name2)
    
    if relations and "relations" in relations:
        for rel in relations["relations"]:
            rel_type_id = rel["type"]
            rel_id = rel["id"]
            rel_type_name = api.get_relation_name_by_type_id(rel_type_id)
            if rel_type_name == relation:
                return get_annotations_by_rel_id(rel_id)
            
def inference_synonymique_double(name1, name2, relation_name, relation_id, rafs1=None, rafs2=None, res_inf_directe=None):
    # Initialisation des listes si None
    print(f"----------Inférences par expansion synonymique double de {name1} --({relation_name})--> {name2}----------sachant que {res_inf_directe}\n")
    if not rafs1: rafs1 = [{"name": name1, "id": api.get_node_id_by_name(name1)}]
    if not rafs2: rafs2 = [{"name": name2, "id": api.get_node_id_by_name(name2)}]

    results = []

    for r1 in rafs1:
        # Expansion synonymes Terme 1 (Top 4)
        syns1 = api.get_top_synonyms(r1["id"], limit=4) 
        # On ajoute le terme lui-même à la liste pour tester Terme1 -> Syn(Terme2)
        syns1.append({"id": r1["id"], "name": r1["name"], "w": 100}) # Poids arbitraire max pour le mot lui-même

        for r2 in rafs2:
            # Expansion synonymes Terme 2 (Top 4)
            syns2 = api.get_top_synonyms(r2["id"], limit=4)
            syns2.append({"id": r2["id"], "name": r2["name"], "w": 100})

            for s1 in syns1:
                for s2 in syns2:
                    # On évite de tester le cas Direct (déjà fait dans infer())
                    if s1["id"] == r1["id"] and s2["id"] == r2["id"]: continue

                    res = api.get_relations_from_to_by_id(s1["id"], s2["id"], types_ids=relation_id)
                    
                    if res and res.get("relations"):
                        for rel in res["relations"]:
                            if (rel["w"] > 0 and res_inf_directe) or (rel["w"] < 0 and res_inf_directe == False) or (res_inf_directe is None):
                                # On calcule le score
                                if res_inf_directe is not None:
                                    score = math.pow(s1["w"] * abs(rel["w"]) * s2["w"], 1/3)
                                elif rel["w"] > 0:
                                    score = math.pow(s1["w"] * rel["w"] * s2["w"], 1/3)
                                else:
                                    score = -math.pow(s1["w"] * abs(rel["w"]) * s2["w"], 1/3)
                                
                                # CRUCIAL : On récupère les annotations (même vides) pour éviter le crash
                                annotations = get_annotations_by_rel_id(rel["id"])
                                
                                results.append({
                                    "terme1": r1["name"],
                                    "relation": f"{relation_name} (via {s1['name']} et {s2['name']})",
                                    "terme2": r2["name"],
                                    "poids": score,
                                    "annotations": annotations, # Ajoute cette ligne !
                                    "méthode": "Expansion synonymique double"
                                })
    results.sort(key=lambda x: x["poids"], reverse=True)
    return results[:10]
            
def inference_transitive(name1, relation_name, relation_id, name2, rafs1, rafs2, res_inf_directe):
    print(f"----------Inférences par transitivité de {name1} --({relation_name})--> {name2}-------------\n")
    
    transitive_relations_ids = [6, 8, 9, 15, 41, 42, 52, 57, 61, 73, 74, 83, 109, 111, 112, 124, 125, 151]
    
    if relation_id in transitive_relations_ids:
        res = []
        for r1 in rafs1:
            # 1. Récupération des relations sortantes
            resultats_api = api.get_relations_from_by_id(r1["id"], types_ids=relation_id)
            relations_brutes = resultats_api.get("relations", [])
            
            # 2. NETTOYAGE : On ignore les éléments qui sont None ou mal formatés
            relations_propres = [rel for rel in relations_brutes if isinstance(rel, dict)]
            
            # 3. TRI par poids décroissant peu importe la valeur de res_inf_directe car la première transitivité doit être vraie pour inférer
            
            relations_triees = sorted(relations_propres, key=lambda x: x.get("w", 0), reverse=True)

            # 4. COUPURE (Pruning) : On ne garde que le Top 3
            relations_intermediaires = relations_triees[:3]
            
            for r2 in rafs2:
                for rel_inter in relations_intermediaires:
                    node_intermediaire = rel_inter["node2"]
                    
                    # 5. Appel API pour le deuxième maillon
                    resultats_api_2 = api.get_relations_from_to_by_id(node_intermediaire, r2["id"], types_ids=relation_id)
                    relations_finales = resultats_api_2.get("relations", [])
                    
                    # Selon la valeur de res_inf_directe on trie par poids positif ou négatif ou on garde les plus fortes (+/-)
                    
                    if res_inf_directe is not None:
                        if res_inf_directe: # On veut du positif
                            relations_finales = [rel for rel in relations_finales if rel["w"] > 0]
                        else: # On veut du négatif
                            relations_finales = [rel for rel in relations_finales if rel["w"] < 0]
                    
                    for rel_finale in relations_finales:
                        if rel_finale["type"] == relation_id:
                            w1 = rel_inter["w"]
                            w2 = rel_finale["w"]
                            
                            if(w2 > 0 and res_inf_directe) or (w2 < 0 and res_inf_directe == False) or (res_inf_directe is None):
                                if res_inf_directe is not None:
                                    poids_final = math.sqrt(w1 * abs(w2))
                                elif w2 > 0:
                                    poids_final = math.sqrt(w1 * w2)
                                else:
                                    poids_final = -math.sqrt(w1 * abs(w2))
                            
                            annotations = get_annotations_by_rel_id(rel_finale["id"])
                            res.append({
                                "terme1": r1["name"], 
                                "relation": f"{relation_name} (via {api.get_node_by_id(node_intermediaire)['name']})", 
                                "terme2": r2["name"], 
                                "poids": poids_final, 
                                "annotations": annotations, 
                                "méthode": "Inférence transitive"
                            })
                            
                        #{"réponse":reponse,"inférences": [{"terme1":name1, "relation":"r_hypo", "terme2":z, "poids":s["poids"]},{"terme1":z,"relation":relation,"terme2":name2,"poids":poidsSpecCible}]}

        # --- NOUVEAU BLOC DE FILTRAGE ET DE TRI ---
        
        # 1. Filtrer : On ne garde que les dictionnaires dont la liste 'annotations' n'est pas vide
        res_anotes = [inference for inference in res if inference.get("annotations")]
        
        # 3. Couper : On retourne uniquement le Top 10
        return res_anotes[:10]
        
    return None

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
    
    all_types = api.get_relation_types()
    relation_id = next((rt["id"] for rt in all_types if rt["name"] == relation), None)

    if not relation_id:
        return []
    
    print("1. Parallélisation des raffinements de name1 et name2")
    raffinements_name1 = get_refinements(name1)
    raffinements_name2 = get_refinements(name2)
    
    
    print("Inférence directe")
    
    for raf1 in raffinements_name1:
        for raf2 in raffinements_name2:
            weight = relation_weight_between_terms(raf1['name'], relation, raf2['name'])
            if(raf1['name']==name1 and raf2['name']==name2 and weight is None): # il est intéressant d'afficher le poids de la relation directe entre les deux termes de départ, 
                inferences.append({"terme1":raf1['name'], "relation":relation, "terme2":raf2['name'], "poids":0, "annotations":[],"méthode":"Inférence directe "}) # même si elle est nulle ou inexistante car cela dit "le sens direct n'est pas évident"
            if(weight is not None):
                annotations = get_annotations_between_terms(raf1['name'], relation, raf2['name'])
                inferences.append({"terme1":raf1['name'], "relation":relation, "terme2":raf2['name'], "poids":weight, "annotations":annotations,"méthode":"Inférence directe"})
                
    # Initialisation par défaut
    res_inf_directe = None
    
    poids_max = 0

    if inferences:
        # 1. On trouve l'inférence avec la valeur absolue la plus élevée
        # On utilise abs(x['poids']) comme critère de recherche
        infmax = max(inferences, key=lambda x: abs(x['poids']))
        
        # 2. Affichage (Compréhension de liste pour rester rapide si besoin)
        for inf in inferences:
            print(f"  - {inf['terme1']} --({inf['relation']})--> {inf['terme2']} (Poids: {inf['poids']})")

        # 3. Détermination du résultat (Logique compacte)
        poids_max = infmax["poids"]
        if poids_max != 0:
            res_inf_directe = poids_max > 0
    
    print(f"Poids de l'inférence directe la plus forte : {poids_max} (Résultat : {'Vrai' if res_inf_directe else 'Faux' if res_inf_directe==False else 'Inconnu'})")

    # INférence déductive
    inferences += inference_deductive(name1, name2, relation, relation_id, raffinements_name1, raffinements_name2, res_inf_directe)
    
    # Inférence transitive
    inferences_inductives = inference_transitive(name1, relation, relation_id, name2, raffinements_name1, raffinements_name2, res_inf_directe)
    if inferences_inductives:
        inferences += inferences_inductives

    #inferences goat
    inferences_goat = inference_inductive_lemma(name1,relation,name2,res_inf_directe)
    if (inferences_goat):
        inferences += inferences_goat

    #inference synonymique double
    inferences_synonymiques = inference_synonymique_double(name1, name2, relation, relation_id, raffinements_name1, raffinements_name2, res_inf_directe)
    if inferences_synonymiques:
        inferences += inferences_synonymiques

    
    return inferences

if __name__ == "__main__":
    query = interface.messageDépart()
    if len(query)==4 and (query[0]=="S"):
                S=_,name, relation ,name2 = query
                reponseTest = resultatInferenceDirecte(name,relation,name2)
                for z in inference_inductive_lemma(name,relation,name2,reponseTest):
                    printInferencesList(z)

    elif len(query) == 2:
            name, name2 = query
            if (name=="R"):
                print_refinements(name2)
            elif (name=="L"):
                print_lemmas(name2)
                
    elif len(query) == 3:
        name, relation, name2 = query
        inferences = infer(name,relation,name2)
        # Ordonner les inférences par poids décroissant
        inferences.sort(key=lambda x: x["poids"], reverse=True)
        for inf in inferences:
            print(f"Poids: {inf["poids"]} : {inf["terme1"]} --({inf["relation"]})--> {inf["terme2"]} Méthode: {inf["méthode"]}, Annotations: {inf["annotations"]}")
    else:
        interface.messageErreur()