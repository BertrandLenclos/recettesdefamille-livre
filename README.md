pour génerer la page :

    python3 main.py

pour le serveur :

    python3 -m http.server

Pour les pages spéciales : il faut d'abord les créer sur le wiki puis les lister sur cette page IndexDuLivre (tout y est expliqué)
Le script python va sur IndexDuLivre pour savoir quoi mettre dans le livre et dans quel ordre.
Il y aura un petit point a faire sur comment on style ces pages. Mais sinon tu devrait pouvoir être autonome.

Pour les images, il faut que tu les mettes dans les recettes en utilisant le modèle Modèle:ImageDuLivre tu as une explication sur la page du modèle.

    
{{ImageDuLivre
|image1=http://recettesdefamille.wiki/images/7/7f/ACCRASDSC02014.jpg
|position=avant
}}

Attention il faut que tu mette des liens absolus (e.g. qui commencent par https://recettesdefamille.wiki/...) sinon ca marchera pas.
