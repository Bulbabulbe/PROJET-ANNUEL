# SharCode — Présentation du projet

---

## L'idée de départ

Tout le monde a entendu parler de l'importance d'apprendre à coder. Les écoles commencent à l'intégrer, les collèges utilisent Scratch depuis quelques années, et Python arrive progressivement au lycée. Mais entre les deux, il y a un vide.

Scratch, c'est de la programmation par blocs visuels. C'est bien pour comprendre qu'un programme c'est une suite d'instructions. Mais dès qu'on passe à un vrai langage texte comme Python, le choc est brutal : syntaxe en anglais, erreurs incompréhensibles, règles d'indentation invisibles, et une documentation quasi entièrement en anglais.

Beaucoup d'élèves décrochent à ce moment-là. Pas parce qu'ils n'ont pas les capacités — mais parce qu'ils se retrouvent à apprendre deux choses en même temps : la logique de la programmation, et l'anglais technique.

**SharCode est né de cette observation.**

---

## Ce qu'on a fait

On a construit un langage de programmation dont la syntaxe est en français courant, accompagné d'un environnement pour apprendre à l'utiliser.

L'idée centrale : retirer la barrière de la langue pour que l'élève puisse se concentrer sur ce qui compte vraiment — la logique.

```
age vaut 17

si age >= 18 alors
    ecrire "Tu es majeur."
sinon
    ecrire "Tu seras majeur dans " + (18 - age) + " an(s)."
fin
```

Ce code se lit comme du français. Un élève de 4ème qui n'a jamais codé comprend ce qu'il fait sans qu'on lui explique.

SharCode supporte les variables, les conditions, les boucles, les fonctions, la récursivité. C'est un vrai langage de programmation, pas un jouet. Et il est accompagné d'une interface web avec des leçons progressives, une console de sortie, et des exemples prêts à l'emploi.

---

## Ce que SharCode n'est pas

On ne prétend pas avoir inventé quelque chose de révolutionnaire. SharCode ressemble à Python — et c'est voulu.

Le but n'est pas de remplacer Python. Le but est de servir de **passerelle**. Un élève qui maîtrise SharCode connaît déjà toute la logique : variables, conditions, boucles, fonctions. Passer à Python ensuite, c'est apprendre de nouveaux mots pour des concepts qu'il connaît déjà. Ce qui prend des mois devient une affaire de semaines.

La différence concrète avec Python, c'est surtout ça :
- Les mots-clés sont en français (`si`, `alors`, `fin`, `tant que`, `ecrire`)
- Les blocs se ferment avec `fin` — pas d'erreurs d'indentation invisibles
- `vaut` pour assigner une valeur, `==` pour comparer — la confusion `=` / `==` qui fait trébucher tous les débutants n'existe plus
- Les messages d'erreur sont en français et rédigés pour être compris par un élève

---

## Pourquoi ça a du sens à l'école

En France, le programme de technologie au collège intègre Scratch dès la 6ème. C'est une bonne chose. Mais il n'existe rien entre Scratch et Python pour accompagner la transition.

```
  6ème / 5ème          4ème / 3ème             Lycée
    Scratch        →    SharCode        →     Python / JS
  (blocs visuels)    (texte, français)       (texte, anglais)
```

SharCode occupe exactement cette case vide. Il apporte la structure d'un vrai langage texte — fichiers, fonctions, logique formelle — dans une forme accessible à un élève de 13-15 ans qui n't maîtrise pas forcément l'anglais.

Pour un enseignant de technologie, l'intégration est simple : SharCode s'utilise dans n'importe quel navigateur, sans installation. Les élèves ouvrent un lien, les leçons sont intégrées, et ils peuvent commencer à coder en quelques minutes. L'enseignant n'a pas besoin d'être développeur pour l'utiliser en classe.

---

## A qui on s'adresse

**Les élèves de 4ème et 3ème** sont la cible principale. Ils ont déjà vu Scratch, ils sont prêts pour aller plus loin, mais Python directement c'est trop tôt.

**Les enseignants de technologie** qui cherchent un outil pour aller au-delà de Scratch sans plonger directement dans Python.

**Les adultes en reconversion** qui veulent apprendre à coder sans que la barrière de l'anglais soit le premier obstacle.

Et plus largement, les **320 millions de francophones dans le monde** pour qui les outils d'apprentissage du code sont quasi exclusivement en anglais. L'Afrique francophone en particulier est un marché massif, jeune, et sous-équipé en ressources pédagogiques numériques dans sa langue.

---

## Les personas

Trois profils utilisateurs ont guidé les choix de conception du projet.

**Persona 1 — Les collégiens (4ème / 3ème)**
Des élèves qui ont déjà vu Scratch au collège et sont prêts à aller plus loin, mais pour qui Python est encore trop difficile d'accès. Ils se perdent dans les erreurs en anglais et les règles d'indentation. Ils veulent progresser mais se découragent vite dès qu'ils ne comprennent pas ce qui ne va pas. SharCode leur permet de rester dans une syntaxe lisible en français, avec des erreurs explicites dans leur langue.

**Persona 2 — Les adultes en reconversion professionnelle**
Des personnes qui veulent apprendre à coder pour évoluer professionnellement, mais pour qui la barrière de l'anglais technique est un frein réel. Leur niveau d'anglais est souvent fonctionnel, mais pas suffisant pour assimiler en même temps une langue étrangère et des concepts techniques nouveaux. SharCode leur permet de se concentrer sur la logique sans friction linguistique.

**Persona 3 — Les professeurs de technologie au collège**
Des enseignants qui utilisent Scratch avec leurs élèves de 6ème et 5ème et cherchent un outil pour la suite — quelque chose qui s'intègre naturellement dans leur cours sans qu'ils aient à être développeurs eux-mêmes. Ils ont besoin d'un outil simple à déployer, avec des leçons déjà structurées qu'ils peuvent réutiliser ou adapter en classe.

---

## Architecture du projet

SharCode est composé de deux parties distinctes : l'interpréteur du langage et l'interface web.

```
PROJET ANNUEL/
├── frLang/                  # Interpréteur FrLang
│   ├── lexer.py             # Tokenisation — découpe le code en tokens
│   ├── parseur.py           # Parser récursif descendant — construit l'AST
│   ├── noeud.py             # Noeuds de l'arbre syntaxique (dataclasses)
│   ├── interpreteur.py      # Tree-walker interpreter — exécute l'AST
│   └── erreurs.py           # Messages d'erreur en français
│
├── app.py                   # Serveur Flask — API web + routes
├── main.py                  # Point d'entrée CLI (mode fichier + REPL)
├── database.py              # Gestion de la base de données SQLite
│
├── templates/               # Pages HTML (interface web)
├── static/                  # CSS, JavaScript, assets
│
└── exemples/                # Fichiers .frl d'exemple

---

**Flux d'exécution :** Le code source FrLang passe par le lexer (tokenisation), puis le parseur (construction de l'AST), puis l'interpréteur (exécution). Chaque étape produit des erreurs en français si quelque chose ne va pas. L'interface web communique avec l'interpréteur via le serveur Flask, qui reçoit le code, l'exécute en Python côté serveur, et renvoie la sortie au navigateur.

---

## Qui a fait quoi

Le projet est le fruit d'un travail en groupe de trois. Chaque membre a pris en charge un aspect distinct du projet.

**Raphaël Jacq — Développement de l'application**
Raphaël a développé l'intégralité de l'application : l'interpréteur FrLang (lexer, parseur, AST, interpréteur, gestion d'erreurs), le serveur Flask, l'interface web, et la base de données. Il a également conçu l'architecture globale du projet et les exemples de code.

**Théo Corbun — Aspect commercial**
Théo a pris en charge la dimension commerciale du projet : étude de marché, positionnement de l'offre, identification des cibles (établissements scolaires, plateformes EdTech), et construction du modèle économique. Il a également travaillé sur la stratégie de distribution et les arguments de vente pour convaincre des partenaires potentiels.

**Maxime Nectoux — UX et fonctionnalités supplémentaires**
Maxime a travaillé sur l'expérience utilisateur : parcours d'apprentissage, structure des leçons, ergonomie de l'interface, et accessibilité pour des utilisateurs non-techniques. Il a également proposé et défini les fonctionnalités supplémentaires à intégrer pour améliorer l'outil pédagogique.

---

## Ce qu'on a construit concrètement

- Un **interpréteur complet** écrit en Python : lexer, parser, arbre syntaxique, interpréteur, gestion d'erreurs
- Une **interface web** avec éditeur de code, console de sortie, et entrées clavier simulées
- **6 leçons progressives** intégrées à l'interface, de la variable à la fonction récursive
- **5 exemples** prêts à l'emploi (jeu, calculatrice, algorithmes)
- Une **documentation complète** du langage

Le tout fonctionne en local, sans connexion internet, sans installation pour l'utilisateur final — juste un navigateur.

---

## La suite

Ce qu'on aimerait ajouter si le projet continue :

- Les listes (tableaux) pour stocker plusieurs valeurs
- Un mode "pas à pas" pour voir le programme s'exécuter ligne par ligne
- La coloration syntaxique dans l'éditeur
- Une version hébergée accessible par URL, sans rien à installer
- Des exercices avec correction automatique pour les enseignants

---

## En résumé

SharCode, c'est la réponse à une question simple : pourquoi est-ce qu'apprendre à coder en France demande de savoir lire l'anglais ?

Ce n'est pas un projet qui cherche à révolutionner la programmation. C'est un outil pratique, pensé pour un contexte précis, qui comble un vide réel dans les parcours d'apprentissage francophones. Le langage est volontairement proche de Python — parce que l'objectif final, c'est que les élèves arrivent en Python avec de l'avance, pas qu'ils restent sur SharCode.

> *"Coder comme on parle."*
