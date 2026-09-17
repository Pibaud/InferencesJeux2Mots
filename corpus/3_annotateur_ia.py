import os
import json
import time
from enum import Enum
from google import genai
from google.genai import types
from pydantic import BaseModel

CHEMIN_CORPUS = os.path.dirname(os.path.abspath(__file__))
DOSSIER_DATA = os.path.join(CHEMIN_CORPUS, "data")
FICHIER_ENTREE = os.path.join(DOSSIER_DATA, "2_syntagmes_valides.json")
FICHIER_SORTIE = os.path.join(DOSSIER_DATA, "3_syntagmes_annotes_ia.json")

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("Veuillez définir la variable d'environnement GEMINI_API_KEY.")

client = genai.Client(api_key=api_key)

# 1. Énumération stricte des types de relations JDM
class RelationJDM(str, Enum):
    HAS_CAUSATIF = "r_has_causatif"
    HAS_PROPERTY_1 = "r_has_property-1"
    OBJET_MATIERE = "r_objet>matiere"
    LIEU_ORIGINE = "r_lieu>origine"
    TOPIC = "r_topic"
    DEPICT = "r_depict"
    HOLO = "r_holo"
    LIEU = "r_lieu"
    PROCESSUS_AGENT = "r_processus_agent"
    PROCESSUS_PATIENT = "r_processus_patient"
    PROCESSUS_INSTR_1 = "r_processus>instr-1"
    OWN_1 = "r_own-1"
    QUANTIFICATEUR = "r_quantificateur"
    SOCIAL_TIE = "r_social_tie"
    PRODUCT_OF = "r_product_of"
    INCONNU = "inconnu"

# 2. Schéma Pydantic utilisant l'Enum
class SyntagmeAnnote(BaseModel):
    texte_complet: str
    A: str
    B: str
    relation: RelationJDM

SYSTEM_INSTRUCTION = """
Tu es un expert en linguistique, en traitement du langage naturel (TAL) et en sémantique française.
Ta tâche est de classifier la relation sémantique liant le terme A et le terme B dans un syntagme génitif.

Tu dois OBLIGATOIREMENT choisir l'une des étiquettes suivantes issues de la base JeuxDeMots :
- r_has_causatif : A est causé par B (ex: dégâts de la tempête, retard de la circulation)
- r_has_property-1 : A est une propriété de B (ex: sournoiserie du politicien)
- r_objet>matiere : A est composé de B (ex: cuillère de bois, trône de fer)
- r_lieu>origine : A est originaire de B (ex: vin de France, café du Brésil)
- r_topic : A a pour thème B (ex: restaurant de sushis, film d'horreur)
- r_depict : A est une représentation de B (ex: peinture d'un paysage, photo d'une famille)
- r_holo : A fait partie de B (ex: coque du bateau, écaille du poisson)
- r_lieu : A peut avoir pour lieu B (ex: tour de Pise, sahara d'Algérie)
- r_processus_agent : A est l'action dont l'acteur est B (ex: travail de l'ouvrier)
- r_processus_patient : A est l'action subie par B (ex: travail du bois, ouverture de la porte)
- r_processus>instr-1 : A est l'instrument de l'action (ex: clé d'ouverture, clé de la porte)
- r_own-1 : A est possédé par B (ex: fusil du soldat, vélo du cycliste)
- r_quantificateur : A sert de mesure à B (ex: brin d'herbe, minute d'attente)
- r_social_tie : A a un rôle social vis-à-vis de B (ex: avocat d'une femme, chef du groupe)
- r_product_of : A est produit par B (ex: portrait de Van Gogh, gâteau du pâtissier)
- inconnu : Si aucune de ces relations ne s'applique clairement.

Je vais te fournir une liste de syntagmes au format JSON. 
Analyse chaque syntagme, déduis la relation, et renvoie OBLIGATOIREMENT la liste complète mise à jour avec le champ 'relation' rempli.
"""

LABELS_VALIDES = {rel.value for rel in RelationJDM}

def annoter_dataset():
    if not os.path.exists(FICHIER_ENTREE):
        print(f"Erreur : {FICHIER_ENTREE} introuvable.")
        return

    with open(FICHIER_ENTREE, 'r', encoding='utf-8') as f:
        dataset_valide = json.load(f)

    dataset_annote = []
    if os.path.exists(FICHIER_SORTIE):
        with open(FICHIER_SORTIE, 'r', encoding='utf-8') as f:
            dataset_annote = json.load(f)
            
    index_depart = len(dataset_annote)
    if index_depart >= len(dataset_valide):
        print("Le dataset est déjà entièrement annoté !")
        return
        
    print(f"Reprise de l'annotation à partir de l'index {index_depart}/{len(dataset_valide)}...")

    nom_modele = "gemini-3.8-flash"
    
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTION,
        response_mime_type="application/json",
        response_schema=list[SyntagmeAnnote],
        temperature=0.0
    )

    TAILLE_LOT = 50 
    
    MAX_RETRIES = 5

    for i in range(index_depart, len(dataset_valide), TAILLE_LOT):
        lot = dataset_valide[i:i+TAILLE_LOT]
        prompt_json = json.dumps(lot, ensure_ascii=False)
        
        print(f"Envoi du lot {i} à {i+len(lot)-1} à {nom_modele}...")
        
        succes = False
        for tentative in range(1, MAX_RETRIES + 1):
            try:
                chat = client.chats.create(
                    model=nom_modele,
                    config=config
                )
                reponse = chat.send_message(prompt_json)
                donnees_brutes = json.loads(reponse.text)
                
                lot_verifie = []
                for item in donnees_brutes:
                    objet_valide = SyntagmeAnnote(**item)
                    if objet_valide.relation.value not in LABELS_VALIDES:
                        raise ValueError(f"Label non reconnu : {objet_valide.relation}")
                    lot_verifie.append(objet_valide.model_dump())
                
                dataset_annote.extend(lot_verifie)
                
                with open(FICHIER_SORTIE, 'w', encoding='utf-8') as f:
                    json.dump(dataset_annote, f, ensure_ascii=False, indent=4)
                    
                time.sleep(15)  # Respect du quota 5 RPM
                succes = True
                break  # Sortie de la boucle de retry
                
            except Exception as e:
                msg = str(e)
                if "UNAVAILABLE" in msg or "503" in msg:
                    delai = 15 * tentative  # 15s, 30s, 45s...
                    print(f"Serveurs surchargés (tentative {tentative}/{MAX_RETRIES}). Pause de {delai}s...")
                    time.sleep(delai)
                else:
                    print(f"Erreur critique sur le lot {i} : {e}")
                    break

        if not succes:
            print("Échec définitif du lot. Relance ultérieure nécessaire.")
            break

    print(f"\n=== FIN : {len(dataset_annote)} syntagmes annotés dans {FICHIER_SORTIE} ===")

if __name__ == "__main__":
    annoter_dataset()