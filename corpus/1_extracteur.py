import spacy
import json
import os
from spacy.matcher import Matcher
from spacy.util import filter_spans

# Configuration des chemins
DOSSIER_DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(DOSSIER_DATA, exist_ok=True)
FICHIER_SORTIE = os.path.join(DOSSIER_DATA, "1_syntagmes_bruts.json")

# Initialisation spaCy
nlp = spacy.load("fr_core_news_md")
matcher = Matcher(nlp.vocab)

articles_autorises = ["le", "la", "l'", "l'", "les", "un", "une", "des"]
prepositions_autorisees = ["de", "d'", "d'", "d", "du", "des"]

# Motif ultra-strict
pattern = [
    {"POS": {"IN": ["NOUN", "PROPN"]}},
    {"LOWER": {"IN": prepositions_autorisees}},
    {"LOWER": {"IN": articles_autorises}, "OP": "?"},
    {"POS": {"IN": ["NOUN", "PROPN"]}}
]
matcher.add("SYNTAGME_ULTRA_STRICT", [pattern])

def generer_dataset_brut(texte):
    print("Analyse du texte avec spaCy...")
    doc = nlp(texte.lower())
    matches = matcher(doc)
    spans = filter_spans([doc[start:end] for match_id, start, end in matches])
    
    dataset_brut = []
    mots_uniques = set() # Pour éviter les doublons parfaits dans le dataset
    
    for span in spans:
        texte_complet = span.text
        # Découpage propre de A et B
        mot_a = span[0].text
        mot_b = span[-1].text
        
        # Dédoublonnage : on ne garde qu'une seule fois "match de football"
        if texte_complet not in mots_uniques:
            mots_uniques.add(texte_complet)
            dataset_brut.append({
                "texte_complet": texte_complet,
                "A": mot_a,
                "B": mot_b
            })
            
    # Sauvegarde en JSON
    with open(FICHIER_SORTIE, 'w', encoding='utf-8') as f:
        json.dump(dataset_brut, f, ensure_ascii=False, indent=4)
        
    print(f"Extraction terminée : {len(dataset_brut)} syntagmes uniques sauvegardés dans {FICHIER_SORTIE}")

# --- TEST ---
if __name__ == "__main__":
    texte_leipzig = """



    """
    generer_dataset_brut(texte_leipzig)