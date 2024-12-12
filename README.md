# Graph-recommendation

Auteurs :
- David Ross (ROSD08058900)
- Vincent Therrien (THEV17129807)

Système de recommandation de données basé sur des graphes.


## Données

L'ensemble de données choisi pour ce projet est le `Steam Video Game and Bundle Data` accessible à l'adresse https://cseweb.ucsd.edu/~jmcauley/datasets.html#steam_data. Nous utilisons la version 1 (et les métadonnées de la version 2). Ces données contiennent des commentaires de joueurs australiens sur des jeux vidéos du distributeur Steam.


### Installation des données

Le jeux de données contient un fichier de commentaires des utilisateurs, un fichier d'objets (des jeux) détenus par les utilisateurs, et un fichier des métadonnées des jeux.

Dans un dossier vide, téléchargez les fichiers avec `wget` et décompressez-les avec `gunzip`, comme le montre la cellule suivante :

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
WITH j, row WHERE row.publisher IS NOT NULL
UNWIND split(row.publisher, ',') AS publisherSimple
MERGE (p:Publisher {name:publisherSimple})
MERGE (j) - [:PUBLISHED_BY] -> (p)
WITH j, row WHERE row.genres IS NOT NULL
UNWIND split(row.genres, ',') AS genre
MERGE (g:Genre {name:genre})
MERGE (j) - [:HAS_GENRE] -> (g)
WITH j, row WHERE row.tags IS NOT NULL
UNWIND split(row.tags, ',') AS tag
MERGE (t:Tag {name:tag})
MERGE (j) - [:TAGGED_AS] -> (t)
WITH j, row WHERE row.specs IS NOT NULL
UNWIND split(row.specs, ',') AS spec
MERGE (sp:Spec {name:spec})
MERGE (j) - [:HAS_SPECIFICATION] -> (sp)
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


### Recommandations basées sur le contenu

Mettons qu'on soit un nouveau utilisateur, on voudrait trouver lequels jeux sont les plus aimés. Ici on choisit les jeux qui ont un `Sentiment` global d'"Overwhelmingly positive" ou "Very positive" (les niveaux 3 et 4), un `Metascore` de 80+, et qui ont le plus d'utilisateurs qui les `Recommend`:

```
MATCH (s:Sentiment) <- [:HAS_SENTIMENT] - (j:GameID) <- [r:RECOMMENDS] - (u:UserID), (y:Year) <- [:RELEASED_IN] - (j) - [:HAS_SCORE] -> (m:Metascore)
WHERE j.title IS NOT NULL AND s.level >=3 AND m.name >= 80
WITH j, r
WHERE r.recommends = True AND j.price < 80 AND y.name > 2012
RETURN j.title AS most_popular, COUNT(*) AS times_rated
ORDER BY times_rated DESC LIMIT 10
```
Ce requête nous retourne la liste des jeux suivante:

│most_popular                      │times_rated│
│"Team Fortress 2"                 │3611       │
│"Counter-Strike: Global Offensive"│3475       │
│"Left 4 Dead 2"                   │731        │
│"Terraria"                        │723        │
│"Borderlands 2"                   │548        │
│"Portal 2"                        │371        │
│"Sid Meier's Civilization® V"     │332        │
│"Starbound"                       │332        │
│"PlanetSide 2"                    │330        │
│"Rocket League®"                  │260        │

On reconnait le jeu `Portal 2`, et on verifie qu'il est sortie en 2011:

```
match (j:GameID {title:"Portal 2"})
RETURN j
```

On veut donc trouver des jeux similaires qui sont sorties plus récemment. On commence par chercher les jeux qui partagent au moins un `Genre` ET un `Tag` avec Portal 2, et on limite la recherche aux jeux sorties après 2011 (avec cette condition on est confiant que notre recherche ne retournera pas `Portal 2`). Il y a beaucoup plus des Tags que des Genres, donc on utilise le quantité des Tags en commun comme indice de similarité. Notre recherche avec les deux conditions peut générer des Tags en duplicats, donc on COLLECT que les Tags DISTINCT

```
MATCH (new:GameID) - [:HAS_GENRE] -> (g:Genre) <- [:HAS_GENRE] - (j:GameID {title:"Portal 2"}) - [:TAGGED_AS] -> (t:Tag) <- [:TAGGED_AS] - (new),  (new) - [:RELEASED_IN] -> (y:Year)
WHERE y.name > 2011
WITH new.title AS recommendation, y.name AS year, COLLECT(DISTINCT t.name) AS tags, COUNT(DISTINCT t.name) AS shared_tags
RETURN recommendation, year, shared_tags, tags
ORDER BY shared_tags DESC, year DESC LIMIT 20
```

Ce requête nous retourne la liste des jeux suivante (sans la colonne 'tags' pour lisibilité) :

│recommendation                                     │year│shared_tags│
│"Portal Stories: Mel"                              │2015│15         │
│"Thinking with Time Machine"                       │2014│15         │
│"Borderlands: The Pre-Sequel"                      │2014│14         │
│"Polarity"                                         │2014│14         │
│"Aperture Tag: The Paint Gun Testing Initiative"   │2014│14         │
│"LEGO® STAR WARS™: The Force Awakens"              │2016│13         │
│"Who's Your Daddy"                                 │2015│12         │
│"Sanctum 2"                                        │2013│12         │
│"Half Dead"                                        │2016│11         │
│"Battleborn"                                       │2016│11         │
│"Saints Row: Gat out of Hell"                      │2015│11         │
│"LEGO® The Hobbit™"                                │2014│11         │
│"BattleBlock Theater®"                             │2014│11         │
│"Only If"                                          │2014│11         │
│"Tom Clancy’s Splinter Cell Blacklist"             │2013│11         │
│"Resident Evil Revelations / Biohazard Revelations"│2013│11         │
│"Interstellar Marines"                             │2013│11         │
│"Borderlands 2"                                    │2012│11         │
│"Rocketbirds: Hardboiled Chicken"                  │2012│11         │
│"Natural Selection 2"                              │2012│11         │


D'un premier coup, on voit que `Borderlands 2` à été trouvé par nos deux recherches, donc on peut imaginer que c'est un bon choix a essayer premièrement.


### Recommandations par filtrage collaboratif

Ici on peut faire 1 ou 2 requêtes avec le filtrage collaboratif. Par exemple, choisir un UserID aléatoire, utiliser les publishers, genres, tags, time_played, recommendations des jeux pour identifier des utilisateurs similaires (soit tout, ou peut-être les 1000 plus similaires). Ensuite, générer une liste des jeux que ces utilisateurs ont joué le plus, qu'utilisater X n'a jamais joué (playtime does not existe or == 0), filtré par score, # recommendations, sentiment, etc... mais en order de total playtime (en disant qu'on a deja filtré les jeux pour qualité, similarité, donc on veut suggérer les jeux les plus joué).

Ici est une liste de quelques utilisateurs avec > 500 games owned (et des noms que j'ai aimé) donc 
uthequeenpanda
uTheKiwiMantis
uTacticalCrayon
uFEEEEESH
ukittenwithmittens
ukirbysmashed
uNotForPikachu

Et ici des utilisateurs avec 50+ jeux et 5+ recommendations (le max # des recommendations est 20)
uarmouredmarshmallow
uKebabsaregood

match (u:UserID) - [r:RECOMMENDS] -> (:GameID) 
where u.games_owned > 50
with u, count(r) as recs
where recs > 5
return u, recs

```
// Select a random user
MATCH (user1:UserID)
ORDER BY RAND()
LIMIT 1

// Calculate a similarity score
MATCH (user1:UserID)
WITH user1 LIMIT 1000 // Process 1000 users at a time
MATCH (user1) - [:RECOMMENDS] -> (game:GameID) <- [:RECOMMENDS] - (user2:UserID)
WHERE user1 <> user2
WITH user1, user2, COUNT(game) AS sharedGamesCount
WHERE sharedGamesCount > 0
WITH user1, user2, sharedGamesCount
MATCH (user1) - [:RECOMMENDS] -> (:GameID)
WITH user1, user2, sharedGamesCount, COUNT(*) AS totalGames1
MATCH (user2) - [:RECOMMENDS] -> (:GameID)
WITH user1, user2, sharedGamesCount, totalGames1, COUNT(*) AS totalGames2
WITH user1, user2, sharedGamesCount, totalGames1, totalGames2,
     (sharedGamesCount * 1.0) / (totalGames1 + totalGames2 - sharedGamesCount) AS similarityScore
RETURN user1.id AS User1, user2.id AS User2, similarityScore
ORDER BY similarityScore DESC
LIMIT 10
```

On obtient un résultat similaire à l'extrait suivant :

```
╒════════════════════╤═════════════════════════╤═══════════════════╕
│User1               │User2                    │similarityScore    │
╞════════════════════╪═════════════════════════╪═══════════════════╡
│"u76561198075132070"│"uFORTHMINGUTH"          │0.6666666666666666 │
├────────────────────┼─────────────────────────┼───────────────────┤
│"u76561198075132070"│"u76561198122884898"     │0.5                │
├────────────────────┼─────────────────────────┼───────────────────┤
│"u76561198075132070"│"u76561198088785160"     │0.42857142857142855│
├────────────────────┼─────────────────────────┼───────────────────┤
│"u76561198075132070"│"u76561198081343863"     │0.3333333333333333 │
├────────────────────┼─────────────────────────┼───────────────────┤
│"u76561198075132070"│"uonce-i-was-7-years-old"│0.3333333333333333 │
└────────────────────┴─────────────────────────┴───────────────────┘
```


### Recommandations basées sur le similarité entre les utilisateurs

En disant qu'on a joué à Borderlands 2 et on veut trouver des jeux similairement joués, on décide d'utiliser un calcul de similarité Pearson pour en chercher, basé sur des jeux avec un similairité de total_playtime. On utilise la corrélation de Pearson pour adapter a la variabilité de playtime entre utilisateur.  
Apres l'avoir essayé, il y avait un probleme be memoire en utlisant Borderlands 2 comme jeu de reference (avec 9524 joueurs), donc apres avoir généré une liste des jeux similaires (qui partage au moins un Genre et un Tag) avec moins de 8000 utilisateurs on a decidé d'utiliser `Ricochet` comme jeu de reference (qui a 7962 joueurs).

```
MATCH (BL2:GameID {title:"Ricochet"}) <- [p:PLAYED] - (u:UserID)
WITH (BL2), avg(p.playtime) AS BL2_mean
MATCH (BL2) <- [p1:PLAYED] - (u:UserID) - [p2:PLAYED] -> (new:GameID)
WHERE new.title IS NOT NULL
WITH BL2, BL2_mean, new, COLLECT({p1:p1, p2:p2}) AS playtime WHERE size(playtime) > 50
MATCH (new) <- [p:PLAYED] - (u:UserID)
WITH BL2, BL2_mean, new, avg(p.playtime) AS new_mean, playtime
UNWIND playtime AS p
WITH sum ((p.p1.playtime - BL2_mean) * (p.p2.playtime - new_mean)) AS numerator,
sqrt(sum((p.p1.playtime - BL2_mean)^2) * sum((p.p2.playtime - new_mean)^2)) AS denominator,
BL2, new WHERE denominator <> 0
RETURN BL2.title, new.title, numerator/denominator AS Pearson
ORDER BY Pearson DESC LIMIT 20
```



On a choisit d'utiliser un méthod hybrid de recommandation. On identifie un utilisateur au hasard et on calcule le quantité des jeux qu'il/elle a dans son compte Steam. Si l'utilisateur en a moins de 20, le recommendation est basée sur le contenu, en cherchant les jeux les plus populaires sorties dans les 5 dernieres années (nos données arretent en 2017).

Premierement, on établi une limite de prix a la 85e percentile (plus ou moins le moyen + 1xSD), en excluant les jeux gratuits. On identifie les jeux qui ont un `Sentiment` global d'"Overwhelmingly positive" ou "Very positive" (les niveaux 3 et 4), un `Metascore` de 80+. Ensuite, on limite les resultats aux jeux qui ont un prix dans la 85e percentile, qui s'est sortie apres 2012 (donc les dernieres 5 années des données), et qui ont des recommendations positives. On organise les resultats pour montrer les 10 jeux qui ont le plus d'utilisateurs qui les `Recommend`.

Si l'utilisateur a plus de 20 jeux...

```
MATCH (u:UserID)
ORDER BY RAND()
LIMIT 1
MATCH u - [p:PLAYED] -> (j:GameID)
CALL {
    WITH u, p
    WITH u, p
    WHERE COUNT(p) < 20
    MATCH (j:GameID) 
    WHERE j.price IS NOT NULL AND j.price > 0
    WITH percentileCont(j.price, 0.85) AS upper
    MATCH (s:Sentiment) <- [:HAS_SENTIMENT] - (j:GameID) <- [r:RECOMMENDS] - (:UserID), (y:Year) <- [:RELEASED_IN] - (j) - [:HAS_SCORE] -> (m:Metascore)
    WHERE j.title IS NOT NULL AND s.level >=3 AND m.name >= 80
    WITH j, r, y, upper
    WHERE r.recommends = True AND j.price <= upper AND y.name > 2012
    RETURN j.title AS most_popular, COUNT(r) AS times_recommended, y.name AS release_year, j.price AS price
    ORDER BY times_recommended DESC LIMIT 10

    UNION

    WITH u, p
    WITH u, p
    WHERE COUNT(p) >= 20
    MATCH (similarUser:UserID) - [:RECOMMENDS] -> (j:GameID) <- [:RECOMMENDS] - (u)
    WITH similarUser.id AS user, j.title AS game
    RETURN user, game
    LIMIT 5
}
```