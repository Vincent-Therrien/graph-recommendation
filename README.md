# Graph-recommendation

Auteurs :
- David Ross (ROSD08058900)
- Vincent Therrien (THEV17129807)

Système de recommandation de données basé sur des graphes.


## Données

L'ensemble de données choisi pour ce projet est le `Steam Video Game and Bundle Data` accessible à
l'adresse https://cseweb.ucsd.edu/~jmcauley/datasets.html#steam_data. Nous utilisons la version 1.
Ces données contiennent des commentaires de joueurs australiens sur des jeux vidéos du distributeur
Steam.


### Installation des données

Le jeux de données contient un fichier de commentaires des utilisateurs et un ficheir d'objets
détenus par les utilisateurs.

Téléchargez le fichier `Version 1: Review Data` à l'adresse
`https://datarepo.eng.ucsd.edu/mcauley_group/data/steam/australian_user_reviews.json.gz` avec `wget`
et décompressez-le avec `gunzip`, comme le montre la cellule suivante :

```
wget https://datarepo.eng.ucsd.edu/mcauley_group/data/steam/australian_user_reviews.json.gz
gunzip australian_user_reviews.json.gz
```

Le fichier contient des critiques de jeux des utilisateurs formatées de la manière suivante :

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

Téléchargez ensuite le fichier `Version 1: User and Item Data` à l'adresse
`https://datarepo.eng.ucsd.edu/mcauley_group/data/steam/australian_users_items.json.gz` avec `wget`
et décompressez-le avec `gunzip` :

```
wget https://datarepo.eng.ucsd.edu/mcauley_group/data/steam/australian_users_items.json.gz
gunzip australian_users_items.json.gz
```

Le fichier contient le catalogue de jeux des utilisateurs sous la forme d'objets
JSON formatés de la manière suivante :

```
{
    'user_id': <ID>,
    'items_count': <count>,
    'steam_id': <Steam ID>,
    'user_url': URL,
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


### Pré-traitement des données

Cette étape vise à transformer les données contenue dans les fichiers JSON en un format CSV
utilisable par `Neo4j`. La commande suivante permet de pré-traiter les données :

```
python3 preprocess.py  # Linux
py preprocess.py  # Windows
```

Le script `preprocess.py` génère quatre fichiers CSV à partir des données originale :

- `user_nodes.csv` : Noeuds d'identifiants de tous les utilisateurs.
- `item_nodes.csv` : Noeuds d'identifiants de tous les items (c-à-d des jeux).
- `review_relations.csv` : Relations de critiques des utilisateurs envers les jeux.
- `item_relations.csv` : Relations entre les joueurs et le temps de jeu.


## Importation des noeuds et relations dans Neo4j

Cette section présente comment importer les fichiers générés dans la section précédente dans une
base de données `Neo4j`. Il faut effectuer les étapes suivantes :

- Ouvrir `Neo4j` desktop
- Créer un nouveau projet, puis créer une nouvelle database (DBMS) en cliquant sur `
- Lancer (start) la DBMS
- Une fois la DBMS en marche, choisir "Terminal" dans le menu déroulant "Open". Cette opération
  ouvre un terminal `Neo4j` dans le répertoire de la DBMS
  (par exemple, `C:/Users/david/.Neo4jDesktop/relate-data/dbmss/dbms-005f3d71-44eb-4db3-960e-6d9f06ff9713`)
  qui contient un dossier "import". Copier les 4 fichiers produits par preprocess.py dans ce
  dossier. Par exemple, sous Linux, en supposant que `<import>` représente le répertoire
  d'importation de la DBMS, exécuter les commandes :
  - `cp user_nodes.csv <import>`
  - `cp item_nodes.csv <import>`
  - `cp review_relations.csv <import>`
  - `cp item_relations.csv <import>`
- Vérifier dans le fichier `conf/neo4j.conf` (situé dans le répertoire de la DBMS) que la ligne 22
  (`<server.directories.import=import>`) n'est pas masquée.
- Arrêter la DBMS dans `Neo4j desktop` et lancer le commande suivante dans le terminal `Neo4j` dans
  le directoire de la DBMS :
  `bin\neo4j-admin database import full --nodes=import/user_nodes.csv --nodes=import/item_nodes.csv --relationships=import/review_relations.csv --relationships=import/item_relations.csv --overwrite-destination --skip-bad-relationships --skip-duplicate-nodes`
- Relancer la DBMS. Il est maintenant possible d'interagir avec le graphe dans `Neo4j browser`.
