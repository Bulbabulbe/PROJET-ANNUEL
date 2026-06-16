# SharCode — Suivi d'implémentation

## État actuel du chantier (interrompu par erreur serveur)

---

## TERMINÉ ✅

### Backend
- **`database.py`** — complet
  - Hachage PBKDF2 via `werkzeug.security` (migration auto SHA-256 → PBKDF2 à la connexion)
  - `get_exercices_etudiant(licence_id)` — filtre les exercices par école
  - `modifier_eleve(eleve_id, licence_id, ...)` — prof modifie un élève de son école
  - `changer_mdp_eleve(eleve_id, licence_id, nouveau_mdp)` — prof change le MDP élève
  - `modifier_utilisateur_admin(user_id, ...)` — admin modifie n'importe quel user
  - `changer_mdp_utilisateur(user_id, nouveau_mdp)` — admin change n'importe quel MDP
  - `modifier_licence_admin(lic_id, label, max_profs, date_expiration)` — admin modifie une licence

- **`app.py`** — complet
  - Protection CSRF : token en session, decorator `@csrf_requis`, injection `{{ csrf_token }}`
  - `/etudiant/exercices` → filtre par `licence_id` de l'élève (plus "tous les exercices")
  - `/etudiant/importer` → import multi-fichiers .shc (multipart)
  - `/etudiant/programmes/telecharger` → ZIP de tous les fichiers de l'élève
  - `/etudiant/soumettre` → vérifie que l'exercice appartient à l'école de l'élève
  - `/prof/eleve/<id>/modifier` → modifier élève (avec check école)
  - `/prof/eleve/<id>/changer-mdp` → changer MDP élève (avec check école)
  - `/prof/exercice/<id>/soumissions` → vérifie que le prof est l'auteur
  - `/prof/soumission/<id>/telecharger` → vérifie que le prof est l'auteur
  - `/prof/etudiant/<id>/programmes` → vérifie que l'élève est dans l'école du prof
  - `/admin/utilisateur/<id>/modifier` → modifier un utilisateur
  - `/admin/utilisateur/<id>/changer-mdp` → changer MDP
  - `/admin/licence/<id>/modifier` → modifier une licence

### Frontend CSS
- **`static/css/style.css`** — complet
  - Navbar redesignée : gradient `#03045e → #0077b6`, plus de chevauchements, `a { text-decoration: none }`
  - `.user-chip` + `.user-avatar` : affichage moderne de l'utilisateur connecté
  - `.navbar-divider` : séparateur visuel
  - Hauteur navbar réduite à 52px, paddings revus

- **`static/css/auth.css`** — complet
  - `.password-wrapper` + `.eye-toggle` : champ MDP avec icône œil SVG
  - `.btn-warning` : bouton orange pour "Changer MDP"
  - `.soum-editor-wrapper` + `.soum-line-numbers` + `.soum-textarea` : éditeur dans la modale exercice
  - `.modal-dark` : formulaire inline sombre pour édition dans les tableaux
  - `.modal-actions-row` : ligne d'actions au-dessus de l'éditeur de soumission

### Frontend JS
- **`static/js/main.js`** — complet
  - `csrfToken()` → lit le meta tag `<meta name="csrf-token">`
  - Tous les `fetch()` passent `'X-CSRF-Token': csrfToken()` en header
  - `importerFichiers()` → file picker multi, upload vers `/etudiant/importer`
  - `toggleMdp(btn)` → bascule `type="password"` / `type="text"` + swap SVG œil ouvert/fermé
  - Suppression programme : header CSRF ajouté

### Templates HTML
- **`templates/login.html`** — complet
  - CSRF token dans le form
  - Champ MDP `type="password"` avec bouton œil SVG

- **`templates/index.html`** — complet
  - Meta tag CSRF
  - Navbar moderne (user-chip, divider, pas de soulignement)
  - Panel "Mes fichiers" : boutons "+ Nouveau", "Importer .shc", "Tout télécharger"
  - `sauvegarderProgramme()` avec header CSRF

- **`templates/dashboard_etudiant.html`** — complet
  - Meta tag CSRF
  - Navbar moderne
  - Exercices filtrés par école (message si aucune école associée)
  - Modale de réponse avec éditeur complet : numéros de ligne, support Tab, bouton "Depuis l'éditeur"
  - Titre dynamique de la modale = titre de l'exercice

- **`templates/dashboard_prof.html`** — complet
  - Meta tag CSRF
  - Navbar moderne
  - Champ MDP création élève → `type="password"` avec œil
  - Bouton "Modifier" par élève → formulaire inline `.modal-dark` (prénom, nom, email, classe)
  - Bouton "Changer MDP" par élève → formulaire inline avec champ MDP + œil
  - CSRF sur tous les forms
  - Tableau progression élèves simplifié

- **`templates/admin_utilisateurs.html`** — complet
  - Meta tag CSRF
  - Navbar moderne
  - Champ MDP création prof → `type="password"` avec œil
  - Bouton "Modifier" par user → formulaire inline (prénom, nom, email, licence)
  - Bouton "Changer MDP" par user → formulaire inline avec œil
  - CSRF sur tous les forms

---

## RESTE À FAIRE ❌

### Templates HTML
- **`templates/admin_licences.html`**
  - Navbar moderne (user-chip, divider)
  - Bouton "Modifier" par licence → formulaire inline (label, max_profs, date_expiration)
  - CSRF sur tous les forms

- **`templates/admin_dashboard.html`**
  - Navbar moderne (user-chip, divider)
  - Meta tag CSRF

- **`templates/soumissions.html`**
  - Navbar moderne (user-chip, divider)

### Tests
- **`tests/__init__.py`** — fichier vide
- **`tests/conftest.py`** — fixtures Flask test client, DB en mémoire
- **`tests/test_auth.py`** — login OK, login mauvais MDP, logout, CSRF, session
- **`tests/test_exercices.py`** — créer, supprimer, filtrage par école, soumission
- **`tests/test_programmes.py`** — sauvegarder, modifier, supprimer, import, ZIP
- **`tests/test_licences.py`** — créer, modifier, toggle, supprimer, max_profs
- **`tests/test_utilisateurs.py`** — créer prof/élève, modifier, changer MDP, supprimer

---

## Architecture des changements clés

### Exercices filtrés par école
```
AVANT : get_tous_exercices() → tous les exercices de tous les profs
APRÈS : get_exercices_etudiant(licence_id) → JOIN utilisateurs WHERE u.licence_id = élève.licence_id
```

### CSRF
```
Token généré en session dans before_request
Injecté dans templates via context_processor → {{ csrf_token }}
Validé dans chaque route POST via @csrf_requis ou _csrf_valide()
Passé dans les fetch() AJAX via header X-CSRF-Token
```

### Hachage MDP
```
AVANT : hashlib.sha256(mdp).hexdigest()
APRÈS : werkzeug generate_password_hash (PBKDF2-SHA256)
Migration auto : si hash ne commence pas par "pbkdf2:" → compare SHA256, puis re-hash en PBKDF2
```
