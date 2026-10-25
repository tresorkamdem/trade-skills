# Module 09 · Exercices

Solutions : `python modules/09-performance-et-reporting/solutions/solutions_09.py`

1. **Alpha et bêta.** Sur les 10 secteurs depuis 1969, prends le GMV Ledoit-Wolf (fenêtre de 60 mois) comme portefeuille et 1/n comme référence. Calcule alpha, t-stat, bêta, tracking error et information ratio. L'alpha est-il significatif ?

2. **Brinson.** Un portefeuille a 60 % actions (rendement 8 %) et 40 % obligations (2 %). La référence a 50 % actions (rendement 6 %) et 50 % obligations (3 %). Calcule allocation, sélection et interaction. Vérifie que la somme égale l'écart de performance.

3. **TWR contre MWR.** Un client investit 10 000 EUR. Le portefeuille fait +20 % la première année. Le client ajoute alors 20 000 EUR, puis le portefeuille fait −10 % la deuxième année. Calcule le TWR annualisé et le MWR (TRI). Pourquoi sont-ils si différents ?

4. **Rapport.** Génère le rapport de l'exercice 1 avec `report.write_report` dans `rapports/gmv_lw.md` et ouvre-le.

5. **Pour MAÀT.** Adapte le rapport : ajoute l'allocation actuelle, un commentaire de gestion et le logo. Il servira de modèle pour le paquet « reporting de performance ».
