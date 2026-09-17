import sys
import os
import json
import time
import hashlib

# Configuration des chemins
CHEMIN_CORPUS = os.path.dirname(os.path.abspath(__file__))
CHEMIN_MODEL = os.path.join(CHEMIN_CORPUS, "..", "model")
sys.path.append(CHEMIN_MODEL)

from api import JDM_API

DOSSIER_DATA = os.path.join(CHEMIN_CORPUS, "data")
FICHIER_ENTREE = os.path.join(DOSSIER_DATA, "1_syntagmes_bruts.json")
FICHIER_SORTIE = os.path.join(DOSSIER_DATA, "2_syntagmes_valides.json")

def valider_syntagmes():
    if not os.path.exists(FICHIER_ENTREE):
        print(f"Erreur : Le fichier {FICHIER_ENTREE} n'existe pas. Lancez 1_extracteur.py d'abord.")
        return

    # 1. Chargement des données
    with open(FICHIER_ENTREE, 'r', encoding='utf-8') as f:
        dataset_brut = json.load(f)
        
    print(f"Chargement de {len(dataset_brut)} syntagmes à vérifier.")
    
    # 2. Récupération de tous les mots uniques (A et B confondus)
    mots_a_verifier = set()
    for item in dataset_brut:
        mots_a_verifier.add(item["A"])
        mots_a_verifier.add(item["B"])
        
    print(f"Total de mots uniques à valider dans JDM : {len(mots_a_verifier)}")
    
    # 3. Interrogation de JDM avec Smart Sleep
    jdm = JDM_API()
    mots_valides_jdm = set()
    
    for i, mot in enumerate(mots_a_verifier, 1):
        print(f"[{i}/{len(mots_a_verifier)}] '{mot}'...", end=" ")
        
        # Anticipation du cache
        url = f"{jdm.base_url}/node_by_name/{mot}"
        md5_string = hashlib.md5(url.encode()).hexdigest()
        chemin_cache = os.path.join(CHEMIN_MODEL, "cache", "nodeByName", md5_string + ".json")
        est_en_cache = os.path.isfile(chemin_cache)
        
        try:
            node_id = jdm.get_node_id_by_name(mot)
            if node_id:
                mots_valides_jdm.add(mot)
                print(f"✅ (ID: {node_id})")
            else:
                print("❌")
                
            if not est_en_cache:
                time.sleep(1)
        except Exception as e:
            print(f"⚠️ Erreur")
            if not est_en_cache:
                time.sleep(1)
                
    # 4. Création du dataset validé
    dataset_valide = []
    for item in dataset_brut:
        # On ne garde le syntagme que si A ET B existent dans la base
        if item["A"] in mots_valides_jdm and item["B"] in mots_valides_jdm:
            dataset_valide.append(item)
            
    # 5. Sauvegarde
    with open(FICHIER_SORTIE, 'w', encoding='utf-8') as f:
        json.dump(dataset_valide, f, ensure_ascii=False, indent=4)
        
    print(f"\n=== BILAN : {len(dataset_valide)}/{len(dataset_brut)} syntagmes validés et sauvegardés dans {FICHIER_SORTIE} ===")

# --- TEST ---
if __name__ == "__main__":
    valider_syntagmes()