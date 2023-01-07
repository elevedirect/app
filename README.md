# EleveDirect

<img src="https://raw.githubusercontent.com/elevedirect/app/master/static/legal/logo.png">

EleveDirect est un client EcoleDirect open source (sous licence MIT)

Retrouvez ce projet à [eleve-direct.server.camarm.fr](http://eleve-direct.server.camarm.fr) ou [ed.camarm.fr](http://ed.camarm.fr).

## Fonctionnement:

Connectez-vous à votre compte EcoleDirect et retrouvez vos notes (et vos moyennes !), vos devoirs, votre carte de cantine et plus encore...

## Objectifs

- [x] Se connecter avec son compte EcoleDirect
- [x] Voir sa carte de cantine
- [x] Voir ses devoirs
- [x] Pouvoir cocher effectué sur un devoir
- [x] Voir ses notes
- [x] Voir ses moyennes avant la fin du semestre
- [x] Pouvoir télécharger sa carte de cantine
- [x] Voir les actualités
- [ ] Voir sa photo de profil
> - [x] Voir son emploi du temps (abandonné car inutilisé)

## Précisions:

Aucuns cookies hormis ceux qui permettent l'interaction avec EcoleDirect sont stockés sur votre appareil.

Les données affichées proviennent directement d'EcoleDirect et les cartes de cantine sont simplement générées à partir de vos identifiants.

## Auto-hébergement:

Vous pouvez simplement lancer le serveur web et EleveDirect en suivant ces instructions:

1. Prérequis :<br>
EleveDirect est développé en Python avec Flask ;<br>
Il vous faudra donc installer python ainsi que les librairies dépendantes :
```shell
pip install -r requirements.txt
```
2. Lancer le script avec python
```shell
python3 main.py --config config.ini
```
3. Visiter http://localhost:9090 et voilà !

## Aides / mentions légales:

Ce projet est développé par camarm (CAMARM inc.), et propulsé par Labse, qui nous offre l'hébergement et la maintenance du site.

<img alt="Powered By Labse" src="https://www.camarm.dev/powered-by-labse" title="Labse" width="250"/>
