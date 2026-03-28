# Compte rendu — Algorithme génétique pour le problème du voyageur de commerce (TSP)

## 1. Contexte et objectif

Ce travail pratique consiste à implémenter en Python un **algorithme génétique** (AG) pour approcher des solutions au **problème du voyageur de commerce** (TSP, *Traveling Salesman Problem*). Une instance du problème est donnée par une liste de villes (ou de points) avec leurs coordonnées ; il s’agit de trouver un **ordre de visite** qui parcourt **exactement une fois** chaque ville et **minimise** la longueur totale du trajet (boucle fermée : retour au point de départ).

L’objectif pédagogique est double : maîtriser les briques classiques d’un AG (initialisation, évaluation, sélection, variation génétique) et les connecter à une API distante pour récupérer les données et soumettre une solution.

---

## 2. Récupération et envoi des résultats via l’API

### 2.1. Fonction `fetch_data`

La première étape du projet a été de récupérer les données des différentes instances hébergées sur le serveur du TP. Nous avons utilisé la bibliothèque **`requests`** pour effectuer une requête **GET** vers l’URL :

`https://tsp-sra0.onrender.com/instances/{instance}`

où `{instance}` est l’identifiant de l’instance (par exemple `regions`, `hard_hierarchical`, etc.). La réponse est au format **JSON** ; nous exploitons notamment le champ `cities`, qui contient la liste des coordonnées des villes. Un appel à `raise_for_status()` permet de détecter immédiatement les erreurs HTTP.

### 2.2. Fonction `upload_result`

Une fois un trajet calculé, il faut le soumettre au serveur pour évaluation. La fonction **`upload_result`** envoie une requête **POST** vers :

`https://tsp-sra0.onrender.com/submit`

Le corps de la requête est un JSON contenant :

- `student_id` : identifiant du binôme ou de l’étudiant ;
- `instance_id` : nom de l’instance traitée ;
- `tour` : liste des **indices** des villes dans l’ordre de visite, **relatifs à la liste `initial_instances`** fournie par le serveur.

La construction de `tour` est délicate si plusieurs villes ont les **mêmes coordonnées** : nous avons donc implémenté une correspondance **point → file d’indices** pour consommer chaque occurrence exactement une fois, et nous vérifions que le résultat est bien une **permutation** des villes de départ avant l’envoi. En cas de succès, la réponse JSON du serveur indique notamment la distance calculée côté serveur, un éventuel classement, etc.

---

## 3. Rappel : cycle d’un algorithme génétique

Un AG maintient une **population** d’**individus** (ici, chaque individu est un **trajet** : une permutation des villes). À chaque **génération** :

1. **Évaluation** : on attribue à chaque individu une **fitness** (ici, la longueur du trajet ; plus elle est petite, meilleure est la solution).
2. **Sélection** : on choisit les parents (ou les survivants) en fonction de la fitness.
3. **Variation** : **croisement** et/ou **mutation** produisent de nouveaux individus.
4. On remplace (totalement ou partiellement) l’ancienne population et on répète jusqu’à un critère d’arrêt (souvent un nombre fixe de générations).

---

## 4. Initialisation de la population (`init`)

### 4.1. Version initiale

Au début du TP, la fonction **`init`** générait **N** trajets **aléatoires** : pour chaque individu, on tirait au hasard un ordre de visite des villes sans répétition. Cette approche est simple et garantit une diversité initiale, mais les trajets sont en moyenne **très longs**, ce qui ralentit la convergence vers de bonnes solutions.

### 4.2. Amélioration : heuristique « plus proche voisin » avec diversité

Pour améliorer la qualité du point de départ, nous avons remplacé cette initialisation purement aléatoire par une construction **guidée par la distance euclidienne** entre les coordonnées des villes :

- pour chaque individu, on choisit une **ville de départ** au hasard ;
- tant qu’il reste des villes non visitées, on regarde les villes les plus proches de la position courante et on en choisit une **parmi les k plus proches** (par exemple *k* = 3), tirée aléatoirement dans ce petit ensemble.

Cette stratégie combine les idées du **nearest neighbor** (bonnes arêtes locales) et un peu d’**aléa** pour que deux individus ne soient pas identiques. On obtient ainsi une population de trajets **différents** mais déjà **relativement courts**, ce qui améliore souvent les résultats finaux pour un même budget de calcul.

---

## 5. Évaluation et fitness

La fonction **`evaluation`** parcourt la population et associe à chaque trajet le couple *(individu, fitness)*.

La **fitness** est implémentée par **`fitness(trip)`** : elle calcule la **somme des distances euclidiennes** entre villes consécutives dans l’ordre du trajet, **plus** le segment de fermeture (dernière ville → première ville), car le TSP est ici formulé comme un **cycle** fermé.

La distance entre deux points est donnée par **`distance_euclidienne`**, basée sur la norme euclidienne classique en coordonnées du plan.

---

## 6. Sélection : roulette et élitisme

La fonction **`selection`** route vers la méthode choisie par l’utilisateur.

### 6.1. Roulette

La **sélection par roulette** attribue à chaque individu une probabilité d’être choisi **proportionnelle à sa « qualité »**. Comme nous **minimisons** la distance, la « qualité » n’est pas la distance brute : nous utilisons des **poids** inversement liés à la fitness, par exemple une forme du type *1 / (distance + ε)*, puis nous normalisons pour obtenir des probabilités. Les meilleurs trajets ont ainsi une plus grande chance d’être sélectionnés, tout en laissant une possibilité aux moins bons (diversité).

### 6.2. Élitisme

La **sélection par élitisme** conserve uniquement les **meilleurs** individus de la population courante (après tri par fitness). Cette méthode est **très directive** : elle propage rapidement les bons schémas de visite, au prix d’une diversité parfois plus faible si les autres paramètres (mutation, taille de l’élite) ne sont pas bien calibrés.

Dans nos expérimentations sur ce TP, **l’élitisme** a donné les **meilleurs résultats** en termes de précision par rapport à la roulette, ce que nous attribuons à la nature du problème (paysage d’optimisation où les bonnes solutions sont rares) et à notre pipeline (mutation locale, pas de croisement retenu).

---

## 7. Mutation : permutations

Nous n’avons implémenté qu’un seul opérateur de mutation pour l’instant : **`permutation`**.

Étant donné un trajet et un entier **`num`**, la fonction :

- tire **`num`** positions distinctes dans le trajet ;
- réorganise les villes à ces positions de manière à éviter qu’une ville retombe exactement à la même place qu’avant (contrainte de dérangement partiel sur les indices choisis) ;
- renvoie un **nouveau trajet** dérivé du précédent.

La fonction **`mutation`** (au niveau population) repart des individus **sélectionnés**, en extrait les trajets (et non les couples *(trajet, fitness)*), puis regénère une population de taille cible en appliquant répétitivement des permutations aux parents issus de la sélection.

**Observation importante :** si **`num`** est trop grand (par exemple proche du nombre de villes), chaque mutation **casse** largement la structure du trajet et **détruit** les bonnes propriétés héritées de l’élitisme. Nous avons constaté empiriquement que **`n_perm = 2`** offre un bon compromis : des perturbations **locales** suffisantes pour explorer, sans effacer systématiquement les solutions déjà bonnes.

---

## 8. Croisement (`crossover`)

Nous avons également codé un opérateur de **croisement simple** entre deux parents : coupure à un point, échange de segments, puis réparation pour retrouver une permutation valide (**`cs_fix`**).

En pratique, sur nos instances et avec le reste du pipeline, ce croisement **n’améliorait pas** les résultats (voire les dégradait ou compliquait le réglage). Nous avons donc **choisi de ne pas l’activer** dans la boucle principale : l’appel à `crossover` dans **`main`** n’est effectué que si l’utilisateur passe explicitement un `crossover_method`. Cette décision illustre qu’un AG n’est pas une recette figée : la pertinence des opérateurs dépend du codage des individus, de la fitness et du paysage du problème.

---

## 9. Boucle principale (`main`)

La fonction **`main`** orchestre l’ensemble :

1. **Paramètres d’entrée** : liste d’instances (coordonnées), méthode de sélection, éventuellement croisement et mutation, nombre de générations `n_loop`, taille de population `n_individus`, paramètres spécifiques (`n_perm`, `n_elitism`, `n_crossover`, etc.).
2. **Initialisation** : `init` crée la première génération.
3. **Boucle** : pour chaque génération jusqu’à `n_loop` :
   - évaluation de la population ;
   - sélection ;
   - croisement **si demandé** ;
   - mutation **si demandée** (reconstruction de la population à partir des sélectionnés).
4. **Fin** : évaluation finale, recherche du **meilleur individu** (distance minimale), retour du **trajet** correspondant (liste de points dans l’ordre de visite), prêt pour `upload_result`.

---

## 10. Choix des paramètres et compromis calcul / qualité

Nous avons expérimenté différents jeux de paramètres pour chaque instance. Les conclusions principales :

| Paramètre | Choix retenu (exemple) | Justification |
|-----------|------------------------|---------------|
| Sélection | **Élitisme** | Meilleure précision dans nos tests. |
| Mutation | **Permutation**, **`n_perm = 2`**| Équilibre exploration / préservation des bons trajets ; valeurs élevées dégradent la qualité. |
| Taille d’élite | **`n_elitism = 30`** pour **`n_individus = 300`** | Environ **10 %** de la population : compromis empirique entre pression de sélection et diversité. |
| Population | **`n_individus ≈ 300`** | Compromis avec les **performances** de nos machines (temps d’exécution raisonnable). |
| Générations | **`n_loop ≈ 1000`** | Budget de calcul fixé de manière pratique ; augmenter peut aider mais avec un coût CPU croissant. |
| Croisement | **Non utilisé** | Pas d’apport net observé avec notre implémentation actuelle. |

Ces valeurs ne sont pas universellement optimales : elles dépendent de la taille de l’instance, du matériel et du temps disponible. Une piste d’amélioration serait une **recherche systématique** (grille de paramètres) ou un **schéma adaptatif** (par exemple augmenter légèrement la mutation si la population stagne).

---

## 11. Conclusion

Ce TP nous a permis de mettre en œuvre un pipeline complet : **données réseau** (`fetch_data`, `upload_result`), **représentation** des solutions (permutations de villes), **évaluation** par distance euclidienne sur un cycle fermé, **sélection** (roulette vs élitisme), **mutation** par permutations contrôlées, et **croisement** (implémenté mais écarté après expérimentation). L’**initialisation heuristique** et le réglage fin de **`n_perm`** et de l’**élitisme** se sont révélés déterminants pour obtenir de bons trajets dans un temps de calcul acceptable.

---

*Document rédigé dans le cadre du TP « algorithme génétique pour le TSP » — projet `genetic-algo-tsp`.*
