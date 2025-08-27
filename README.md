# Solveur Bus WEI

Ce projet contient le script pour l'attribution des équipes dans les bus pour le WEI.

Le code prinicpal se situe dans le fichier `main.py`.

Il va lire les fichiers du dossier `data/`, lancer le solveur et exporter les résultats dans un dossier `output/`.

## Installation

Prérequis : Avoir une version de python3 installée sur son poste.

1. Ouvrir un terminal de commande
2. Récupérer le repo sur son poste : `git clone git@github.com:FlashD10/buswei.git`
3. Se déplacer dans le dossier du projet : `cd integration-bus`
4. Créer un environnement virtuel : `python3 -m venv .venv`
5. Activer l'environnement virutel : `source .venv/bin/activate`
6. Installer les dépendances : `pip install -r requirements.txt`
7. Charger les données dans le dossier `data/`
8. Exécuter le script : `python main.py`

La création de l'environnement virtruel (étapes 4 et 5) n'est pas nécessaire mais permet d'éviter de mélanger différentes versions de librairies avec d'éventuels d'autres projets python.
Dans ce cas, pour exécuter le script il faudra lancer la commande `python3 main.py`.

## Données

Les 3 fichiers de données vierges sont présents dans le dossier `template/`. Il faut les copier,
les modifier et les mettre dans le dossier `data/` avant de lancer le script.

Le fichier `bus.csv` contient les informations des bus.
- numero *entier* : Le numéro / id du bus
- capacite *entier* : La capacite du bus

Le fichier `equipes.csv` contient les informations des équipes.
- numero *entier* : Le numéro / id de l'équipe
- nom *string* : Le nom de l'équipe
- faction *-1 ou 1* : La faction de l'équipe

Le fichier `participants.csv` contient les informations des participants.
- id *entier* : L'id du participant
- prenom *string* : Le prenom du participant
- nom *string* : Le nom du participant
- mail *string* : L'adresse mail du participant
- telephone *string* : Le numero de téléphone du participant
- nouveau *booléen* : Si le participant est nouveau ou non
- ce *booléen* : Si le participant est CE ou non
- num_equipe *entier* : Le numéro de l'équipe du participant (vide si pas d'équipe)
- orga *booléen* : Si le participant est orga ou non
- bénévole *booléen* : Si le participant est bénévole ou non
- majeur *booléen* : Si le participant est majeur ou non
- bus_manual *entier* : Affectation manuelle du participant dans un bus


## Résultats

Le script va renvoyer 3 types de fichiers résultats.

Un fichier `export_bus.csv` qui contient pour chaque bus sa capacité totale, son nombre de places occupées dans un bus et la liste de ses équipes.

Un fichier `export_participant.csv` qui contient pour chaque participant les mêmes informations que le fichier de données `participant.csv` avec en plus un colonne `bus_affectation` qui contient l'affecation finale du bus pour chaque participant.

Un fichier `bus_x.csv` par bus qui contient la liste des participants qui montent dans le bus *x*.