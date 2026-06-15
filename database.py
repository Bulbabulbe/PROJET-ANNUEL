"""
SharCode — Base de données SQLite
Gère les utilisateurs, leçons, programmes, exercices, soumissions, licences.
"""

import sqlite3
import hashlib
import os
import secrets
import string
from datetime import datetime

DB_PATH = os.environ.get(
    'DATABASE_PATH',
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sharcode.db')
)


def get_db():
    """Retourne une connexion à la base de données."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Crée les tables si elles n'existent pas et applique les migrations."""
    conn = get_db()
    c = conn.cursor()

    c.executescript("""
        CREATE TABLE IF NOT EXISTS licences (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            code            TEXT NOT NULL UNIQUE,
            label           TEXT NOT NULL,
            max_profs       INTEGER DEFAULT 5,
            date_expiration TEXT,
            active          INTEGER DEFAULT 1,
            date_creation   TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS utilisateurs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            nom         TEXT NOT NULL,
            prenom      TEXT NOT NULL,
            email       TEXT NOT NULL UNIQUE,
            mot_de_passe TEXT NOT NULL,
            role        TEXT NOT NULL DEFAULT 'etudiant',
            classe      TEXT DEFAULT '',
            actif       INTEGER DEFAULT 1,
            licence_id  INTEGER,
            date_inscription TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (licence_id) REFERENCES licences(id)
        );

        CREATE TABLE IF NOT EXISTS lecons_completees (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            utilisateur_id  INTEGER NOT NULL,
            lecon_id        INTEGER NOT NULL,
            lecon_titre     TEXT NOT NULL,
            date_completion TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs(id),
            UNIQUE(utilisateur_id, lecon_id)
        );

        CREATE TABLE IF NOT EXISTS programmes (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            utilisateur_id  INTEGER NOT NULL,
            nom             TEXT NOT NULL,
            code            TEXT NOT NULL,
            date_sauvegarde TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs(id)
        );

        CREATE TABLE IF NOT EXISTS exercices (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            prof_id         INTEGER NOT NULL,
            titre           TEXT NOT NULL,
            description     TEXT NOT NULL,
            code_exemple    TEXT DEFAULT '',
            date_creation   TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (prof_id) REFERENCES utilisateurs(id)
        );

        CREATE TABLE IF NOT EXISTS soumissions (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            exercice_id     INTEGER NOT NULL,
            etudiant_id     INTEGER NOT NULL,
            code            TEXT NOT NULL,
            commentaire     TEXT DEFAULT '',
            date_soumission TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (exercice_id) REFERENCES exercices(id),
            FOREIGN KEY (etudiant_id) REFERENCES utilisateurs(id)
        );
    """)

    # Migrations : ajout de colonnes sur table existante
    for migration in [
        "ALTER TABLE utilisateurs ADD COLUMN actif INTEGER DEFAULT 1",
        "ALTER TABLE utilisateurs ADD COLUMN licence_id INTEGER",
        "ALTER TABLE exercices ADD COLUMN date_limite TEXT",
    ]:
        try:
            c.execute(migration)
        except Exception:
            pass

    conn.commit()
    conn.close()

    _init_admin()


def _init_admin():
    """Crée le compte admin par défaut s'il n'existe pas."""
    admin_email = os.environ.get('ADMIN_EMAIL', 'admin@sharcode.fr')
    admin_mdp   = os.environ.get('ADMIN_PASSWORD', 'Admin2024!')
    conn = get_db()
    existing = conn.execute(
        "SELECT id FROM utilisateurs WHERE role = 'admin'"
    ).fetchone()
    if not existing:
        conn.execute(
            "INSERT OR IGNORE INTO utilisateurs (nom, prenom, email, mot_de_passe, role) "
            "VALUES (?, ?, ?, ?, ?)",
            ('Admin', 'SharCode', admin_email, hasher_mdp(admin_mdp), 'admin')
        )
        conn.commit()
    conn.close()


def hasher_mdp(mdp):
    """Hash SHA-256 du mot de passe."""
    return hashlib.sha256(mdp.encode('utf-8')).hexdigest()


# ── Utilisateurs ──────────────────────────────────────────

def creer_utilisateur(nom, prenom, email, mdp, role='etudiant', classe='', licence_id=None):
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO utilisateurs (nom, prenom, email, mot_de_passe, role, classe, licence_id) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (nom, prenom, email, hasher_mdp(mdp), role, classe, licence_id)
        )
        conn.commit()
        return True, None
    except sqlite3.IntegrityError:
        return False, "Cette adresse email est déjà utilisée."
    finally:
        conn.close()


def verifier_login(email, mdp):
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM utilisateurs WHERE email = ? AND mot_de_passe = ? AND actif = 1",
        (email, hasher_mdp(mdp))
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_utilisateur(user_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM utilisateurs WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_tous_etudiants():
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM utilisateurs WHERE role = 'etudiant' ORDER BY nom, prenom"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_etudiants_licence(licence_id):
    """Élèves rattachés à une école (licence) — vue côté professeur."""
    conn = get_db()
    rows = conn.execute("""
        SELECT u.*, lic.label as ecole
        FROM utilisateurs u
        LEFT JOIN licences lic ON u.licence_id = lic.id
        WHERE u.role = 'etudiant' AND u.licence_id = ?
        ORDER BY u.classe, u.nom, u.prenom
    """, (licence_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def supprimer_eleve(eleve_id, licence_id):
    """Le prof supprime un élève de SON école uniquement (sécurité)."""
    conn = get_db()
    row = conn.execute(
        "SELECT id FROM utilisateurs WHERE id = ? AND role = 'etudiant' AND licence_id = ?",
        (eleve_id, licence_id)
    ).fetchone()
    if row:
        conn.execute("DELETE FROM lecons_completees WHERE utilisateur_id = ?", (eleve_id,))
        conn.execute("DELETE FROM programmes WHERE utilisateur_id = ?", (eleve_id,))
        conn.execute("DELETE FROM soumissions WHERE etudiant_id = ?", (eleve_id,))
        conn.execute("DELETE FROM utilisateurs WHERE id = ?", (eleve_id,))
        conn.commit()
    conn.close()


# ── Leçons ────────────────────────────────────────────────

def marquer_lecon(user_id, lecon_id, lecon_titre):
    conn = get_db()
    conn.execute(
        "INSERT OR IGNORE INTO lecons_completees (utilisateur_id, lecon_id, lecon_titre) VALUES (?, ?, ?)",
        (user_id, lecon_id, lecon_titre)
    )
    conn.commit()
    conn.close()


def get_lecons_etudiant(user_id):
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM lecons_completees WHERE utilisateur_id = ? ORDER BY lecon_id",
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_stats_lecons(licence_id=None):
    """Retourne pour chaque étudiant son nombre de leçons complétées.
    Si licence_id est fourni, ne renvoie que les élèves de cette école."""
    conn = get_db()
    params = []
    filtre = ""
    if licence_id is not None:
        filtre = "AND u.licence_id = ?"
        params.append(licence_id)
    rows = conn.execute(f"""
        SELECT u.id, u.nom, u.prenom, u.classe,
               lic.label as ecole,
               COUNT(l.id) as nb_lecons
        FROM utilisateurs u
        LEFT JOIN lecons_completees l ON u.id = l.utilisateur_id
        LEFT JOIN licences lic ON u.licence_id = lic.id
        WHERE u.role = 'etudiant' {filtre}
        GROUP BY u.id
        ORDER BY u.nom, u.prenom
    """, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── Programmes ────────────────────────────────────────────

def sauvegarder_programme(user_id, nom, code):
    conn = get_db()
    cursor = conn.execute(
        "INSERT INTO programmes (utilisateur_id, nom, code) VALUES (?, ?, ?)",
        (user_id, nom, code)
    )
    prog_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return prog_id


def modifier_programme(prog_id, user_id, nom, code):
    """Met à jour un programme existant — uniquement s'il appartient à l'élève."""
    conn = get_db()
    conn.execute(
        "UPDATE programmes SET nom = ?, code = ?, date_sauvegarde = datetime('now') "
        "WHERE id = ? AND utilisateur_id = ?",
        (nom, code, prog_id, user_id)
    )
    conn.commit()
    conn.close()


def get_programmes_etudiant(user_id):
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM programmes WHERE utilisateur_id = ? ORDER BY date_sauvegarde DESC",
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_programme(prog_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM programmes WHERE id = ?", (prog_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def supprimer_programme(prog_id, user_id):
    conn = get_db()
    conn.execute("DELETE FROM programmes WHERE id = ? AND utilisateur_id = ?", (prog_id, user_id))
    conn.commit()
    conn.close()


# ── Exercices ─────────────────────────────────────────────

def creer_exercice(prof_id, titre, description, code_exemple='', date_limite=None):
    conn = get_db()
    cursor = conn.execute(
        "INSERT INTO exercices (prof_id, titre, description, code_exemple, date_limite) "
        "VALUES (?, ?, ?, ?, ?)",
        (prof_id, titre, description, code_exemple, date_limite or None)
    )
    exo_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return exo_id


def get_tous_exercices():
    conn = get_db()
    rows = conn.execute("""
        SELECT e.*, u.nom as prof_nom, u.prenom as prof_prenom
        FROM exercices e
        JOIN utilisateurs u ON e.prof_id = u.id
        ORDER BY e.date_creation DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_exercices_prof(prof_id):
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM exercices WHERE prof_id = ? ORDER BY date_creation DESC",
        (prof_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_exercice(exo_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM exercices WHERE id = ?", (exo_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def supprimer_exercice(exo_id, prof_id):
    conn = get_db()
    conn.execute("DELETE FROM exercices WHERE id = ? AND prof_id = ?", (exo_id, prof_id))
    conn.commit()
    conn.close()


# ── Soumissions ───────────────────────────────────────────

def soumettre_exercice(exercice_id, etudiant_id, code, commentaire=''):
    """Enregistre la soumission. Si l'élève a déjà rendu, met à jour sa réponse
    (il peut corriger une erreur) et réinitialise la date de soumission."""
    conn = get_db()
    existante = conn.execute(
        "SELECT id FROM soumissions WHERE exercice_id = ? AND etudiant_id = ?",
        (exercice_id, etudiant_id)
    ).fetchone()
    if existante:
        conn.execute(
            "UPDATE soumissions SET code = ?, commentaire = ?, "
            "date_soumission = datetime('now') WHERE id = ?",
            (code, commentaire, existante['id'])
        )
    else:
        conn.execute(
            "INSERT INTO soumissions (exercice_id, etudiant_id, code, commentaire) "
            "VALUES (?, ?, ?, ?)",
            (exercice_id, etudiant_id, code, commentaire)
        )
    conn.commit()
    conn.close()


def _est_en_retard(date_soumission, date_limite):
    """Vrai si la soumission a été faite après la date limite.
    Le jour de la date limite compte comme « à temps »."""
    if not date_limite or not date_soumission:
        return False
    return date_soumission[:10] > date_limite[:10]


def get_soumissions_exercice(exercice_id):
    conn = get_db()
    rows = conn.execute("""
        SELECT s.*, u.nom, u.prenom, u.classe,
               lic.label as ecole,
               e.date_limite
        FROM soumissions s
        JOIN utilisateurs u ON s.etudiant_id = u.id
        JOIN exercices e ON s.exercice_id = e.id
        LEFT JOIN licences lic ON u.licence_id = lic.id
        WHERE s.exercice_id = ?
        ORDER BY s.date_soumission DESC
    """, (exercice_id,)).fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        d['en_retard'] = _est_en_retard(d['date_soumission'], d.get('date_limite'))
        result.append(d)
    return result


def get_soumissions_etudiant(etudiant_id):
    conn = get_db()
    rows = conn.execute("""
        SELECT s.*, e.titre as exercice_titre, e.date_limite
        FROM soumissions s
        JOIN exercices e ON s.exercice_id = e.id
        WHERE s.etudiant_id = ?
        ORDER BY s.date_soumission DESC
    """, (etudiant_id,)).fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        d['en_retard'] = _est_en_retard(d['date_soumission'], d.get('date_limite'))
        result.append(d)
    return result


# ── Licences ──────────────────────────────────────────────

def _generer_code_licence():
    alphabet = string.ascii_uppercase + string.digits
    segment  = lambda n: ''.join(secrets.choice(alphabet) for _ in range(n))
    return f"SHC-{segment(4)}-{segment(4)}-{segment(4)}"


def creer_licence(label, max_profs=5, date_expiration=None):
    conn = get_db()
    code = _generer_code_licence()
    # Garantir l'unicité du code
    while conn.execute("SELECT id FROM licences WHERE code = ?", (code,)).fetchone():
        code = _generer_code_licence()
    conn.execute(
        "INSERT INTO licences (code, label, max_profs, date_expiration) VALUES (?, ?, ?, ?)",
        (code, label, max_profs, date_expiration)
    )
    conn.commit()
    conn.close()
    return code


def get_toutes_licences():
    conn = get_db()
    rows = conn.execute("""
        SELECT l.*,
               COUNT(u.id) as nb_profs_actifs
        FROM licences l
        LEFT JOIN utilisateurs u ON u.licence_id = l.id AND u.role = 'prof' AND u.actif = 1
        GROUP BY l.id
        ORDER BY l.date_creation DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_licence(licence_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM licences WHERE id = ?", (licence_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_licence_par_code(code):
    conn = get_db()
    row = conn.execute("SELECT * FROM licences WHERE code = ?", (code.strip().upper(),)).fetchone()
    conn.close()
    return dict(row) if row else None


def toggle_licence(licence_id):
    conn = get_db()
    conn.execute(
        "UPDATE licences SET active = CASE WHEN active = 1 THEN 0 ELSE 1 END WHERE id = ?",
        (licence_id,)
    )
    conn.commit()
    conn.close()


def supprimer_licence(licence_id):
    conn = get_db()
    # Détacher les profs liés avant suppression
    conn.execute("UPDATE utilisateurs SET licence_id = NULL WHERE licence_id = ?", (licence_id,))
    conn.execute("DELETE FROM licences WHERE id = ?", (licence_id,))
    conn.commit()
    conn.close()


def valider_licence_prof(code):
    """
    Retourne (ok, message, licence_id).
    Vérifie que la licence existe, est active, non expirée et a de la place.
    """
    lic = get_licence_par_code(code)
    if not lic:
        return False, "Code de licence invalide.", None
    if not lic['active']:
        return False, "Cette licence est désactivée.", None
    if lic['date_expiration']:
        if lic['date_expiration'] < datetime.now().strftime('%Y-%m-%d'):
            return False, "Cette licence a expiré.", None
    conn = get_db()
    nb = conn.execute(
        "SELECT COUNT(*) FROM utilisateurs WHERE licence_id = ? AND role = 'prof' AND actif = 1",
        (lic['id'],)
    ).fetchone()[0]
    conn.close()
    if nb >= lic['max_profs']:
        return False, f"Cette licence est pleine ({lic['max_profs']} professeurs max).", None
    return True, "OK", lic['id']


# ── Admin — gestion utilisateurs ─────────────────────────

def get_tous_utilisateurs():
    conn = get_db()
    rows = conn.execute("""
        SELECT u.*, l.label as licence_label, l.code as licence_code
        FROM utilisateurs u
        LEFT JOIN licences l ON u.licence_id = l.id
        ORDER BY u.role, u.nom, u.prenom
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def toggle_utilisateur(user_id):
    conn = get_db()
    conn.execute(
        "UPDATE utilisateurs SET actif = CASE WHEN actif = 1 THEN 0 ELSE 1 END WHERE id = ?",
        (user_id,)
    )
    conn.commit()
    conn.close()


def supprimer_utilisateur_admin(user_id):
    conn = get_db()
    conn.execute("DELETE FROM lecons_completees WHERE utilisateur_id = ?", (user_id,))
    conn.execute("DELETE FROM programmes WHERE utilisateur_id = ?", (user_id,))
    conn.execute("DELETE FROM soumissions WHERE etudiant_id = ?", (user_id,))
    conn.execute("DELETE FROM exercices WHERE prof_id = ?", (user_id,))
    conn.execute("DELETE FROM utilisateurs WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()


def get_stats_admin():
    conn = get_db()
    stats = {}
    stats['nb_etudiants']  = conn.execute(
        "SELECT COUNT(*) FROM utilisateurs WHERE role = 'etudiant' AND actif = 1"
    ).fetchone()[0]
    stats['nb_profs']      = conn.execute(
        "SELECT COUNT(*) FROM utilisateurs WHERE role = 'prof' AND actif = 1"
    ).fetchone()[0]
    stats['nb_licences']   = conn.execute(
        "SELECT COUNT(*) FROM licences WHERE active = 1"
    ).fetchone()[0]
    stats['nb_exercices']  = conn.execute("SELECT COUNT(*) FROM exercices").fetchone()[0]
    stats['nb_soumissions']= conn.execute("SELECT COUNT(*) FROM soumissions").fetchone()[0]
    stats['nb_programmes'] = conn.execute("SELECT COUNT(*) FROM programmes").fetchone()[0]
    conn.close()
    return stats
