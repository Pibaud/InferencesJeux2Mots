# ProjetJeu2Mot

## Validation croisee stratifiee

Le dataset contient les exemples utilisables dans `vecteurs/dataset.json`. Pour
une validation 80/20, lancer cinq plis :

```bash
cd vecteurs
../.venv/bin/python build_vecteurs.py
../.venv/bin/python evaluation.py --jeu-test dataset.json --kfold 5 --seed 42
```

Chaque pli utilise 80 % des points pour l'apprentissage. Une collection Qdrant
temporaire est clonee avec ces seuls points, puis les fusions sont realisees
dans cette collection. Les 20 % du pli de test ne sont donc jamais presents
dans la collection interrogee. La collection temporaire est supprimee apres
chaque pli.

`--seed` permet de reproduire le meme decoupage. Les classes sont les valeurs
de `relation_humaine` et sont reparties de maniere stratifiee dans chaque pli.