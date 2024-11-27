# Graph-recommendation

Système de recommandation de données basé sur des graphes.


## Données

L'ensemble de données choisi pour ce projet est le `Steam Video Game and Bundle Data` accessible à
l'adresse https://cseweb.ucsd.edu/~jmcauley/datasets.html#steam_data. Nous utilisons la version 1.
Ces données contiennent des commentaires de joueurs australiens sur des jeux vidéos du distributeur
Steam.


### Installation des données

Le jeux de données contient un fichier de commentaires des utilisateurs et un ficheir d'objets
détenus par les utilisateurs.

Téléchargez le fichier `Version 1: Review Data` à l'adresse suivante et décompressez-le:  

**COMMENT FAIT SUR WINDOWS AVEC DES COMMANDES *copier-coller*?**

```
wget https://datarepo.eng.ucsd.edu/mcauley_group/data/steam/australian_user_reviews.json.gz
gunzip australian_user_reviews.json.gz
```

Le fichier contient des critiques de jeux des utilisateurs formatées de
la manière suivante :

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

Téléchargez ensuite le fichier `Version 1: User and Item Data` à l'adresse suivante et décompressez-le.  

**COMMENT FAIT SUR WINDOWS AVEC DES COMMANDES *copier-coller*?**
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

```
python preprocess.py
```

Le script `preprocess.py` traite les fichiers bruts présentés à la section précédente pour obtenir quatre fichiers CSV :

- `user_nodes.csv` : Noeuds d'identifiants de tous les utilisateurs.
- `item_nodes.csv` : Noeuds d'identifiants de tous les items (c-à-d des jeux).
- `review_relations.csv` : Relations de critiques des utilisateurs envers les jeux.
- `item_relations.csv` : Relations entre les joueurs et le temps de jeu.

## Importation des noeuds, relations

Ouvrir neo4j desktop, crée un nouveau projet si desiré, et ensuite un nouveau database (DBMS). Debute (start) ce DBMS, et un fois que ca roule, choisir "Terminal" du "Open" drop-down menu. Ca va ouvrir un terminal neo4j dans le directoire du DBMS (le mien est C:/Users/david/.Neo4jDesktop/relate-data/dbmss/dbms-005f3d71-44eb-4db3-960e-6d9f06ff9713), qui contient un dossier "import". Veulliez copier les 4 fichiers produits par preprocess.py dans ce dossier.  

En plus, dans le fichier conf/neo4j.conf, veulliez assurer que la ligne 22 <server.directories.import=import> n'est pas masquée.  

Une fois c'est fait, arreter le DBMS dans neo4j desktop et lancer le commande suivant dans le terminal neo4j dans le directoire du DBMS: 

```
bin\neo4j-admin database import full --nodes=import/user_nodes.csv --nodes=import/item_nodes.csv --relationships=import/review_relations.csv --relationships=import/item_relations.csv --overwrite-destination --skip-bad-relationships --skip-duplicate-nodes
```
Après, le DBMS peut être relancé et ouvert par neo4j browser