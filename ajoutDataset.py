import json

def traiter_et_ajouter_json(chemin_base, chemin_ajout):
    # Chargement des deux fichiers
    with open(chemin_base, 'r', encoding='utf-8') as f:
        base = json.load(f)
    with open(chemin_ajout, 'r', encoding='utf-8') as f:
        ajout = json.load(f)

    # Indexation de la base par relation humaine
    index_base = {}
    for item in base:
        relation = item["relation_humaine"]
        if relation not in index_base:
            index_base[relation] = {"mots_a": set(), "mots_b": set()}
        
        index_base[relation]["mots_a"].add(item["mot_a"])
        index_base[relation]["mots_b"].add(item["mot_b"])

    # Vérification et ajout
    expressions_problematiques = []
    compteur_ajouts = 0
    
    for item in ajout:
        relation = item["relation_humaine"]
        mot_a = item["mot_a"]
        mot_b = item["mot_b"]
        
        conflit_a = False
        conflit_b = False
        
        if relation in index_base:
            conflit_a = mot_a in index_base[relation]["mots_a"]
            conflit_b = mot_b in index_base[relation]["mots_b"]
            
        if conflit_a or conflit_b:
            raisons = []
            if conflit_a:
                raisons.append(f"mot_a '{mot_a}' déjà utilisé")
            if conflit_b:
                raisons.append(f"mot_b '{mot_b}' déjà utilisé")
                
            expressions_problematiques.append({
                "texte_complet": item["texte_complet"],
                "relation_humaine": relation,
                "details": " et ".join(raisons)
            })
        else:
            # Aucun conflit : on ajoute à la liste de base
            base.append(item)
            compteur_ajouts += 1
            
            # On met à jour l'index immédiatement pour éviter les doublons internes au fichier d'ajout
            if relation not in index_base:
                index_base[relation] = {"mots_a": set(), "mots_b": set()}
            index_base[relation]["mots_a"].add(mot_a)
            index_base[relation]["mots_b"].add(mot_b)

    # Sauvegarde du fichier mis à jour (écrase l'ancien fichier de base)
    with open(chemin_base, 'w', encoding='utf-8') as f:
        json.dump(base, f, ensure_ascii=False, indent=4)

    return expressions_problematiques, compteur_ajouts

# Exemple d'utilisation :
if __name__ == "__main__":
    problemes, ajouts = traiter_et_ajouter_json("vecteurs/dataset.json", "vecteurs/elouandajouts.json")
    
    print(f"[{ajouts} syntagmes ajoutés avec succès]")
    for p in problemes:
        print(f"[CONFLIT REJETÉ] {p['texte_complet']} ({p['relation_humaine']}) -> {p['details']}")