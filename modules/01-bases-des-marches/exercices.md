# Module 01 · Exercices

Les solutions chiffrées se trouvent dans `solutions/solutions_01.py` (lance `python modules/01-bases-des-marches/solutions/solutions_01.py`). Essaie d'abord sans regarder.

1. **Carnet d'ordres.** Avec le carnet de la leçon, tu passes un ordre d'achat au marché de 700 titres. Quel est ton prix moyen ? Combien perds-tu par rapport au milieu de fourchette (100,01) ?

2. **Coût d'une stratégie.** Tu fais 3 allers-retours par jour, 20 jours par mois, avec 0,03 % de spread, 0,02 % de slippage et 1 EUR de frais par ordre, sur une position de 5 000 EUR. Quel est ton coût annuel en pourcentage de la position ? Quel rendement brut faut-il pour être à zéro ?

3. **Gap et stop.** Tu détiens 100 actions achetées à 50 EUR avec un stop à 47 EUR. Une mauvaise nouvelle tombe la nuit et l'action ouvre à 42 EUR. Combien perds-tu, et combien pensais-tu risquer ? Quel type d'ordre aurait pu éviter cette surprise, et à quel prix ?

4. **Levier.** Avec 2 000 EUR et un levier de 5 sur le DAX, quelle baisse de l'indice efface 50 % de ton capital ? Et 100 % ?

5. **Ta thèse.** Dans ta Bachelorarbeit, l'estimateur empirique a un turnover mensuel de 1,907 (fenêtre de 60 mois). Avec un coût de 0,20 % par unité de rotation, combien de rendement annuel perd-il ? Et Ledoit-Wolf (turnover 0,246) ? Vérifie ensuite avec `tradeskills.portfolio.compare(..., cost_bps=20)`.

6. **Pratique.** Ouvre un compte démo chez un broker régulé et sur TradingView. Passe un ordre limite, un ordre stop et un ordre au marché sur un ETF. Note pour chacun le prix demandé, le prix obtenu et les frais dans `journal/modele_journal.csv`.
