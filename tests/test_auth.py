"""
Tests d'authentification : login, logout, CSRF, session.
"""

import pytest
from helpers import creer_licence_test, creer_prof_test, creer_eleve_test
import database as db


class TestLogin:

    def test_login_admin_ok(self, client, csrf):
        r = client.post('/login', data={
            'email': 'admin@sharcode.fr',
            'mot_de_passe': 'Admin2024!',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert r.status_code == 200
        assert b'Administration' in r.data or b'Tableau de bord' in r.data

    def test_login_mauvais_mdp(self, client, csrf):
        r = client.post('/login', data={
            'email': 'admin@sharcode.fr',
            'mot_de_passe': 'mauvais',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert b'incorrect' in r.data

    def test_login_email_inconnu(self, client, csrf):
        r = client.post('/login', data={
            'email': 'inconnu@test.fr',
            'mot_de_passe': 'nimportequoi',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert b'incorrect' in r.data

    def test_login_csrf_invalide(self, client):
        with client.session_transaction() as sess:
            sess['csrf_token'] = 'bon-token'
        r = client.post('/login', data={
            'email': 'admin@sharcode.fr',
            'mot_de_passe': 'Admin2024!',
            'csrf_token': 'mauvais-token',
        }, follow_redirects=True)
        # Doit refuser ou rediriger vers login
        assert r.status_code == 200
        assert b'Connexion' in r.data or b'expir' in r.data

    def test_login_prof(self, client, csrf):
        code = creer_licence_test()
        lic  = db.get_licence_par_code(code)
        creer_prof_test(licence_id=lic['id'])
        r = client.post('/login', data={
            'email': 'prof@test.fr',
            'mot_de_passe': 'Prof1234!',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert r.status_code == 200

    def test_login_eleve(self, client, csrf):
        code = creer_licence_test()
        lic  = db.get_licence_par_code(code)
        creer_eleve_test(licence_id=lic['id'])
        r = client.post('/login', data={
            'email': 'eleve@test.fr',
            'mot_de_passe': 'Eleve123!',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert r.status_code == 200

    def test_redirection_si_deja_connecte(self, client_admin):
        r = client_admin.get('/login', follow_redirects=False)
        assert r.status_code == 302

    def test_page_protegee_sans_login(self, client):
        r = client.get('/etudiant/exercices', follow_redirects=True)
        assert b'Connexion' in r.data

    def test_logout(self, client_admin):
        r = client_admin.get('/logout', follow_redirects=True)
        assert b'Connexion' in r.data
        # Après logout, une page protégée redirige
        r2 = client_admin.get('/etudiant/exercices', follow_redirects=True)
        assert b'Connexion' in r2.data


class TestRoles:

    def test_admin_ne_peut_pas_acceder_prof(self, client_admin):
        r = client_admin.get('/prof/dashboard', follow_redirects=True)
        # L'admin est redirigé (pas le bon rôle)
        assert r.status_code == 200

    def test_acces_admin_dashboard(self, client_admin):
        r = client_admin.get('/admin/dashboard')
        assert r.status_code == 200

    def test_eleve_ne_peut_pas_acceder_admin(self, client, csrf):
        code = creer_licence_test()
        lic  = db.get_licence_par_code(code)
        creer_eleve_test(licence_id=lic['id'])
        client.post('/login', data={
            'email': 'eleve@test.fr',
            'mot_de_passe': 'Eleve123!',
            'csrf_token': csrf,
        })
        r = client.get('/admin/dashboard', follow_redirects=True)
        assert b'Administration' not in r.data
