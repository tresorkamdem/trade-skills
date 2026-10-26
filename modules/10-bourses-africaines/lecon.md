# Module 10 · Bourses africaines : BRVM et BVMAC

**Objectif** : savoir comment fonctionnent la bourse régionale d'Afrique de l'Ouest (BRVM) et celle d'Afrique centrale (BVMAC), ce qui les distingue des marchés européens, et comment les analyser sans tomber dans les pièges des marchés peu liquides.

**Durée** : 3 semaines · **Prérequis** : modules 01, 02 et 08 · **Outils** : `tradeskills.afrique`

> Les chiffres de cette leçon (nombre de sociétés cotées, limites de variation, délais de règlement, fiscalité) changent avec le temps. Vérifie chacun sur les sites officiels avant de t'en servir : brvm.org, amf-umoa.org, bvm-ac.com, cosumaf.org, bceao.int, beac.int.

## 1. Pourquoi s'y intéresser

- **Lien avec tes projets** : le pilier D de MAÀT Analytics (diaspora, Afrique) a besoin de quelqu'un qui sait lire ces marchés avec des outils quantitatifs. Très peu d'analystes le font.
- **Des entreprises rentables qui versent beaucoup de dividendes** : télécoms, banques, agro-industrie, distribution. Les rendements en dividende sont souvent bien plus élevés qu'en Europe.
- **Une diversification réelle** : ces marchés suivent surtout l'économie locale, peu le S&P 500.
- **Mais** : peu de titres, peu d'échanges, une information moins abondante et des frais plus élevés. Ce sont des marchés pour l'investissement de long terme, **pas pour le day trading ni le swing trading**.

## 2. Le franc CFA : deux monnaies, une parité fixe

| | UEMOA (Afrique de l'Ouest) | CEMAC (Afrique centrale) |
| --- | --- | --- |
| Monnaie | Franc CFA BCEAO (code **XOF**) | Franc CFA BEAC (code **XAF**) |
| Banque centrale | BCEAO, Dakar | BEAC, Yaoundé |
| Pays | Bénin, Burkina Faso, Côte d'Ivoire, Guinée-Bissau, Mali, Niger, Sénégal, Togo | Cameroun, Centrafrique, Congo, Gabon, Guinée équatoriale, Tchad |
| Bourse | BRVM, Abidjan | BVMAC, Douala |

Les deux francs CFA valent la même chose (**1 EUR = 655,957 FCFA**, parité fixe garantie par la France), mais ils ne sont pas interchangeables : un billet XOF ne s'utilise pas au Cameroun.

Pour toi, investisseur en euros, cela veut dire :
- **pas de risque de change au quotidien** : 1 000 000 FCFA valent toujours 1 524,49 EUR ;
- **un risque extrême rare mais réel** : en janvier 1994, le franc CFA a été dévalué de 50 % face au franc français. Une dévaluation ferait perdre d'un coup une grosse partie de la valeur en euros. C'est un risque de queue, que les mesures habituelles (volatilité, VaR historique) ne voient pas du tout ;
- la zone UEMOA a engagé en 2019 une réforme (projet de monnaie « Eco », fin du dépôt de la moitié des réserves au Trésor français) ; la parité avec l'euro a été conservée. Suis l'actualité de ces réformes.

`afrique.vers_eur(montant)` convertit des FCFA en euros.

## 3. La BRVM (Afrique de l'Ouest)

- **Bourse commune aux 8 pays de l'UEMOA**, siège à Abidjan, cotations depuis 1998. C'est l'une des rares bourses régionales au monde.
- **Régulateur** : AMF-UMOA (anciennement CREPMF). **Dépositaire central et banque de règlement** : DC/BR.
- **Intermédiaires** : les SGI (Sociétés de Gestion et d'Intermédiation). Pour acheter une action, tu passes obligatoirement par une SGI agréée.
- **Environ 45 sociétés cotées**, avec des secteurs dominés par les télécoms (Sonatel, Orange Côte d'Ivoire), les banques (Société Générale Côte d'Ivoire, Ecobank, SIB...), l'agro-industrie et la distribution. Quelques titres font une grande part de la capitalisation : un indice pondéré par la capitalisation est très concentré.
- **Indices** : BRVM Composite (toutes les actions), BRVM 30 (les 30 plus liquides), BRVM Prestige.
- **Limite de variation** : une action ne peut pas varier de plus d'un certain pourcentage en une séance (7,5 % au moment où cette leçon est écrite). Quand un titre touche la limite, la séance suivante continue souvent dans le même sens : le vrai prix met plusieurs jours à apparaître.
- **Publication** : le Bulletin Officiel de la Cote (BOC), chaque jour sur brvm.org, donne cours, volumes et dividendes.
- Il existe aussi un marché obligataire actif (emprunts d'États et d'entreprises).

## 4. La BVMAC (Afrique centrale)

- **Bourse des 6 pays de la CEMAC**, issue en 2019 de la fusion de l'ancienne BVMAC (Libreville) et de la Douala Stock Exchange ; siège à Douala.
- **Régulateur** : COSUMAF, à Libreville. **Intermédiaires** : les PSI (Prestataires de Services d'Investissement), souvent des banques.
- **Très peu d'actions cotées** (une dizaine au plus) et des échanges rares : certains titres restent des semaines sans transaction. Les noms connus viennent de l'agro-industrie (SOCAPALM, SAFACAM), de l'eau (SEMC) et de quelques sociétés gabonaises.
- **Le marché est surtout obligataire** : emprunts des États (Cameroun, Gabon, Congo...) et de quelques entreprises. Pour un investisseur, c'est souvent là que se trouvent les opportunités, avec des rendements élevés et un risque souverain à analyser.

## 5. Comparaison avec ce que tu connais

| | Xetra (Allemagne) | BRVM | BVMAC |
| --- | --- | --- | --- |
| Sociétés cotées | des centaines | environ 45 | une dizaine |
| Échanges par titre | continus | quotidiens pour les plus gros, rares pour les autres | rares |
| Accès depuis l'Allemagne | n'importe quel broker | SGI agréée | PSI agréé |
| Données | Yahoo, TradingView | BOC (brvm.org), sites spécialisés | site de la BVMAC, presse |
| Usage | tous styles | long terme, dividendes | long terme, obligations |

## 6. Le piège du quant : les cours figés

Quand un titre ne s'échange pas, le cours affiché reste celui du dernier échange. Sur des rendements journaliers, on voit donc beaucoup de 0, puis un rattrapage brutal. Conséquences :

1. **Corrélations et bêtas fortement sous-estimés.** Le titre réagit au marché avec des jours de retard ; une régression sur le même jour ne voit qu'une partie de ce lien. Le portefeuille paraît bien plus diversifié qu'il ne l'est, et une optimisation de variance minimale (module 08) va surpondérer précisément les titres les moins liquides.
2. **Correction de Dimson** : régresser le titre sur le marché du jour, de la veille et du lendemain, puis additionner les bêtas (`afrique.beta_dimson`). Autre solution simple : travailler en **rendements hebdomadaires ou mensuels**, où le retard compte beaucoup moins.
3. **Mesurer la liquidité avant tout** (`afrique.liquidite`) : part des séances sans échange, valeur moyenne échangée, illiquidité d'Amihud. Un titre où ta position représente plusieurs jours de volume ne se vend pas quand tu veux.
4. **Coûts élevés** : commission de la SGI, frais de la bourse et du dépositaire, spread large. Avec un turnover élevé, comme dans ta thèse, les coûts mangent toute la performance. Rééquilibrer rarement est encore plus important ici.
5. **Peu d'observations, beaucoup de bruit** : c'est exactement le cadre où l'estimation Ledoit-Wolf de la covariance apporte le plus.

## 7. Dividendes et fiscalité

- Les dividendes sont souvent la plus grosse partie du rendement. Le BOC indique les montants et les dates de paiement. Un backtest sur les seuls cours (sans dividendes) sous-estime fortement la performance.
- Une **retenue à la source** est prélevée dans le pays de la société (le taux dépend du pays et de la nature du titre), puis le revenu est imposé en Allemagne (Abgeltungsteuer). Selon la convention fiscale (Doppelbesteuerungsabkommen) entre l'Allemagne et le pays concerné, une partie de la retenue peut être imputée. Vérifie avec un Steuerberater avant d'investir.

## 8. Investir depuis l'Allemagne

1. Choisir une SGI agréée par l'AMF-UMOA (liste sur amf-umoa.org) ou un PSI agréé par la COSUMAF ; plusieurs proposent une ouverture de compte à distance pour la diaspora.
2. Fournir les pièces d'identité et justificatifs (KYC), puis virer des euros, convertis en FCFA.
3. Demander la grille de frais complète (courtage, droits de garde, frais de virement) et calculer le coût d'un aller-retour comme au module 01.
4. Passer des **ordres à cours limité** : avec des carnets d'ordres peu fournis, un ordre au marché peut être exécuté très loin du dernier cours.

Ces marchés ne sont pas accessibles via Trade Republic, Scalable ou IBKR au moment où cette leçon est écrite.

## 9. Avec les outils de ce dépôt

- **Données** : télécharge les cours depuis le BOC ou un site spécialisé, et enregistre un CSV par titre (`date,open,high,low,close,volume`) dans `agents/donnees/`. `data.load_ohlcv_csv` et la source `csv:agents/donnees` des agents les lisent directement.
- **Analyse** : `afrique.liquidite`, `afrique.jours_a_la_limite`, `afrique.beta_dimson`, puis `portfolio.cov_ledoit_wolf` sur des rendements hebdomadaires.
- **Une poche « afrique »** : style `long_terme` (rééquilibrage mensuel, parité de risque ou 1/n plutôt que GMV), univers limité aux titres les plus liquides, frais réalistes (`cout_bps`) et `poids_max` faible. Pas de poche swing ou day sur ces marchés.

## 10. À retenir

- Deux bourses, deux zones, deux francs CFA à la même parité fixe avec l'euro.
- La BRVM est la plus grande et la plus liquide des deux ; la BVMAC est surtout un marché obligataire.
- Les cours figés cachent le risque : utilise des rendements hebdomadaires ou le bêta de Dimson, et mesure la liquidité avant tout.
- Horizon long, dividendes, peu de transactions, ordres à cours limité.
