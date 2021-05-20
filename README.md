# 
![Python 3.9.5](https://img.shields.io/badge/python-3.9.5%2B-brightgreen)
![Paramiko 2.7.2](https://img.shields.io/badge/Paramiko-2.7.2-lightgrey)


# Cross-platform-import-log

Cet outil permet d'automatiser **l'importation des logs system Windows ou Linux** depuis un système Windows ou Linux. 

## Compatibilité

Testé sous Windows 10, Debian 10 et Ubuntu Desktop 20.04.

## Pré-requis

Installation du module **Paramiko** :
```
pip install paramiko
```

Accès **SSH** pour vous connecter sur les machines distantes.

## Lancement

Windows :

```
python main.py
```

Linux :

```
python3 main.py
```

## Exemples de fonctionnement

Linux :

![Menu](https://zupimages.net/up/21/20/61mv.png)

Windows :

![Menu](https://zupimages.net/up/21/20/w90d.png)

## Construction

Le script contient deux fonctions :
<br/>
- **networkscan** : ping la plage définie d'une adresse réseau jusqu'à 254 machines et affiche sous forme de tableau les machines disponibles avec les adresses IP.
<br/>
- **runningSSH** : effectue la connexion ssh sur l'hôte choisi et importe le fichier de log système.

## Licence
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
