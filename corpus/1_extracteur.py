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

Jules Le Ray n'a que dix-huit ans quand il peint ce portrait de Moret. La peinture sur le chevalet représente le champ du "Roulage au Pouldu", le cheval y est absent. L'artiste a continué toute sa vie à peindre en amateur. Cette œuvre permet d'évoquer de manière pédagogique le style lié à l'Ecole de Pont-Aven et d'exposer le travail d'un peintre connu.

David est une sculpture de la Renaissance réalisée par Michel-Ange entre 1501 et 1504. Elle mesure 5,17 mètres de hauteur (sans le piédestal)[a] et elle est tirée d'un bloc de marbre blanc de Carrare qui avait été laissé à l'abandon après l'échec d'autres sculpteurs. Michel-Ange a su tirer parti de l'étroitesse du bloc de marbre et contourner un de ses défauts (une brèche dans laquelle il a creusé l'espace entre le bras droit et le torse). L'œuvre représente David, une fronde (lanière de cuir servant de lance-pierre) à la main, juste avant son combat contre le géant Goliath.

Initialement placé devant le palazzo Vecchio pour symboliser la détermination d'une jeune république face au tyran, l'original est, depuis 1873, exposé dans la Galleria dell'Accademia de Florence. Le David que l'on peut désormais voir devant la façade du palazzo Vecchio est une réplique installée en 1910.

La musique est un art et une activité culturelle consistant à combiner sons et silences au cours du temps. Les paramètres principaux sont le rythme (façon de combiner les sons dans le temps), la hauteur (combinaison dans les fréquences), les nuances et le timbre ainsi que la mélodie (ce qui rend agréable l'écoute). Elle est aujourd'hui[Quand ?] considérée[Par qui ?] comme une forme de poésie moderne.

La musique donne lieu à des créations (des œuvres d'art créées par des compositeurs), des représentations. Elle utilise généralement certaines règles ou systèmes de composition, des plus simples aux plus complexes (souvent les notes de musique, les gammes et autres). Elle peut utiliser divers objets, le corps, mais aussi des instruments de musique spécialement conçus, et de plus en plus tous les sons (concrets, de synthèses, abstraits…).

La musique existe dans toutes les sociétés humaines, depuis la Préhistoire, probablement avant même l'époque de ses premières traces historiques. Elle est à la fois forme d'expression individuelle (notamment l'expression des sentiments), source de rassemblement collectif et de plaisir (fête, chant, danse) et symbole d'une communauté culturelle, nationale (hymne national, musique traditionnelle, musique folklorique, musique militaire) ou spirituelle (musique religieuse). Il n'est pas de civilisation qui, tôt ou tard, n'ait développé son propre système musical ou n'en ait adopté un en l'adaptant à ses nécessités et à ses goûts.

Comme celui de « musée », le terme de « musique » dérive du grec ancien Μοῦσαι / Moûsai (« Muses »). Le concept occidental de musique est donc une allusion aux sciences et aux arts rappelant l'idée d'une chose parfaite, agréable et bien ordonnée.

compositeur de musique baroque.

L'architecture est l'art majeur de concevoir des espaces et de bâtir des édifices, en respectant des règles de construction empiriques ou scientifiques, ainsi que des concepts esthétiques, classiques ou nouveaux, de forme et d'agencement d'espace, en y incluant les aspects sociaux et environnementaux liés à la fonction de l'édifice et à son intégration dans son environnement, quelle que soit cette fonction : habitable, sépulcrale, rituelle, institutionnelle, religieuse, défensive, artisanale, commerciale, scientifique, signalétique, muséale, industrielle, monumentale, décorative, paysagère, voire purement artistique.

C'est pourquoi l'architecture est définie comme « une expression de la culture ». Elle est reconnue comme le premier des arts majeurs dans la classification des arts, communément admise, du XXe siècle, des neuf arts majeurs et fait partie des beaux-arts.

L'Architecture désigne également l'ensemble des connaissances et des techniques de cet art de concevoir et de construire des structures complexes, englobant les édifices terrestres, les espaces et les paysages modifiés par l'homme répondant à des critères architecturaux, les artefacts habitables naviguant sur l'eau et sous l'eau (architecture navale) et dans l'espace (architecture spatiale), que l'humanité a pu imaginer et réaliser au fil des millénaires.

L'architecture intègre le domaine de la planification spatiale et met en pratique les méthodes de la planification au service de l'aménagement du territoire et de l'urbanisme. On distingue différentes échelles de la planification spatiale[1] :

le territoire national : l'aménagement du territoire ;
la région, le massif ou une bande littorale : la planification régionale ;
le quartier, la ville, jusqu'à l'agglomération : l'urbanisme ;
l'îlot ou un groupe de bâtiments dont la composition n'atteint pas la superficie du quartier : la composition urbaine ;
le bâtiment : l'architecture.
Dans le cadre des études d'aménagement et d'urbanisme, l'architecte intervient fréquemment dans les réflexions relative à la composition urbaine, notamment à travers la pratique de la conception urbaine.

La cathédrale Saint-Pierre de Beauvais, XIIIe siècle, toute en pierre de taille, est l’exemple le plus aérien et dématérialisé de l'architecture gothique qui atteint là ses limites techniques.

La coupole du Panthéon, construit dans l'Antiquité romaine au début du IIe siècle, est restée de loin la plus large coupole du monde durant de nombreux siècles. Elle ne sera égalée qu'au XVe siècle par le dôme de la cathédrale de Florence qui marque de ce fait le début de la Renaissance, pour n'être dépassée qu'à partir du XXe siècle par les dômes contemporains.

Fragile collier Songhaï composé de paille, cire d'abeille et fil de coton.

Muziri, population bembe, plateaux de la vallée du Niari. République du Congo. Matériaux : tissus, rotin, fibres végétales, laiton, poils et pigments. H. 80 cm env. Muséum d'histoire naturelle de La Rochelle[7].

Bas-relief sculpté dans des blocs de grès rose réappareillés (art khmer)

Sculpture de sable, Tossens, Allemagne.

La palette du peintre à l'huile. Graines de lin.
La Joconde (en italien : La Gioconda [la dʒoˈkonda] ou Monna Lisa [ˈmɔnna ˈliːza]), ou Portrait de Mona Lisa, est un tableau de Léonard de Vinci, réalisé entre 1503 et 1506 ou entre 1513 et 1516[1],[2], et peut-être jusqu'à 1517 (l'artiste étant mort le 2 mai 1519)[3], qui représente un portrait mi-corps, celui de la Florentine Lisa Gherardini, épouse de Francesco del Giocondo. Très probablement acquise par François Ier, cette peinture à l'huile sur panneau de bois de peuplier de 79 × 53 cm[4] est exposée au musée du Louvre à Paris. La Joconde est l'un des rares tableaux attribués de façon certaine à Léonard de Vinci.

La Joconde est devenue un tableau éminemment célèbre car, depuis sa réalisation, nombre d'artistes l'ont pris comme référence. À l'époque romantique, les artistes ont été fascinés par ce tableau et ont contribué à développer le mythe qui l'entoure, en faisant de ce tableau l’une des œuvres d'art les plus célèbres du monde, si ce n'est la plus célèbre : elle est en tout cas considérée comme l'une des représentations d'un visage féminin les plus célèbres au monde[5]. Au XXIe siècle, elle est devenue l'objet d'art le plus visité au monde, devant le diamant Hope[6], avec 20 000 visiteurs qui viennent l'admirer et la photographier quotidiennement[7].

Description
portrait d'une femme.
La Joconde avec son encadrement.
La Joconde est le portrait d'une jeune femme, sur fond d'un paysage montagneux aux horizons lointains et brumeux. Elle est disposée de trois quarts et représentée jusqu'à la taille, bras et mains compris, regardant le spectateur, ce qui est relativement nouveau à l'époque et rompt avec les portraits jusque-là répandus, qui coupent le buste à hauteur des épaules ou de la poitrine et sont entièrement de profil[8].

La femme porte une robe vert sombre en soie plissée sur le devant, avec des manches jaunes. Elle est ornée d'entrelacs dorés et d'une broderie au décolleté. Un voile noir translucide couvre la chevelure et est bien visible sur le haut du front. Cette sorte de mantille plaque les cheveux crêpés ou finement bouclés qui tombent sur les épaules. Les yeux étroits sont nettement cernés et le regard semble suivre le spectateur même lorsqu'il se déplace car il est perpendiculaire au plan de l’image. Le corsage décolleté dégage la gorge et la poitrine jusqu'à la naissance des seins et l'esquisse de l'épaule gauche, ce qui adoucit la sévérité de son voile. Une légende tenace née de la présence de ce voile grège et de l'absence de bijoux veut que Mona porte le deuil de sa fille Camilla morte en 1499. En réalité, ses vêtements sombres sont dus à l'obscurcissement des vernis successifs, le voile noir est une coiffure traditionnelle à cette époque et l'absence de bijoux résulte aussi bien du choix du peintre que du modèle de ne céder ni à la vanité, ni à la mode bien que Mona Lisa soit une femme aisée. Le propos de ce portrait vise ainsi à souligner l'intemporalité de son expression psychologique[9]. La région du cœur, avec la couleur claire de la peau qui tranche sur le vêtement foncé, se trouve au centre du tableau, au croisement de ses deux diagonales.

Crème de Bresse, Pineau des Charentes, Huile d'olive de Nîmes, Châtaigne des Cévennes, Taureau de Camargue, Camembert de Normandie

Une alidade (de l'arabe العضادة, al-idhâdah, « réglette ») est une réglette mobile en rotation autour de l'axe vertical ou horizontal d'un instrument permettant la mesure d'angle. Cette réglette est équipée d'un système de visée qui peut être une lunette ou une pinnule de visée à chaque extrémité.

Une alidade est utilisée en travaux publics et en navigation pour se repérer, ou encore en artillerie pour fixer l'axe du fût du canon.

De ce mot dérive « théodolite », longtemps attribué à tort à l'anglais puis au grec, alors qu'il est issu de la même racine arabe, corrompue par emprunt et réemprunt entre l'anglais et le français[1].

Coupez ou faites une incision sur la gaine. Vous devez couper environ 13 mm de la pointe de chaque fil que vous souderez. Pour ce faire, servez-vous d’une pince à dénuder ou d’une lame de rasoir. Veillez à ne pas couper les brins de cuivre du câble sinon, il deviendra inutilisable.
Déterminez la taille du fil et servez-vous du trou approprié pour bien le couper. Si vous n’êtes pas sûr de la taille du câble, vous devez essayer les différents trous de la pince afin de trouver celui qui convient à la gaine tout en veillant à ne pas couper le fil.
Serrez le fil avec le trou d’épaisseur approprié de la pince. À présent, tournez-le à 90 degrés, puis répétez cela. Vous devez faire cela plusieurs fois pour obtenir une ligne légèrement coupée et définie autour de la gaine. Si vous utilisez une lame, vous devez vous assurer de faire l’incision autour de la circonférence de l’enveloppe isolante.

Le comte désespéré se préparait à retourner à sa terre, en abandonnant avec noblesse ses prétentions à toute indemnité. En ce moment, les événements du Vingt Mars annoncèrent une nouvelle tempête qui menaçait d'engloutir le roi légitime et ses défenseurs. Semblable à ces gens généreux qui ne renvoient pas un serviteur par un temps de pluie, monsieur de Fontaine emprunta sur sa terre pour suivre la monarchie en déroute, sans savoir si cette complicité d'émigration lui serait plus propice que ne l'avait été son dévouement passé; mais après avoir observé que les compagnons de l'exil étaient plus en faveur que les braves qui, jadis, avaient protesté, les armes à la main, contre l'établissement de la république, peut-être espéra-t-il trouver dans ce voyage à l'étranger plus de profit que dans un service actif et périlleux à l'intérieur. Ses calculs 88de courtisan ne furent pas une de ces vaines spéculations qui promettent sur le papier des résultats superbes, et ruinent par leur exécution. Il fut donc, selon le mot du plus spirituel et du plus habile de nos diplomates, un des cinq cents fidèles serviteurs qui partagèrent l'exil de la cour à Gand, et l'un des cinquante mille qui en revinrent.

Pendant cette courte absence de la royauté, monsieur de Fontaine eut le bonheur d'être employé par Louis XVIII, et rencontra plus d'une occasion de donner au roi les preuves d'une grande probité politique et d'un attachement sincère. Un soir que le monarque n'avait rien de mieux à faire, il se souvint du bon mot dit par monsieur de Fontaine aux Tuileries. Le vieux Vendéen ne laissa pas échapper un tel à-propos, et raconta son histoire assez spirituellement pour que ce roi, qui n'oubliait rien, pût se la rappeler en temps utile. L'auguste littérateur remarqua la tournure fine donnée à quelques notes dont la rédaction avait été confiée au discret gentilhomme. Ce petit mérite inscrivit monsieur de Fontaine, dans la mémoire du roi, parmi les plus loyaux serviteurs de sa couronne. Au second retour, le comte fut un de ces envoyés extraordinaires qui parcoururent les départements, avec la mission de juger souverainement les fauteurs de la rébellion; mais il usa modérément de son terrible pouvoir. Aussitôt que cette juridiction temporaire eut cessé, le grand-prévôt s'assit dans un des fauteuils du Conseil-d'État, devint député, parla peu, écouta beaucoup, et changea considérablement d'opinion. Quelques circonstances, inconnues aux biographes, le firent entrer assez avant dans l'intimité du prince, pour qu'un jour le malicieux monarque l'interpellât ainsi en le voyant entrer:

—Mon ami Fontaine, je ne m'aviserais pas de vous nommer directeur-général ni ministre! Ni vous ni moi, si nous étions employés, ne resterions en place, à cause de nos opinions. Le gouvernement représentatif a cela de bon qu'il nous ôte la peine que nous avions jadis, de renvoyer nous-mêmes nos secrétaires d'État. Notre conseil est une véritable hôtellerie, où l'opinion publique nous envoie souvent de singuliers voyageurs; mais enfin nous saurons toujours où placer nos fidèles serviteurs.

Cette ouverture moqueuse fut suivie d'une ordonnance qui donnait à monsieur de Fontaine une administration dans le domaine extraordinaire de la Couronne. Par suite de l'intelligente attention 89avec laquelle il écoutait les sarcasmes de son royal ami, son nom se trouva sur les lèvres de Sa Majesté, toutes les fois qu'il fallut créer une commission dont les membres devaient être lucrativement appointés. Il eut le bon esprit de taire la faveur dont l'honorait le monarque et sut l'entretenir par une manière piquante de narrer, dans une de ces causeries familières auxquelles Louis XVIII se plaisait autant qu'aux billets agréablement écrits, les anecdotes politiques et, s'il est permis de se servir de cette expression, les cancans diplomatiques ou parlementaires qui abondaient alors. On sait que les détails de sa gouvernementabilité, mot adopté par l'auguste railleur, l'amusaient infiniment. Grâce au bon sens, à l'esprit et à l'adresse de monsieur le comte de Fontaine, chaque membre de sa nombreuse famille, quelque jeune qu'il fût, finit, ainsi qu'il le disait plaisamment à son maître, par se poser comme un ver-à-soie sur les feuilles du budget. Ainsi, par les bontés du roi, l'aîné de ses fils parvint à une place éminente dans la magistrature inamovible. Le second, simple capitaine avant la restauration, obtint une légion immédiatement après son retour de Gand; puis, à la faveur des mouvements de 1815 pendant lesquels on méconnut les règlements, il passa dans la garde royale, repassa dans les gardes-du-corps, revint dans la ligne, et se trouva lieutenant-général avec un commandement dans la garde, après l'affaire du Trocadéro. Le dernier, nommé sous-préfet, devint bientôt maître des requêtes et directeur d'une administration municipale de la Ville de Paris, où il se trouvait à l'abri des tempêtes législatives. Ces grâces sans éclat, secrètes comme la faveur du comte, pleuvaient inaperçues. Quoique le père et les trois fils eussent chacun assez de sinécures pour jouir d'un revenu budgétaire presque aussi considérable que celui d'un directeur-général, leur fortune politique n'excita l'envie de personne. Dans ces temps de premier établissement du système constitutionnel, peu de personnes avaient des idées justes sur les régions paisibles du budget, où d'adroits favoris surent trouver l'équivalent des abbayes détruites. Monsieur le comte de Fontaine, qui naguère encore se vantait de n'avoir pas lu la Charte et se montrait si courroucé contre l'avidité des courtisans, ne tarda pas à prouver à son auguste maître qu'il comprenait aussi bien que lui l'esprit et les ressources du représentatif. Cependant, malgré la sécurité des carrières ouvertes à ses trois fils, malgré les avantages pécuniaires 90qui résultaient du cumul de quatre places, monsieur de Fontaine se trouvait à la tête d'une famille trop nombreuse pour pouvoir promptement et facilement rétablir sa fortune. Ses trois fils étaient riches d'avenir, de faveur et de talent; mais il avait trois filles, et craignait de lasser la bonté du monarque. Il imagina de ne jamais lui parler que d'une seule de ces vierges pressées d'allumer leur flambeau. Le roi avait trop bon goût pour laisser son œuvre imparfaite. Le mariage de la première avec un receveur-général fut conclu par une de ces phrases royales qui ne coûtent rien et valent des millions. Un soir où le monarque était maussade, il sourit en apprenant l'existence d'une autre demoiselle de Fontaine qu'il fit épouser à un jeune magistrat d'extraction bourgeoise, il est vrai, mais riche, plein de talent, et qu'il créa baron. Lorsque, l'année suivante, le Vendéen parla de Mademoiselle Émilie de Fontaine, le roi lui répondit, de sa petite voix aigrelette:—Amicus Plato, sed magis amica Natio. Puis, quelques jours après, il régala son ami Fontaine d'un quatrain assez innocent qu'il appelait une épigramme, et dans lequel il le plaisantait sur ses trois filles si habilement produites sous la forme d'une trinité. S'il faut en croire la chronique, le monarque avait été chercher son bon mot dans l'unité des trois personnes divines.

Après la place de la Concorde, ils prirent par le quai de la Conférence et le quai de Billy, où l’on remarque un cèdre dans un jardin. Rosanette croyait le Liban situé en Chine; elle rit elle-même de son ignorance et pria Frédéric de lui donner des leçons de géographie. Puis, laissant à droite le Trocadéro, ils traversèrent le pont d’Iéna et s’arrêtèrent enfin, au milieu du Champ de Mars, près des autres voitures, déjà rangées dans l’Hippodrome.

Les tertres de gazon étaient couverts de menu peuple. On apercevait des curieux sur le balcon de l’École militaire; et les deux pavillons en dehors du pesage, les deux tribunes comprises dans son enceinte, et une troisième devant celle du Roi se trouvaient remplis d’une foule en toilette qui témoignait, par son maintien, 4de la révérence pour ce divertissement encore nouveau. Le public des courses, plus spécial dans ce temps-là, avait un aspect moins vulgaire; c’était l’époque des sous-pieds, des collets de velours et des gants blancs. Les femmes, vêtues de couleurs brillantes, portaient des robes à taille longue, et assises sur les gradins des estrades, elles faisaient comme de grands massifs de fleurs, tachetées de noir, çà et là, par les sombres costumes des hommes. Mais tous les regards se tournaient vers le célèbre Algérien Bou-Maza, qui se tenait impassible, entre deux officiers d’état-major, dans une des tribunes particulières. Celle du Jockey-Club contenait exclusivement des messieurs graves.

Les plus enthousiastes s’étaient placés, en bas, contre la piste, défendue par deux lignes de bâtons supportant des cordes; dans l’ovale immense que décrivait cette allée, des marchands de coco agitaient leur crécelle, d’autres vendaient le programme des courses, d’autres criaient des cigares, un vaste bourdonnement s’élevait; les gardes municipaux passaient et repassaient; une cloche, suspendue à un poteau couvert de chiffres, tinta. Cinq chevaux parurent, et on rentra dans les tribunes.

Cependant de gros nuages effleuraient de leurs volutes la cime des ormes en face. Rosanette avait peur de la pluie.

«J’ai des riflards, dit Frédéric, et tout ce qu’il faut pour se distraire, ajouta-t-il en soulevant le coffre, où il y avait des provisions de bouche dans un panier.

5

—Bravo! nous nous comprenons!

—Et on se comprendra encore mieux, n’est-ce pas?

—Cela se pourrait!» fit-elle en rougissant.

Les jockeys, en casaque de soie, tâchaient d’aligner leurs chevaux et les retenaient à deux mains. Quelqu’un abaissa un drapeau rouge. Alors, tous les cinq, se penchant sur les crinières, partirent. Ils restèrent d’abord serrés en une seule masse; bientôt elle s’allongea, se coupa; celui qui portait la casaque jaune, au milieu du premier tour, faillit tomber; longtemps il y eut de l’incertitude entre Filly et Tibi; puis Tom-Pouce parut en tête; mais Clubstick, en arrière depuis le départ, les rejoignit et arriva premier, battant Sir Charles de deux longueurs; ce fut une surprise, on criait; les baraques de planches vibraient sous les trépignements.

«Nous nous amusons! dit la Maréchale. Je t’aime, mon chéri!»

Frédéric ne douta plus de son bonheur; ce dernier mot de Rosanette le confirmait.

A cent pas de lui, dans un cabriolet milord, une dame parut. Elle se penchait en dehors de la portière, puis se renfonçait vivement; cela recommença plusieurs fois, Frédéric ne pouvait distinguer sa figure. Un soupçon le saisit, il lui sembla que c’était Mme Arnoux. Impossible, cependant! Pourquoi serait-elle venue?

Il descendit de voiture, sous prétexte de flâner au pesage.

«Vous n’êtes guère galant!» dit Rosanette.

6

Il n’écouta rien et s’avança. Le milord, tournant bride, se mit au trot.

Frédéric, au même moment, fut happé par Cisy.

«Bonjour, cher! comment allez-vous? Hussonnet est là-bas! Écoutez donc!»

Frédéric tâchait de se dégager pour rejoindre le milord. La Maréchale lui faisait signe de retourner près d’elle. Cisy l’aperçut et voulait obstinément lui dire bonjour.

Depuis que le deuil de sa grand’mère était fini, il réalisait son idéal, parvenait à avoir du cachet. Gilet écossais, habit court, larges bouffettes sur l’escarpin et carte d’entrée dans la ganse du chapeau, rien ne manquait effectivement à ce qu’il appelait lui-même son «chic», un chic anglomane et mousquetaire. Il commença par se plaindre du Champ de Mars, turf exécrable, parla ensuite des courses de Chantilly et des farces qu’on y faisait, jura qu’il pouvait boire douze verres de vin de Champagne pendant les douze coups de minuit, proposa à la Maréchale de parier, caressait doucement ses deux bichons; et de l’autre coude s’appuyant sur la portière, il continuait à débiter des sottises, le pommeau de son stick dans la bouche, les jambes écartées, les reins tendus. Frédéric, à côté de lui, fumait, tout en cherchant à découvrir ce que le milord était devenu.

La cloche ayant tinté, Cisy s’en alla, au grand plaisir de Rosanette, qu’il ennuyait beaucoup, disait-elle.

La seconde épreuve n’eut rien de particulier, la troisième non plus, sauf un homme qu’on emporta sur 7un brancard. La quatrième, où huit chevaux disputèrent le prix de la ville, fut plus intéressante.

Les spectateurs des tribunes avaient grimpé sur les bancs. Les autres, debout dans les voitures, suivaient avec des lorgnettes à la main l’évolution des jockeys; on les voyait filer comme des taches rouges, jaunes, blanches et bleues sur toute la longueur de la foule, qui bordait le tour de l’Hippodrome. De loin, leur vitesse n’avait pas l’air excessive; à l’autre bout du Champ de Mars, ils semblaient même se ralentir et ne plus avancer que par une sorte de glissement, où les ventres des chevaux touchaient la terre sans que leurs jambes étendues pliassent. Mais, revenant bien vite, ils grandissaient; leur passage coupait le vent, le sol tremblait, les cailloux volaient; l’air s’engouffrant dans les casaques des jockeys les faisait palpiter comme des voiles; à grands coups de cravache, ils fouaillaient leurs bêtes pour atteindre le poteau, c’était le but. On enlevait les chiffres, un autre était hissé; et, au milieu des applaudissements, le cheval victorieux se traînait jusqu’au pesage, tout couvert de sueur, les genoux raidis, l’encolure basse, tandis que son cavalier, comme agonisant sur sa selle, se tenait les côtes.

Une contestation retarda le dernier départ. La foule qui s’ennuyait se répandit. Des groupes d’hommes causaient au bas des tribunes. Les propos étaient libres; des femmes du monde partirent scandalisées par le voisinage des lorettes.

Il y avait aussi des illustrations de bals publics, des 8comédiennes du boulevard;—et ce n’était pas les plus belles qui recevaient le plus d’hommages. La vieille Georgine Aubert, celle qu’un vaudevilliste appelait le Louis XI de la prostitution, horriblement maquillée et poussant de temps à autre une espèce de rire pareil à un grognement, restait tout étendue dans sa longue calèche, sous une palatine de martre comme en plein hiver. Mme de Remoussot, mise à la mode par son procès, trônait sur le siège d’un break en compagnie d’Américains; et Thérèse Bachelu, avec son air de vierge gothique, emplissait de ses douze falbalas l’intérieur d’un escargot qui avait, à la place du tablier, une jardinière pleine de roses. La Maréchale fut jalouse de ces gloires; pour qu’on la remarquât, elle se mit à faire de grands gestes et à parler très haut.

Et la berline se lança vers les Champs-Élysées au milieu des autres voitures, calèches, briskas, wurts, tandems, tilburys, dog-carts, tapissières à rideaux de cuir où chantaient des ouvriers en goguette, demi-fortune que dirigeaient avec prudence des pères de famille eux-mêmes. Dans des victorias bourrées de monde, quelque garçon, assis sur les pieds des autres, laissait pendre en dehors ses deux jambes. De grands coupés à siège de drap promenaient des douairières qui sommeillaient; ou bien un stopper magnifique passait, emportant une chaise, simple et coquette comme l’habit noir d’un dandy. L’averse cependant redoublait. On tirait les parapluies, les parasols, les mackintosh; on se criait de loin: «Bonjour!—Ça va 11bien?—Oui!—Non!—A tantôt!» et les figures se succédaient avec une vitesse d’ombres chinoises. Frédéric et Rosanette ne se parlaient pas, éprouvant une sorte d’hébétude à voir auprès d’eux continuellement toutes ces roues tourner.

Par moments, les files de voitures, trop pressées, s’arrêtaient toutes à la fois sur plusieurs lignes. Alors, on restait les uns près des autres, et l’on s’examinait. Du bord des panneaux armoriés, des regards indifférents tombaient sur la foule; des yeux pleins d’envie brillaient au fond des fiacres; des sourires de dénigrement répondaient aux ports de tête orgueilleux; des bouches grandes ouvertes exprimaient des admirations imbéciles; et, çà et là, quelque flâneur, au milieu de la voie, se rejetait en arrière d’un bond pour éviter un cavalier qui galopait entre les voitures et parvenait à en sortir. Puis tout se remettait en mouvement; les cochers lâchaient les rênes, abaissaient leurs longs fouets; les chevaux, animés, secouant leur gourmette, jetaient de l’écume autour d’eux; et les croupes et les harnais humides fumaient, dans la vapeur d’eau que le soleil couchant traversait. Passant sous l’Arc de triomphe, il allongeait à hauteur d’homme une lumière roussâtre, qui faisait étinceler les moyeux des roues, les poignées des portières, le bout des timons, les anneaux des sellettes; et sur les deux côtés de la grande avenue,—pareille à un fleuve où ondulaient des crinières, des vêtements, des têtes humaines,—les arbres tout reluisants de pluie se dressaient, comme deux murailles vertes. Le bleu du ciel, au-dessus, 12reparaissant à de certaines places, avait des douceurs de satin.

Alors, Frédéric se rappela les jours déjà loin où il enviait l’inexprimable bonheur de se trouver dans une de ces voitures, à côté d’une de ces femmes. Il le possédait, ce bonheur-là, et n’en était pas plus joyeux.

La pluie avait fini de tomber. Les passants, réfugiés entre les colonnes du Garde-Meuble, s’en allaient. Des promeneurs, dans la rue Royale, remontaient vers le boulevard. Devant l’hôtel des Affaires étrangères, une file de badauds stationnait sur les marches.

A la hauteur des Bains Chinois, comme il y avait des trous dans le pavé, la berline se ralentit. Un homme en paletot noisette marchait au bord du trottoir. Une éclaboussure, jaillissant de dessous les ressorts, s’étala dans son dos. L’homme se retourna, furieux. Frédéric devint pâle; il avait reconnu Deslauriers.

A la porte du café Anglais, il renvoya la voiture. Rosanette était montée devant lui, pendant qu’il payait le postillon.

Il la retrouva dans l’escalier, causant avec un monsieur. Frédéric prit son bras. Mais au milieu du corridor, un deuxième seigneur l’arrêta.

«Va toujours! dit-elle, je suis à toi!»

Et il entra seul dans le cabinet. Par les deux fenêtres ouvertes on apercevait du monde aux croisées des autres maisons vis-à-vis. De larges moires frissonnaient sur l’asphalte qui séchait, et un magnolia posé au bord du balcon embaumait l’appartement. Ce 13parfum et cette fraîcheur détendirent ses nerfs; il s’affaissa sur le divan rouge, au-dessous de la glace.

La Maréchale revint, et le baisant au front:

«On a des chagrins, pauvre Mimi?

—Peut-être! répliqua-t-il.

—Tu n’es pas le seul, va! ce qui voulait dire: Oublions chacun les nôtres dans une félicité commune!»

Puis elle posa un pétale de fleur entre ses lèvres et le lui tendit à becqueter. Ce mouvement, d’une grâce et presque d’une mansuétude lascive, attendrit Frédéric.

«Pourquoi me fais-tu de la peine? dit-il en songeant à Mme Arnoux.

—Moi, de la peine?»

Et, debout devant lui, elle le regardait, les cils rapprochés et les deux mains sur les épaules.

Toute sa vertu, toute sa rancune sombra dans une lâcheté sans fond.

Il reprit:

«Puisque tu ne veux pas m’aimer!» en l’attirant sur ses genoux.

Elle se laissait faire; il lui entourait la taille à deux bras; le pétillement de sa robe de soie l’enflammait.

«Où sont-ils?» dit la voix d’Hussonnet dans le corridor.

La Maréchale se leva brusquement et alla se mettre à l’autre bout du cabinet, tournant le dos à la porte.

Elle demanda des huîtres et ils s’attablèrent.

Hussonnet ne fut pas drôle. A force d’écrire quotidiennement 14sur toute sorte de sujets, de lire beaucoup de journaux, d’entendre beaucoup de discussions et d’émettre des paradoxes pour éblouir, il avait fini par perdre la notion exacte des choses, s’aveuglant lui-même avec ses faibles pétards. Les embarras d’une vie légère autrefois, mais à présent difficile, l’entretenaient dans une agitation perpétuelle; et son impuissance, qu’il ne voulait pas s’avouer, le rendait hargneux, sarcastique. A propos d’Ozaï, un ballet nouveau, il fit une sortie à fond contre la danse, et, à propos de la danse, contre l’Opéra; puis, à propos de l’Opéra, contre les Italiens, remplacés maintenant par une troupe d’acteurs espagnols, «comme si l’on n’était pas rassasié des Castilles»! Frédéric fut choqué dans son amour romantique de l’Espagne; et, afin de rompre la conversation, il s’informa du Collège de France, d’où l’on venait d’exclure Edgar Quinet et Mickiewicz. Mais Hussonnet, admirateur de M. de Maistre, se déclara pour l’Autorité et le Spiritualisme. Il doutait cependant des faits les mieux prouvés, niait l’histoire et contestait les choses les plus positives, jusqu’à s’écrier au mot géométrie: «Quelle blague que la géométrie!» Le tout entremêlé d’imitations d’acteurs. Sainville était particulièrement son modèle.

Ces calembredaines assommaient Frédéric. Dans un mouvement d’impatience, il attrapa, avec sa botte, un des bichons sous la table.

Tous deux se mirent à aboyer d’une façon odieuse.

«Vous devriez les faire reconduire!» dit-il brusquement.

15

Rosanette n’avait confiance en personne.

Alors, il se tourna vers le bohème.

«Voyons, Hussonnet, dévouez-vous!

—Oh! oui, mon petit! Ce serait bien aimable!»

Hussonnet s’en alla sans se faire prier.

De quelle manière payait-on sa complaisance? Frédéric n’y pensa pas. Il commençait même à se réjouir du tête-à-tête, lorsqu’un garçon entra.

«Madame, quelqu’un vous demande!

—Comment! encore?

—Il faut pourtant que je voie!» dit Rosanette.

Il en avait soif, besoin. Cette disparition lui semblait une forfaiture, presque une grossièreté. Que voulait-elle donc? n’était-ce pas assez d’avoir outragé Mme Arnoux? Tant pis pour celle-là, du reste! Maintenant il haïssait toutes les femmes; et des pleurs l’étouffaient, car son amour était méconnu et sa concupiscence trompée.


 ne te moque pas de moi! Tu m’agaces!»

Il jugea prudent d’inventer une histoire, une passion. Il trouva des détails circonstanciés. Cette personne, du reste, l’avait rendu fort malheureux.

«Décidément, tu n’as pas de chance! dit Rosanette.

—Oh! oh! peut-être!» voulant faire entendre par là plusieurs bonnes fortunes, afin de donner de lui meilleure opinion, de même que Rosanette n’avouait pas tous ses amants pour qu’il l’estimât davantage;—car, au milieu des confidences les plus intimes, il y a toujours des restrictions, par fausse honte, délicatesse, pitié. On découvre chez l’autre ou dans soi-même des précipices ou des fanges qui empêchent de poursuivre; on sent d’ailleurs que l’on ne serait pas compris; il est difficile d’exprimer exactement quoi que ce soit; aussi les unions complètes sont rares.

La pauvre Maréchale n’en avait jamais connu de meilleure. Souvent, quand elle considérait Frédéric, des larmes lui arrivaient aux paupières; puis elle levait les yeux ou les projetait vers l’horizon, comme si elle 196avait aperçu quelque grande aurore, des perspectives de félicité sans bornes. Enfin, un jour, elle avoua qu’elle souhaitait faire dire une messe, «pour que ça porte bonheur à notre amour».

D’où venait donc qu’elle lui avait résisté pendant si longtemps? Elle n’en savait rien elle-même. Il renouvela plusieurs fois sa question, et elle répondait en le serrant dans ses bras:

«C’est que j’avais peur de t’aimer trop, mon chéri!»

Le dimanche matin, Frédéric lut dans un journal, sur une liste de blessés, le nom de Dussardier. Il jeta un cri, et, montrant le papier à Rosanette, déclara qu’il allait partir immédiatement.

«Pourquoi faire?

—Mais pour le voir, le soigner!

—Tu ne vas pas me laisser seule, j’imagine?

—Viens avec moi.

—Ah! que j’aille me fourrer dans une bagarre pareille! Merci bien!

—Cependant je ne peux pas...

—Ta ta ta! Comme si on manquait d’infirmiers dans les hôpitaux! Et puis, qu’est-ce que ça le regardait encore, celui-là? Chacun pour soi!»

Il fut indigné de cet égoïsme et il se reprocha de n’être pas là-bas avec les autres. Tant d’indifférence aux malheurs de la patrie avait quelque chose de mesquin et de bourgeois. Son amour lui pesa tout à coup comme un crime. Ils se boudèrent pendant une heure.

197

Puis elle le supplia d’attendre, de ne pas s’exposer.

«Si par hasard on te tue!

—Eh! je n’aurai fait que mon devoir!»

Rosanette bondit. D’abord, son devoir était de l’aimer. C’est qu’il ne voulait plus d’elle, sans doute! Ça n’avait pas le sens commun! Quelle idée, mon Dieu!

Frédéric sonna pour avoir la note. Mais il n’était pas facile de s’en retourner à Paris. La voiture des messageries Leloir venait de partir, les berlines Lecomte ne partiraient pas, la diligence du Bourbonnais ne passerait que tard dans la nuit et serait peut-être pleine; on n’en savait rien. Quand il eut perdu beaucoup de temps à ces informations, l’idée lui vint de prendre la poste. Le maître de poste refusa de fournir des chevaux, Frédéric n’ayant point de passeport. Enfin, il loua une calèche (la même qui les avait promenés) et ils arrivèrent devant l’hôtel du Commerce, à Melun, vers cinq heures.

La place du Marché était couverte de faisceaux d’armes. Le préfet avait défendu aux gardes nationaux de se porter sur Paris. Ceux qui n’étaient pas de son département voulaient continuer leur route. On criait. L’auberge était pleine de tumulte.

Rosanette, prise de peur, déclara qu’elle n’irait pas plus loin et le supplia encore de rester. L’aubergiste et sa femme se joignirent à elle. Un brave homme qui dînait s’en mêla, affirmant que la bataille serait terminée d’ici à peu; d’ailleurs, il fallait faire son devoir. Alors, la Maréchale redoubla de sanglots. Frédéric 198était exaspéré. Il lui donna sa bourse, l’embrassa vivement et disparut.

Arrivé à Corbeil, dans la gare, on lui apprit que les insurgés avaient de distance en distance coupé les rails, et le cocher refusa de le conduire plus loin; ses chevaux, disait-il, étaient «rendus».

Par sa protection cependant, Frédéric obtint un mauvais cabriolet qui, pour la somme de soixante francs, sans compter le pourboire, consentit à le mener jusqu’à la barrière d’Italie. Mais, à cent pas de la barrière, son conducteur le fit descendre et s’en retourna. Frédéric marchait sur la route, quand tout à coup une sentinelle croisa la baïonnette. Quatre hommes l’empoignèrent en vociférant:

«C’en est un! Prenez garde! Fouillez-le! Brigand! Canaille!»

Et sa stupéfaction fut si profonde, qu’il se laissa entraîner au poste de la barrière, dans le rond-point même où convergent les boulevards des Gobelins et de l’Hôpital et les rues Godefroy et Mouffetard.

Quatre barricades formaient, au bout des quatre voies, d’énormes talus de pavés; des torches çà et là grésillaient; malgré la poussière qui s’élevait, il distingua des fantassins de la ligne et des gardes nationaux, tous le visage noir, débraillés, hagards. Ils venaient de prendre la place, avaient fusillé plusieurs hommes; leur colère durait encore. Frédéric dit qu’il arrivait de Fontainebleau au secours d’un camarade blessé logeant rue de Bellefond; personne d’abord ne voulut le croire; on examina ses mains, on flaira 199même son oreille pour s’assurer qu’il ne sentait pas la poudre.

Cependant, à force de répéter la même chose, il finit par convaincre un capitaine, qui ordonna à deux fusiliers de le conduire au poste du Jardin des Plantes.

Ils descendirent le boulevard de l’Hôpital. Une forte brise soufflait. Elle le ranima.

Ils tournèrent ensuite par la rue du Marché-aux-Chevaux. Le Jardin des Plantes, à droite, faisait une grande masse noire; tandis qu’à gauche, la façade entière de la Pitié, éclairée à toutes ses fenêtres, flambait comme un incendie, et des ombres passaient rapidement sur les carreaux.

Les deux hommes de Frédéric s’en allèrent. Un autre l’accompagna jusqu’à l’École polytechnique.

La rue Saint-Victor était toute sombre, sans un bec de gaz ni une lumière aux maisons. De dix minutes en dix minutes, on entendait:

«Sentinelles! prenez garde à vous!» Et ce cri, jeté au milieu du silence, se prolongeait comme la répercussion d’une pierre tombant dans un abîme.

Quelquefois, un battement de pas lourds s’approchait. C’était une patrouille de cent hommes au moins; des chuchotements, de vagues cliquetis de fer s’échappaient de cette masse confuse, et, s’éloignant avec un balancement rythmique, elle se fondait dans l’obscurité.

Il y avait au centre des carrefours un dragon à cheval, immobile. De temps en temps, une estafette passait au grand galop, puis le silence recommençait. Des 200canons en marche faisaient au loin sur le pavé un roulement sourd et formidable; le cœur se serrait à ces bruits différant de tous les bruits ordinaires. Ils semblaient même élargir le silence, qui était profond, absolu,—un silence noir. Des hommes en blouse blanche abordaient les soldats, leur disaient un mot et s’évanouissaient comme des fantômes.

Le poste de l’École polytechnique regorgeait de monde. Des femmes encombraient le seuil, demandant à voir leur fils ou leur mari. On les renvoyait au Panthéon transformé en dépôt de cadavres,—et on n’écoutait pas Frédéric. Il s’obstina, jurant que son ami Dussardier l’attendait, allait mourir. On lui donna enfin un caporal pour le mener au haut de la rue Saint-Jacques, à la mairie du XIIe arrondissement.

La place du Panthéon était pleine de soldats couchés sur de la paille. Le jour se levait. Les feux de bivouac s’éteignaient.

L’insurrection avait laissé dans ce quartier-là des traces formidables. Le sol des rues se trouvait, d’un bout à l’autre, inégalement bosselé. Sur les barricades en ruines, il restait des omnibus, des tuyaux de gaz, des roues de charrettes; de petites flaques noires, en de certains endroits, devaient être du sang. Les maisons étaient criblées de projectiles, et leur charpente se montrait sous des écaillures du plâtre. Des jalousies, tenant par un clou, pendaient comme des haillons. Les escaliers ayant croulé, des portes s’ouvraient sur le vide. On apercevait l’intérieur des chambres avec leurs papiers en lambeaux; des choses délicates s’y étaient 201conservées quelquefois. Frédéric observa une pendule, un bâton de perroquet, des gravures.

Quand il entra dans la mairie, les gardes nationaux bavardaient intarissablement sur les morts de Bréa et de Négrier, du représentant Charbonnel et de l’archevêque de Paris. On disait que le duc d’Aumale était débarqué à Boulogne, Barbès enfui de Vincennes, que l’artillerie arrivait de Bourges et que les secours de la province affluaient. Vers trois heures, quelqu’un apporta de bonnes nouvelles; des parlementaires de l’émeute étaient chez le président de l’Assemblée.

Alors, on se réjouit; et, comme il avait encore douze francs, Frédéric fit venir douze bouteilles de vin, espérant par là hâter sa délivrance. Tout à coup, on crut entendre une fusillade. Les libations s’arrêtèrent; on regarda l’inconnu avec des yeux méfiants; ce pouvait être Henri V.

Pour n’avoir aucune responsabilité, ils le transportèrent à la mairie du XIe arrondissement, d’où on ne lui permit pas de sortir avant neuf heures du matin.

Il alla en courant jusqu’au quai Voltaire. A une fenêtre ouverte, un vieillard en manches de chemise pleurait, les yeux levés. La Seine coulait paisiblement. Le ciel était tout bleu; dans les arbres des Tuileries, des oiseaux chantaient.

Frédéric traversait le Carrousel quand une civière vint à passer. Le poste, tout de suite, présenta les armes, et l’officier dit en mettant la main à son shako: «Honneur au courage malheureux!» Cette parole était 202devenue presque obligatoire; celui qui la prononçait paraissait toujours solennellement ému. Un groupe de gens furieux escortait la civière en criant:

«Nous vous vengerons! nous vous vengerons!»

Les voitures circulaient sur le boulevard, et des femmes devant les portes faisaient de la charpie. Cependant l’émeute était vaincue, ou à peu près; une proclamation de Cavaignac, affichée tout à l’heure, l’annonçait. Au haut de la rue Vivienne, un peloton de mobiles parut. Alors, les bourgeois poussèrent des cris d’enthousiasme; ils levaient leurs chapeaux, applaudissaient, dansaient, voulaient les embrasser, leur offrir à boire,—et des fleurs jetées par des dames tombaient des balcons.

Enfin, à dix heures, au moment où le canon grondait pour prendre le faubourg Saint-Antoine, Frédéric arriva chez Dussardier. Il le trouva dans sa mansarde, étendu sur le dos et dormant. De la pièce voisine une femme sortit à pas muets, Mlle Vatnaz.

Elle emmena Frédéric à l’écart et lui apprit comment Dussardier avait reçu sa blessure.

Le samedi, au haut d’une barricade, dans la rue Lafayette, un gamin enveloppé d’un drapeau tricolore criait aux gardes nationaux: «Allez-vous tirer contre vos frères!» Comme ils s’avançaient, Dussardier avait jeté bas son fusil, écarté les autres, bondi sur la barricade, et, d’un coup de savate, abattu l’insurgé en lui arrachant le drapeau. On l’avait retrouvé sous les décombres, la cuisse percée d’un lingot de cuivre. Il avait fallu débrider la plaie, extraire le projectile. 203Mlle Vatnaz était arrivée le soir même, et, depuis ce temps-là, ne le quittait plus.

Pendant plusieurs jours de suite des lambeaux d'armée en déroute avaient traversé la ville. Ce n'était point de la troupe, mais des hordes débandées. Les hommes avaient la barbe longue et sale, des uniformes en guenilles, et ils avançaient d'une allure molle, sans drapeau, sans régiment. Tous semblaient accablés, éreintés, incapables d'une pensée ou d'une résolution, marchant seulement par habitude, et tombant de fatigue sitôt qu'ils s'arrêtaient. On voyait surtout des mobilisés, gens pacifiques, rentiers tranquilles, pliant sous le poids du fusil; des petits moblots alertes, faciles à l'épouvante et prompts à l'enthousiasme, prêts à l'attaque comme à la fuite; puis, au milieu d'eux, quelques culottes rouges, débris d'une division moulue dans une grande bataille; des artilleurs sombres alignés avec des fantassins divers; et, parfois, le casque brillant d'un dragon au pied pesant qui suivait avec peine la marche plus légère des lignards.

Des légions de francs-tireurs aux appellations héroïques: «les Vengeurs de la Défaite—les Citoyens de la Tombe—les Partageurs de la Mort«—passaient à leur tour, avec des airs de bandits.

Leurs chefs, anciens commerçants en draps ou en graines, ex-marchands de suif ou de savon, guerriers de circonstance, nommés officiers pour leurs écus ou la longueur de leurs moustaches, couverts d'armes, de flanelle et de galons, parlaient d'une voix retentissante, discutaient plans de campagne, et prétendaient soutenir seuls la France agonisante sur leurs épaules de fanfarons; mais ils redoutaient parfois leurs propres soldats, gens de sac et de corde, souvent braves à outrance, pillards et débauchés.

Les Prussiens allaient entrer dans Rouen, disait-on.

La Garde nationale qui, depuis deux mois, faisait des reconnaissances très prudentes dans les bois voisins, fusillant parfois ses propres sentinelles, et se préparant au combat quand un petit lapin remuait sous des broussailles, était rentrée dans ses foyers. Ses armes, ses uniformes, tout son attirail meurtrier, dont elle épouvantait naguère les bornes des routes nationales à trois lieues à la ronde, avaient subitement disparu.

Les derniers soldats français venaient enfin de traverser la Seine pour gagner Pont-Audemer par Saint-Sever et Bourg-Achard; et, marchant après tous, le général, désespéré, ne pouvant rien tenter avec ces loques disparates, éperdu lui-même dans la grande débâcle d'un peuple habitué à vaincre et désastreusement battu malgré sa bravoure légendaire, s'en allait à pied, entre deux officiers d'ordonnance.

Puis un calme profond, une attente épouvantée et silencieuse avaient plané sur la cité. Beaucoup de bourgeois bedonnants, émasculés par le commerce, attendaient anxieusement les vainqueurs, tremblant qu'on ne considérât comme une arme leurs broches à rôtir ou leurs grands couteaux de cuisine.

La vie semblait arrêtée; les boutiques étaient closes, la rue muette. Quelquefois un habitant, intimidé par ce silence, filait rapidement le long des murs.

L'angoisse de l'attente faisait désirer la venue de l'ennemi.

Dans l'après-midi du jour qui suivit le départ des troupes françaises, quelques uhlans, sortis on ne sait d'où, traversèrent la ville avec célérité. Puis, un peu plus tard, une masse noire descendit de la côte Sainte-Catherine, tandis que deux autres flots envahisseurs apparaissaient par les routes de Darnetal et de Boisguillaume. Les avant-gardes des trois corps, juste au même moment, se joignirent sur la place de l'Hôtel-de-Ville; et par toutes les rues voisines, l'armée allemande arrivait, déroulant ses bataillons qui faisaient sonner les pavés sous leur pas dur et rythmé.

Des commandements criés d'une voix inconnue et gutturale montaient le long des maisons qui semblaient mortes et désertes, tandis que, derrière les volets fermés, des yeux guettaient ces hommes victorieux, maîtres de la cité, des fortunes et des vies, de par le «droit de guerre». Les habitants, dans leurs chambres assombries, avaient l'affolement que donnent les cataclysmes, les grands bouleversements meurtriers de la terre, contre lesquels toute sagesse et toute force sont inutiles. Car la même sensation reparaît chaque fois que l'ordre établi des choses est renversé, que la sécurité n'existe plus, que tout ce que protégeaient les lois des hommes ou celles de la nature, se trouve à la merci d'une brutalité inconsciente et féroce. Le tremblement de terre écrasant sous les maisons croulantes un peuple entier; le fleuve débordé qui roule les paysans noyés avec les cadavres des boeufs et les poutres arrachées aux toits, ou l'armée glorieuse massacrant ceux qui se défendent, emmenant les autres prisonniers, pillant au nom du Sabre et remerciant un Dieu au son du canon, sont autant de fléaux effrayants qui déconcertent toute croyance à la justice éternelle, toute la confiance qu'on nous enseigne en la protection du Ciel et en la raison de l'homme.

Mais à chaque porte des petits détachements frappaient, puis disparaissaient dans les maisons. C'était l'occupation après l'invasion. Le devoir commençait pour les vaincus de se montrer gracieux envers les vainqueurs.

Au bout de quelque temps, une fois la première terreur disparue, un calme nouveau s'établit. Dans beaucoup de familles, l'officier prussien mangeait à table. Il était parfois bien élevé, et, par politesse, plaignait la France, disait sa répugnance en prenant part à cette guerre. On lui était reconnaissant de ce sentiment; puis on pouvait, un jour ou l'autre, avoir besoin de sa protection. En le ménageant on obtiendrait peut-être quelques hommes de moins à nourrir. Et pourquoi blesser quelqu'un dont on dépendait tout à fait? Agir ainsi serait moins de la bravoure que de la témérité.—Et la témérité n'est plus un défaut des bourgeois de Rouen, comme au temps des défenses héroïques où s'illustra leur cité.—On se disait enfin, raison suprême tirée de l'urbanité française, qu'il demeurait bien permis d'être poli dans son intérieur pourvu qu'on ne se montrât pas familier, en public, avec le soldat étranger. Au dehors on ne se connaissait plus, mais dans la maison on causait volontiers, et l'Allemand demeurait plus longtemps, chaque soir, à se chauffer au foyer commun.

La ville même reprenait peu à peu de son aspect ordinaire. Les Français ne sortaient guère encore, mais les soldats prussiens grouillaient dans les rues. Du reste, les officiers de hussards bleus, qui traînaient avec arrogance leurs grands outils de mort sur le pavé, ne semblaient pas avoir pour les simples citoyens énormément plus de mépris que les officiers de chasseurs, qui, l'année d'avant, buvaient aux mêmes cafés.

Il y avait cependant quelque chose dans l'air, quelque chose de subtil et d'inconnu, une atmosphère étrangère intolérable, comme une odeur répandue, l'odeur de l'invasion. Elle emplissait les demeures et les places publiques, changeait le goût des aliments, donnait l'impression d'être en voyage, très loin, chez des tribus barbares et dangereuses.

Les vainqueurs exigeaient de l'argent, beaucoup d'argent. Les habitants payaient toujours; ils étaient riches d'ailleurs. Mais plus un négociant normand devient opulent et plus il souffre de tout sacrifice, de toute parcelle de sa fortune qu'il voit passer aux mains d'un autre.

Cependant, à deux ou trois lieues sous la ville, en suivant le cours de la rivière, vers Croisset, Dieppedalle ou Biessart, les mariniers et les pêcheurs ramenaient souvent du fond de l'eau quelque cadavre d'Allemand gonflé dans son uniforme, tué d'un coup de couteau ou de savate, la tête écrasée par une pierre, ou jeté à l'eau d'une poussée du haut d'un pont. Les vases du fleuve ensevelissaient ces vengeances obscures, sauvages et légitimes, héroïsmes inconnus, attaques muettes, plus périlleuses que les batailles au grand jour et sans le retentissement de la gloire.

Car la haine de l'Étranger arme toujours quelques Intrépides prêts à mourir pour une Idée.

Enfin, comme les envahisseurs, bien qu'assujétissant la ville à leur inflexible discipline, n'avaient accompli aucune des horreurs que la renommée leur faisait commettre tout le long de leur marche triomphale, on s'enhardit, et le besoin du négoce travailla de nouveau le coeur des commerçants du pays. Quelques-uns avaient de gros intérêts engagés au Havre que l'armée française occupait, et ils voulurent tenter de gagner ce port en allant par terre à Dieppe où ils s'embarqueraient.

On employa l'influence des officiers allemands dont on avait fait la connaissance, et une autorisation de départ fut obtenue du général en chef.

Donc, une grande diligence à quatre chevaux ayant été retenue pour ce voyage, et dix personnes s'étant fait inscrire chez le voiturier, on résolut de partir un mardi matin, avant le jour, pour éviter tout rassemblement.

Depuis quelque temps déjà la gelée avait durci la terre, et le lundi, vers trois heures, de gros nuages noirs venant du Nord apportèrent la neige qui tomba sans interruption pendant toute la soirée et toute la nuit.

A quatre heures et demie du matin, les voyageurs se réunirent dans la cour de l'Hôtel de Normandie, où l'on devait monter en voiture.

Ils étaient encore pleins de sommeil, et grelottaient de froid sous leurs couvertures. On se voyait mal dans l'obscurité; et l'entassement des lourds vêtements d'hiver faisait ressembler tous ces corps à des curés obèses avec leurs longues soutanes. Mais deux hommes se reconnurent, un troisième les aborda, ils causèrent:—«J'emmène ma femme,»—dit l'un.—«J'en fais autant.»—«Et moi aussi.»—Le premier ajouta:—«Nous ne reviendrons pas à Rouen, et si les Prussiens approchent du Havre nous gagnerons l'Angleterre.»—Tous avaient les mêmes projets, étant de complexion semblable.

Cependant on n'attelait pas la voiture. Une petite lanterne, que portait un valet d'écurie, sortait de temps à autre d'une porte obscure pour disparaître immédiatement dans une autre. Des pieds de chevaux frappaient la terre, amortis par le fumier des litières, et une voix d'homme parlant aux bêtes et jurant s'entendait au fond du bâtiment. Un léger murmure de grelots annonça qu'on maniait les harnais; ce murmure devint bientôt un frémissement clair et continu, rythmé par le mouvement de l'animal, s'arrêtant parfois, puis reprenant dans une brusque secousse qu'accompagnait le bruit mat d'un sabot ferré battant le sol.

La porte subitement se ferma. Tout bruit cessa. Les bourgeois gelés s'étaient tus; ils demeuraient immobiles et roidis.

Un rideau de flocons blancs ininterrompu miroitait sans cesse en descendant vers la terre; il effaçait les formes, poudrait les choses d'une mousse de glace; et l'on n'entendait plus, dans le grand silence de la ville calme et ensevelie sous l'hiver, que ce froissement vague, innommable et flottant, de la neige qui tombe, plutôt sensation que bruit, entremêlement d'atomes légers qui semblaient emplir l'espace, couvrir le monde.

L'homme reparut, avec sa lanterne, tirant au bout d'une corde un cheval triste qui ne venait pas volontiers. Il le plaça contre le timon, attacha les traits, tourna longtemps autour pour assurer les harnais, car il ne pouvait se servir que d'une main, l'autre portant sa lumière. Comme il allait chercher la seconde bête, il remarqua tous ces voyageurs immobiles, déjà blancs de neige, et leur dit:—«Pourquoi ne montez-vous pas dans la voiture, vous serez à l'abri, au moins.»

Ils n'y avaient pas songé, sans doute, et ils se précipitèrent. Les trois hommes installèrent leurs femmes dans le fond, montèrent ensuite; puis les autres formes indécises et voilées prirent à leur tour les dernières places sans échanger une parole.

Le plancher était couvert de paille où les pieds s'enfoncèrent. Les dames du fond, ayant apporté des petites chaufferettes en cuivre avec un charbon chimique, allumèrent ces appareils, et, pendant quelque temps, à voix basse, elles en énumérèrent les avantages, se répétant des choses qu'elles savaient déjà depuis longtemps.

Enfin, la diligence étant attelée, avec six chevaux au lieu de quatre à cause du tirage plus pénible, une voix du dehors demanda:—«Tout le monde est-il monté?»—Une voix du dedans répondit:—«Oui.»—On partit.

La voiture avançait lentement, lentement, à tout petits pas. Les roues s'enfonçaient dans la neige; le coffre entier geignait avec des craquements sourds; les bêtes glissaient, soufflaient, fumaient; et le fouet gigantesque du cocher claquait sans repos, voltigeait de tous les côtés, se nouant et se déroulant comme un serpent mince, et cinglant brusquement quelque croupe rebondie qui se tendait alors sous un effort plus violent.

Mais le jour imperceptiblement grandissait. Ces flocons légers qu'un voyageur, Rouennais pur sang, avait comparés à une pluie de coton, ne tombaient plus. Une lueur sale filtrait à travers de gros nuages obscurs et lourds qui rendaient plus éclatante la blancheur de la campagne où apparaissaient tantôt une ligne de grands arbres vêtus de givre, tantôt une chaumière avec un capuchon de neige.

Dans la voiture, on se regardait curieusement, à la triste clarté de cette aurore.

Tout au fond, aux meilleures places, sommeillaient, en face l'un de l'autre, M. et Mme Loiseau, des marchands de vins en gros de la rue Grand-Pont.

Ancien commis d'un patron ruiné dans les affaires, Loiseau avait acheté le fonds et fait fortune. Il vendait à très bon marché de très mauvais vin aux petits débitants des campagnes et passait parmi ses connaissances et ses amis pour un fripon madré, un vrai Normand plein de ruses et de jovialité.

Sa réputation de filou était si bien établie, qu'un soir, à la préfecture, M. Tournel, auteur de fables et de chansons, esprit mordant et fin, une gloire locale, ayant proposé aux dames qu'il voyait un peu somnolentes de faire une partie de «Loiseau vole», le mot lui-même vola à travers les salons du préfet, puis, gagnant ceux de la ville, avait fait rire pendant un mois toutes les mâchoires de la province.

Loiseau était en outre célèbre par ses farces de toute nature, ses plaisanteries bonnes ou mauvaises; et personne ne pouvait parler de lui sans ajouter immédiatement:—«Il est impayable, ce Loiseau.»

De taille exiguë, il présentait un ventre en ballon surmonté d'une face rougeaude entre deux favoris grisonnants.

Sa femme, grande, forte, résolue, avec la voix haute et la décision rapide, était l'ordre et l'arithmétique de la maison de commerce, qu'il animait par son activité joyeuse.

A côté d'eux se tenait, plus digne, appartenant à une caste supérieure, M. Carré-Lamadon, homme considérable, posé dans les cotons, propriétaire de trois filatures, officier de la Légion d'honneur et membre du Conseil général. Il était resté, tout le temps de l'Empire, chef de l'opposition bienveillante, uniquement pour se faire payer plus cher son ralliement à la cause qu'il combattait avec des armes courtoises, selon sa propre expression. Mme Carré-Lamadon, beaucoup plus jeune que son mari, demeurait la consolation des officiers de bonne famille envoyés à Rouen en garnison.

Elle faisait vis-à-vis à son époux, toute petite, toute mignonne, toute jolie, pelotonnée dans ses fourrures, et regardait d'un oeil navré l'intérieur lamentable de la voiture.

Ses voisins, le comte et la comtesse Hubert de Bréville, portaient un des noms les plus anciens et les plus nobles de Normandie. Le comte, vieux gentilhomme de grande tournure, s'efforçait d'accentuer, par les artifices de sa toilette, sa ressemblance naturelle avec le roy Henri IV qui, suivant une légende glorieuse pour la famille, avait rendu grosse une dame de Bréville dont le mari, pour ce fait, était devenu comte et gouverneur de province.

Collègue de M. Carré-Lamadon au Conseil général, le comte Hubert représentait le parti orléaniste dans le département. L'histoire de son mariage avec la fille d'un petit armateur de Nantes était toujours demeurée mystérieuse. Mais comme la comtesse avait grand air, recevait mieux que personne, passait même pour avoir été aimée par un des fils de Louis-Philippe, toute la noblesse lui faisait fête, et son salon demeurait le premier du pays, le seul où se conservât la vieille galanterie, et dont l'entrée fût difficile.

Et pourtant, dernièrement encore, j'étais prêt à les aimer.

Voici deux ans, je vous l'ai dit, que l'homme, mon père, entra chez moi pour la première fois. Je ne soupçonnais rien. Il me commanda deux meubles. Il avait pris, je le sus plus tard, des renseignements auprès du curé, sous le sceau du secret, bien entendu.

Il revint souvent; il me faisait travailler et payait bien. Parfois même il causait un peu de choses et d'autres. Je me sentais de l'affection pour lui.

Au commencement de cette année il amena sa femme, ma mère. Quand elle entra, elle tremblait si fort que je la crus atteinte d'une maladie nerveuse. Puis elle demanda un siège et un verre d'eau. Elle ne dit rien; elle regarda mes meubles d'un air fou, et elle ne répondait que oui et non, à tort et à travers, à toutes les questions qu'il lui posait! Quand elle fut partie, je la crus un peu toquée.

Elle revint le mois suivant. Elle était calme, maîtresse d'elle. Ils restèrent, ce jour-là, assez longtemps à bavarder, et ils me firent une grosse commande. Je la revis encore trois fois, sans rien deviner; mais un jour voilà qu'elle se mit à me parler de ma vie, de mon enfance, de mes parents. Je répondis: «Mes parents, madame, étaient des misérables qui m'ont abandonné.» Alors elle porta la main sur son coeur, et tomba sans connaissance. Je pensai tout de suite: «C'est ma mère!» mais je me gardai bien de laisser rien voir. Je voulais la regarder venir.

Par exemple, je pris de mon côté mes renseignements. J'appris qu'ils n'étaient mariés que du mois de juillet précédent, ma mère n'étant devenue veuve que depuis trois ans. On avait bien chuchoté qu'ils s'étaient aimés du vivant du premier mari, mais on n'en avait aucune preuve. C'était moi la preuve, la preuve qu'on avait cachée d'abord, espéré détruire ensuite.

J'attendis. Elle reparut un soir, toujours accompagnée de mon père. Ce jour-là, elle semblait fort émue, je ne sais pourquoi. Puis, au moment de s'en aller, elle me dit: «Je vous veux du bien, parce que vous m'avez l'air d'un honnête garçon et d'un travailleur; vous penserez sans doute à vous marier quelque jour; je viens vous aider à choisir librement la femme qui vous conviendra. Moi, j'ai été mariée contre mon coeur une fois, et je sais comme on en souffre. Maintenant, je suis riche, sans enfants, libre, maîtresse de ma fortune. Voici votre dot.»

Elle me tendit une grande enveloppe cachetée.

Je la regardai fixement, puis je lui dis: «Vous êtes ma mère?»

Elle recula de trois pas et se cacha les yeux de la main pour ne plus me voir. Lui, l'homme, mon père, la soutint dans ses bras et il me cria: «Mais vous êtes fou!»

Je répondis: «Pas du tout. Je sais bien que vous êtes mes parents. On ne me trompe pas ainsi. Avouez-le et je vous garderai le secret; je ne vous en voudrai pas; je resterai ce que je suis, un menuisier.»

Il reculait vers la sortie en soutenant toujours sa femme qui commençait à sangloter. Je courus fermer la porte, je mis la clef dans ma poche, et je repris: «Regardez-la donc et niez encore qu'elle soit ma mère.»

Alors il s'emporta, devenu très pâle, épouvanté par la pensée que le scandale évité jusqu'ici pouvait éclater soudain; que leur situation, leur renom, leur honneur seraient perdus d'un seul coup; il balbutiait: «Vous êtes une canaille qui voulez nous tirer de l'argent. Faites donc du bien au peuple, à ces manants-là, aidez-les, secourez-les!»

Ma mère, éperdue, répétait coup sur coup: «Allons-nous-en, allons-nous-en!»

Alors, comme la porte était fermée, il cria: «Si vous ne m'ouvrez pas tout de suite, je vous fais flanquer en prison pour chantage et violence!»

J'étais resté maître de moi; j'ouvris la porte et je les vis s'enfoncer dans l'ombre.

Alors il me sembla tout à coup que je venais d'être fait orphelin, d'être abandonné, poussé au ruisseau. Une tristesse épouvantable, mêlée de colère, de haine, de dégoût, m'envahit; j'avais comme un soulèvement de tout mon être, un soulèvement de la justice, de la droiture, de l'honneur, de l'affection rejetée. Je me mis à courir pour les rejoindre le long de la Seine qu'il leur fallait suivre pour gagner la gare de Chatou.

—Je les rattrapai bientôt. La nuit était venue toute noire. J'allais à pas de loup sur l'herbe, de sorte qu'ils ne m'entendirent pas. Ma mère pleurait toujours. Mon père disait: «C'est votre faute. Pourquoi avez-vous tenu à le voir? C'était une folie dans notre position. On aurait pu lui faire du bien de loin, sans se montrer. Puisque nous ne pouvons le reconnaître, à quoi servaient ces visites dangereuses?»

Haricots rouges à la créole
Salade originale de haricots rouges
Salade de haricots rouges
Salade aux haricots rouges
Salade aux haricots rouges, maïs et thon
Riz et haricots rouges (à la créole)
Pâtes aux haricots rouges, à la tomate et aux olives
Dombrés aux haricots rouges
Houmous de haricots rouges

Couper l'oignon en fines lamelles, ainsi que le poivron ( pas besoin de retirer la peau, il suffit seulement de l'épépiner). Faire frire ces lamelles de poivron et d'oignon dans une poêle avec l'huile d'olive pendant environ 5 minutes. Ensuite, ajouter les tomates pelées avec leur jus, ajouter l'origan, le thym, le piment et le sel, mélanger. Laisser mijoter 5 minutes. Pendant ce temps, couper les blancs de poulet en gros dés, les saler, puis les incorporer à la sauce. Laisser cuire pendant 5 minutes. Ajouter les haricots rouges, mélanger délicatement, et laisser mijoter à feux doux pendant 10 minutes.

étape 1
raisins secs
Faites tremper les raisins secs dans de l'eau tiède 1 h avant.

étape 2
Égouttez-les avant l'utilisation.

étape 3
Lavez et coupez tous vos légumes en morceaux.

étape 4
ail
oignon
Épluchez oignons et ail.

étape 5
ail
oignon
Hachez grossièrement l'oignon, coupez l'ail en 4.

étape 6
ail
huile d'olive
oignon
pois chiches
Faites chauffer votre tajine avec l'huile d'olive, ajoutez les oignons, l'ail et les légumes (sauf pois chiches).

étape 7
sel
Épicez selon votre goût.

étape 8
poulet
Déposez dessus le poulet et l'agneau.

étape 9
Épicez de nouveau.

étape 10
Laissez cuire 3 à 4 h.

étape 11
merguez
Ajoutez les merguez.

étape 12
Laissez cuire environ 1 heure.

étape 13
pois chiches
Ajoutez les pois chiches (ils sont déjà cuits).

étape 14
Laissez mijoter jusqu'au moment de servir en baissant le feu si nécessaire.

étape 15
Servez avec une semoule préparée à part.

Anonyme
Note de l'auteur :
« Les raisins secs peuvent être servis à part ou incorporés directement à la préparation. Attention lorsque les merguez cuisent, en effet il peut y avoir beaucoup de jus, dans ce cas, en enlever pour éviter que ça ne déborde. Vous pouvez bien sûr ajouter d'autres légumes ou d'autres viandes selon vos préférences. Le principe reste le même. »

Un gratin super facile et rapide à préparer, gourmand et réconfortant. A servir comme plat végétarien, accompagné d'une salade verte.

Ingrédients
 4 personnes 
Ravioles du Dauphiné / Royans
480 g de ravioles du Dauphiné / Royans
Crème liquide entière ( 30% de MG )
60 cl de crème liquide entière ( 30% de MG )
Noix de muscade
4 pincées de noix de muscade
Poivre du moulin
4 pincées de poivre du moulin
Comté râpé
140 g de comté râpé
Beurre
10 g de beurre pour le plat
Matériel
Four traditionnel
Four traditionnel
Acheter
Plat à gratin
Plat à gratin
Acheter
En cliquant sur "Acheter", vous serez redirigé vers un site externe.

Préparation
Préparation : 10min
Cuisson : 20min
1
Préchauffez le four à 200°C. Beurrez un plat à gratin de 20*26 cm. Séparez délicatement les plaques de ravioles.

2
Versez un peu de crème liquide dans le fond du plat. Ajoutez une couche de ravioles, ajoutez de la crème, parsemez de comté râpé et assaisonnez de poivre du moulin et de noix muscade moulue.
Faites une nouvelle couche de ravioles, ajoutez de la crème, parsemez de comté râpé et assaisonnez de poivre du moulin et de noix muscade moulue.
Renouvelez l'opération jusqu'à épuisement des ingrédients.
Terminez en saupoudrant de comté râpé et ajoutez un tour de poivre du moulin.

3
Enfournez et faites cuire 20 à 25 minutes, jusqu'à ce que la surface du gratin soit bien dorée.
Servez bien chaud an ajoutant du persil haché avant de déguster.

KIT Ensemble de sonomètre et calibrateur
KIT de sonomètre R8050 et calibrateur R8090 avec étui de transport
414,80 € 488,00 €- 15%

Sonomètre PCE-SLM 10
Sonomètre enregistreur PCE-SLM 10
234,60 € 276,00 €- 15%

Tachymètre PCE-DT 65
Tachymètre PCE-DT 65
98,60 € 116,00 €- 15%

Mesureur d'isolement - Calibre automatique
Mesureur d'isolement digital - Calibre automatique
280,33 € 289,00 €- 3%

Sonomètre enregistreur dB A et dB C, 30 à 130 dB, mémoire 32000 points
Sonomètre enregistreur dB A et dB C, 30 à 130 dB, mémoire 32000 points
194,65 € 229,00 €- 15%

Kit Thermo Connect avec capteur et passerelle, suivi à distance des températures
Kit Thermo Connect avec capteur et passerelle, suivi à distance des...
165,75 € 195,00 €- 15%

Hygromètre pour matériaux sans pénétration, mesure de 0 à 100 RH
Hygromètre pour matériaux sans pénétration, mesure de 0 à 100
81,20 € 116,00 €- 30%
Expédition 48/72h

Détecteur de CO2 professionnel très précis pour la mesure de la qualité de l'air
Détecteur de CO2 professionnel très précis pour la mesure de la qualité...
106,95 € 115,00 €- 7%

Thermo-anémomètre compact, mesure de 0.4 à 30 m/s
Thermo-anémomètre compact, mesure de 0.4 à 30 m/s
45,50 € 65,00 €- 30%
Expédition 48/72h

Luxmètre intérieur/extérieur, mesure jusqu'à 400 000 Lux
Luxmètre professionnel intérieur/extérieur, jusqu'à 400 000 Lux
132,30 € 189,00 €- 30%
Expédition 48/72h

,Jauge de l'épaisseur du revêtement,, 0 à 1 000 um/0 à 40 mils,
Jauge de l'épaisseur du revêtement, mesure de 0 à 1 000 µm
390,15 € 459,00 €- 15%

REED R8085 Dosimètre de bruit
Dosimètre de bruit REED R8085 – Mesure précise de l'exposition sonore
610,30 € 718,00 €- 15%

Enregistreur de données de température et d'humidité, mesure de -40 à 70°C et 0 à 100% HR
Thermomètre enregistreur de données de température et d'humidité,...
146,20 € 172,00 €- 15%
Rupture

CenterScanner Plus
CenterScanner pour alignement simple du canal de perçage
648,93 € 669,00 €- 3%

Balance à ressort, LightLine 1000g,d:10g, transparente, bleu foncé, avec pince
Peson à ressort, portée 1000g, résolution 10g, transparent, bleu foncé,...

Anémomètre

Caméra thermique

Détecteur de CO2

Duromètre

Hygromètre

Luxmètre

Mesure de l'épaisseur

Mesure de force

Multimètre

Niveau Laser

Odomètre

Enregistreur de données

Peson à ressort

pH-mètre

Pince ampèremétrique

Sonde Thermocouple

Sonomètre

Tachymètre

Télémètre laser

Thermomètre

Testeur électrique

Divers

Certificats d'étalonnage

Accessoires et compléments

Anémomètre à fil chaud
Chronomètre de contrainte thermique, mesure de -5 à 50°C
51,00 € 60,00 €- 15%

Thermo-hygromètre compact à tiges, mesure de 5 à 70% RH
Thermo-hygromètre compact à tiges, mesure de 5 à 70% RH
58,50 € 65,00 €- 10%
Rupture

Détecteur d?humidité de poche
Hygromètre de poche, de 6 à 44% pour bois et de 0.2 à 2.0% pour matériaux
64,60 € 76,00 €- 15%

Thermo-hygromètre compact 2MP, mesure de 45 à 75% RH
Thermo-hygromètre compact 2MP, mesure de 0 à 100% RH
67,50 € 75,00 €- 10%
Rupture

Thermo/hygromètre stylo
Thermo-hygromètre format stylo, mesure de 20 à 100% RH
67,90 € 70,00 €- 3%

DETECTEUR HUMIDITE FHM10-GF
DETECTEUR HUMIDITE FHM10-GF
71,00 €

Enregistreur de données PCE-HT 71N
Thermomètre enregistreur de données PCE-HT 71N
75,65 € 89,00 €- 15%
Rupture

Hygromètre pour matériaux sans pénétration, mesure de 0 à 100 RH
Hygromètre pour matériaux sans pénétration, mesure de 0 à 100
81,20 € 116,00 €- 30%
Expédition 48/72h

thermo hygrometre FHT60 - GF
thermo hygrometre FHT60 - GF
83,30 € 98,00 €- 15%

Mesureur d''humidité à cœur avec sondes 40 cm - Spécial Agriculture/Agronomie
Hygromètre avec sonde double pointe, mesure de 2 à 30.5 %
83,42 € 86,00 €- 3%

Enregistreur de données USB de temp. et d'humidité, mesure de -40 à 70°C et 0 à 100% HR
Thermomètre enregistreur de données USB de temp. et d'humidité, -40...
89,25 € 105,00 €- 15%

,Hygromètre double,, avec ou sans tige,
Hygromètre double, avec ou sans tige avec alerte sonore
96,90 € 114,00 €- 15%

Appareil de mesure d'humidité PCE-PMI 1BT
Appareil de mesure d'humidité PCE-PMI 1BT
99,45 € 117,00 €- 15%

Psychromètre/thermo-hygromètre numérique
Thermo-hygromètre numérique, -20 à 70°C, 0-100% HR
113,90 € 134,00 €- 15%

Double thermomètre - Type K - Hygromètre
Thermo-hygromètre type K digital, mesure de 0 à 100% RH
130,95 € 135,00 €- 3%

Thermo-hygromètre, mesure de -20 à 60C et HR de 10 à 100%
Thermo-hygromètre, mesure de -20 à 60C et HR de 10 à 100%
137,70 € 162,00 €- 15%

Humidimètre pour bois, plage de mesure 6 à 99.9%
Humidimètre pour bois REED R6015 – Mesure précise de l'humidité du...
146,20 € 172,00 €- 15%

Enregistreur de données de température et d'humidité, mesure de -40 à 70°C et 0 à 100% HR
Thermomètre enregistreur de données de température et d'humidité,...
146,20 € 172,00 €- 15%
Rupture

Thermohygromètre PCE-THD 50
Thermo-hygromètre à sonde Type K avec mémoire 32000 points, de -20° à +60°C
147,05 € 173,00 €- 15%
Rupture

Thermo/hygro/Psychromètre digital - Transmission Bluetooth pour smartphone
Thermo-hygromètre digital avec transmission Bluetooth pour smartphone
150,35 € 155,00 €- 3%

DETECTEUR HUMIDITE FHM 20-GF
DETECTEUR HUMIDITE FHM 20-GF
153,00 €

Compteur de contrainte thermique WBGT
Compteur de contrainte thermique, mesure de 0 à 80°C
153,85 € 181,00 €- 15%
Rupture

Compteur environnemental multifonction 6-en-1
Compteur environnemental multifonction 6 en 1
162,35 € 191,00 €- 15%

THERMO HYGROMETRE FHT100-GF
THERMO HYGROMETRE FHT100-GF
165,00 €

Thermomètre / Hygromètre / Anémomètre / Luxmètre
Mesureur d'environnement multifonction 4 en 1

Minuterie d'entrainement "X-Train Timer"
249,95 €
Luxmètre digital - 200 000 Lux
 Aperçu rapide
Luxmètre digital - 200 000 Lux
60,95 €
Thermomètre / Hygromètre / Sonomètre / Luxmètre
 Aperçu rapide
Thermomètre / Hygromètre / Sonomètre / Luxmètre
194,95 €
Télémètre laser 60 mètres
 Aperçu rapide
Télémètre laser 60 mètres
109,95 €
Microscope digital ultra compact - 100x-400x - Beaverlab
 Aperçu rapide
Microscope digital ultra compact - 100x-400x
64,95 €
Thermomètre congélateur avec adhésif
 Aperçu rapide
Thermomètre congélateur avec adhésif
5,95 €
Thermomètre étanche à sonde amovible 10 mémoires
 Aperçu rapide
Thermomètre étanche à sonde amovible 10 mémoires
94,95 €
Compte-seconde cruciforme de piscine mural 100x100cm
 Aperçu rapide
Compte-seconde cruciforme de piscine mural 100x100cm
479,95 €

En promo
Emetteur température et hygrométrie
 Aperçu rapide
Emetteur température et hygrométrie
39,90 € -10% 35,91 €
Tensiomètre poignet
 Aperçu rapide
Tensiomètre automatique brassard

    """
    generer_dataset_brut(texte_leipzig)