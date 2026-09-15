import spacy
from spacy.matcher import Matcher
from spacy.util import filter_spans

# Chargement du modèle français
nlp = spacy.load("fr_core_news_md")
matcher = Matcher(nlp.vocab)

# Définition du motif flexible
pattern = [
    {"POS": "ADJ", "OP": "*"},                  # Optionnel : adjectif avant A (ex: "grand")
    {"POS": {"IN": ["NOUN", "PROPN"]}},         # Obligatoire : Mot A
    {"POS": "ADJ", "OP": "*"},                  # Optionnel : adjectif après A
    {"LOWER": {"IN": ["de", "d'", "d’", "d", "du", "des"]}}, # Obligatoire : Préposition
    {"POS": "DET", "OP": "?"},                  # Optionnel : la, l', un... (et le "le" caché dans "du")
    {"POS": "ADJ", "OP": "*"},                  # Optionnel : adjectif avant B
    {"POS": {"IN": ["NOUN", "PROPN"]}, "OP": "+"}, # Obligatoire : Mot B (1 ou plusieurs pour "Van Gogh")
    {"POS": {"IN": ["ADJ", "VERB"]}, "OP": "*"} # Optionnel : adjectif/participe passé après B (ex: "battu")
]

matcher.add("SYNTAGME_COMPLET", [pattern])

# Liste de vos exemples pour le test
texte = """
les nausées du stress
la paralysie de l'averse
l'effondrement de la délocalisation
le choc de la piqûre
la sournoiserie du politicien
cuillère de bois
la vin de France 
la café du Brésil
le restaurant de sushis
le film d’horreur
la peinture d’un paysage
la photo d’une famille 
la coque du bateau
l'écaille du poisson
tour de Pise
sahara d’Algérie 
travail de l’ouvrier
cours du professeur
travail du bois
ouverture de la porte 
clé d’ouverture
clé de la porte 
fusil du soldat
vélo du cycliste
brin d’herbe
minute d’attente 
avocat d’une femme battu
chef du groupe 
gâteau du pâtissier
"""

doc = nlp(texte)
matches = matcher(doc)

# ÉTAPE CRUCIALE : Filtrage des sous-chaînes
# spaCy trouve "la clé de la porte" ET "clé de la porte". 
# filter_spans permet de ne conserver que la séquence la plus longue et complète.
spans = [doc[start:end] for match_id, start, end in matches]
spans_filtres = filter_spans(spans)

for span in spans_filtres:
    print(f"[{span.text}]")
    
print("\nNombre de syntagmes complets trouvés :", len(spans_filtres))