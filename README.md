# Graph-recommendation

Auteurs :
- David Ross (ROSD08058900)
- Vincent Therrien (THEV17129807)

Système de recommandation de données basé sur des graphes.


## Données

L'ensemble de données choisi pour ce projet est le `Steam Video Game and Bundle Data` accessible à l'adresse https://cseweb.ucsd.edu/~jmcauley/datasets.html#steam_data. Nous utilisons la version 1 (et les métadonnées de la version 2). Ces données contiennent des commentaires de joueurs australiens sur des jeux vidéos du distributeur Steam.


### Installation des données

Le jeux de données contient un fichier de commentaires des utilisateurs, un fichier d'objets (des jeux) détenus par les utilisateurs, et un fichier des métadonnées des jeux.

Dans un dossier vide, mettez le fichier `preprocess.py`, téléchargez les fichiers suivants avec `wget` et décompressez-les avec `gunzip`, comme le montre la cellule suivante :

```
# `Version 1: Review Data`
wget https://datarepo.eng.ucsd.edu/mcauley_group/data/steam/australian_user_reviews.json.gz
# `Version 1: User and Item Data`
wget https://datarepo.eng.ucsd.edu/mcauley_group/data/steam/australian_users_items.json.gz
# `Version 2: Item metadata`
wget https://cseweb.ucsd.edu/~wckang/steam_games.json.gz
gunzip *.json.gz
```

Le fichier `Version 1: Review Data` contient des critiques de jeux des utilisateurs formatées de la manière suivante :

```
{
    'user_id': <ID>,
    'user_url': <URL>.
    'reviews': [
        {
            'funny': <comment>,
            'posted': <date>,
            'last_edited': <date>,
            'item_id': <item ID>,
            'helpful': <How many people found the review helpful>,
            'recommend': <True / False>,
            'review': <comment>
        },
    ]
}
```

Le fichier `Version 1: User and Item Data` contient le catalogue de jeux des utilisateurs sous la forme d'objets JSON formatés de la manière suivante :

```
{
    'user_id': <ID>,
    'items_count': <count>,
    'steam_id': <Steam ID>,
    'user_url': <URL>,
    'items': [
        {
            'item_id': <ID>,
            'item_name': <name>,
            'playtime_forever': <n>,
            'playtime_2weeks': <n>,
        }
    ]
}
```

Le fichier `Version 2: Item metadata` contient les métadonnées des jeux sous la forme d'objets JSON formatés de la manière suivante :

```
{
    'publisher': <name>,
    'genres': [<genres>],
    'app_name': <name>,
    'sentiment': <rating>,
    'title': <title>,
    'url': <URL>,
    'release_date': <date>,
    'tags': [<tags>],
    'reviews_url': <URL>,
    'specs': [<specifications>],
    'price': <price>,
    'metascore': <n>,
    'early_access': <True / False>,
    'id': <ID>,
    'developer': <name>
}
```


### Pré-traitement des données

Cette étape vise à transformer les données contenue dans les fichiers JSON en un format CSV
utilisable par `Neo4j`. La commande suivante permet de pré-traiter les données :

```
python3 preprocess.py  # Linux
py preprocess.py  # Windows
```

Le script `preprocess.py` génère cinq fichiers CSV à partir des données originale :

- `user_nodes.csv` : Noeuds d'identifiants de tous les utilisateurs.
- `item_nodes.csv` : Noeuds d'identifiants de tous les items (c-à-d des jeux).
- `review_relations.csv` : Relations de critiques des utilisateurs envers les jeux.
- `item_relations.csv` : Relations entre les joueurs et le temps de jeu.
- `item_metadata.csv` : Métadonnées pour chaque jeux, comme leur genre et leur prix.

L'exécution du script prend quelques minutes à compléter.


## Importation des noeuds et relations dans Neo4j

Cette section présente comment importer les fichiers générés dans la section précédente dans une
base de données `Neo4j`. Il faut effectuer les étapes suivantes :

- Ouvrir `Neo4j` desktop
- Créer un nouveau projet, puis créer une nouvelle database (DBMS) en cliquant sur `Add Local DMBS`
- Lancer (start) la DBMS
- Une fois la DBMS en marche, choisir "Terminal" dans le menu déroulant "Open". Cette opération
  ouvre un terminal `Neo4j` dans le répertoire de la DBMS
  (par exemple, `C:/Users/david/.Neo4jDesktop/relate-data/dbmss/dbms-005f3d71-44eb-4db3-960e-6d9f06ff9713`)
  qui contient un dossier "import". Copier les 5 fichiers produits par preprocess.py dans ce
  dossier. Par exemple, sous Linux, en supposant que `<import>` représente le répertoire
  d'importation de la DBMS, exécuter les commandes :
  - `cp user_nodes.csv <import>`
  - `cp item_nodes.csv <import>`
  - `cp review_relations.csv <import>`
  - `cp item_relations.csv <import>`
  - `cp item_metadata.csv <import>`
- Vérifier dans le fichier `conf/neo4j.conf` (situé dans le répertoire de la DBMS) que la ligne 22
  (`<server.directories.import=import>`) n'est pas masquée.
- Arrêter la DBMS dans `Neo4j desktop` et lancer le commande suivante dans le terminal `Neo4j` dans le directoire de la DBMS :
```
bin\neo4j-admin database import full --nodes=import/user_nodes.csv --nodes=import/item_nodes.csv --relationships=import/review_relations.csv --relationships=import/item_relations.csv --overwrite-destination --skip-bad-relationships --skip-duplicate-nodes
```
- Relancer la DBMS. Il est maintenant possible d'interagir avec le graphe dans `Neo4j browser`.
- Importer les métadonnées et créer les relations correspondantes en utilisant le code suivante dans le `Neo4j browser`:

```
LOAD CSV WITH HEADERS from 'file:///item_metadata.csv' as row FIELDTERMINATOR '|'
WITH row WHERE row.GameID IS NOT NULL
MERGE (j:GameID {id:row.GameID})
SET j.title=row.title, j.price=toFloat(row.price), j.release_date=row.release
WITH j, row WHERE row.release IS NOT NULL
MERGE (y:Year {name:toInteger(substring((trim(row.release)),0,4))})
MERGE (j) - [r:RELEASED_IN] -> (y)
WITH j, row WHERE row.sentiment IS NOT NULL
MERGE (se:Sentiment {name:row.sentiment})
MERGE (j) - [:HAS_SENTIMENT] -> (se)
WITH j, row WHERE row.metascore IS NOT NULL
MERGE (m:Metascore {name:toInteger(row.metascore)})
MERGE (j) - [:HAS_SCORE] -> (m)
```

On termine l'importation par modifier quelques propriétés pour qu'elles soient plus conviviales d'utilisation dans les requêtes :

```
MATCH (j:GameID) <- [r:RECOMMENDS] - (u:UserID)
SET r.recommends = toBoolean(r.recommends)
```

```
MATCH (s:Sentiment) WHERE s.name IS NOT NULL
WITH s,
(CASE s.name
WHEN "Overwhelmingly Positive" THEN 4
WHEN "Very Positive" THEN 3
WHEN "Mostly Positive" THEN 2
WHEN "Positive" THEN 1
WHEN "Mixed" THEN 0
WHEN "Negative" THEN -1
WHEN "Mostly Negative" THEN -2
WHEN "Very Negative" THEN -3
WHEN "Overwhelmingly Negative" THEN -4
ELSE NULL END) AS category
SET s.level = category
```


## Recommandations

Maintenant que les données sont nettoyées et importées, et le DBMS est populée des relations, on peut générer des recommandations, selon différents critères.

### Recommandations hybrides

On a choisit d'utiliser un méthod hybrid de recommandation. On identifie un utilisateur au hasard et on calcule le quantité des jeux qu'il/elle a joué. Si l'utilisateur en a joué moins de 20, la recommendation est basée sur le contenu, en cherchant les jeux les plus populaires sorties dans les 10 dernieres années (nos données arretent en 2017). Si l'utilisateur a joué 20 ou plus jeux, la recommendation est basée sur le filtrage collaboratif, en cherchant les jeux les plus joués par les utilisateurs similaires.

Le système de recommandation hybride se divise en deux approches selon la quantité de jeux auxquels les joueurs ont joué :

#### Approche hybride 1 : faible quantité de jeux (moins de 20)

1. Établir une limite de prix a la 85e percentile (plus ou moins le moyen + 1xSD), en excluant les jeux gratuits.
2. Identifier les jeux qui ont un `Sentiment` global d'"Overwhelmingly positive" ou "Very positive" (les niveaux 3 et 4), un `Metascore` de 80+.
3. Limiter les resultats aux jeux qui ont un prix dans la 85e percentile, qui s'est sortie apres 2007 (donc les dernieres 10 années des données), et qui ont des recommendations positives.
4. Organiser les résultats pour trouver les 50 jeux qui ont le plus d'utilisateurs qui les `Recommend`, et on montre un selection au hasard de 10 de ces 50 jeux pour qu'ils aillent de la variation si on montre les mêmes recommendations au même utilisateur plusieurs fois.


#### Approche hybride 2 : plus grande quantité de jeux (20 ou plus)

Le filtrage collaboratif permet de sélectionner des jeux avec le potentiel de plaire à des
utilisateurs qui n'y ont jamais joué. Le code effectue les opérations suivantes :

1. Dresser une liste des 20 utilisateurs les plus similaires au joueur sélectionné à l'étape 1 en utilisant
   l'indice de Jaccard. Les utilisateurs qui ont joué au plus de jeux en commun sont plus similaires.
2. Générer une liste des 50 jeux auxquels les utilisateurs similaires ont joué les plus, mais auquel
   l'utilisateur sélectionné à l'étape 1 n'a jamais joué. Cette liste est organisé premièrement par quantité des joueurs en commun, ensuite par temps moyen joué. 
3. Montrer encore un selection au hasard de 10 de ces 50 jeux.

```
MATCH (u:UserID)
ORDER BY RAND()
LIMIT 1
MATCH (u) - [p:PLAYED] -> (j:GameID)
WHERE p.playtime > 0
CALL {
    WITH u, p
    WITH u, p, COUNT(p) AS games
    WHERE games < 20
    MATCH (j:GameID)
    WHERE j.price IS NOT NULL AND j.price > 0
    WITH percentileCont(j.price, 0.85) AS upper
    MATCH (s:Sentiment) <- [:HAS_SENTIMENT] - (j:GameID) <- [r:RECOMMENDS] - (:UserID), (y:Year) <- [:RELEASED_IN] - (j) - [:HAS_SCORE] -> (m:Metascore)
    WHERE j.title IS NOT NULL AND s.level >=3 AND m.name >= 80
    WITH j, r, y, upper
    WHERE r.recommends = True AND j.price <= upper AND y.name > 2007
    WITH j.title AS recommendation, COUNT(r) AS times_recommended, y.name AS release_year, j.price AS price
    ORDER BY times_recommended DESC LIMIT 50
    RETURN recommendation

    UNION

    WITH u, p
    WITH u, p, COUNT(p) AS games
    WHERE games >= 20
    MATCH (user1) - [sp1:PLAYED] -> (sharedGames:GameID) <- [sp2:PLAYED] - (user2:UserID)
    WHERE user1 <> user2 AND sp1.playtime > 0 AND sp2.playtime > 0 AND sharedGames.title IS NOT NULL
    WITH user1, user2, COLLECT(distinct sharedGames.title) AS sharedGames, COUNT(distinct sharedGames) AS sharedGamesCount
    MATCH (user1) - [p1:PLAYED] -> (:GameID)
    WHERE p1.playtime > 0
    WITH user1, user2, sharedGames, sharedGamesCount, COUNT(p1) AS games1
    MATCH (user2) - [p2:PLAYED] -> (:GameID)
    WHERE p2.playtime > 0
    WITH user1, user2, sharedGames, sharedGamesCount, games1, COUNT(p2) AS games2
    WITH user1, user2, sharedGames, sharedGamesCount, games1, games2, ((sharedGamesCount*100) / ((games1 + games2) - sharedGamesCount)) AS similarityScore
    ORDER BY similarityScore DESC
    LIMIT 20
    MATCH (user2) - [p:PLAYED] -> (newGame:GameID)
    WHERE NOT newGame.title IN sharedGames AND newGame.title IS NOT NULL AND p.playtime > 0
    WITH newGame.title AS recommendation, AVG(p.playtime) AS mean_likeUser_playtime, SUM(p.playtime) AS total_likeUser_playtime, COUNT(distinct user2.id) AS sharedUsers, AVG(similarityScore) AS mean_similarity
    ORDER BY sharedUsers DESC, mean_likeUser_playtime DESC LIMIT 50
    RETURN recommendation
}
RETURN u.id AS user, recommendation, COUNT(p) AS games_played
ORDER BY RAND() LIMIT 10
```

Le code ci-dessous rapporte le résultat de l'approche hybride qui combine les deux cas de figure. Due a l'utilisation de `CALL{... UNION ...}` pour générer les résultats qui dépendent sur l'information du joueur au hasard, et que les sorties des deux approches sont différentes, on peut sortir que la colonne `recommendation` et les information sur le joueur sélectionné. Pour mettre en lumière les détails des résultats des deux approches, nous rapportons leurs sorties individuellement avec toutes leurs colonnes.

Avec l'approche **basée sur le contenu**, on obtient les résultats semblants aux suivants :

```
╒══════════════════════════════════╤═════════════════╤════════════╤═════╕
│recommendation                    │times_recommended│release_year│price│
╞══════════════════════════════════╪═════════════════╪════════════╪═════╡
│"Counter-Strike: Global Offensive"│3475             │2012        │14.99│
├──────────────────────────────────┼─────────────────┼────────────┼─────┤
│"Left 4 Dead 2"                   │731              │2009        │19.99│
├──────────────────────────────────┼─────────────────┼────────────┼─────┤
│"Terraria"                        │723              │2011        │9.99 │
├──────────────────────────────────┼─────────────────┼────────────┼─────┤
│"Borderlands 2"                   │548              │2012        │19.99│
├──────────────────────────────────┼─────────────────┼────────────┼─────┤
```

Avec le **filtrage collaboratif**, on obtient les résultats semblants aux suivants :

```
╒══════════════════════╤═════════════╤══════════════╤═══════════╤═══════════════╕
│recommendation        │mean playtime│total playtime│sharedUsers│mean similarity│
╞══════════════════════╪═════════════╪══════════════╪═══════════╪═══════════════╡
│"The Elder Scrolls IV"│837.312500000│13397         │16         │26.624999999999│
├──────────────────────┼─────────────┼──────────────┼───────────┼───────────────┤
│"Batman: Arkham Asylu"│692.2        │10383         │15         │26.599999999999│
├──────────────────────┼─────────────┼──────────────┼───────────┼───────────────┤
│"Goat Simulator"      │337.4        │5061          │15         │26.599999999999│
├──────────────────────┼─────────────┼──────────────┼───────────┼───────────────┤
│"Batman: Arkham City "│703.428571428│9848          │14         │26.714285714285│
├──────────────────────┼─────────────┼──────────────┼───────────┼───────────────┤
```

Chaque approche utilise les données les plus pertinentes pour proposer des jeux (le contenu s'il n'y a pas assez de recommandations et les recomandations s'il y en a suffisament).
