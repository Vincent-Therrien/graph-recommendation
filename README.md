# graph-recommendation

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
https://datarepo.eng.ucsd.edu/mcauley_group/data/steam/australian_user_reviews.json.gz et
décompressez-le. Le fichier contient des critiques de jeux des utilisateurs formatées de
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

Téléchargez ensuite le fichier `Version 1: User and Item Data` à l'adresse
https://datarepo.eng.ucsd.edu/mcauley_group/data/steam/australian_users_items.json.gz et
décompressez-le. Le fichier contient le catalogue de jeux des utilisateurs sous la forme d'objets
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

Le script `preprocess.py` traite les fichiers
