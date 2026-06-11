# Documentation Technique — SharCode

> Projet annuel 2025/2026 — Équipe : Raphaël Jacq (dev), Théo Corbun (business), Maxime Nectoux (UX)
> Dernière mise à jour : 2026-06-11

---

## Table des matières

1. [Vue d'ensemble](#1-vue-densemble)
2. [Architecture](#2-architecture)
3. [Stack technique](#3-stack-technique)
4. [Structure des fichiers](#4-structure-des-fichiers)
5. [L'interpréteur SharCode](#5-linterpréteur-sharcode)
6. [Application web Flask](#6-application-web-flask)
7. [Système de licences et rôles](#7-système-de-licences-et-rôles)
8. [IDE en ligne (Monaco Editor)](#8-ide-en-ligne-monaco-editor)
9. [Base de données](#9-base-de-données)
10. [Modes d'utilisation](#10-modes-dutilisation)
11. [Déploiement Docker](#11-déploiement-docker)
12. [Variables d'environnement](#12-variables-denvironnement)
13. [Routes API](#13-routes-api)
14. [Sécurité](#14-sécurité)
15. [Développement local](#15-développement-local)

---

## 1. Vue d'ensemble

**SharCode** est un langage de programmation éducatif en français naturel, accompagné d'un IDE web intégré style VS Code. Il s'adresse aux élèves francophones (12-18 ans) qui découvrent la programmation, en servant de pont entre Scratch et Python.

### Fonctionnalités principales

| Fonctionnalité | Description |
|---|---|
| Interpréteur | Lexer → Parser → Interpréteur en Python pur |
| IDE web VS Code | Monaco Editor, explorateur de fichiers, console intégrée, autocomplétion |
| 3 rôles | Admin (plateforme), Professeur (cours), Étudiant (apprentissage) |
| Système de licences | Codes d'accès par établissement, gestion par l'admin |
| Exercices | Création par le prof, soumission + correction par étudiant |
| CLI | Mode REPL et exécution de fichiers `.shc` (conservé) |

---

## 2. Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Navigateur (client)                │
│          HTML/CSS/JS vanilla  ─  Fetch API           │
└────────────────────┬────────────────────────────────┘
                     │  HTTP (port 5000)
┌────────────────────▼────────────────────────────────┐
│              Gunicorn  (WSGI, 2 workers)             │
│  ┌──────────────────────────────────────────────┐   │
│  │              Flask  (app.py)                  │   │
│  │  Routes auth  ·  Routes étudiant  ·  Routes prof│  │
│  │                    ▼                          │   │
│  │         Interpréteur SharCode (frLang/)       │   │
│  │      Lexer → Parser → AST → Interpréteur     │   │
│  └──────────────────────┬───────────────────────┘   │
│                         │                            │
│              SQLite  (database.py)                   │
│              /data/sharcode.db  [volume]             │
└─────────────────────────────────────────────────────┘

Mode CLI (indépendant du serveur web)
  python main.py            → REPL interactif
  python main.py prog.shc   → Exécution de fichier
  docker exec -it sharcode_web python main.py
```

### Pipeline d'exécution du code

```
Code source (texte)
      │
      ▼
   Lexer.tokeniser()          →  liste de Token
      │
      ▼
   Parseur.analyser()         →  AST (Noeud*)
      │
      ▼
   Interpreteur.executer()    →  effets de bord (stdout)
      │
      ▼
   Capture via redirect_stdout → JSON { succes, sortie }
```

---

## 3. Stack technique

| Couche | Technologie | Version |
|---|---|---|
| Langage backend | Python | 3.11 |
| Framework web | Flask | ≥ 3.0.0 |
| Serveur WSGI (prod) | Gunicorn | ≥ 21.2.0 |
| Base de données | SQLite 3 | intégré Python |
| Frontend | HTML5 / CSS3 / JS vanilla | — |
| Conteneurisation | Docker | 20+ |
| Orchestration | Docker Compose | v3.9 |

---

## 4. Structure des fichiers

```
PROJET-ANNUEL-main/
│
├── frLang/                   # Interpréteur du langage SharCode
│   ├── __init__.py
│   ├── lexer.py              # Tokenisation du code source
│   ├── parseur.py            # Analyse syntaxique → AST
│   ├── noeud.py              # Définitions des nœuds AST (dataclasses)
│   ├── interpreteur.py       # Exécution de l'AST
│   └── erreurs.py            # Exception ErreurFrLang
│
├── templates/                # Templates Jinja2
│   ├── index.html            # IDE principal
│   ├── login.html
│   ├── register.html
│   ├── dashboard_etudiant.html
│   ├── dashboard_prof.html
│   └── soumissions.html
│
├── static/
│   ├── css/
│   │   ├── style.css         # Thème principal (palette océan)
│   │   └── auth.css          # Styles pages auth
│   └── js/
│       └── main.js           # Logique frontend (éditeur, console, leçons)
│
├── exemples/                 # Programmes SharCode d'exemple
│   ├── bonjour.shc
│   ├── boucles.shc
│   └── fonctions.shc
│
├── app.py                    # Serveur Flask (routes web)
├── main.py                   # Point d'entrée CLI (REPL + fichier)
├── database.py               # Couche d'accès SQLite
├── generer_document.py       # Générateur de doc Word
├── requirements.txt          # Dépendances Python
│
├── Dockerfile                # Image Docker pour l'app web
├── docker-compose.yml        # Orchestration Docker
├── .env.example              # Template des variables d'environnement
├── .dockerignore             # Fichiers exclus du contexte Docker
│
├── README.md                 # Documentation du langage SharCode
├── PRESENTATION.md           # Présentation du projet
└── DOCUMENTATION_TECHNIQUE.md  ← ce fichier
```

---

## 5. L'interpréteur SharCode

### 5.1 Lexer (`frLang/lexer.py`)

Transforme le texte source en une liste de `Token(type, valeur, ligne)`.

Exemples de tokens produits :

| Code source | Type token |
|---|---|
| `age` | `IDENTIFIANT` |
| `vaut` | `VAUT` |
| `17` | `NOMBRE` |
| `"Alice"` | `CHAINE` |
| `si` | `SI` |
| `est superieur a` | `SUP` |
| `ecrire` | `ECRIRE` |

### 5.2 Parser (`frLang/parseur.py`)

Analyse descendante récursive. Produit un AST composé de nœuds définis dans `noeud.py`.

Principaux nœuds :

```
NoeudAffectation    age vaut 17
NoeudCondition      si … alors … sinon … fin
NoeudPourBoucle     pour i de 1 a 10 … fin
NoeudTantQue        tant que … fin
NoeudFonction       fonction nom(params) … fin
NoeudAppel          nom(args)
NoeudRetourner      retourner expr
NoeudEcrire         ecrire expr
NoeudLire           lire "invite"
NoeudBinaire        expr op expr
NoeudUnaire         non expr
```

### 5.3 Interpréteur (`frLang/interpreteur.py`)

Parcourt l'AST et exécute chaque nœud. Gère :

- **Environnements** : dictionnaire de variables par portée (closures)
- **Fonctions** : stockées comme objets Python, appelées récursivement
- **E/S** : `ecrire` → `print()`, `lire` → `input_fn()` (injectable pour les tests web)
- **Built-ins** : `nombre()`, `texte()`, `arrondir()`, `racine()`, `taille()`, `hasard()`, `minuscules()`, `majuscules()`, `contient()`, `partie()`

### 5.4 Gestion des erreurs (`frLang/erreurs.py`)

Toutes les erreurs remontent via `ErreurFrLang` avec des messages en français :

```
Erreur ligne 3 : variable 'age' non définie
Erreur ligne 7 : division par zéro
Erreur ligne 12 : argument manquant pour 'racine'
```

### 5.5 Syntaxe du langage

```sharcode
# Variables
age vaut 17
nom vaut "Alice"

# Conditions
si age est superieur ou egal a 18 alors
    ecrire "Majeur"
sinon
    ecrire "Mineur"
fin

# Boucle pour
pour i de 1 a 5
    ecrire i
fin

# Boucle tant que
reponse vaut ""
tant que reponse est different de "oui"
    reponse vaut lire "Continuer ? "
fin

# Fonctions
fonction carre(n)
    retourner n fois n
fin

ecrire carre(4)   # affiche 16
```

**Opérateurs arithmétiques** : `plus`, `moins`, `fois`, `divise par`, `modulo`

**Opérateurs de comparaison** : `est egal a`, `est different de`, `est inferieur a`, `est superieur a`, `est inferieur ou egal a`, `est superieur ou egal a`

**Opérateurs logiques** : `et`, `ou`, `non`

---

## 6. Application web Flask

### 6.1 Fichier `app.py`

Serveur Flask qui expose :
- Les pages HTML via Jinja2
- Une API JSON pour l'exécution du code (`/executer`)
- La gestion de session (cookie de session chiffré par `SECRET_KEY`)

La clé secrète est lue depuis `os.environ.get('SECRET_KEY', ...)` pour ne jamais être codée en dur en production.

### 6.2 Authentification

Système maison sans bibliothèque externe :

1. Hachage du mot de passe SHA-256 à l'inscription
2. Vérification à la connexion : `SHA-256(mdp_saisi) == hash_stocké`
3. Identifiant stocké en session Flask (`session['user_id']`)
4. Décorateur `login_requis(role=None)` sur chaque route protégée

> **Nota** : SHA-256 sans sel est acceptable pour un projet éducatif. En production réelle, préférer `bcrypt` ou `argon2`.

### 6.3 Rôles

| Rôle | Accès | Code d'inscription |
|---|---|---|
| `etudiant` | IDE, leçons, exercices assignés | aucun |
| `prof` | Dashboard, création d'exercices, consultation soumissions | `PROF2024` |

### 6.4 Exécution distante du code

Route `POST /executer` — reçoit `{ code, entrees }` en JSON :

1. Le code est passé au pipeline Lexer → Parser → Interpréteur
2. `stdout` est capturé via `contextlib.redirect_stdout`
3. `input()` est remplacé par `mock_input` qui consomme le tableau `entrees`
4. Réponse : `{ succes: true, sortie: "..." }` ou `{ succes: false, erreur: "..." }`

Cela permet d'exécuter des programmes interactifs côté serveur sans terminal.

---

## 7. Système de licences et rôles

### 7.1 Les trois rôles

| Rôle | Accès | Création |
|---|---|---|
| `admin` | Dashboard admin, gestion licences/utilisateurs | Créé automatiquement au démarrage |
| `prof` | IDE, dashboard prof, création exercices, consultation soumissions | Inscription avec un **code de licence** valide |
| `etudiant` | IDE, leçons, exercices, sauvegarde programmes | Inscription libre |

### 7.2 Compte admin par défaut

Créé automatiquement au premier démarrage :

| Champ | Valeur par défaut | Variable d'env pour changer |
|---|---|---|
| Email | `admin@sharcode.fr` | `ADMIN_EMAIL` |
| Mot de passe | `Admin2024!` | `ADMIN_PASSWORD` |

> **Changez ces valeurs en production** via les variables d'environnement.

Après login, l'admin est redirigé vers `/admin/dashboard` (et non vers l'IDE).

### 7.3 Licences

Une **licence** est un code d'accès créé par l'admin pour un établissement. Elle autorise un certain nombre de professeurs à s'inscrire.

**Format du code** : `SHC-XXXX-XXXX-XXXX` (généré aléatoirement)

**Cycle de vie** :
```
Admin crée la licence (label, max_profs, date_expiration?)
        ↓
Admin communique le code à l'établissement
        ↓
Prof s'inscrit avec le code → validé contre la table licences
        ↓
prof.licence_id = licences.id  (lien permanent)
        ↓
Admin peut désactiver/supprimer la licence
```

**Validation à l'inscription prof** :
1. Le code existe dans la table `licences`
2. La licence est `active = 1`
3. La date d'expiration n'est pas dépassée (si définie)
4. Le nombre de profs actifs n'atteint pas `max_profs`

### 7.4 Dashboard Admin

Accessible à `/admin/dashboard` — réservé `role = 'admin'`.

**Pages disponibles** :
- `/admin/dashboard` — statistiques globales (nb étudiants, profs, licences, exercices…)
- `/admin/licences` — CRUD licences (créer, désactiver, supprimer, copier code)
- `/admin/utilisateurs` — liste tous les utilisateurs, filtres par rôle, activation/désactivation/suppression

---

## 8. IDE en ligne (Monaco Editor)

L'IDE a été entièrement refondu avec **Monaco Editor** (le moteur de VS Code), offrant une expérience proche de GitHub Codespaces.

### 8.1 Layout VS Code

```
┌──────────── TITLEBAR (38px) ─────────────────────────────────┐
│ 🦈 SharCode v1.0  │  fichier.shc  │  Alice (etudiant)  Quitter│
├────┬──────────────────────────────────────────────────────────┤
│ AB │  SIDEBAR (240px)             │  EDITOR AREA              │
│    │                              │  ┌──────────────────────┐ │
│ 📁 │  Explorer / Leçons           │  │ Tab bar + actions    │ │
│ 📚 │  Référence / Exemples        │  ├──────────────────────┤ │
│ 📖 │                              │  │                      │ │
│ 💡 │  (collapsible)               │  │  MONACO EDITOR       │ │
│    │                              │  │  - Syntax highlighting│ │
│    │                              │  │  - Autocomplétion    │ │
│    │                              │  │  - Minimap           │ │
│    │                              │  ├──────────────────────┤ │
│    │                              │  │ PANEL: Console/Input │ │
│    │                              │  └──────────────────────┘ │
├────┴──────────────────────────────┴──────────────────────────┤
│ STATUS BAR (22px): SharCode │ Ln 1, Col 1 │ UTF-8 │ role     │
└──────────────────────────────────────────────────────────────┘
```

### 8.2 Composants

| Zone | Description |
|---|---|
| **Activity bar** | Barre d'icônes (48px) pour changer le panel sidebar |
| **Sidebar** | Explorateur fichiers / Leçons / Référence / Exemples (collapsible) |
| **Tab bar** | Nom du fichier actif, boutons Lancer / Sauvegarder / Effacer |
| **Monaco Editor** | Éditeur VS Code avec langage SharCode custom |
| **Panel bas** | Deux onglets : Console (sortie) + Entrées (stdin) |
| **Status bar** | Curseur, encodage, langage, rôle utilisateur |

### 8.3 Langage SharCode dans Monaco

Le fichier [main.js](static/js/main.js) enregistre un langage `sharcode` avec :
- **Tokenisation** : mots-clés (bleus), types (verts), built-ins (oranges), commentaires (gris), chaînes (verts), nombres (oranges)
- **Thème dark** : basé sur `vs-dark` avec les couleurs Catppuccin Mocha
- **Autocomplétion** : tous les mots-clés et fonctions built-in

### 8.4 Raccourcis clavier IDE

| Raccourci | Action |
|---|---|
| `Ctrl+Entrée` | Lancer le code |
| `Ctrl+S` | Sauvegarder |
| `Échap` | Fermer les modales |
| `Tab` | Indenter (géré nativement par Monaco) |
| Clic icône sidebar | Changer de panel / fermer la sidebar |

### 8.5 Explorateur de fichiers

- Les programmes sauvegardés apparaissent comme des fichiers `.shc`
- Clic sur un fichier → chargement dans l'éditeur
- Clic droit → menu contextuel (Renommer / Supprimer)
- Bouton `+` en haut → nouveau fichier vide
- Bouton `↻ Charger mes fichiers` → rafraîchit depuis la BDD

---

## 9. Base de données

SQLite via le module standard Python. Fichier unique `sharcode.db`.

### Schéma

```sql
licences (
    id, code,           -- SHC-XXXX-XXXX-XXXX (unique)
    label,              -- "Lycée Jean Moulin"
    max_profs,          -- capacité (défaut 5)
    date_expiration,    -- NULL = illimitée
    active,             -- 1/0
    date_creation
)

utilisateurs (
    id, nom, prenom, email, mot_de_passe,
    role,       -- 'admin' | 'prof' | 'etudiant'
    classe,
    actif,      -- 1/0 (désactivable par l'admin)
    licence_id, -- FK → licences.id (NULL pour etudiant/admin)
    date_inscription
)

lecons_completees (
    id, utilisateur_id, lecon_id, lecon_titre,
    date_completion
    -- UNIQUE(utilisateur_id, lecon_id)
)

programmes (
    id, utilisateur_id, nom, code,
    date_sauvegarde
)

exercices (
    id, prof_id, titre, description, code_exemple,
    date_creation
)

soumissions (
    id, exercice_id, etudiant_id, code, commentaire,
    date_soumission
)
```

### Chemin de la base

Contrôlé par la variable d'environnement `DATABASE_PATH` (défaut : `sharcode.db` à côté du code).

En Docker, ce chemin pointe vers `/data/sharcode.db`, monté sur un **volume nommé** `sharcode_data` pour assurer la persistance entre redémarrages.

---

## 10. Modes d'utilisation

### Mode CLI (conservé)

```bash
# REPL interactif
python main.py

# Exécuter un fichier
python main.py exemples/bonjour.shc

# Via Docker (le conteneur doit être démarré)
docker exec -it sharcode_web python main.py
docker exec -it sharcode_web python main.py exemples/bonjour.shc
```

### Mode Web

```bash
# Développement (sans Docker)
python app.py

# Production (avec Docker)
docker compose up
```

Les deux modes utilisent le même interpréteur (`frLang/`). Le mode CLI est totalement indépendant du mode web.

---

## 11. Déploiement Docker

### 9.1 Prérequis

- Docker Desktop ≥ 20 (Windows/macOS/Linux)
- Docker Compose v2+ (inclus dans Docker Desktop)

### 9.2 Démarrage rapide

```bash
# 1. Copier le fichier de configuration
cp .env.example .env

# 2. Éditer .env (SECRET_KEY au minimum)
# SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")

# 3. Construire et démarrer
docker compose up --build

# Accéder à l'application
# http://localhost:5000
```

### 9.3 Commandes utiles

```bash
# Démarrer en arrière-plan
docker compose up -d

# Voir les logs
docker compose logs -f

# Arrêter
docker compose down

# Arrêter ET supprimer les volumes (⚠️ efface la BDD)
docker compose down -v

# Reconstruire après modification du code
docker compose up --build

# Shell dans le conteneur
docker exec -it sharcode_web bash

# Utiliser le CLI SharCode depuis Docker
docker exec -it sharcode_web python main.py
```

### 9.4 Ce que fait le Dockerfile

```
1. Image de base : python:3.11-slim
2. Installation de curl (pour le healthcheck)
3. Installation des dépendances Python (requirements.txt)
4. Copie du code source
5. Création du répertoire /data (point de montage du volume)
6. Exposition du port 5000
7. Démarrage via Gunicorn (2 workers, timeout 60s)
```

### 9.5 Volumes et persistance

| Volume | Contenu | Supprimé avec `down -v` |
|---|---|---|
| `sharcode_data` | Base SQLite `/data/sharcode.db` | Oui |

Sans volume, chaque redémarrage du conteneur efface toutes les données (utilisateurs, programmes, exercices). Le volume `sharcode_data` est automatiquement créé par Docker Compose.

### 9.6 Healthcheck

Docker vérifie toutes les 30 secondes que `GET /login` répond avec un code 200. Après 3 échecs, le conteneur est marqué `unhealthy`.

---

## 12. Variables d'environnement

| Variable | Obligatoire | Défaut | Description |
|---|---|---|---|
| `SECRET_KEY` | ✅ en prod | `sharcode-dev-key-...` | Clé de chiffrement des sessions Flask |
| `DATABASE_PATH` | Non | `sharcode.db` (local) | Chemin absolu vers la BDD SQLite |
| `FLASK_ENV` | Non | `production` | `production` ou `development` |
| `FLASK_PORT` | Non | `5000` | Port d'écoute (mode `python app.py` direct) |
| `PORT` | Non | `5000` | Port exposé sur l'hôte (Docker Compose) |
| `ADMIN_EMAIL` | Non | `admin@sharcode.fr` | Email du compte admin créé au démarrage |
| `ADMIN_PASSWORD` | Non | `Admin2024!` | Mot de passe admin (**changez-le en prod**) |

> En mode `development`, Flask active le rechargement automatique et les pages d'erreur détaillées. Ne jamais utiliser `development` en production.

---

## 13. Routes API

### Authentification

| Méthode | Route | Description |
|---|---|---|
| `GET/POST` | `/login` | Page de connexion |
| `GET/POST` | `/register` | Page d'inscription |
| `GET` | `/logout` | Déconnexion |

### Pages

| Méthode | Route | Rôle requis |
|---|---|---|
| `GET` | `/` | Connecté |
| `GET` | `/etudiant/exercices` | Connecté |
| `GET` | `/prof/dashboard` | `prof` |
| `GET` | `/prof/exercice/<id>/soumissions` | `prof` |

### API JSON

| Méthode | Route | Corps / Réponse |
|---|---|---|
| `POST` | `/executer` | `{ code, entrees[] }` → `{ succes, sortie\|erreur }` |
| `POST` | `/etudiant/sauvegarder` | `{ nom, code }` → `{ succes }` |
| `GET` | `/etudiant/programmes` | → `{ programmes[] }` |
| `POST` | `/etudiant/programme/<id>/supprimer` | → `{ succes }` |
| `POST` | `/etudiant/lecon` | `{ lecon_id, lecon_titre }` → `{ succes }` |
| `POST` | `/etudiant/soumettre` | `{ exercice_id, code, commentaire }` → `{ succes }` |

### Téléchargement

| Méthode | Route | Résultat |
|---|---|---|
| `GET` | `/prof/soumission/<id>/telecharger` | Fichier `.shc` |
| `GET` | `/prof/etudiant/<id>/programmes` | Archive `.zip` |

### Gestion exercices (prof)

| Méthode | Route | Corps |
|---|---|---|
| `POST` | `/prof/exercice/creer` | Form data : `titre, description, code_exemple` |
| `POST` | `/prof/exercice/<id>/supprimer` | — |

### Administration (admin uniquement)

| Méthode | Route | Description |
|---|---|---|
| `GET` | `/admin/dashboard` | Statistiques globales |
| `GET` | `/admin/licences` | Liste des licences |
| `POST` | `/admin/licence/creer` | Créer une licence |
| `POST` | `/admin/licence/<id>/toggle` | Activer/désactiver |
| `POST` | `/admin/licence/<id>/supprimer` | Supprimer (détache les profs) |
| `GET` | `/admin/utilisateurs` | Liste tous les utilisateurs |
| `POST` | `/admin/utilisateur/<id>/toggle` | Activer/désactiver compte |
| `POST` | `/admin/utilisateur/<id>/supprimer` | Supprimer compte + données |

---

## 14. Sécurité

### Ce qui est en place

- Sessions Flask signées (cookie `HttpOnly`, clé secrète via env var)
- Hachage des mots de passe (SHA-256)
- Contrôle d'accès par rôle sur chaque route sensible (`login_requis`)
- Paramètres SQL préparés (protection injection SQL)
- Code utilisateur exécuté dans l'espace Python standard (pas d'accès filesystem)
- `SECRET_KEY` jamais codée en dur (variable d'environnement)
- Comptes désactivables sans suppression des données
- Licences avec expiration et quota de profs

### Limites connues (projet éducatif)

| Limite | Impact | Mitigation possible |
|---|---|---|
| SHA-256 sans sel | Vulnérable aux tables arc-en-ciel | Remplacer par `bcrypt` |
| Exécution du code en même processus | Risque de timeout / mémoire | Sandbox séparé (subprocess + timeout) |
| SQLite en mono-fichier | Pas de concurrence d'écriture | PostgreSQL pour production à grande échelle |
| Pas de HTTPS | Sessions en clair sur le réseau | Reverse proxy Nginx + Let's Encrypt |
| Mot de passe admin par défaut | Risque si non changé | Forcer le changement au 1er login |

---

## 15. Développement local

### Sans Docker

```bash
# Créer un environnement virtuel
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # Linux/macOS

# Installer les dépendances
pip install -r requirements.txt

# Lancer le serveur de développement
set FLASK_ENV=development        # Windows
export FLASK_ENV=development     # Linux/macOS
python app.py
```

Accès : http://localhost:5000

### Avec Docker (développement)

Pour voir les modifications du code en temps réel sans reconstruire l'image :

```yaml
# Ajouter dans docker-compose.yml > services > web
    volumes:
      - sharcode_data:/data
      - .:/app          # montage du code source
    environment:
      - FLASK_ENV=development
    command: python app.py
```

### Lancer les tests de l'interpréteur

```bash
# Tester un fichier exemple
python main.py exemples/bonjour.shc
python main.py exemples/boucles.shc
python main.py exemples/fonctions.shc

# REPL
python main.py
```

### Créer un compte professeur

Au moment de l'inscription sur `/register`, sélectionner le rôle **Professeur** et saisir le code `PROF2024`.

---

*Documentation générée le 2026-06-11 — SharCode v1.0*
