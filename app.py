"""
SharCode — Serveur web (Flask)
Lance avec : python app.py
Puis ouvre  : http://localhost:5000
"""

import io
import os
from contextlib import redirect_stdout

from flask import (Flask, render_template, request, jsonify,
                   redirect, url_for, session, send_file, flash)

from frLang.lexer        import Lexer
from frLang.parseur      import Parseur
from frLang.interpreteur import Interpreteur
from frLang.erreurs      import ErreurFrLang

import database as db

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'sharcode-dev-key-changez-moi-en-prod')

# Initialise la base de données au démarrage
db.init_db()


# ── Helpers session ───────────────────────────────────────

def utilisateur_connecte():
    """Retourne l'utilisateur connecté ou None."""
    uid = session.get('user_id')
    if uid:
        return db.get_utilisateur(uid)
    return None


def login_requis(role=None):
    """Décorateur maison pour protéger les routes."""
    def decorateur(f):
        from functools import wraps
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


@app.route('/register', methods=['GET', 'POST'])
def register():
    if utilisateur_connecte():
        return redirect(url_for('index'))

    if request.method == 'POST':
        nom    = request.form.get('nom', '').strip()
        prenom = request.form.get('prenom', '').strip()
        email  = request.form.get('email', '').strip().lower()
        mdp    = request.form.get('mot_de_passe', '')
        mdp2   = request.form.get('mot_de_passe2', '')
        role   = request.form.get('role', 'etudiant')
        classe = request.form.get('classe', '').strip()
        code_prof = request.form.get('code_prof', '').strip()

        if not all([nom, prenom, email, mdp]):
            flash("Tous les champs sont obligatoires.", "erreur")
        elif mdp != mdp2:
            flash("Les mots de passe ne correspondent pas.", "erreur")
        elif len(mdp) < 6:
            flash("Le mot de passe doit faire au moins 6 caractères.", "erreur")
        elif role == 'prof':
            ok_lic, msg_lic, licence_id = db.valider_licence_prof(code_prof)
            if not ok_lic:
                flash(msg_lic, "erreur")
            else:
                ok, err = db.creer_utilisateur(nom, prenom, email, mdp, role, classe,
                                               licence_id=licence_id)
                if ok:
                    u = db.verifier_login(email, mdp)
                    session['user_id'] = u['id']
                    return redirect(url_for('index'))
                flash(err, "erreur")
        else:
            ok, err = db.creer_utilisateur(nom, prenom, email, mdp, role, classe)
            if ok:
                u = db.verifier_login(email, mdp)
                session['user_id'] = u['id']
                return redirect(url_for('index'))
            flash(err, "erreur")

    return render_template('register.html')


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
    u    = utilisateur_connecte()
    data = request.get_json()
    nom  = data.get('nom', 'mon_programme').strip() or 'mon_programme'
    code = data.get('code', '').strip()
    if not code:
        return jsonify({'succes': False, 'erreur': 'Code vide.'})
    db.sauvegarder_programme(u['id'], nom, code)
    return jsonify({'succes': True})


@app.route('/etudiant/programmes')
@login_requis()
def mes_programmes():
    u    = utilisateur_connecte()
    prog = db.get_programmes_etudiant(u['id'])
    return jsonify({'programmes': prog})


@app.route('/etudiant/programme/<int:prog_id>/supprimer', methods=['POST'])
@login_requis()
def supprimer_programme(prog_id):
    u = utilisateur_connecte()
    db.supprimer_programme(prog_id, u['id'])
    return jsonify({'succes': True})


@app.route('/etudiant/lecon', methods=['POST'])
@login_requis()
def marquer_lecon():
    u    = utilisateur_connecte()
    data = request.get_json()
    db.marquer_lecon(u['id'], data.get('lecon_id'), data.get('lecon_titre', ''))
    return jsonify({'succes': True})


@app.route('/etudiant/exercices')
@login_requis()
def exercices_etudiant():
    u    = utilisateur_connecte()
    exos = db.get_tous_exercices()
    soum = db.get_soumissions_etudiant(u['id'])
    soum_ids = {s['exercice_id'] for s in soum}
    return render_template('dashboard_etudiant.html', user=u,
                           exercices=exos, soumissions_ids=soum_ids,
                           soumissions=soum)


@app.route('/etudiant/soumettre', methods=['POST'])
@login_requis()
def soumettre():
    u    = utilisateur_connecte()
    data = request.get_json()
    db.soumettre_exercice(
        data.get('exercice_id'),
        u['id'],
        data.get('code', ''),
        data.get('commentaire', '')
    )
    return jsonify({'succes': True})


# ── Routes professeur ─────────────────────────────────────

@app.route('/prof/dashboard')
@login_requis(role='prof')
def dashboard_prof():
    u     = utilisateur_connecte()
    stats = db.get_stats_lecons()
    exos  = db.get_exercices_prof(u['id'])
    return render_template('dashboard_prof.html', user=u, stats=stats, exercices=exos)


@app.route('/prof/exercice/creer', methods=['POST'])
@login_requis(role='prof')
def creer_exercice():
    u    = utilisateur_connecte()
    data = request.form
    titre       = data.get('titre', '').strip()
    description = data.get('description', '').strip()
    code_ex     = data.get('code_exemple', '').strip()
    if titre and description:
        db.creer_exercice(u['id'], titre, description, code_ex)
        flash("Exercice créé.", "succes")
    else:
        flash("Titre et description obligatoires.", "erreur")
    return redirect(url_for('dashboard_prof'))


@app.route('/prof/exercice/<int:exo_id>/supprimer', methods=['POST'])
@login_requis(role='prof')
def supprimer_exercice(exo_id):
    u = utilisateur_connecte()
    db.supprimer_exercice(exo_id, u['id'])
    flash("Exercice supprimé.", "succes")
    return redirect(url_for('dashboard_prof'))


@app.route('/prof/exercice/<int:exo_id>/soumissions')
@login_requis(role='prof')
def voir_soumissions(exo_id):
    u    = utilisateur_connecte()
    exo  = db.get_exercice(exo_id)
    soum = db.get_soumissions_exercice(exo_id)
    return render_template('soumissions.html', user=u, exercice=exo, soumissions=soum)


@app.route('/prof/soumission/<int:soum_id>/telecharger')
@login_requis(role='prof')
def telecharger_code(soum_id):
    """Télécharge le code d'une soumission en fichier .shc"""
    conn = db.get_db()
    row = conn.execute("""
        SELECT s.code, s.date_soumission, u.nom, u.prenom, e.titre
        FROM soumissions s
        JOIN utilisateurs u ON s.etudiant_id = u.id
        JOIN exercices e ON s.exercice_id = e.id
        WHERE s.id = ?
    """, (soum_id,)).fetchone()
    conn.close()

    if not row:
        flash("Soumission introuvable.", "erreur")
        return redirect(url_for('dashboard_prof'))

    nom_fichier = f"{row['prenom']}_{row['nom']}_{row['titre']}.shc".replace(' ', '_')
    buf = io.BytesIO(row['code'].encode('utf-8'))
    buf.seek(0)
    return send_file(buf, as_attachment=True,
                     download_name=nom_fichier,
                     mimetype='text/plain')


@app.route('/prof/etudiant/<int:etudiant_id>/programmes')
@login_requis(role='prof')
def voir_programmes_etudiant(etudiant_id):
    """Télécharge tous les programmes d'un étudiant en archive ZIP."""
    import zipfile
    etudiant = db.get_utilisateur(etudiant_id)
    if not etudiant or etudiant['role'] != 'etudiant':
        flash("Étudiant introuvable.", "erreur")
        return redirect(url_for('dashboard_prof'))

    programmes = db.get_programmes_etudiant(etudiant_id)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w') as zf:
        for p in programmes:
            nom = f"{p['nom']}.shc".replace(' ', '_')
            zf.writestr(nom, p['code'])
    buf.seek(0)

    nom_zip = f"programmes_{etudiant['prenom']}_{etudiant['nom']}.zip".replace(' ', '_')
    return send_file(buf, as_attachment=True,
                     download_name=nom_zip,
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
def admin_creer_licence():
    label      = request.form.get('label', '').strip()
    max_profs  = int(request.form.get('max_profs', 5))
    date_exp   = request.form.get('date_expiration', '').strip() or None
    if not label:
        flash("Le libellé est obligatoire.", "erreur")
    else:
        code = db.creer_licence(label, max_profs, date_exp)
        flash(f"Licence créée : {code}", "succes")
    return redirect(url_for('admin_licences'))


@app.route('/admin/licence/<int:lic_id>/toggle', methods=['POST'])
@login_requis(role='admin')
def admin_toggle_licence(lic_id):
    db.toggle_licence(lic_id)
    flash("Statut de la licence modifié.", "succes")
    return redirect(url_for('admin_licences'))


@app.route('/admin/licence/<int:lic_id>/supprimer', methods=['POST'])
@login_requis(role='admin')
def admin_supprimer_licence(lic_id):
    db.supprimer_licence(lic_id)
    flash("Licence supprimée.", "succes")
    return redirect(url_for('admin_licences'))


@app.route('/admin/utilisateurs')
@login_requis(role='admin')
def admin_utilisateurs():
    u     = utilisateur_connecte()
    users = db.get_tous_utilisateurs()
    return render_template('admin_utilisateurs.html', user=u, utilisateurs=users)


@app.route('/admin/utilisateur/<int:user_id>/toggle', methods=['POST'])
@login_requis(role='admin')
def admin_toggle_utilisateur(user_id):
    db.toggle_utilisateur(user_id)
    flash("Statut de l'utilisateur modifié.", "succes")
    return redirect(url_for('admin_utilisateurs'))


@app.route('/admin/utilisateur/<int:user_id>/supprimer', methods=['POST'])
@login_requis(role='admin')
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
    print('\n  [SharCode] Serveur lance !')
    print(f'  Ouvre ton navigateur sur : http://localhost:{port}\n')
    app.run(debug=debug, host='0.0.0.0', port=port)
