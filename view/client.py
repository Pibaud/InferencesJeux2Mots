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
from concurrent.futures import ThreadPoolExecutor, as_completed

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
            
            rel_node_name = f":r{rel_id}"
            try:
                reified_node_id = api.get_node_id_by_name(rel_node_name)
                
                if reified_node_id:
                    out_relations = api.get_relations_from_by_id(reified_node_id)
                    
                    annotations_trouvees = False
                    print(f"  ↳ Annotations trouvées pour cette relation :")
                    
                    for r_ann in out_relations.get("relations", []):
                        if r_ann["type"] == 998:
                            annotations_trouvees = True
                            
                            id_annotation = r_ann['node2']
                            poids_annotation = r_ann['w']
                            
                            try:
                                noeud_annotation = api.get_node_by_id(id_annotation)
                                nom_annotation = noeud_annotation.get("name", "Nom inconnu")
                                
                                print(f"    - [{nom_annotation}] (Poids: {poids_annotation})")
                            except HTTPError:
                                print(f"    - [ID {id_annotation} introuvable] (Poids: {poids_annotation})")
                            
                    if not annotations_trouvees:
                        print("    - Aucune annotation de type 998.")
                        
            except HTTPError:
                print("  ↳ [Aucune annotation existante pour cette relation]")
            except Exception as e:
                print(f"  ↳ [Erreur lors de la recherche d'annotation : {e}]")
                
    else:
        print("Aucune relation trouvée entre les deux termes.")

def inference_deductive(name1, relation_name,name2, res_inf_directe=None, rafs1=None, rafs2=None):
    """
    Vérifie par déduction avec gestion des raffinements et calcul de poids par moyenne géométrique.
    """
    all_types = api.get_relation_types()

    relation_id = next((rt["id"] for rt in all_types if rt["name"] == relation_name), None)

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

            for rel_isa in sorted_rels[:7]:
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
                                "réponse":None if w2==None else w2>0,
                                "inférences":[
                                    {"terme1":n1, "relation":"r_isa", "terme2":parent_name, "poids":w1},
                                    {"terme1":parent_name,"relation":relation_name,"terme2":n2,"poids":w2}],
                                "poids":poids_final,
                                "annotations": annotations,
                                "méthode": "Inférence déductive par r_isa"
                                            })
    return results[:3]


        
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
    maxSpes = 25 #On peut augmenter un peu
    node1 = api.get_node_id_by_name(node_name)
    relations = api.get_relations_from_by_id(node1, 8, 0, maxSpes)
    spécifiques = []
    
    if relations and "relations" in relations:
        for rel in relations["relations"]:
            if rel["w"] > 0:
                full_name = api.get_node_by_id(rel["node2"]).get("name", "")
                
             
                if not full_name or ":" in full_name or full_name.isdigit():
                    continue
                
                
                # Application du split pour nettoyer les raffinements restants
                splitted = full_name.split(">")
                name2 = splitted[1] if len(splitted) > 1 else splitted[0]
                
                # On évite de rajouter des doublons ou des trucs techniques après split
                if name2.startswith(":") or name2 == node_name:
                    continue

                spécifiques.append({"specifique": name2, "poids": rel["w"]})
 
    spécifiques.sort(key=lambda x: x["poids"], reverse=True)
    return spécifiques

def inference_inductive(name1,relation, name2, reponse):
    all_types = api.get_relation_types()

    relation_id = next((rt["id"] for rt in all_types if rt["name"] == relation), None)

    nbInferencesInductives = 5
    maxSpecs = 15
    spec = getSpécifiques(name1)


    raw_spec = getSpécifiques(name1)
    if raw_spec is None:
        return None

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

    spec = list(unique_specs.values())[0:maxSpecs]
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
                        ],
                        "poids":math.sqrt(s["poids"] * poidsSpecCible),
                        "annotations": get_annotations_by_rel_id(relation_id),
                        "méthode": "Inférence inductive par r_hypo"
                                }) 
                if  (reponse==False and poidsSpecCible<0):
                    inferences.append({"réponse":reponse,"inférences": [
                        {"terme1":name1, "relation":"r_hypo", "terme2":z, "poids":s["poids"]},
                        {"terme1":z,"relation":"not "+relation,"terme2":name2,"poids":poidsSpecCible}
                        ],
                         "poids":-math.sqrt(s["poids"] * abs(poidsSpecCible)),
                        "annotations": get_annotations_by_rel_id(relation_id),
                        "méthode": "Inférence inductive par r_hypo"})
            if len(inferences)>=nbInferencesInductives: return inferences
        return inferences
    else:
        nbvraies = 0
        nbfaux = 0
        for s in spec:
            z = s["specifique"]
            poidsSpecCible = relation_weight_between_terms(z,relation,name2)
            if (poidsSpecCible!=None):
                if (poidsSpecCible>0):
                    nbvraies+=1
                    inferences.append({"réponse":reponse,"inférences": [
                        {"terme1":name1, "relation":"r_hypo", "terme2":z, "poids":s["poids"]},
                        {"terme1":z,"relation":relation,"terme2":name2,"poids":poidsSpecCible}
                        ],
                        "poids":math.sqrt(s["poids"] * abs(poidsSpecCible)),
                        "annotations": get_annotations_by_rel_id(relation_id),
                        "méthode": "Inférence inductive par r_hypo"})
                else:
                    nbfaux+=1
                    inferences.append({"réponse":reponse,"inférences": [
                        {"terme1":name1, "relation":"r_hypo", "terme2":z, "poids":s["poids"]},
                        {"terme1":z,"relation":"not "+relation,"terme2":name2,"poids":poidsSpecCible}
                        ],
                        "poids":-math.sqrt(s["poids"] * abs(poidsSpecCible)),
                        "annotations": get_annotations_by_rel_id(relation_id),
                        "méthode": "Inférence inductive par r_hypo"})
                
        decision = nbvraies>nbfaux
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
    

def infer_on_lemma(name1,relation,name2,reponse,fonction):
    infBase = fonction(name1,relation,name2,reponse)
    if (infBase!=None and len(infBase)>0): return infBase

    lemmaName1 = get_lemmas(name1)  
    lemmaName2 = get_lemmas(name2)

    for z in lemmaName1:            
        for zz in lemmaName2:
            reponseLem = resultatInferenceDirecte(z["lemma"],relation,zz["lemma"])

            inflem = fonction(z["lemma"],relation,zz["lemma"],reponseLem)
            if inflem and len(inflem)>0:
                for zzz in inflem:

                    if name1!=z["lemma"]: zzz["inférences"].insert(0,{"terme1":name1,"relation":"r_lemma","terme2":z["lemma"],"poids":z["poids"]})
                    if name2!=zz["lemma"]: zzz["inférences"].append({"terme1":name2,"relation":"r_lemma","terme2":zz["lemma"],"poids":zz["poids"]})
                return inflem
def printInferencesList(retourInf):
    listeInf = retourInf["inférences"]
    reponseBool = retourInf["réponse"]
    
    if len(listeInf) > 1 and listeInf[-1]["relation"] in ['r_raff_inv', 'r_lemma_inv']:
        step_efficace = listeInf[-2]
    else:
        step_efficace = listeInf[-1]
            
    main_rel = step_efficace["relation"]
    
    if not reponseBool:
        if not main_rel.startswith("not "):
            main_rel = "not " + main_rel
    else:
        main_rel = main_rel.replace("not ", "")

    t1 = listeInf[0]["terme1"]
    t2 = listeInf[-1]["terme2"]

    stri = f"{t1} ({main_rel}) {t2} "
    stri += "oui | " if reponseBool else "non | "
    
    steps_str = []
    for inf in listeInf:
        rel = inf["relation"]
        
     
        if inf.get("poids") is not None and inf["poids"] < 0:
            if not rel.startswith("not "):
                rel = "not " + rel
                
        steps_str.append(f"{inf['terme1']} {rel} {inf['terme2']}")
    
    stri += "  &  ".join(steps_str)
    stri += f"\n   -> Poids:{retourInf['poids']:.4f} | Méthode: {retourInf['méthode']}"
    if retourInf.get("annotations"):
        stri += " | Annotations: " + " ".join([f"{a[0]}" for a in retourInf["annotations"]])
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
    print(f"----------Inférences par expansion synonymique double de {name1} --({relation_name})--> {name2}----------sachant que {res_inf_directe}\n")
    if not rafs1: rafs1 = [{"name": name1, "id": api.get_node_id_by_name(name1)}]
    if not rafs2: rafs2 = [{"name": name2, "id": api.get_node_id_by_name(name2)}]

    results = []

    for r1 in rafs1:
        syns1 = api.get_top_synonyms(r1["id"], limit=4) 
        # On ajoute le terme lui-même à la liste pour tester Terme1 -> Syn(Terme2)
        syns1.append({"id": r1["id"], "name": r1["name"], "w": 100}) # Poids arbitraire max pour le mot lui-même

        for r2 in rafs2:
            syns2 = api.get_top_synonyms(r2["id"], limit=4)
            syns2.append({"id": r2["id"], "name": r2["name"], "w": 100})

            for s1 in syns1:
                for s2 in syns2:
                    if s1["id"] == r1["id"] and s2["id"] == r2["id"]: continue

                    res = api.get_relations_from_to_by_id(s1["id"], s2["id"], types_ids=relation_id)
                    
                    if res and res.get("relations"):
                        for rel in res["relations"]:
                            if (rel["w"] > 0 and res_inf_directe) or (rel["w"] < 0 and res_inf_directe == False) or (res_inf_directe is None):
                                if res_inf_directe is not None:
                                    score = math.pow(s1["w"] * abs(rel["w"]) * s2["w"], 1/3)
                                elif rel["w"] > 0:
                                    score = math.pow(s1["w"] * rel["w"] * s2["w"], 1/3)
                                else:
                                    score = -math.pow(s1["w"] * abs(rel["w"]) * s2["w"], 1/3)
                                
                                annotations = get_annotations_by_rel_id(rel["id"])
                                
                                results.append({
                                    "terme1": r1["name"],
                                    "relation": f"{relation_name} (via {s1['name']} et {s2['name']})",
                                    "terme2": r2["name"],
                                    "poids": score,
                                    "annotations": annotations,
                                    "méthode": "Expansion synonymique double"
                                })
    results.sort(key=lambda x: x["poids"], reverse=True)
    return results[:10]
            
def inference_transitive(name1, relation_name, name2, res_inf_directe=None, rafs1=None, rafs2=None):
    all_types = api.get_relation_types()

    relation_id = next((rt["id"] for rt in all_types if rt["name"] == relation_name), None)

    transitive_relations_ids = [6, 8, 9, 15, 41, 42, 52, 57, 61, 73, 74, 83, 109, 111, 112, 124, 125, 151]
    if not rafs1: rafs1 = [{"name": name1, "id": api.get_node_id_by_name(name1)}]
    if not rafs2: rafs2 = [{"name": name2, "id": api.get_node_id_by_name(name2)}]

    if relation_id in transitive_relations_ids:
        res = []
        for r1 in rafs1:
            resultats_api = api.get_relations_from_by_id(r1["id"], types_ids=relation_id)
            relations_brutes = resultats_api.get("relations", [])
            
            relations_propres = [rel for rel in relations_brutes if isinstance(rel, dict)]
            
            relations_triees = sorted(relations_propres, key=lambda x: x.get("w", 0), reverse=True)

            relations_intermediaires = relations_triees[:5]
            
            for r2 in rafs2:
                for rel_inter in relations_intermediaires:
                    node_intermediaire = rel_inter["node2"]
                    
                    resultats_api_2 = api.get_relations_from_to_by_id(node_intermediaire, r2["id"], types_ids=relation_id)
                    relations_finales = resultats_api_2.get("relations", [])
                    
                    if res_inf_directe is not None:
                        if res_inf_directe: 
                            relations_finales = [rel for rel in relations_finales if rel["w"] > 0]
                        else: 
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
                                
                                try:
                                    name_intermédiaire = api.get_node_by_id(node_intermediaire).get("name", "Inconnu")
                                except:
                                    continue
                                    
                                annotations = get_annotations_by_rel_id(rel_finale["id"])
                                res.append({"réponse":None if w2==None else w2>0,
                                    "inférences": [
                                        {"terme1":r1["name"], "relation":relation_name, "terme2":name_intermédiaire, "poids":w1},
                                        {"terme1":name_intermédiaire,"relation":relation_name,"terme2":r2["name"],"poids":w2}
                                    ],
                                    "poids":poids_final,
                                    "annotations": annotations,
                                    "méthode": "Inférence transitive"})

        return res[:10] 
        
    return []


def infer_parallel(name1, relation, name2, max_workers=10):
    all_types = api.get_relation_types()
    relation_id = next((rt["id"] for rt in all_types if rt["name"] == relation), None)
    if not relation_id: return []

    print(f"--- Recherche exhaustive : {name1} --({relation})--> {name2} ---")
    
    def prepare_refs(word):
        unique_nodes = {}
        lemmes = get_lemmas(word) or [{"lemma": word, "poids": 100}]
        for z in lemmes:
            l_name = z["lemma"]
            l_id = api.get_node_id_by_name(l_name)
            if l_id:
                path = []
                if l_name.lower() != word.lower():
                    path.append({"terme1": word, "relation": "r_lemma", "terme2": l_name, "poids": z["poids"]})
                
                if l_id not in unique_nodes:
                    unique_nodes[l_id] = {"id": l_id, "name": l_name, "path": path}
                
                for raf in get_refinements(l_name):
                    if raf['id'] not in unique_nodes:
                        new_path = list(path) + [{"terme1": l_name, "relation": "r_raff", "terme2": raf['name'], "poids": 100}]
                        unique_nodes[raf['id']] = {"id": raf['id'], "name": raf['name'], "path": new_path}
        return list(unique_nodes.values())

    rafs1, rafs2 = prepare_refs(name1), prepare_refs(name2)
    res_inf_directe = resultatInferenceDirecte(name1, relation, name2)
    
    vague_prioritaire, vague_secondaire = [], []
    for r1 in rafs1:
        for r2 in rafs2:
            w = relation_weight_between_terms(r1['name'], relation, r2['name'])
            pair = (r1, r2, w)
            if w is not None: vague_prioritaire.append(pair)
            else: vague_secondaire.append(pair)

    def process_pair(r1, r2, weight, relation, global_rep):
    
        if global_rep is not None and weight is not None:
            local_rep = (weight > 0)
            if local_rep != global_rep:
                return [] 

        n1, n2 = r1['name'], r2['name']
        path1 = r1.get('path', [])
        path2 = r2.get('path', [])
        
        path2_inv = []
        for step in reversed(path2):
            path2_inv.append({
                "terme1": step["terme2"], 
                "relation": step["relation"] + "_inv", 
                "terme2": step["terme1"], 
                "poids": step["poids"]
            })

        pair_results = []
        
        local_rep = global_rep if global_rep is not None else ((weight > 0) if weight is not None else None)
        
        def add_transformation_steps(inf_list):
            for res in inf_list:
                res["inférences"] = path1 + res["inférences"] + path2_inv
            return inf_list

        #Inférence directe locale
        if weight is not None:
            direct_res = [{
                "réponse": weight > 0,
                "inférences": [{"terme1": n1, "relation": relation, "terme2": n2, "poids": weight}],
                "poids": weight,
                "annotations": get_annotations_between_terms(n1, relation, n2) or [],
                "méthode": "Inférence directe"
            }]
            pair_results.extend(add_transformation_steps(direct_res))
        
        #stratégies indirectes
        for strategy_func in [inference_deductive, inference_inductive, inference_transitive]:
            try:
                res_strat = strategy_func(n1, relation, n2, local_rep)
                if res_strat:
                    pair_results.extend(add_transformation_steps(res_strat))
            except Exception: pass
            
        return pair_results

    def execute_wave(pairs):
        wave_results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(process_pair, p[0], p[1], p[2], relation, res_inf_directe): p for p in pairs}
            for future in as_completed(futures):
                res = future.result()
                if res: wave_results.extend(res)
        return wave_results

    
    results = execute_wave(vague_prioritaire)
    results.extend(execute_wave(vague_secondaire))

    #dédoublonnage
    unique_results = []
    seen = set()
    for r in results:
        sig = "|".join([f"{i['terme1']}-{i['relation']}-{i['terme2']}" for i in r['inférences']])
        if sig not in seen:
            unique_results.append(r)
            seen.add(sig)





    annotation_map = {
            "peu pertinent": -0.2,
            "pertinent": 0.3,
            "possible": 0.15,
            "très pertinent": 0.3,
            "contrastif" : 0.4,
            "non spécifique": -0.2
        }
    
    processed_results = []
    seen = set()

    for r in results:
        #dédoublonnage(éviter les doublons de threads)
        sig = "|".join([f"{i['terme1']}-{i['relation']}-{i['terme2']}" for i in r['inférences']])
        if sig in seen: continue
        seen.add(sig)

        if any(step['relation'] in ['r_lemma', 'r_lemma_inv'] for step in r['inférences']):
            r['poids'] -= 0.5
        if any(step['relation'] in ['r_raff', 'r_raff_inv'] for step in r['inférences']):
            r['poids'] -= 0.5

        if r.get('annotations'):
            for ann, _ in r['annotations']:
                r['poids'] += annotation_map.get(ann.lower(), 0.0)

        processed_results.append(r)

    if not processed_results: return []

    #normalisation poids
    max_abs = max(abs(r['poids']) for r in processed_results)
    if max_abs > 0:
        for r in processed_results:
            r['poids'] = abs(r['poids']) / max_abs

    #Sélection 2 meilleurs résultats par stratégie
    final_selection = []
    strat_counters = {}
    
    processed_results.sort(key=lambda x: x['poids'], reverse=True)

    for r in processed_results:
        strat = r['méthode']
        strat_counters[strat] = strat_counters.get(strat, 0) + 1
        
        if strat_counters[strat] <= 2:
            final_selection.append(r)

    return sorted(final_selection, key=lambda x: x['poids'], reverse=True)










if __name__ == "__main__":
    query = interface.messageDépart()

    if len(query) == 2:
            name, name2 = query
            if (name=="R"):
                print_refinements(name2)
            elif (name=="L"):
                print_lemmas(name2)

                
    elif len(query) == 3:
        name, relation, name2 = query
        '''for inf in inferences:
            print(f"Poids: {inf["poids"]} : {inf["terme1"]} --({inf["relation"]})--> {inf["terme2"]} Méthode: {inf["méthode"]}, Annotations: {inf["annotations"]}")'''
        already_printed = False
        for z in infer_parallel(name,relation,name2):
            if not already_printed:
                print("\n")
                match z["réponse"]:
                    case True:
                            print("Justifications en partant du principe que la relation est vraie :")
                    case False:
                            print("Justifications en partant du principe que la relation est fausse :")
                    case _:
                        print("Justifications positives ou négatives en partant du principe que la relation est indéterminée :")
                already_printed = True
                    
            printInferencesList(z)  
            print("\n")

    else:
        interface.messageErreur()