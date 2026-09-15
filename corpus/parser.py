import re
import urllib.request
import json

def get_random_wikipedia_text():
    """Récupère le texte d'un article Wikipédia en français au hasard via l'API."""
    url = "https://fr.wikipedia.org/w/api.php?action=query&format=json&generator=random&grnnamespace=0&prop=extracts&explaintext=1"
    
    # Création d'une requête personnalisée avec un User-Agent
    req = urllib.request.Request(
        url,
        headers={
            'User-Agent': 'TestRegexPython/1.0 (https://fr.wikipedia.org/wiki/Utilisateur:Test)'
        }
    )
    
    try:
        # On utilise req au lieu de url directement
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            # Extraction du titre et du texte de la réponse JSON
            pages = data['query']['pages']
            page_id = list(pages.keys())[0]
            titre = pages[page_id].get('title', 'Titre inconnu')
            texte = pages[page_id].get('extract', '')
            
            return titre, texte
    except Exception as e:
        print(f"Erreur lors de la récupération : {e}")
        return None, ""

# 1. On récupère la page aléatoire
titre_article, texte_article = get_random_wikipedia_text()

if not texte_article:
    print("Impossible de récupérer l'article. Fin du programme.")
    exit()

print(f"=== Analyse de l'article : {titre_article} ===\n")

# 2. Compilation de la regex
pattern = re.compile(r"\b([a-zA-ZÀ-ÿ]+)\s+(de\s+la|des|du|de|d['’])\s*([a-zA-ZÀ-ÿ]+)\b", re.IGNORECASE)

# 3. Recherche dans le texte de l'article
resultats = pattern.findall(texte_article)

# 4. Affichage des résultats
if resultats:
    for match in resultats:
        mot_A, particule, mot_B = match
        print(f"[{mot_A}] + [{particule}] + [{mot_B}]")
    print(f"\nTotal trouvé : {len(resultats)} syntagmes.")
else:
    print("Aucun syntagme correspondant trouvé dans cet article.")