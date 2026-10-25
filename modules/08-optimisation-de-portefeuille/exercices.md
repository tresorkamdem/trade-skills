# Module 08 · Exercices

Solutions : `python modules/08-optimisation-de-portefeuille/solutions/solutions_08.py` (environ 10 secondes de calcul).

1. **Shrinkage non linéaire.** Ajoute `optim.cov_nonlinear_shrinkage` au backtest de ta thèse (48 secteurs, fenêtres de 60 et 120 mois). Compare la volatilité hors échantillon à l'estimateur empirique et à Ledoit-Wolf.

2. **Long-only.** Sur les 10 secteurs, fenêtre de 60 mois, compare GMV avec ventes à découvert, GMV long-only et GMV long-only plafonné à 25 %, avec Ledoit-Wolf. Volatilité, Sharpe, turnover.

3. **Parité de risque.** Sur la même base, ajoute la parité de risque. Vérifie que les contributions au risque sont égales sur la dernière fenêtre.

4. **Black-Litterman.** Sur les 10 secteurs, prends des poids de marché égaux comme approximation, δ = 2,5, τ = 0,05. Exprime la vue « HiTec fera 3 % de plus par an que Utils ». Compare les rendements d'équilibre et a posteriori, puis le portefeuille tangent long-only obtenu.

5. **CVaR.** Sur les 120 derniers mois des 10 secteurs, compare la CVaR à 95 % du GMV long-only, de la parité de risque et du portefeuille min-CVaR.

6. **Pour MAÀT.** Rédige une page « méthodologie » pour l'offre C1 : quel estimateur, quelles contraintes, quel rééquilibrage, et pourquoi. Appuie-toi sur tes résultats et sur le tableau de la section 8.
