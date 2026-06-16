"""
Tests licences : créer, modifier, toggle, supprimer, max_profs.
"""

import pytest
from helpers import creer_licence_test, creer_prof_test
import database as db


class TestLicencesCRUD:

    def test_creer_licence(self):
        code = db.creer_licence('Mon École', max_profs=3)
        assert code.startswith('SHC-')
        lic = db.get_licence_par_code(code)
        assert lic is not None
        assert lic['label'] == 'Mon École'
        assert lic['max_profs'] == 3
        assert lic['active'] == 1

    def test_creer_licence_avec_expiration(self):
        code = db.creer_licence('Temporaire', date_expiration='2030-01-01')
        lic  = db.get_licence_par_code(code)
        assert lic['date_expiration'] == '2030-01-01'

    def test_code_unique(self):
        codes = {db.creer_licence(f'École {i}') for i in range(10)}
        assert len(codes) == 10

    def test_get_toutes_licences(self):
        avant = len(db.get_toutes_licences())
        db.creer_licence('Nouvelle école')
        assert len(db.get_toutes_licences()) == avant + 1

    def test_modifier_licence(self):
        code = creer_licence_test('Avant')
        lic  = db.get_licence_par_code(code)
        db.modifier_licence_admin(lic['id'], 'Après', 10, '2035-06-01')
        updated = db.get_licence(lic['id'])
        assert updated['label'] == 'Après'
        assert updated['max_profs'] == 10
        assert updated['date_expiration'] == '2035-06-01'

    def test_toggle_licence(self):
        code = creer_licence_test()
        lic  = db.get_licence_par_code(code)
        assert lic['active'] == 1
        db.toggle_licence(lic['id'])
        assert db.get_licence(lic['id'])['active'] == 0
        db.toggle_licence(lic['id'])
        assert db.get_licence(lic['id'])['active'] == 1

    def test_supprimer_licence(self):
        code = creer_licence_test()
        lic  = db.get_licence_par_code(code)
        db.supprimer_licence(lic['id'])
        assert db.get_licence(lic['id']) is None

    def test_supprimer_licence_detache_profs(self):
        code = creer_licence_test()
        lic  = db.get_licence_par_code(code)
        prof = creer_prof_test(licence_id=lic['id'])
        db.supprimer_licence(lic['id'])
        updated = db.get_utilisateur(prof['id'])
        assert updated['licence_id'] is None


class TestValidationLicence:

    def test_valider_licence_ok(self):
        code = creer_licence_test()
        ok, msg, lic_id = db.valider_licence_prof(code)
        assert ok is True
        assert lic_id is not None

    def test_valider_licence_code_invalide(self):
        ok, msg, _ = db.valider_licence_prof('SHC-0000-0000-0000')
        assert ok is False
        assert 'invalide' in msg

    def test_valider_licence_desactivee(self):
        code = creer_licence_test()
        lic  = db.get_licence_par_code(code)
        db.toggle_licence(lic['id'])
        ok, msg, _ = db.valider_licence_prof(code)
        assert ok is False
        assert 'désactivée' in msg

    def test_valider_licence_expiree(self):
        code = db.creer_licence('Expirée', date_expiration='2000-01-01')
        ok, msg, _ = db.valider_licence_prof(code)
        assert ok is False
        assert 'expiré' in msg

    def test_valider_licence_pleine(self):
        code = db.creer_licence('Petite école', max_profs=1)
        lic  = db.get_licence_par_code(code)
        creer_prof_test('p1@test.fr', licence_id=lic['id'])
        ok, msg, _ = db.valider_licence_prof(code)
        assert ok is False
        assert 'pleine' in msg


class TestAdminLicences:

    def test_creer_licence_via_route(self, client_admin, csrf):
        with client_admin.session_transaction() as sess:
            sess['csrf_token'] = csrf
        r = client_admin.post('/admin/licence/creer', data={
            'label': 'Via route',
            'max_profs': '3',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert r.status_code == 200
        assert b'Via route' in r.data or b'cr' in r.data

    def test_modifier_licence_via_route(self, client_admin, csrf):
        code = creer_licence_test('Avant modif')
        lic  = db.get_licence_par_code(code)
        with client_admin.session_transaction() as sess:
            sess['csrf_token'] = csrf
        r = client_admin.post(f'/admin/licence/{lic["id"]}/modifier', data={
            'label': 'Après modif',
            'max_profs': '7',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert r.status_code == 200
        updated = db.get_licence(lic['id'])
        assert updated['label'] == 'Après modif'
