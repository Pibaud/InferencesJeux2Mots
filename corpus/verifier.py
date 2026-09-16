import sys
import os
import time
import hashlib
import spacy

# 1. Gestion des chemins pour importer api.py depuis le dossier parent
chemin_corpus = os.path.dirname(os.path.abspath(__file__))
chemin_model = os.path.join(chemin_corpus, "..", "model")
sys.path.append(chemin_model)

from api import JDM_API
from parser import extraire_relations_genitives # Assurez-vous que le fichier s'appelle bien parser.py

# On réutilise spaCy juste pour séparer proprement le Mot A du Mot B
nlp = spacy.load("fr_core_news_md")

def filtrer_syntagmes_par_jdm(texte):
    # 1. Extraction brute via votre parser
    syntagmes_bruts = extraire_relations_genitives(texte)
    print(f"Trouvé {len(syntagmes_bruts)} syntagmes dans le texte.")
    
    jdm = JDM_API()
    mots_uniques = set()
    donnees_structurees = []
    
    # 2. Séparation de A et B 
    for syntagme in syntagmes_bruts:
        doc = nlp(syntagme)
        # Grâce à spaCy, "arc d'or" donne doc[-1] = "or" (et non "d'or").
        mot_A = doc[0].text
        mot_B = doc[-1].text 
        
        mots_uniques.add(mot_A)
        mots_uniques.add(mot_B)
        
        donnees_structurees.append({
            "texte_complet": syntagme,
            "A": mot_A,
            "B": mot_B
        })
        
    print(f"Dédoublonnage : {len(mots_uniques)} mots uniques à vérifier sur JDM.\n")
    
    # 3. Interrogation de JDM optimisée (Smart Sleep)
    mots_valides_jdm = set()
    
    for i, mot in enumerate(mots_uniques, 1):
        print(f"[{i}/{len(mots_uniques)}] Vérification de '{mot}'...", end=" ")
        
        # Astuce : on recrée la logique de votre api.py pour anticiper le cache
        url = f"{jdm.base_url}/node_by_name/{mot}"
        md5_string = hashlib.md5(url.encode()).hexdigest()
        chemin_cache = os.path.join("cache", "nodeByName", md5_string + ".json")
        est_en_cache = os.path.isfile(chemin_cache)
        
        try:
            # Appel à votre API
            node_id = jdm.get_node_id_by_name(mot)
            if node_id:
                mots_valides_jdm.add(mot)
                print(f"✅ (ID: {node_id})")
            else:
                print("❌ (Introuvable)")
                
            # On ne met en pause le script QUE si on a frappé le vrai serveur
            if not est_en_cache:
                time.sleep(1)
                
        except Exception as e:
            print(f"⚠️ Erreur API : {e}")
            if not est_en_cache:
                time.sleep(1)
                
    # 4. Reconstruction du jeu de données final
    syntagmes_finaux = []
    for data in donnees_structurees:
        if data["A"] in mots_valides_jdm and data["B"] in mots_valides_jdm:
            syntagmes_finaux.append(data["texte_complet"])
            
    print(f"\n=== BILAN : {len(syntagmes_finaux)}/{len(syntagmes_bruts)} syntagmes 100% valides dans JDM ===")
    return syntagmes_finaux


# --- TEST ---
if __name__ == "__main__":
    texte_leipzig = """
    Plus il s'amenuise, plus les Etats-Unis ont de la peine à attirer les flux...
    Icône de détail Article détaillé : Match de football France - Brésil (1998).
    Un zébu est attaché, très court, à la barrière de bambou.
    Il s'y trouvait une statue de bois peint de la Vierge datant du XVIième.
    """
    
    resultats = filtrer_syntagmes_par_jdm(texte_leipzig)
    for r in resultats:
        print(f"- {r}")