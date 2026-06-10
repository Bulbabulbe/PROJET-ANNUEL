# SharCode 🦈
### Le premier langage de programmation en français naturel

> *"Coder comme on parle."*

---

## Pourquoi SharCode existe

### Le problème

Aujourd'hui, apprendre à programmer c'est faire face à **deux obstacles en même temps** :

1. **Comprendre la logique** — les conditions, les boucles, les fonctions, les variables
2. **Le faire en anglais** — `if`, `while`, `def`, `return`, `True`, `False`...

Pour les **320 millions de francophones** dans le monde — dont une grande partie en Afrique subsaharienne, au Maghreb, en Belgique, au Canada — cette double barrière est un frein réel. Des études en sciences de l'éducation montrent qu'apprendre un concept dans sa langue maternelle réduit significativement la charge cognitive. Autrement dit : quand t'as pas à traduire dans ta tête, tu peux mieux réfléchir.

**SharCode enlève l'obstacle de la langue pour que les apprenants se concentrent sur l'essentiel : la logique.**

---

### Le chaînon manquant dans les programmes scolaires

En France, le programme de technologie au collège intègre **Scratch** dès la 6ème. C'est un excellent outil pour découvrir la programmation par blocs visuels. Mais il y a un problème : le saut entre Scratch et les vrais langages de programmation (Python, JavaScript) est brutal.

```
   6ème / 5ème          4ème / 3ème             Lycée
  ┌─────────────┐      ┌─────────────┐        ┌─────────────┐
  │   Scratch   │ ───▶ │  SharCode   │ ──────▶│  Python /   │
  │   (blocs)   │      │  (texte,    │        │     JS      │
  │   visuel    │      │  français)  │        │  (anglais)  │
  └─────────────┘      └─────────────┘        └─────────────┘
   "Je glisse           "J'écris du            "Je code comme
    des blocs"           vrai code,             un pro"
                         dans ma langue"
```

Aujourd'hui, ce chaînon du milieu **n'existe pas**. Les élèves passent directement de glisser des blocs à écrire du Python en anglais — et beaucoup décrochent à ce moment-là.

**SharCode est précisément cette transition.** Il apporte :
- La **vraie structure** d'un langage texte (fichiers, fonctions, logique)
- Les **bonnes pratiques** de programmation (nommer ses variables, découper son code en fonctions)
- Dans une **syntaxe française et lisible** qui ne met pas en échec

Un élève qui maîtrise SharCode comprend déjà les structures fondamentales. Passer à Python devient alors une simple question de traduction, pas d'apprentissage.

---

### Notre vision

Un lycéen à Dakar, une mère de famille à Lyon qui veut se reconvertir, un prof de maths au Maroc qui veut initier ses élèves au code — tous peuvent aujourd'hui écrire :

```
age vaut 17

si age est superieur ou egal a 18 alors
    ecrire "Tu peux voter."
sinon
    ecrire "Encore " plus 18 moins age plus " an(s) a attendre."
fin
```

Et ça tourne. Pas besoin de savoir ce que veut dire `elif` ou `>=`. Pas besoin d'anglais.

### Pourquoi "SharCode" ?

Le requin (*shark*) apprend vite, il est efficace, il va droit au but. SharCode c'est pareil : un outil tranchant pour rentrer dans le code sans se perdre dans les détails. Et ça mord.

---

## A qui s'adresse SharCode

| Public | Besoin | Ce que SharCode apporte |
|---|---|---|
| **Élèves de 4ème / 3ème** | Passer de Scratch (blocs) à un vrai langage texte | La transition naturelle, en français, sans rupture brutale |
| **Élèves de lycée** | Arriver en cours de Python avec les bases déjà solides | Maîtriser la logique avant de changer de langue |
| **Enseignants de technologie** | Un outil qui s'intègre dans le programme officiel | Un langage pédagogique pensé pour la classe |
| **Adultes en reconversion** | Entrer dans la programmation sans barrière | Une courbe d'apprentissage douce |
| **Francophones hors Europe** | Accès à l'informatique dans leur langue | Un langage pensé pour les 320M de francophones |

---

## Ce qui différencie SharCode

| Outil | Ce qu'il fait | Limite |
|---|---|---|
| **Scratch** | Programmation visuelle par blocs | Pas du vrai code texte — on ne prépare pas à Python |
| **Python** | Vrai langage, très accessible | En anglais — trop grand saut depuis Scratch |
| **Blockly** | Blocs + code généré automatiquement | L'élève ne construit pas la logique lui-même |
| **SharCode** | Vrai code texte, en français courant, bonnes pratiques intégrées | Le chaînon qui manquait |

**Ni Scratch ni Python ne couvrent la zone de transition.** SharCode occupe exactement cet espace : du vrai code, dans la langue de l'élève, avec les mêmes concepts qu'un langage professionnel.

> Concrètement : un élève qui sait faire une boucle en SharCode sait déjà faire une boucle en Python. Il lui reste juste à apprendre les mots anglais.

---

## Installation

### Prérequis
- Python 3.9 ou supérieur (téléchargeable sur [python.org](https://python.org))
- Aucune autre dépendance

### Lancer SharCode

```bash
# Exécuter un programme SharCode
python main.py mon_programme.shc

# Mode interactif (taper du code ligne par ligne)
python main.py
```

---

## Documentation du langage

### Les variables

Une variable stocke une valeur. On l'assigne avec `vaut`.

```
# Nombre entier
score vaut 0

# Nombre décimal
pi vaut 3.14159

# Texte (chaîne de caractères)
prenom vaut "Alice"

# Booléen (vrai ou faux)
connecte vaut vrai
```

---

### Affichage et saisie

```
# Afficher une valeur
ecrire "Bonjour !"
ecrire score

# Afficher plusieurs choses en les combinant
ecrire "Ton score est : " plus score

# Demander une saisie à l'utilisateur
reponse vaut lire "Quel est ton prénom ? "
```

---

### Les opérations arithmétiques

| Opération | Mot-clé SharCode | Exemple |
|---|---|---|
| Addition | `plus` | `3 plus 4` → `7` |
| Soustraction | `moins` | `10 moins 3` → `7` |
| Multiplication | `fois` | `5 fois 6` → `30` |
| Division | `divise par` | `15 divise par 4` → `3.75` |
| Modulo (reste) | `modulo` | `10 modulo 3` → `1` |

```
resultat vaut 10 plus 5 fois 2
ecrire resultat
# Affiche : 20  (la multiplication est prioritaire)

# Forcer un ordre avec des parenthèses
resultat vaut (10 plus 5) fois 2
ecrire resultat
# Affiche : 30
```

---

### Les conditions

```
si condition alors
    # instructions si vrai
sinon si autre_condition alors
    # instructions si cette condition est vraie
sinon
    # instructions si tout est faux
fin
```

**Exemples :**

```
note vaut 14

si note est superieur ou egal a 16 alors
    ecrire "Très bien !"
sinon si note est superieur ou egal a 10 alors
    ecrire "Admis"
sinon
    ecrire "Insuffisant"
fin
```

**Opérateurs de comparaison :**

| Comparaison | SharCode |
|---|---|
| Égal à | `est egal a` |
| Différent de | `est different de` |
| Inférieur à | `est inferieur a` |
| Supérieur à | `est superieur a` |
| Inférieur ou égal | `est inferieur ou egal a` |
| Supérieur ou égal | `est superieur ou egal a` |

**Opérateurs logiques :**

```
# Combiner des conditions
si age est superieur a 18 et possede_permis est egal a vrai alors
    ecrire "Tu peux conduire."
fin

si jour est egal a "samedi" ou jour est egal a "dimanche" alors
    ecrire "C'est le week-end !"
fin

# Inverser une condition
si non connecte alors
    ecrire "Tu n'es pas connecté."
fin
```

---

### Les boucles

#### Boucle `pour` — répéter un nombre de fois précis

```
pour variable de debut a fin
    # instructions répétées
fin
```

```
# Afficher les nombres de 1 à 10
pour i de 1 a 10
    ecrire i
fin

# Table de multiplication de 8
pour i de 1 a 10
    ecrire "8 x " plus i plus " = " plus 8 fois i
fin
```

#### Boucle `tant que` — répéter jusqu'à ce qu'une condition soit fausse

```
tant que condition
    # instructions répétées
fin
```

```
# Deviner un nombre
secret vaut 42
reponse vaut 0

tant que reponse est different de secret
    reponse vaut nombre(lire "Devine le nombre : ")
    si reponse est inferieur a secret alors
        ecrire "Trop petit !"
    sinon si reponse est superieur a secret alors
        ecrire "Trop grand !"
    fin
fin

ecrire "Bravo, tu as trouvé !"
```

---

### Les fonctions

Les fonctions permettent de réutiliser du code.

```
fonction nom_de_la_fonction(parametre1, parametre2)
    # instructions
    retourner valeur
fin
```

```
# Fonction sans retour
fonction saluer(prenom)
    ecrire "Bonjour, " plus prenom plus " !"
fin

saluer("Alice")
saluer("Bob")

# Fonction avec retour
fonction maximum(a, b)
    si a est superieur a b alors
        retourner a
    sinon
        retourner b
    fin
fin

grand vaut maximum(17, 42)
ecrire "Le plus grand est : " plus grand

# Fonction récursive (qui s'appelle elle-même)
fonction factorielle(n)
    si n est inferieur ou egal a 1 alors
        retourner 1
    fin
    retourner n fois factorielle(n moins 1)
fin

ecrire factorielle(10)
```

---

### Les fonctions natives

SharCode intègre des fonctions prêtes à l'emploi.

#### Conversion de types

| Fonction | Description | Exemple |
|---|---|---|
| `nombre(x)` | Convertit en nombre | `nombre("42")` → `42` |
| `texte(x)` | Convertit en texte | `texte(3.14)` → `"3.14"` |
| `booleen(x)` | Convertit en booléen | `booleen(0)` → `faux` |

#### Mathématiques

| Fonction | Description | Exemple |
|---|---|---|
| `arrondir(x, n)` | Arrondit à n décimales | `arrondir(3.14159, 2)` → `3.14` |
| `absolu(x)` | Valeur absolue | `absolu(0 moins 5)` → `5` |
| `racine(x)` | Racine carrée | `racine(16)` → `4` |
| `puissance(x, n)` | x à la puissance n | `puissance(2, 8)` → `256` |
| `minimum(a, b)` | Le plus petit | `minimum(3, 7)` → `3` |
| `maximum(a, b)` | Le plus grand | `maximum(3, 7)` → `7` |

#### Texte

| Fonction | Description | Exemple |
|---|---|---|
| `taille(x)` | Longueur d'un texte | `taille("bonjour")` → `7` |
| `majuscules(x)` | Tout en majuscules | `majuscules("abc")` → `"ABC"` |
| `minuscules(x)` | Tout en minuscules | `minuscules("ABC")` → `"abc"` |
| `contient(x, y)` | x contient-il y ? | `contient("bonjour", "jour")` → `vrai` |

---

### Les commentaires

Tout ce qui suit un `#` est ignoré par SharCode.

```
# Ceci est un commentaire
age vaut 25   # on peut aussi mettre un commentaire en fin de ligne
```

---

### Les valeurs spéciales

| Valeur | Signification |
|---|---|
| `vrai` | Booléen vrai (True) |
| `faux` | Booléen faux (False) |
| `rien` | Absence de valeur (None) |

---

## Messages d'erreur

SharCode affiche des erreurs en français, claires et précises.

```
# Si tu utilises une variable qui n'existe pas
ecrire x

# → Ligne 1 — La variable 'x' n'existe pas. As-tu pensé à l'initialiser ?
```

```
# Si tu divises par zéro
resultat vaut 10 divise par 0

# → Ligne 1 — Division par zéro impossible !
```

```
# Si tu te trompes dans la syntaxe
si x est egal 3 alors

# → Ligne 1 — Attendu 'a', mais j'ai trouvé '3'
```

---

## Exemple complet — Mini jeu

```
# ── Jeu : deviner un nombre secret ──────────
ecrire "=== Jeu du nombre secret ==="
ecrire ""

secret vaut 37
essais vaut 0
gagne vaut faux

tant que non gagne
    reponse vaut nombre(lire "Propose un nombre : ")
    essais vaut essais plus 1

    si reponse est egal a secret alors
        gagne vaut vrai
    sinon si reponse est inferieur a secret alors
        ecrire "Trop petit !"
    sinon
        ecrire "Trop grand !"
    fin
fin

ecrire ""
ecrire "Bravo ! Trouvé en " plus essais plus " essai(s) !"
```

---

## Roadmap — Ce qui vient ensuite

- [ ] **Listes** — stocker plusieurs valeurs (`ma_liste vaut liste(1, 2, 3)`)
- [ ] **Importer des fichiers** — découper un programme en plusieurs fichiers
- [ ] **Éditeur web** — coder SharCode directement dans le navigateur
- [ ] **Mode débogage** — exécuter pas à pas, voir les variables à chaque étape
- [ ] **Coloration syntaxique** — extension VS Code
- [ ] **Bibliothèque standard** — fonctions pour les fichiers, les dates, les maths avancées

---

## Contribuer au projet

SharCode est un projet étudiant ouvert. Si tu veux proposer une amélioration :

1. Identifie le fichier concerné dans `frLang/`
2. La logique de tokenisation est dans `lexer.py`
3. La grammaire est dans `parseur.py`
4. L'exécution est dans `interpreteur.py`

Chaque fichier est commenté pour être compris sans expérience préalable des compilateurs.

---

## Équipe

Projet réalisé dans le cadre du **Projet Annuel** — 2025/2026.

---

*SharCode — Coder comme on parle.*
