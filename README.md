Projet API

Sommaire 

1. Pré-requis
  - Langage et version
  - Dépendance
  - Moteur de base de donnée
2. Installation
  -  Cloner le projet depuis GitHub
  -  Installer pipenv
  -  Installer les dépendances avec pip
  -  Importation de la base de donnée
  -  Mise en place de l'environnement
3. Lancement
4. Utilisation


1. Pré-requis

  - Langage et version :
python 3.11.2

  - Dépendance :
pip 22.3.1
pipenv 2022.9.8

 - Moteur de base de donnée
MySQL 8.0.31

2.Installation

 - Cloner le projet GitHub

Creer un dossier, ouvrir un terminal et aller dans ce dossier.
Executer la commande suivante
> git clone https://github.com/julienles879/API.git

 - Installer le pipenv
   
Maintenant, ce rendre dans le projet avec la commande :

> cd api

> pipenv install

 - Installer les dépendances
   
> pip install -r requirements.txt

 - Mise en place de l'environnement
   
Ce rendre dans le sous-dossier api et créer ici un fichier .env 

# exemple de fichier .env
SECRET_KEY=votre_clé_secrete

DATABASES_ENGINE=django.db.backends.mysql
DATABASES_NAME=nom_de_la_base
DATABASES_USER=utilisateur_de_la_base
DATABASES_PASSWORD=mot_de_passe_de_la_base
DATABASES_HOST=127.0.0.1
DATABASES_PORT=3306

OPENAI_API_KEY=clé_secrete_api
SD_API_KEY=clé_secrete_stable_diffusion

3. Lancement

Revenir à la racine du projet (ou se trouve le fichier manage.py)

> pipenv shell

Cette commande peut vous changer de dossier et vous sortir du dossier dans lequel vous vous trouvez.
Dans ce cas, vous devez retourner dans le dossier racine, c'est à dire le dossier qui contient le fichier manage.py

> cd ..
(pour aller dans le dossier parent)

> cd nom_du_dossier
(pour aller dans le dossier enfant)

> py manage.py runserver

4. Utilisation

