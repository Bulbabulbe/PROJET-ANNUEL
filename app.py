"""
SharCode — Serveur web (Flask)
"""

import io
import os
import secrets
import zipfile
from contextlib import redirect_stdout
from functools import wraps

from flask import (Flask, render_template, request, jsonify,
                   redirect, url_for, session, send_file, flash)

from frLang.lexer        import Lexer
from frLang.parseur      import Parseur
from frLang.interpreteur import Interpreteur
from frLang.erreurs      import ErreurFrLang

import database as db

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'sharcode-dev-key-changez-moi-en-prod')

db.init_db()


# ── CSRF ──────────────────────────────────────────────────

@app.before_request
def _ensure_csrf_token():
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(32)


@app.context_processor
def _inject_csrf():
    return {'csrf_token': session.get('csrf_token', '')}


def _csrf_valide():
    token = request.form.get('csrf_token') or request.headers.get('X-CSRF-Token', '')
    return token == session.get('csrf_token', '')


def csrf_requis(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if request.method == 'POST' and not _csrf_valide():
            flash("Session expirée. Veuillez recommencer.", "erreur")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper


# ── Helpers session ───────────────────────────────────────

def utilisateur_connecte():
    uid = session.get('user_id')
    return db.get_utilisateur(uid) if uid else None


def login_requis(role=None):
    def decorateur(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            u = utilisateur_connecte()
            if not u:
                flash("Connecte-toi pour accéder à cette page.", "info")
                return redirect(url_for('login'))
            if role and u['role'] != role:
                flash("Accès réservé.", "erreur")
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return wrapper
    return decorateur


# ── Authentification ──────────────────────────────────────

@app.route('/login', methods=['GET', 'POST'])
def login():
    if utilisateur_connecte():
        return redirect(url_for('index'))

    if request.method == 'POST':
        if not _csrf_valide():
            flash("Session expirée. Veuillez recommencer.", "erreur")
            return render_template('login.html')
        email = request.form.get('email', '').strip().lower()
        mdp   = request.form.get('mot_de_passe', '')
        u = db.verifier_login(email, mdp)
        if u:
            session['user_id'] = u['id']
            if u['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('index'))
        flash("Email ou mot de passe incorrect.", "erreur")

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ── Page principale ───────────────────────────────────────

@app.route('/')
def index():
    u = utilisateur_connecte()
    if not u:
        return redirect(url_for('login'))
    if u['role'] == 'admin':
        return redirect(url_for('admin_dashboard'))
    return render_template('index.html', user=u)


# ── Exécution du code ─────────────────────────────────────

@app.route('/executer', methods=['POST'])
def executer():
    if not utilisateur_connecte():
        return jsonify({'succes': False, 'erreur': 'Non connecté.'})
    if not _csrf_valide():
        return jsonify({'succes': False, 'erreur': 'Token invalide.'})

    data    = request.get_json()
    code    = data.get('code', '').strip()
    entrees = data.get('entrees', '').splitlines()

    if not code:
        return jsonify({'succes': False, 'erreur': 'Le programme est vide.'})

    sortie     = io.StringIO()
    entree_idx = [0]

    def mock_input(prompt=''):
        if prompt:
            sortie.write(prompt)
        if entree_idx[0] < len(entrees):
            val = entrees[entree_idx[0]]
            entree_idx[0] += 1
            sortie.write(val + '\n')
            return val
        sortie.write('\n')
        return ''

    try:
        tokens = Lexer(code).tokeniser()
        ast    = Parseur(tokens).analyser()
        interp = Interpreteur(input_fn=mock_input)
        with redirect_stdout(sortie):
            interp.executer(ast)
        return jsonify({'succes': True, 'sortie': sortie.getvalue()})
    except ErreurFrLang as e:
        return jsonify({'succes': False, 'erreur': str(e)})
    except RecursionError:
        return jsonify({'succes': False,
                        'erreur': "Récursion trop profonde — une fonction s'appelle trop souvent."})
    except Exception as e:
        return jsonify({'succes': False, 'erreur': f'Erreur inattendue : {e}'})


# ── Routes étudiant ───────────────────────────────────────

@app.route('/etudiant/sauvegarder', methods=['POST'])
@login_requis()
def sauvegarder_programme():
    if not _csrf_valide():
        return jsonify({'succes': False, 'erreur': 'Token invalide.'})
    u    = utilisateur_connecte()
    data = request.get_json()
    nom  = (data.get('nom') or 'mon_programme').strip() or 'mon_programme'
    code = data.get('code', '').strip()
    if not code:
        return jsonify({'succes': False, 'erreur': 'Code vide.'})
    prog_id = db.sauvegarder_programme(u['id'], nom, code)
    return jsonify({'succes': True, 'id': prog_id})


@app.route('/etudiant/importer', methods=['POST'])
@login_requis()
def importer_fichiers():
    """Importe un ou plusieurs fichiers .shc envoyés en multipart."""
    if not _csrf_valide():
        return jsonify({'succes': False, 'erreur': 'Token invalide.'})
    u = utilisateur_connecte()
    fichiers = request.files.getlist('fichiers')
    if not fichiers:
        return jsonify({'succes': False, 'erreur': 'Aucun fichier reçu.'})
    sauvegardes = []
    for f in fichiers:
        nom  = os.path.splitext(f.filename)[0] if f.filename else 'import'
        code = f.read().decode('utf-8', errors='replace').strip()
        if code:
            pid = db.sauvegarder_programme(u['id'], nom, code)
            sauvegardes.append({'id': pid, 'nom': nom})
    return jsonify({'succes': True, 'sauvegardes': sauvegardes})


@app.route('/etudiant/programme/<int:prog_id>/modifier', methods=['POST'])
@login_requis()
def modifier_mon_programme(prog_id):
    if not _csrf_valide():
        return jsonify({'succes': False, 'erreur': 'Token invalide.'})
    u    = utilisateur_connecte()
    data = request.get_json()
    nom  = (data.get('nom') or 'mon_programme').strip() or 'mon_programme'
    code = data.get('code', '').strip()
    if not code:
        return jsonify({'succes': False, 'erreur': 'Code vide.'})
    db.modifier_programme(prog_id, u['id'], nom, code)
    return jsonify({'succes': True})


@app.route('/etudiant/programmes')
@login_requis()
def mes_programmes():
    u = utilisateur_connecte()
    return jsonify({'programmes': db.get_programmes_etudiant(u['id'])})


@app.route('/etudiant/programmes/telecharger')
@login_requis()
def telecharger_mes_programmes():
    """ZIP de tous les fichiers de l'étudiant connecté."""
    u    = utilisateur_connecte()
    prog = db.get_programmes_etudiant(u['id'])
    buf  = io.BytesIO()
    with zipfile.ZipFile(buf, 'w') as zf:
        for p in prog:
            zf.writestr(f"{p['nom']}.shc".replace(' ', '_'), p['code'])
    buf.seek(0)
    nom_zip = f"mes_programmes_{u['prenom']}_{u['nom']}.zip".replace(' ', '_')
    return send_file(buf, as_attachment=True, download_name=nom_zip,
                     mimetype='application/zip')


@app.route('/etudiant/programme/<int:prog_id>/supprimer', methods=['POST'])
@login_requis()
def supprimer_programme(prog_id):
    if not _csrf_valide():
        return jsonify({'succes': False, 'erreur': 'Token invalide.'})
    u = utilisateur_connecte()
    db.supprimer_programme(prog_id, u['id'])
    return jsonify({'succes': True})


@app.route('/etudiant/lecon', methods=['POST'])
@login_requis()
def marquer_lecon():
    if not _csrf_valide():
        return jsonify({'succes': False, 'erreur': 'Token invalide.'})
    u    = utilisateur_connecte()
    data = request.get_json()
    db.marquer_lecon(u['id'], data.get('lecon_id'), data.get('lecon_titre', ''))
    return jsonify({'succes': True})


@app.route('/etudiant/exercices')
@login_requis()
def exercices_etudiant():
    u = utilisateur_connecte()
    # Filtrage par école : l'élève ne voit que les exercices de ses profs
    if u.get('licence_id'):
        exos = db.get_exercices_etudiant(u['licence_id'])
    else:
        exos = []
    soum        = db.get_soumissions_etudiant(u['id'])
    soum_ids    = {s['exercice_id'] for s in soum}
    soum_par_exo = {s['exercice_id']: s for s in soum}
    return render_template('dashboard_etudiant.html', user=u,
                           exercices=exos, soumissions_ids=soum_ids,
                           soumissions=soum, soumissions_par_exo=soum_par_exo)


@app.route('/etudiant/soumettre', methods=['POST'])
@login_requis()
def soumettre():
    if not _csrf_valide():
        return jsonify({'succes': False, 'erreur': 'Token invalide.'})
    u    = utilisateur_connecte()
    data = request.get_json()
    exo_id = data.get('exercice_id')

    # Vérifie que l'exercice appartient à l'école de l'élève
    exo = db.get_exercice(exo_id)
    if not exo:
        return jsonify({'succes': False, 'erreur': 'Exercice introuvable.'})
    prof = db.get_utilisateur(exo['prof_id'])
    if u.get('licence_id') and prof and prof.get('licence_id') != u['licence_id']:
        return jsonify({'succes': False, 'erreur': 'Exercice non autorisé.'})

    db.soumettre_exercice(exo_id, u['id'], data.get('code', ''), data.get('commentaire', ''))
    return jsonify({'succes': True})


# ── Routes professeur ─────────────────────────────────────

@app.route('/prof/dashboard')
@login_requis(role='prof')
def dashboard_prof():
    u      = utilisateur_connecte()
    stats  = db.get_stats_lecons(u.get('licence_id'))
    exos   = db.get_exercices_prof(u['id'])
    eleves = db.get_etudiants_licence(u['licence_id']) if u.get('licence_id') else []
    lic    = db.get_licence(u['licence_id']) if u.get('licence_id') else None
    ecole  = lic['label'] if lic else None
    licences = db.get_toutes_licences()
    return render_template('dashboard_prof.html', user=u, stats=stats,
                           exercices=exos, eleves=eleves, ecole=ecole,
                           licences=licences)


@app.route('/prof/eleve/creer', methods=['POST'])
@login_requis(role='prof')
@csrf_requis
def creer_eleve():
    u = utilisateur_connecte()
    if not u.get('licence_id'):
        flash("Ton compte n'est rattaché à aucune école. Contacte l'administrateur.", "erreur")
        return redirect(url_for('dashboard_prof'))
    nom    = request.form.get('nom', '').strip()
    prenom = request.form.get('prenom', '').strip()
    email  = request.form.get('email', '').strip().lower()
    mdp    = request.form.get('mot_de_passe', '')
    classe = request.form.get('classe', '').strip()
    if not all([nom, prenom, email, mdp]):
        flash("Nom, prénom, email et mot de passe sont obligatoires.", "erreur")
    elif len(mdp) < 6:
        flash("Le mot de passe doit faire au moins 6 caractères.", "erreur")
    else:
        ok, err = db.creer_utilisateur(nom, prenom, email, mdp, role='etudiant',
                                       classe=classe, licence_id=u['licence_id'])
        flash("Élève créé." if ok else err, "succes" if ok else "erreur")
    return redirect(url_for('dashboard_prof'))


@app.route('/prof/eleve/<int:eleve_id>/modifier', methods=['POST'])
@login_requis(role='prof')
@csrf_requis
def modifier_eleve(eleve_id):
    u      = utilisateur_connecte()
    nom    = request.form.get('nom', '').strip()
    prenom = request.form.get('prenom', '').strip()
    email  = request.form.get('email', '').strip().lower()
    classe = request.form.get('classe', '').strip()
    if not all([nom, prenom, email]):
        flash("Nom, prénom et email sont obligatoires.", "erreur")
    else:
        ok, err = db.modifier_eleve(eleve_id, u['licence_id'], nom, prenom, email, classe)
        flash("Élève mis à jour." if ok else err, "succes" if ok else "erreur")
    return redirect(url_for('dashboard_prof'))


@app.route('/prof/eleve/<int:eleve_id>/changer-mdp', methods=['POST'])
@login_requis(role='prof')
@csrf_requis
def changer_mdp_eleve(eleve_id):
    u   = utilisateur_connecte()
    mdp = request.form.get('nouveau_mdp', '')
    if len(mdp) < 6:
        flash("Le mot de passe doit faire au moins 6 caractères.", "erreur")
    else:
        ok, err = db.changer_mdp_eleve(eleve_id, u['licence_id'], mdp)
        flash("Mot de passe mis à jour." if ok else err, "succes" if ok else "erreur")
    return redirect(url_for('dashboard_prof'))


@app.route('/prof/eleve/<int:eleve_id>/supprimer', methods=['POST'])
@login_requis(role='prof')
@csrf_requis
def supprimer_eleve(eleve_id):
    u = utilisateur_connecte()
    if u.get('licence_id'):
        db.supprimer_eleve(eleve_id, u['licence_id'])
        flash("Élève supprimé.", "succes")
    return redirect(url_for('dashboard_prof'))


@app.route('/prof/exercice/creer', methods=['POST'])
@login_requis(role='prof')
@csrf_requis
def creer_exercice():
    u           = utilisateur_connecte()
    titre       = request.form.get('titre', '').strip()
    description = request.form.get('description', '').strip()
    code_ex     = request.form.get('code_exemple', '').strip()
    date_limite = request.form.get('date_limite', '').strip() or None
    if titre and description:
        db.creer_exercice(u['id'], titre, description, code_ex, date_limite)
        flash("Exercice créé.", "succes")
    else:
        flash("Titre et description obligatoires.", "erreur")
    return redirect(url_for('dashboard_prof'))


@app.route('/prof/exercice/<int:exo_id>/supprimer', methods=['POST'])
@login_requis(role='prof')
@csrf_requis
def supprimer_exercice(exo_id):
    u = utilisateur_connecte()
    db.supprimer_exercice(exo_id, u['id'])
    flash("Exercice supprimé.", "succes")
    return redirect(url_for('dashboard_prof'))


@app.route('/prof/exercice/<int:exo_id>/soumissions')
@login_requis(role='prof')
def voir_soumissions(exo_id):
    u   = utilisateur_connecte()
    exo = db.get_exercice(exo_id)
    # Vérifie que le prof est bien l'auteur de l'exercice
    if not exo or exo['prof_id'] != u['id']:
        flash("Exercice introuvable.", "erreur")
        return redirect(url_for('dashboard_prof'))
    soum = db.get_soumissions_exercice(exo_id)
    return render_template('soumissions.html', user=u, exercice=exo, soumissions=soum)


@app.route('/prof/soumission/<int:soum_id>/telecharger')
@login_requis(role='prof')
def telecharger_code(soum_id):
    u    = utilisateur_connecte()
    conn = db.get_db()
    row  = conn.execute("""
        SELECT s.code, s.date_soumission, u.nom, u.prenom, e.titre, e.prof_id
        FROM soumissions s
        JOIN utilisateurs u ON s.etudiant_id = u.id
        JOIN exercices e ON s.exercice_id = e.id
        WHERE s.id = ?
    """, (soum_id,)).fetchone()
    conn.close()

    if not row or row['prof_id'] != u['id']:
        flash("Soumission introuvable.", "erreur")
        return redirect(url_for('dashboard_prof'))

    nom_fichier = f"{row['prenom']}_{row['nom']}_{row['titre']}.shc".replace(' ', '_')
    buf = io.BytesIO(row['code'].encode('utf-8'))
    buf.seek(0)
    return send_file(buf, as_attachment=True, download_name=nom_fichier,
                     mimetype='text/plain')


@app.route('/prof/etudiant/<int:etudiant_id>/programmes')
@login_requis(role='prof')
def voir_programmes_etudiant(etudiant_id):
    u        = utilisateur_connecte()
    etudiant = db.get_utilisateur(etudiant_id)
    # Vérifie que l'élève appartient à l'école du prof
    if (not etudiant or etudiant['role'] != 'etudiant'
            or etudiant.get('licence_id') != u.get('licence_id')):
        flash("Étudiant introuvable.", "erreur")
        return redirect(url_for('dashboard_prof'))

    programmes = db.get_programmes_etudiant(etudiant_id)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w') as zf:
        for p in programmes:
            zf.writestr(f"{p['nom']}.shc".replace(' ', '_'), p['code'])
    buf.seek(0)
    nom_zip = f"programmes_{etudiant['prenom']}_{etudiant['nom']}.zip".replace(' ', '_')
    return send_file(buf, as_attachment=True, download_name=nom_zip,
                     mimetype='application/zip')


# ── Routes admin ──────────────────────────────────────────

@app.route('/admin/dashboard')
@login_requis(role='admin')
def admin_dashboard():
    u     = utilisateur_connecte()
    stats = db.get_stats_admin()
    return render_template('admin_dashboard.html', user=u, stats=stats)


@app.route('/admin/licences')
@login_requis(role='admin')
def admin_licences():
    u        = utilisateur_connecte()
    licences = db.get_toutes_licences()
    return render_template('admin_licences.html', user=u, licences=licences)


@app.route('/admin/licence/creer', methods=['POST'])
@login_requis(role='admin')
@csrf_requis
def admin_creer_licence():
    label     = request.form.get('label', '').strip()
    max_profs = int(request.form.get('max_profs', 5))
    date_exp  = request.form.get('date_expiration', '').strip() or None
    if not label:
        flash("Le libellé est obligatoire.", "erreur")
    else:
        code = db.creer_licence(label, max_profs, date_exp)
        flash(f"Licence créée : {code}", "succes")
    return redirect(url_for('admin_licences'))


@app.route('/admin/licence/<int:lic_id>/modifier', methods=['POST'])
@login_requis(role='admin')
@csrf_requis
def admin_modifier_licence(lic_id):
    label     = request.form.get('label', '').strip()
    max_profs = int(request.form.get('max_profs', 5))
    date_exp  = request.form.get('date_expiration', '').strip() or None
    if not label:
        flash("Le libellé est obligatoire.", "erreur")
    else:
        db.modifier_licence_admin(lic_id, label, max_profs, date_exp)
        flash("Licence mise à jour.", "succes")
    return redirect(url_for('admin_licences'))


@app.route('/admin/licence/<int:lic_id>/toggle', methods=['POST'])
@login_requis(role='admin')
@csrf_requis
def admin_toggle_licence(lic_id):
    db.toggle_licence(lic_id)
    flash("Statut de la licence modifié.", "succes")
    return redirect(url_for('admin_licences'))


@app.route('/admin/licence/<int:lic_id>/supprimer', methods=['POST'])
@login_requis(role='admin')
@csrf_requis
def admin_supprimer_licence(lic_id):
    db.supprimer_licence(lic_id)
    flash("Licence supprimée.", "succes")
    return redirect(url_for('admin_licences'))


@app.route('/admin/utilisateurs')
@login_requis(role='admin')
def admin_utilisateurs():
    u        = utilisateur_connecte()
    users    = db.get_tous_utilisateurs()
    licences = db.get_toutes_licences()
    return render_template('admin_utilisateurs.html', user=u,
                           utilisateurs=users, licences=licences)


@app.route('/admin/utilisateur/creer', methods=['POST'])
@login_requis(role='admin')
@csrf_requis
def admin_creer_utilisateur():
    nom        = request.form.get('nom', '').strip()
    prenom     = request.form.get('prenom', '').strip()
    email      = request.form.get('email', '').strip().lower()
    mdp        = request.form.get('mot_de_passe', '')
    licence_id = request.form.get('licence_id', '').strip()
    if not all([nom, prenom, email, mdp, licence_id]):
        flash("Tous les champs (dont l'école) sont obligatoires.", "erreur")
    elif len(mdp) < 6:
        flash("Le mot de passe doit faire au moins 6 caractères.", "erreur")
    elif not db.get_licence(licence_id):
        flash("École (licence) introuvable.", "erreur")
    else:
        ok, err = db.creer_utilisateur(nom, prenom, email, mdp, role='prof',
                                       licence_id=int(licence_id))
        flash("Professeur créé." if ok else err, "succes" if ok else "erreur")
    return redirect(url_for('admin_utilisateurs'))


@app.route('/admin/utilisateur/<int:user_id>/modifier', methods=['POST'])
@login_requis(role='admin')
@csrf_requis
def admin_modifier_utilisateur(user_id):
    u_admin    = utilisateur_connecte()
    nom        = request.form.get('nom', '').strip()
    prenom     = request.form.get('prenom', '').strip()
    email      = request.form.get('email', '').strip().lower()
    licence_id = request.form.get('licence_id', '').strip() or None
    if not all([nom, prenom, email]):
        flash("Nom, prénom et email sont obligatoires.", "erreur")
    else:
        ok, err = db.modifier_utilisateur_admin(
            user_id, nom, prenom, email,
            int(licence_id) if licence_id else None
        )
        flash("Utilisateur mis à jour." if ok else err, "succes" if ok else "erreur")
    return redirect(url_for('admin_utilisateurs'))


@app.route('/admin/utilisateur/<int:user_id>/changer-mdp', methods=['POST'])
@login_requis(role='admin')
@csrf_requis
def admin_changer_mdp(user_id):
    mdp = request.form.get('nouveau_mdp', '')
    if len(mdp) < 6:
        flash("Le mot de passe doit faire au moins 6 caractères.", "erreur")
    else:
        db.changer_mdp_utilisateur(user_id, mdp)
        flash("Mot de passe mis à jour.", "succes")
    return redirect(url_for('admin_utilisateurs'))


@app.route('/admin/utilisateur/<int:user_id>/toggle', methods=['POST'])
@login_requis(role='admin')
@csrf_requis
def admin_toggle_utilisateur(user_id):
    db.toggle_utilisateur(user_id)
    flash("Statut de l'utilisateur modifié.", "succes")
    return redirect(url_for('admin_utilisateurs'))


@app.route('/admin/utilisateur/<int:user_id>/supprimer', methods=['POST'])
@login_requis(role='admin')
@csrf_requis
def admin_supprimer_utilisateur(user_id):
    u = utilisateur_connecte()
    if user_id == u['id']:
        flash("Impossible de supprimer votre propre compte.", "erreur")
    else:
        db.supprimer_utilisateur_admin(user_id)
        flash("Utilisateur supprimé.", "succes")
    return redirect(url_for('admin_utilisateurs'))


if __name__ == '__main__':
    port  = int(os.environ.get('FLASK_PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'production') == 'development'
    print('\n  [SharCode] Serveur lancé !')
    print(f'  Ouvre ton navigateur sur : http://localhost:{port}\n')
    app.run(debug=debug, host='0.0.0.0', port=port)
