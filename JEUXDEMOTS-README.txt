// THIS FILE IS A READ ME FILE 

//
// JEUXDEMOT LEXICAL NET
// Réseau Lexical du Français - French Lexical Network
// Réseau lexico-sémantique
//
// Données de JeuxDeMots.  Mathieu Lafourcade et LIRMM, 2008-2050
// Data of JeuxDeMots.  Mathieu Lafourcade and LIRMM, 2008-2050
// Licence CreativeCommons Libre de droit - cc0
// http://creativecommons.org/about/cc0
//
// Filename: JEUXDEMOTS-README.txt
// File avalable at:  http://www.jeuxdemots.org/JDM-LEXICALNET-FR/
// jeuxdeMots :  http://www.jeuxdemots.org
//
// THIS FILE IS ENCODED in CP-1252 (Windows)
//
//
// Aknowledgments
// Thank to all people who particpated to the design and development of JeuxDemots, namely:
// Gilles Sérasset, Stéphane Riou, Alain Joubert, Mehdi Yousfi-Monod, Mathieu Mangeot, n@t and
// all other people I might have forgotten.
// Many many thanks to all players of JeuxDeMots.
//
// The POS (part of speech) definitions are partially from ABU (http://abu.cnam.fr).
// Concepts (unused) - terms starting with c0,c1,c2,c3,c4 are inspired from thesaurus Larousse
//
//   Mathieu Lafourcade
//   Sunday 05th of January 2020 11:17:22 AM
//
// Maître de Conférence à L'Université Montpellier 2 - LIRMM - Equipe TEXTE
// 161, rue ADA  -  F-34392 Montpellier Cedex 5
// 33 (0)4 67 41 85 71 -- 33 (0)6 09 57 25 91
// mathieu.lafourcade@lirmm.fr
// http://www.jeuxdemots.org
// http://www.lirmm.fr/jeuxdemots
// http://www.jeuxdemots.org/world-of-jeuxdemots.php
//
// Portal : http://imaginat.name/Page_Liens_JDMv1.html
//
// STRUCTURE
//
// A node, for example eid=336|n="Astrakhan"|t=1|w=50
// has:
// * a unique identifier eid (entry id)
// * a name n
// * a type t (see STATS for the list of node type)
// * a weight w
//
// A relation, for example rid=133275|n1=141480|n2=18280|t=10|w=50
// has:
// * a unique identifier rid (relation id)
// * a starting node id n1
// * an ending node id n2
// * a type t (see STATS for the list of relation types)
// * a weight w
//
// ATTENTION : il est possible que certaines relations impliquent des noeuds inexistants.
// Vous devez vérifier vous-même l'intégrité des données.
//
// WARNING: some nodes used as node id in relations may not exist.
// Check the data integrity by yourself.
//
// Although the data found in this file have been produced and processed from sources assumed to be reliable,
// no warranty expressed or implied is made regarding accuracy, adequacy, completeness, legality, reliability or usefulness
// of any information. This disclaimer applies to both isolated and aggregate uses of the information.
// LIRMM provide this information on an "AS IS" basis. All warranties of any kind, express or implied,
// including but not limited to the IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE,
// and non-infringement of proprietary rights ARE DISCLAIMED.
// Changes may be periodically added to the information herein; these changes may or may not be incorporated
// in any new version of the publication. If the user has obtained this file from
// from a source other than JeuxDeMots/LIRMM web site,
// the user must be aware that electronic data can be altered subsequent to original distribution.
// Data can also quickly become out-of-date.
//
//



// -- STATS

// SEPARATOR = | 

// MAX NODE ID = 14170582 

// ---- 50 most frequents terms

// n="femme"|w=29562
// n="homme"|w=28270
// n="enfant"|w=18504
// n="animal"|w=13341
// n="maison"|w=12100
// n="voiture"|w=11040
// n="cuisine"|w=10672
// n="eau"|w=10551
// n="personne"|w=9840
// n="manger"|w=9676
// n="musique"|w=9288
// n="mer"|w=8968
// n="ville"|w=8688
// n="maladie"|w=7659
// n="école"|w=7436
// n="film"|w=7351
// n="oiseau"|w=7112
// n="amour"|w=6814
// n="argent"|w=6810
// n="livre"|w=6794
// n="cinéma"|w=6682
// n="rue"|w=6675
// n="poisson"|w=6599
// n="***"|w=6584
// n="lettre"|w=6538
// n="main"|w=6512
// n="médecine"|w=6496
// n="mort"|w=6402
// n="_INFO-NO-MORE-QUESTION"|w=6094
// n="dormir"|w=6056
// n="fruit"|w=5897
// n="lit"|w=5818
// n="individu"|w=5792
// n="fille"|w=5722
// n="bateau"|w=5570
// n="guerre"|w=5543
// n="tête"|w=5464
// n="chien"|w=5302
// n="avion"|w=5253
// n="médecin"|w=5130
// n="sexe"|w=5122
// n="chat"|w=5110
// n="arbre"|w=5046
// n="chambre"|w=4990
// n="rouge"|w=4981
// n="jeu"|w=4978
// n="restaurant"|w=4968
// n="peur"|w=4964
// n="soleil"|w=4894
// n="pays"|w=4820

// MAX RELATION ID = 360162576 

// ---- RELATION TYPES

rtid=0|name="r_associated"|nom_etendu="idée associée"|info="Il est demandé d'énumérer les termes les plus étroitement associés au mot cible... Ce mot vous fait penser à quoi ?"
rtid=1|name="r_raff_sem"|nom_etendu="raffinement sémantique"|info="Raffinement sémantique vers un usage particulier du terme source"
rtid=2|name="r_raff_morpho"|nom_etendu="raffinement morphologique"|info="Raffinement morphologique vers un usage particulier du terme source"
rtid=3|name="r_domain"|nom_etendu="domaine"|info="Il est demandé de fournir des domaines relatifs au mot cible. Par exemple, pour 'corner', on pourra donner les domaines 'football' ou 'sport'."
rtid=4|name="r_pos"|nom_etendu="POS"|info="Partie du discours (Nom, Verbe, Adjectif, Adverbe, etc.)"
rtid=5|name="r_syn"|nom_etendu="synonyme"|info="Il est demandé d'énumérer les synonymes ou quasi-synonymes de ce terme."
rtid=6|name="r_isa"|nom_etendu="générique"|info="Il est demandé d'énumérer les GENERIQUES/hyperonymes du terme. Par exemple, 'animal' et 'mammifère' sont des génériques de 'chat'."
rtid=7|name="r_anto"|nom_etendu="contraire"|info="Il est demandé d'énumérer des contraires du terme. Par exemple, 'chaud' est le contraire de 'froid'."
rtid=8|name="r_hypo"|nom_etendu="spécifique"|info="Il est demandé d'énumérer des SPECIFIQUES/hyponymes du terme. Par exemple, 'mouche', 'abeille', 'guêpe' pour 'insecte'."
rtid=9|name="r_has_part"|nom_etendu="partie"|info="Il faut donner des PARTIES/constituants/éléments (a pour méronymes) du mot cible. Par exemple, 'voiture' a comme parties : 'porte', 'roue', 'moteur', ..."
rtid=10|name="r_holo"|nom_etendu="tout"|info="Il est démandé d'énumérer des 'TOUT' (a pour holonymes)  de l'objet en question. Pour 'main', on aura 'bras', 'corps', 'personne', etc... Le tout est aussi l'ensemble comme 'classe' pour 'élève'."
rtid=11|name="r_locution"|nom_etendu="locution"|info="A partir d'un terme, il est demandé d'énumérer les locutions, expression ou mots composés en rapport avec ce terme. Par exemple, pour 'moulin', ou pourra avoir 'moulin à vent', 'moulin à eau', 'moulin à café'. Pour 'vendre', on pourra avoir 'vendre la peau de l'ours avant de l'avoir tué', 'vendre à perte', etc.."
rtid=12|name="r_flpot"|nom_etendu=" 	r_flpot"|info="(relation interne) potentiel de relation"
rtid=13|name="r_agent"|nom_etendu="action>agent"|info="L'agent (qu'on appelle aussi le sujet) est l'entité qui effectue l'action, OU la subit pour des formes passives ou des verbes d'état. Par exemple, dans - Le chat mange la souris -, l'agent est le chat. Des agents typiques de 'courir' peuvent être 'sportif', 'enfant',... (manger r_agent chat)"
rtid=14|name="r_patient"|nom_etendu="action>patient"|info="Le patient (qu'on appelle aussi l'objet) est l'entité qui subit l'action. Par exemple dans - Le chat mange la souris -, le patient est la souris. Des patients typiques de manger peuvent être 'viande', 'légume', 'pain', ... (manger r_patient pain)"
rtid=15|name="r_lieu"|nom_etendu="chose>lieu"|info="Il est demandé d'énumérer les LIEUX typiques où peut se trouver le terme/objet en question. (carotte r_lieu potager)"
rtid=16|name="r_instr"|nom_etendu="action>instrument"|info="L'instrument est l'objet avec lequel on fait l'action. Dans - Il mange sa salade avec une fourchette -, fourchette est l'instrument. Des instruments typiques de 'tuer' peuvent être 'arme', 'pistolet', 'poison', ... (couper r_instr couteau)"
rtid=17|name="r_carac"|nom_etendu="caractéristique"|info="Pour un terme donné, souvent un objet, il est demandé d'en énumérer les CARACtéristiques (adjectifs) possibles/typiques. Par exemple, 'liquide', 'froide', 'chaude', pour 'eau'."
rtid=18|name="r_data"|nom_etendu="r_data"|info="Informations diverses (plutôt d'ordre lexicales)"
rtid=19|name="r_lemma"|nom_etendu="r_lemma"|info="Le lemme (par exemple 'mangent a pour lemme  'manger' ; 'avions' a pour lemme 'avion' ou 'avoir')."
rtid=20|name="r_has_magn"|nom_etendu="magn"|info="La magnification ou amplification, par exemple - forte fièvre - ou - fièvre de cheval - pour fièvre. Ou encore - amour fou - pour amour, - peur bleue - pour peur."
rtid=21|name="r_has_antimagn"|nom_etendu="antimagn"|info="L'inverse de la magnification, par exemple - bruine - pour pluie."
rtid=22|name="r_family"|nom_etendu="famille"|info="Des mots de la même famille lexicale sont demandés (dérivation morphologique, par exemple). Par exemple, pour 'lait' on pourrait mettre 'laitier', 'laitage', 'laiterie', etc."
rtid=23|name="r_carac-1"|nom_etendu="caractéristique-1"|info="Quels sont les objets (des noms) possédant typiquement/possiblement la caractérisque suivante ? Par exemple, 'soleil', 'feu', pour 'chaud'."
rtid=24|name="r_agent-1"|nom_etendu="agent typique-1"|info="Que peut faire ce SUJET ? (par exemple chat => miauler, griffer, etc.) (chat r_agent-1 manger)"
rtid=25|name="r_instr-1"|nom_etendu="instrument>action"|info="L'instrument est l'objet avec lequel on fait l'action. Dans - Il mange sa salade avec une fourchette -, fourchette est l'instrument. On demande ici, ce qu'on peut faire avec un instrument donné... (scie r_instr-1 scier)"
rtid=26|name="r_patient-1"|nom_etendu="patient-1"|info="(inverse de r_patient) Que peut-on faire à cet OBJET. Pour 'pomme', on pourrait avoir 'manger', 'croquer', couper', 'éplucher',  etc. (pomme r_patient-1 manger)"
rtid=27|name="r_domain-1"|nom_etendu="domaine-1"|info="inverse de r_domain : à un domaine, on associe des termes"
rtid=28|name="r_lieu-1"|nom_etendu="lieu>chose"|info="A partir d'un lieu, il est demandé d'énumérer ce qui peut typiquement s'y trouver. Par exemple : Paris r_lieu-1 tour Eiffel"
rtid=29|name="r_chunk_pred"|nom_etendu="predicat"|info="(interne) d'un prédicat quel chunk ?"
rtid=30|name="r_lieu_action"|nom_etendu="lieu>action"|info="A partir d'un lieu, énumérer les actions typiques possibles dans ce lieu."
rtid=31|name="r_action_lieu"|nom_etendu="action>lieu"|info="A partir d'une action (un verbe), énumérer les lieux typiques possibles où peut être réalisée cette action."
rtid=32|name="r_sentiment"|nom_etendu="sentiment"|info="Pour un terme donné, évoquer des mots liés à des SENTIMENTS ou des EMOTIONS que vous pourriez associer à ce terme. Par exemple, la joie, le plaisir, le dégoût, la peur, la haine, l'amour, l'indifférence, l'envie, avoir peur, horrible, etc."
rtid=33|name="r_error"|nom_etendu="erreur"|info="lien d'erreur"
rtid=34|name="r_manner"|nom_etendu="manière"|info="De quelles MANIERES peut être effectuée l'action (le verbe) proposée. Il s'agira d'un adverbe ou d'un équivalent comme une locution adverbiale, par exemple : 'rapidement', 'sur le pouce', 'goulûment', 'salement' ... pour 'manger'."
rtid=35|name="r_meaning/glose"|nom_etendu="glose/sens/signification"|info="Quels SENS/SIGNIFICATIONS pouvez vous donner au terme proposé. Il s'agira de termes (des gloses) évoquant chacun des sens possibles, par exemple : 'forces de l'ordre', 'contrat d'assurance', 'police typographique', ... pour 'police'."
rtid=36|name="r_infopot"|nom_etendu="information potentielle"|info="Information sémantique potentielle"
rtid=37|name="r_telic_role"|nom_etendu="rôle télique"|info="Le rôle télique indique la fonction du nom ou du verbe. Par exemple, couper pour couteau, scier pour scie, etc. C'est le rôle qu'on lui destine communément pour un artéfact, ou bien un rôle qu'on peut attribuer à un objet naturel (réchauffer, éclairer pour soleil)."
rtid=38|name="r_agentif_role"|nom_etendu="rôle agentif"|info="De quelle(s)  manière(s)  peut être CRÉE/CONSTRUIT le terme suivant. On demande des verbes transitifs (le terme en est un complément d'objet) qui DONNENT NAISSANCE à l'entité désignée par le terme,  par exemple, 'construire' pour 'maison', 'rédiger'/'imprimer' pour 'livre' ou 'lettre'."
rtid=39|name="r_verbe-action"|nom_etendu="verbe>action"|info="du verbe vers l'action. Par exemple, construire -> construction , jardiner -> jardinage . C'est un terme directement dérivé (ayant la même racine). Applicable que pour un verbe et inverse de la relation 40 (action vers verbe)."
rtid=40|name="r_action-verbe"|nom_etendu="action>verbe"|info="de l'action vers le verbe. Par exemple, construction -> construire, jardinage -> jardiner. C'est un terme directement dérivé (ayant la même racine). Applicable que pour un nom et inverse de la relation 39 (verbe vers action)."
rtid=41|name="r_conseq"|nom_etendu="conséquence"|info="B (que vous devez donner) est une CONSEQUENCE possible de A. A et B sont des verbes ou des noms.  Exemples : tomber -> se blesser ; faim -> voler ; allumer -> incendie ; négligence --> accident ; etc."
rtid=42|name="r_causatif"|nom_etendu="cause"|info="B (que vous devez donner) est une CAUSE possible de A. A et B sont des verbes ou des noms.  Exemples : se blesser -> tomber ; vol -> pauvreté ; incendie -> négligence ; mort --> maladie ; etc."
rtid=43|name="r_adj-verbe"|nom_etendu="adj>verbe"|info="Pour un adjectif de potentialité/possibilité, son verbe correspondant. Par exemple pour 'lavable' -> 'laver'"
rtid=44|name="r_verbe-adj"|nom_etendu="verbe>adj"|info="Pour un verbe, son adjectif de potentialité/possibilité correspondant. Par exemple pour 'laver' -> 'lavable'"
rtid=45|name="r_chunk_sujet"|nom_etendu="r_chunk_sujet"|info="(interne)"
rtid=46|name="r_chunk_objet"|nom_etendu="r_chunk_objet"|info="(interne)"
rtid=47|name="r_chunk_loc"|nom_etendu="r_chunk_loc"|info="(interne)"
rtid=48|name="r_chunk_instr"|nom_etendu="r_chunk_instr"|info="(interne)"
rtid=49|name="r_time"|nom_etendu="action>temps"|info="Donner une valeur temporelle -quel moment- peut-on associer au terme indiqué (par exemple 'dormir' -> nuit, 'bronzer' -> été, 'fatigue' -> 'soir')"
rtid=50|name="r_object>mater"|nom_etendu="objet>matiere"|info="Quel est la ou les MATIERE/SUBSTANCE pouvant composer l'objet qui suit. Par exemple, 'bois' pour 'poutre'."
rtid=51|name="r_mater>object"|nom_etendu="matière>objet"|info="Quel est la ou les CHOSES qui sont composés de la MATIERE/SUBSTANCE qui suit (exemple 'bois' -> poutre, table, ...)."
rtid=52|name="r_successeur-time"|nom_etendu="successeur"|info="Qu'est ce qui peut SUIVRE temporellement (par exemple Noêl -> jour de l'an, guerre -> paix, jour -> nuit,  pluie -> beau temps, repas -> sieste, etc) le terme suivant :"
rtid=53|name="r_make"|nom_etendu="produit"|info="Que peut PRODUIRE le terme ? (par exemple abeille -> miel, usine -> voiture, agriculteur -> blé,  moteur -> gaz carbonique ...)"
rtid=54|name="r_product_of"|nom_etendu="est le produit de"|info="Le terme est le RESULTAT/PRODUIT de qui/quoi ?"
rtid=55|name="r_against"|nom_etendu="s'oppose à"|info="A quoi le terme suivant S'OPPOSE/COMBAT/EMPECHE ? Par exemple, un médicament s'oppose à la maladie."
rtid=56|name="r_against-1"|nom_etendu="a comme opposition"|info="Inverse de r_against (s'oppose à) - a comme opposition active (S'OPPOSE/COMBAT/EMPECHE). Par exemple, une bactérie à comme opposition antibiotique."
rtid=57|name="r_implication"|nom_etendu="implication"|info="Qu'est-ce que le terme implique logiquement ? Par exemple : ronfler implique dormir, courir implique se déplacer, câlin implique contact physique. (attention ce n'est pas la cause ni le but...)"
rtid=58|name="r_quantificateur"|nom_etendu="quantificateur"|info="Quantificateur(s) typique(s) pour le terme,  indiquant une quantité. Par exemples, sucre -> grain, morceau - sel -> grain, pincée - herbe -> brin, touffe - ..."
rtid=59|name="r_masc"|nom_etendu="équivalent masc"|info="L'équivalent masculin du terme : lionne --> lion."
rtid=60|name="r_fem"|nom_etendu="équivalent fem"|info="L'équivalent féminin du terme : lion --> lionne."
rtid=61|name="r_equiv"|nom_etendu="équivalent"|info="Termes strictement équivalent/identique : acronymes et sigles (PS -> parti socialiste), apocopes (ciné -> cinéma), entités nommées (Louis XIV -> Le roi soleil), etc. (attention il ne s'agit pas de synonyme)"
rtid=62|name="r_manner-1"|nom_etendu="maniere-1"|info="Quelles ACTIONS (verbes) peut-on effectuer de cette manière ? Par exemple, rapidement -> courir, manger, ..."
rtid=63|name="r_agentive_implication"|nom_etendu="implication agentive"|info="Les verbes ou actions qui sont impliqués dans la création de l'objet. Par exemple pour 'construire' un livre, il faut, imprimer, relier, brocher, etc. Il s'agit des étapes nécessaires à la réalisation du rôle agentif."
rtid=64|name="r_has_instance"|nom_etendu="a pour instance"|info="Une instance d'un 'type' est un individu particulier de ce type. Il s'agit d'une entité nommée (personne, lieu, organisation, etc) - par exemple, 'cheval' a pour instance possible 'Jolly Jumper', ou encore 'transatlantique' a pour instance possible 'Titanic'."
rtid=65|name="r_verb_real"|nom_etendu="verbe>real"|info="Pour un verbe, celui qui réalise l'action (par dérivation morphologique). Par exemple, chasser -> chasseur, naviguer -> navigateur."
rtid=66|name="r_chunk_head"|nom_etendu="r_chunk_head"|info=""
rtid=67|name="r_similar"|nom_etendu="similaire"|info="Similaire/ressemble à ; par exemple le congre est similaire à une anguille, ..."
rtid=68|name="r_set>item"|nom_etendu="ensemble>item"|info="Quel est l'ELEMENT qui compose l'ENSEMBLE qui suit (par exemple, un essaim est composé d'abeilles)"
rtid=69|name="r_item>set"|nom_etendu="item>ensemble"|info="Quel est l'ENSEMBLE qui est composé de l'ELEMENT qui suit (par exemple, un essaim est composé d'abeilles)"
rtid=70|name="r_processus>agent"|nom_etendu="processus>agent"|info="Quel est l'acteur de ce processus/événement ? Par exemple,  'nettoyage' peut avoir comme acteur 'technicien de surface'."
rtid=71|name="r_variante"|nom_etendu="variante"|info="Variantes du termes cible. Par exemple, yaourt, yahourt, ou encore évènement, événement."
rtid=72|name="r_syn_strict"|nom_etendu="r_syn_strict"|info="Termes strictement substituables, pour des termes hors du domaine général, et pour la plupart des noms (exemple : endométriose intra-utérine --> adénomyose)"
rtid=73|name="r_is_smaller_than"|nom_etendu="est plus petit que"|info="Qu'est-ce qui est physiquement plus gros que... (la comparaison doit être pertinente)"
rtid=74|name="r_is_bigger_than"|nom_etendu="est plus gros que"|info="Qu'est-ce qui est physiquement moins gros que... (la comparaison doit être pertinente)"
rtid=75|name="r_accomp"|nom_etendu="accompagne"|info="Est souvent accompagné de, se trouve avec... Par exemple : Astérix et Obelix, le pain et le fromage, les fraises et la chantilly."
rtid=76|name="r_processus>patient"|nom_etendu="processus>patient"|info="Quel est le patient de ce processus/événement ? Par exemple,  'découpe' peut avoir comme patient 'viande'."
rtid=77|name="r_verb_ppas"|nom_etendu="r_verb_ppas"|info="Le participe passé (au masculin singulier) du verbe infinitif. Par exemple, pour manger => mangé"
rtid=78|name="r_cohypo"|nom_etendu="co-hyponyme"|info="Il est demandé d'énumérer les CO-HYPONYMES du terme. Par exemple, 'chat' et 'tigre' sont des co-hyponymes (de 'félin')."
rtid=79|name="r_verb_ppre"|nom_etendu="r_verb_ppre"|info="Le participe présent(au masculin singulier) du verbe infinitif. Par exemple, pour manger => mangeant"
rtid=80|name="r_processus>instr"|nom_etendu="processus>instrument"|info="Quel est l'instrument/moyen de ce processus/événement ? Par exemple,  'découpe' peut avoir comme instrument 'couteau'."
rtid=99|name="r_der_morpho"|nom_etendu="dérivation morphologique"|info="Des termes dériviés morphologiquement sont demandés). Par exemple, pour 'lait' on pourrait mettre 'laitier', 'laitage', 'laiterie', etc. (mais pas 'lactose'). Pour 'jardin', on mettra 'jardinier', 'jardinage', 'jardiner', etc. "
rtid=100|name="r_has_auteur"|nom_etendu="a comme auteur"|info="Quel est l'auteur de l'oeuvre suivante ?"
rtid=101|name="r_has_personnage"|nom_etendu="a comme personnages"|info="Quels sont les personnages présents dans l'oeuvre qui suit ?"
rtid=102|name="r_can_eat"|nom_etendu="se nourrit de"|info="De quoi peut se nourir l'animal suivant ?"
rtid=103|name="r_has_actors"|nom_etendu="a comme acteurs"|info="A comme acteurs (pour un film ou similaire)."
rtid=104|name="r_deplac_mode"|nom_etendu="mode de déplacement"|info="Mode de déplacement. chat r_deplac_node marche"
rtid=105|name="r_has_interpret"|nom_etendu="a comme interprètes"|info="Interprète de personnages (cinéma ou théâtre)"
rtid=106|name="r_color"|nom_etendu="couleur"|info="A comme couleur(s)... chat r_color noir"
rtid=107|name="r_cible"|nom_etendu="a comme cible"|info="Cible de la maladie : myxomatose => lapin, rougeole => enfant, ..."
rtid=108|name="r_symptomes"|nom_etendu="a comme symptomes"|info="Symptomes de la maladie : myxomatose => yeux rouges, rougeole => boutons, ..."
rtid=109|name="r_predecesseur-time"|nom_etendu="prédécesseur"|info="Qu'est ce qui peut PRECEDER temporellement (par exemple -  inverse de successeur) le terme suivant :"
rtid=110|name="r_diagnostique"|nom_etendu="diagnostique"|info="Diagnostique pour la maladie : diabète => prise de sang, rougeole => examen clinique, ..."
rtid=111|name="r_predecesseur-space"|nom_etendu="prédécesseur"|info="Qu'est ce qui peut PRECEDER spatialement (par exemple -  inverse de successeur spatial) le terme suivant :"
rtid=112|name="r_successeur-space"|nom_etendu="successeur"|info="Qu'est ce qui peut SUIVRE spatialement (par exemple Locomotive à vapeur -> tender, wagon etc.) le terme suivant :"
rtid=113|name="r_social_tie"|nom_etendu="relation sociale/famille"|info="Relation sociale/familliale entre les individus... (annotation pour la nature exacte : frère, mari, etc.)"
rtid=114|name="r_tributary"|nom_etendu="r_tributary"|info="Tributaire de (physique ou spatial)."
rtid=115|name="r_sentiment-1"|nom_etendu="sentiment-1"|info="Pour un SENTIMENT ou EMOTION donné, il est demandé d’énumérer les termes que vous pourriez associer. Par exemple, pour 'joie', on aurait 'cadeau', 'naissance', 'bonne nouvelle', etc."
rtid=116|name="r_linked-with"|nom_etendu="linked-with"|info="A quoi est-ce relié (un wagon est relié à un autre wagon ou à une locomotive) ?"
rtid=117|name="r_foncteur"|nom_etendu="r_foncteur"|info="La fonction de ce terme par rapport à d'autres. Pour les prépositions notamment, 'chez' => relation r_location. (demande un type de relation comme valeur)"
rtid=118|name="r_comparison"|nom_etendu="r_comparison"|info="(interne)"
rtid=119|name="r_but"|nom_etendu="r_but"|info="But de l'action (nom ou verbe)"
rtid=120|name="r_but-1"|nom_etendu="r_but-1"|info="Quel sont les actions ou verbes qui ont le terme cible comme but ?"
rtid=121|name="r_own"|nom_etendu="pers>possession"|info="Que POSSEDE le terme suivant ? (un soldat possède un fusil, une cavalière des bottes, ...  soldat r_own fusil, ...)"
rtid=122|name="r_own-1"|nom_etendu="possession>pers"|info="Par qui ou quoi EST POSSEDE le terme suivant ? (par exemple, fusil r_own-1 soldat)"
rtid=123|name="r_verb_aux"|nom_etendu="r_verb_aux"|info="Auxiliaire utilisé pour ce verbe"
rtid=124|name="r_predecesseur-logic"|nom_etendu="prédécesseur logique"|info="Qu'est ce qui peut PRECEDER logiquement (par exemple : A précède B -  inverse de successeur logique) le terme suivant :"
rtid=125|name="r_successeur-logic"|nom_etendu="successeur logique"|info="Qu'est ce qui peut SUIVRE logiquement (par exemple A -> B, C etc.) le terme suivant :"
rtid=126|name="r_isa-incompatible"|nom_etendu="r_isa-incompatible"|info="Relation d'incompatibilité pour les génériques. Si A r_isa-incompatible B alors X ne peut pas être à la fois A et B ou alors X est polysémique. Par exemple, poisson r_isa-incompatible oiseau. Colin est à la fois un oiseau et un poisson, donc colin est polysémique."
rtid=127|name="r_incompatible"|nom_etendu="r_incompatible"|info="Relation d'incompatibilité, ne doivent pas être présents ensemble. Par exemple, alcool r_incompatible antibiotique."
rtid=128|name="r_node2relnode"|nom_etendu="r_node2relnode"|info="Relation entre un noeud (quelconque) et un noeud de relation (type = 10) - permet de rendre le graphe connexe même avec les annotations de relations"
rtid=129|name="r_require"|nom_etendu="nécessite / requiert"|info="Il est demandé d'énumérer les termes nécessaires au mot mot cible... Par exemple, 'se reposer' => 'calme', ou 'pain' => 'farine'."
rtid=130|name="r_is_instance_of"|nom_etendu="est une instance de"|info="Une instance est un individu particulier. Il s'agit d'une entité nommée (personne, lieu, organisation, etc) - par exemple, 'Jolly Jumper' est une instance de 'cheval', 'Titanic' en est une de 'transatlantique'."
rtid=131|name="r_is_concerned_by"|nom_etendu="est concerné par"|info="A peut être concerné par B. Par exemple, une personne a un rendez-vous a une maladie, une idée, une opinion, etc..."
rtid=132|name="r_symptomes-1"|nom_etendu="est un symptome de"|info="Inverse de symptômes de la maladie : myxomatose => yeux rouges, rougeole => boutons, ..."
rtid=133|name="r_units"|nom_etendu="a pour unités"|info="A comme unités pour une propriété, ou une mesure. Par exemple vitesse a pour unités m/s ou km/h, etc."
rtid=134|name="r_promote"|nom_etendu="favorise"|info="Qu'est-ce que le terme suivant FAVORISE ? Par exemple, un catalyseur favorise une réaction chimique."
rtid=135|name="r_circumstances"|nom_etendu="circumstances"|info="Les circonstances possibles pour un événements, ou un objet"
rtid=136|name="r_has_auteur-1"|nom_etendu="est l'auteur de"|info="Quel sont les oeuvres de l'auteur suivant ?"
rtid=137|name="r_processus>agent-1"|nom_etendu="processus>agent-1"|info=""
rtid=138|name="r_processus>patient-1"|nom_etendu="processus>patient-1"|info=""
rtid=139|name="r_processus>instr-1"|nom_etendu="processus>instrument-1"|info=""
rtid=149|name="r_compl_agent"|nom_etendu="complément d'agent"|info="Le complément d'agent est celui qui effectue l'action dans les formes passives. Par exemple, pour 'être mangé', la souris est l'agent et le chat le complément d'agent."
rtid=150|name="r_beneficiaire"|nom_etendu="action>bénéficiaire"|info="Le bénéficiaire est l'entité qui tire bénéfice/préjudice de l'action (un complément d'objet indirect introduit par 'à', 'pour', ...). Par exemple dans - La sorcière donne une pomme à Blanche Neige -, la bénéficiaire est Blanche Neige ... enfin, bref, vous avez compris l'idée."
rtid=151|name="r_descend_de"|nom_etendu="descend de"|info="Descend de (évolution)..."
rtid=152|name="r_domain_subst"|nom_etendu="domain_subst"|info="Quels sont le ou les domaines de substitution pour ce terme quand il est utilisé comme domaine (par exemple, 'muscle' => 'anatomie du système musculaire')"
rtid=153|name="r_prop"|nom_etendu="propriété"|info="Pour le terme donné, il faut indiquer les noms de propriétés pertinents (par exemple pour 'voiture', le 'prix', la 'puissance', la 'longueur', le 'poids', etc. On ne met que des noms et pas des adjectifs)."
rtid=154|name="r_activ_voice"|nom_etendu="voix active"|info="Pour un verbe à la voix passive, sa voix active. Par exemple, pour 'être mangé' on aura 'manger'."
rtid=155|name="r_make_use_of"|nom_etendu="r_make_use_of"|info="Peut utiliser un objet ou produit (par exemple électricité pour frigo)."
rtid=156|name="r_is_used_by"|nom_etendu="r_is_used_by"|info="Est utilisé par (par exemple essence pour voiture)."
rtid=157|name="r_adj-nomprop"|nom_etendu="adj>nomprop"|info="Pour un adjectif, donner le nom de propriété correspondant. Par exemple, pour 'friable' -> 'friabilité'"
rtid=158|name="r_nomprop-adj"|nom_etendu="nomprop>adj"|info="Pour un nom de propriété, donner l'adjectif correspondant. Par exemple, pour 'friabilité' -> 'friable'"
rtid=159|name="r_adj-adv"|nom_etendu="adj>adv"|info="Pour un adjectif, donner l'adverbe correspondant. Par exemple, pour 'rapide' -> 'rapidement'"
rtid=160|name="r_adv-adj"|nom_etendu="adv>adj"|info="Pour un adverbe, donner l'adjectif correspondant. Par exemple, pour 'rapidement' -> 'rapide'"
rtid=161|name="r_homophone"|nom_etendu="homophone"|info="Il est demandé d'énumérer les homophones ou quasi-homophones de ce terme."
rtid=162|name="r_potential_confusion"|nom_etendu="confusion potentielle"|info="Confusion potentielle avec un autre terme (par exemple, acre et âcre, détonner et détoner)."
rtid=163|name="r_concerning"|nom_etendu="concernant"|info="Qui concerne quelque chose ou quelqu'un. Par exemple: maladie r_concerning personne, ou disparition r_concerning emploi. (inverse de r_is_concerned_by)"
rtid=164|name="r_adj>nom"|nom_etendu="r_adj>nom"|info="Le nom associé à l'adjectif. Par exemple, 'urinaire' -> 'urine'"
rtid=165|name="r_nom>adj"|nom_etendu="r_nom>adj"|info="L'adjectif associé au nom. Par exemple, 'urine' -> 'urinaire' "
rtid=166|name="r_opinion_of"|nom_etendu="r_opinion_of"|info="L'opinion de tel groupe ou telle personne. Utilisé comme relation d'annotation."
rtid=200|name="r_context"|nom_etendu="r_context"|info="Relation de contexte entre un terme et un noeud contexte."
rtid=333|name="r_translation"|nom_etendu="r_translation"|info="Traduction vers une autre langue."
rtid=444|name="r_link"|nom_etendu="r_link"|info="Lien vers une ressource externe (WordNet, RadLex, UMLS, Wikipedia, etc...)"
rtid=555|name="r_cooccurrence"|nom_etendu="r_cooccurrence"|info="co-occurences (non utilisée)"
rtid=666|name="r_aki"|nom_etendu="r_aki"|info="(TOTAKI) equivalent pour TOTAKI de l'association libre"
rtid=777|name="r_wiki"|nom_etendu="r_wiki"|info="Associations issues de wikipedia..."
rtid=997|name="r_annotation_exception"|nom_etendu="r_annotation_exception"|info="Relation pour indiquer qu'il s'agit d'une exception par rapport à la cible.  L'autruche ne vole pas, et c'est une exception par rapport à l'oiseau prototypique."
rtid=998|name="r_annotation"|nom_etendu="r_annotation"|info="Relation pour annoter (de façon générale) des relations"
rtid=999|name="r_inhib"|nom_etendu="r_inhib"|info="relation d'inhibition, le terme inhibe les termes suivants... ce terme a tendance à exclure le terme associé."
rtid=1000|name="r_prev"|nom_etendu="r_prev"|info="(interne)"
rtid=1001|name="r_succ"|nom_etendu="r_succ"|info="(interne)"
rtid=1002|name="r_termgroup"|nom_etendu="r_termgroup"|info="(interne)"
rtid=2000|name="r_raff_sem-1"|nom_etendu="r_raff_sem-1"|info="Inverse de r_raff_sem (automatique)"
rtid=2001|name="r_learning_model"|nom_etendu="r_learning_model"|info="(interne)"

// ---- NODE TYPES

ntid=-1|name="n_junk"|info="inutilisé - cas d'erreur"
ntid=1|name="n_term"|info="Noeud de terme standard."
ntid=2|name="n_form"|info="Noeud de terme fléchi, si aucune information sémantique particulière"
ntid=3|name="n_definition"|info="inutilisé"
ntid=4|name="n_pos"|info="Noeud de Part of Speech"
ntid=5|name="n_concept"|info="Noeud de concept"
ntid=6|name="n_flpot"|info="Noeud de potentiel de réponse pour une fonction lexicale "
ntid=7|name="n_hub"|info="inutilisé"
ntid=8|name="n_chunk"|info="Noeud d'aggrégat"
ntid=9|name="n_question"|info="Noeud de question = aggrégat + relation cible"
ntid=10|name="n_relation"|info="Noeud représentant une relation (réification)"
ntid=11|name="n_rule"|info="Noeud de règle"
ntid=12|name="n_analogy"|info="Noeud d'analogie"
ntid=13|name="n_commands"|info="Noeud de commandes (interne, pour bots et contributeurs)"
ntid=14|name="n_synt_function"|info="Noeud de fonction syntaxique (GN, COD, COI, ...)"
ntid=18|name="n_data"|info="Noeud d'informations lexicales/syntaxiques"
ntid=36|name="n_data_pot"|info="Noeud d'informations sémantiques"
ntid=200|name="n_context"|info="Noeud de contexte : groupement de termes"
ntid=444|name="n_link"|info="Noeud lien vers autres ressources (LOD)"
ntid=666|name="n_AKI"|info="Noeud terme issu de TOTAKI"
ntid=777|name="n_wikipedia"|info="Noeud terme issu de Wikipedia"
ntid=1002|name="n_group"|info="Noeud de groupes de termes (pour expérience diverses)"
ntid=1003|name="n_generic"|info="Noeud de failsafe - en principe pas d'instance."

// -- NODES



// -- RELATIONS



//(0 relations) 

//EOF