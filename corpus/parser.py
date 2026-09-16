import spacy
from spacy.matcher import Matcher
from spacy.util import filter_spans

# Initialisation globale (à ne faire qu'une seule fois au lancement de votre programme)
nlp = spacy.load("fr_core_news_md")
matcher = Matcher(nlp.vocab)

articles_autorises = ["le", "la", "l'", "l’", "les", "un", "une", "des"]
prepositions_autorisees = ["de", "d'", "d’", "d", "du", "des"]

# Le motif commence DIRECTEMENT par le mot A, on a supprimé le déterminant initial
pattern = [
    {"POS": {"IN": ["NOUN", "PROPN"]}},                        # OBLIGATOIRE : Mot A 
    {"LOWER": {"IN": prepositions_autorisees}},                # OBLIGATOIRE : Préposition
    {"LOWER": {"IN": articles_autorises}, "OP": "?"},          # Optionnel : déterminant
    {"POS": {"IN": ["NOUN", "PROPN"]}}                         # OBLIGATOIRE : Mot B (1 seul et unique mot !)
]

matcher.add("SYNTAGME_ULTRA_STRICT", [pattern])

def extraire_relations_genitives(texte):
    # Cela empêche spaCy de confondre les verbes en début de ligne avec des Noms Propres
    texte_nettoye = texte.lower()
    
    doc = nlp(texte_nettoye)
    matches = matcher(doc)
    
    spans = filter_spans([doc[start:end] for match_id, start, end in matches])
    resultats = [span.text for span in spans]
    
    return resultats

# Liste de vos exemples pour le test
texte = """

Plus il s'amenuise, plus les Etats-Unis ont de la peine à attirer les flux nécessaires au financement du déficit de leur compte-courant" et plus le dollar est sous pression.
Sous la flamme rouge du dernier kilomètre, Linus Gerdemann ( Allemagne, T-Mobile) a toujours 35 secondes sur Inigo Landaluze ( Espagne, Euskaltel-Euskadi).
Timoléon (1794), avec des chœurs mis en musique par Étienne Nicolas Méhul, parut attaquer Robespierre dans le personnage de l'ambitieux Timophane que ses amis veulent maladroitement couronner au milieu de l'assemblée du peuple.
Le grand écart entre les discours et les actes doit cesser, si l'on veut que le Grenelle soit autre chose qu'une opération de communication et si le gouvernement ne veut pas perdre tout crédit sur sa démarche", écrivent-ils.
Ces derniers doivent être effectués par un entrepreneur ayant les licences appropriées auprès de la Régie du bâtiment du Québec.
2378	Les 39 réseaux de surveillance de la qualité de lair répartis sur lensemble du territoire, regroupent lEtat, les collectivités locales, les industriels et les associations de protection de lenvironnement.
2379	En plus d'un coup droit aux allures de coup de fusil (37 coups gagnants), d'un service très efficace (77% de points remportés derrière sa première balle), le joueur ibérique mettait en exergue d'autres qualités, insoupçonnées jusqu'alors.
2380	Un zébu est attaché, très court, à la barrière de bambou.
2381	Vendredi, après sept jours d'un procès à huis-clos, David Rufer, 21 ans, dont la présence sur les lieux du drame n'avait pas été formellement établie par l'enquête, a été acquitté bien qu'une peine de 18 ans ait été requise contre lui.
2382	Téléfilm Canada augmentera la part qu'elle accorde aux projets sélectionnés par jury, au détriment des enveloppes basées sur la performance au guichet.
2383	Des rumeurs circulent sur Internet à l'effet que le groupe Heaven and Hell, composé de Ronnie James Dio (photo), Tony Iommi, Geezer Butler et Vinny Appice, donnent des spectacles au Québec d'ici quelques mois.
2384	Admis dans la réserve en 1916, il se retire à Pau.
2385	Impossible, alors, d'éluder la question pécuniaire.
2386	Mais il suffit de se pencher sur la santé des commerces voisins pour comprendre que ce premier pas en pays francophone est un succès.
2387	Des dizaines de vedettes ont défilé dimanche après-midi sur le tapis rouge à l'entrée du théâtre Kodak à Hollywood, l'écrin des 78e Oscars entouré de mesures de sécurité draconiennes.
2388	Il sinscrit, plus précisément, dans laxe prioritaire se rapportant à la "configuration des Etats et des régimes politiques" et aux "procédures de ré-invention de lEtat : dispositifs, normes et institutions".
2389	Dans les liens hypertexte :
2390	Ce CD-Rom est entièrement gratuit pour les adhérents de l'association quelquesoit le nombre de dessins 3vues.
2391	Il s'y trouvait une statue de bois peint de la Vierge datant du XVIième.
2392	Jean-Daniel Fekete et Nicole Dufournaud, Document Numérique, numéro spécial " Les documents anciens ", (Hermès), vol.3, 1-2, 1999, pp. 117-134.
2393	Le boeing kenyan 737-800 avait décollé du Cameroun pour rejoindre la capitale du Kenya, Nairobi.
2394	Icône de détail Article détaillé : Match de football France - Brésil (1998).
2395	Les ventes de Mercedes-Benz ont quant à elles reculé de 37% et celles de BMW ont diminué de 8,7%.
2396	En effet, de Gouye Dioulancar à Ndiaga Samb, en passant par Ndiayène, Ngounou et Ndiandia, beaucoup de maisons se sont effrondrées sous l'effet de la mer qui, selon les habitants, a avancé de vingt mètres.

"""

syntagmes_trouves = extraire_relations_genitives(texte)

print("=== Syntagmes parfaits extraits ===")
for s in syntagmes_trouves:
    print(f"[{s}]")