# Quel courtier ouvrir ?

Pour des agents, le critère principal est l'**API** : sans elle, les agents ne peuvent pas passer les ordres eux-mêmes. Le deuxième critère est le **compte papier**, pour tester avec de l'argent fictif sur la vraie plateforme. Vérifie les frais et les conditions sur le site de chaque courtier : ils changent souvent.

| Courtier | API pour les agents | Compte papier | Impôts en Allemagne | Pour quelle poche |
| --- | --- | --- | --- | --- |
| **Interactive Brokers** | Oui (TWS / IB Gateway, bibliothèque Python `ib_async`) | Oui, gratuit avec le compte | Pas de retenue automatique : déclaration dans l'Anlage KAP | Swing et day : **mon premier choix** |
| **LYNX** | Oui (même plateforme qu'IBKR) | Oui (démo) | Pas de retenue automatique | Comme IBKR, avec un support en allemand, mais plus cher |
| **Alpaca** | Oui, conçue pour les API | Oui, sans ouvrir de compte réel | Ouverture d'un compte réel en Allemagne à vérifier | Pour tester les agents en papier très vite |
| **Saxo** | Oui (OpenAPI) | Oui (démo) | À vérifier | Alternative à IBKR, frais plus élevés |
| **comdirect** | Oui (API REST pour les particuliers, fonctions limitées) | Non | Retenue automatique (courtier allemand) | Possible pour le long terme |
| **Trade Republic**, **Scalable Capital** | Non | Non | Retenue automatique | Long terme en plan d'épargne (Sparplan), passé à la main |

## Ma recommandation

1. **Maintenant :** reste sur le courtier papier des agents. Ouvre en parallèle un compte papier chez Interactive Brokers (ou Alpaca, plus rapide) pour te familiariser avec une vraie plateforme.
2. **Compte réel pour le swing et le day trading :** Interactive Brokers. C'est le seul qui combine une API complète, des frais bas, l'accès aux marchés allemands et américains et un compte papier identique au compte réel. Un adaptateur pour son API sera la prochaine brique de l'agent Courtier.
3. **Poche long terme :** un courtier allemand bon marché (Trade Republic ou Scalable) en plan d'épargne sur les ETF UCITS. Tout est déclaré automatiquement au fisc, et le rééquilibrage mensuel proposé par les agents se fait à la main en quelques minutes.

## À savoir

- **Impôts :** en Allemagne, les plus-values sont soumises à l'Abgeltungsteuer (25 % plus Soli et éventuellement l'impôt d'église), après le Sparerpauschbetrag de 1 000 € par an. Un courtier allemand retient l'impôt lui-même ; avec IBKR ou LYNX, tu le déclares toi-même. Demande un *Freistellungsauftrag* chez le courtier allemand.
- **Day trading :** vérifie auprès du courtier choisi les règles qui s'appliquent à ton compte (marge, nombre d'allers-retours par jour, règle « pattern day trader » des comptes américains).
- **ETF américains :** pas accessibles aux particuliers de l'UE (voir le README des agents). Utilise les équivalents UCITS.
- **Clients :** gérer l'argent d'autres personnes avec ces agents demande un agrément BaFin. Ce dépôt reste pour ton propre compte.

Ce n'est pas un conseil juridique ou fiscal.
