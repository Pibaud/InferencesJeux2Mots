# ProjetJeu2Mot

Afin de lancer le projet, il faut se placer à la racine du dépôt et exécuter "main.py".


Les instructions d'utilisation sont assez claires: il suffit d'entrer une requête sous la forme <terme1> <relation> <terme2>

Pour évaluer un dataset et exporter le détail des classifications ainsi qu'un rapport HTML graphique :

```bash
python3 evaluateur.py --dataset vecteurs/test.json --mode seuil \
	--csv sorties/evaluation.csv --graphiques sorties/evaluation.html \
	--ouvrir-graphiques
```

Le CSV contient une ligne par exemple, avec la classe attendue, la classe prédite,
le statut, la correction et les éventuelles erreurs. Le rapport HTML contient le
taux de réussite par classe et la matrice de confusion.