# Journal de trading

Ton journal est la source de ton **track record**. Sans journal, pas de progrès mesurable ni de crédibilité auprès de futurs clients.

## Règles

1. Une ligne par trade, saisie **le jour même**, y compris les trades perdants.
2. Le stop est noté **avant** l'entrée : c'est lui qui définit 1R.
3. `setup` reprend toujours les mêmes noms (par exemple `cassure`, `rebond_mm50`), sinon les statistiques par setup ne veulent rien dire.
4. `sens` vaut `achat` ou `vente`.

## Analyse

```bash
python -m tradeskills.journal journal/modele_journal.csv
```

Le script affiche le taux de réussite, le gain et la perte moyens en R, l'espérance par trade, le profit factor et le résultat par setup. Remplace les lignes d'exemple par tes propres trades (commence en paper trading).
