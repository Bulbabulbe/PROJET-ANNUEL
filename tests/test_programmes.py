"""
Tests programmes : sauvegarder, modifier, supprimer, import, ZIP.
"""

import io
import json
import zipfile
import pytest
from helpers import creer_licence_test, creer_eleve_test
import database as db


def login(client, email, mdp, csrf):
    client.post('/login', data={
        'email': email, 'mot_de_passe': mdp, 'csrf_token': csrf
    })


class TestProgrammesCRUD:

    def setup_method(self):
        code = creer_licence_test()
        lic  = db.get_licence_par_code(code)
        self.eleve = creer_eleve_test(licence_id=lic['id'])

    def test_sauvegarder_programme(self):
        pid = db.sauvegarder_programme(self.eleve['id'], 'mon_prog', 'ecrire "hi"')
        assert pid is not None
        p = db.get_programme(pid)
        assert p['nom'] == 'mon_prog'
        assert p['code'] == 'ecrire "hi"'

    def test_modifier_programme_proprietaire(self):
        pid = db.sauvegarder_programme(self.eleve['id'], 'v1', 'code v1')
        db.modifier_programme(pid, self.eleve['id'], 'v2', 'code v2')
        p = db.get_programme(pid)
        assert p['nom'] == 'v2'
        assert p['code'] == 'code v2'

    def test_modifier_programme_autre_user_sans_effet(self):
        pid = db.sauvegarder_programme(self.eleve['id'], 'mon', 'code')
        db.modifier_programme(pid, 9999, 'hack', 'code hacker')
        p = db.get_programme(pid)
        assert p['nom'] == 'mon'

    def test_supprimer_programme(self):
        pid = db.sauvegarder_programme(self.eleve['id'], 'à suppr', 'x')
        db.supprimer_programme(pid, self.eleve['id'])
        assert db.get_programme(pid) is None

    def test_supprimer_programme_autre_user_sans_effet(self):
        pid = db.sauvegarder_programme(self.eleve['id'], 'protégé', 'x')
        db.supprimer_programme(pid, 9999)
        assert db.get_programme(pid) is not None

    def test_get_programmes_eleve(self):
        db.sauvegarder_programme(self.eleve['id'], 'p1', 'c1')
        db.sauvegarder_programme(self.eleve['id'], 'p2', 'c2')
        progs = db.get_programmes_etudiant(self.eleve['id'])
        assert len(progs) == 2

    def test_sauvegarder_via_api(self, client, csrf):
        login(client, 'eleve@test.fr', 'Eleve123!', csrf)
        r = client.post('/etudiant/sauvegarder',
                        data=json.dumps({'nom': 'api_prog', 'code': 'ecrire 1'}),
                        content_type='application/json',
                        headers={'X-CSRF-Token': csrf})
        data = json.loads(r.data)
        assert data['succes'] is True
        assert 'id' in data

    def test_modifier_via_api(self, client, csrf):
        login(client, 'eleve@test.fr', 'Eleve123!', csrf)
        # Crée d'abord
        r = client.post('/etudiant/sauvegarder',
                        data=json.dumps({'nom': 'test', 'code': 'v1'}),
                        content_type='application/json',
                        headers={'X-CSRF-Token': csrf})
        pid = json.loads(r.data)['id']
        # Modifie
        r2 = client.post(f'/etudiant/programme/{pid}/modifier',
                         data=json.dumps({'nom': 'test', 'code': 'v2'}),
                         content_type='application/json',
                         headers={'X-CSRF-Token': csrf})
        assert json.loads(r2.data)['succes'] is True

    def test_supprimer_via_api(self, client, csrf):
        login(client, 'eleve@test.fr', 'Eleve123!', csrf)
        r = client.post('/etudiant/sauvegarder',
                        data=json.dumps({'nom': 'del', 'code': 'x'}),
                        content_type='application/json',
                        headers={'X-CSRF-Token': csrf})
        pid = json.loads(r.data)['id']
        r2 = client.post(f'/etudiant/programme/{pid}/supprimer',
                         headers={'X-CSRF-Token': csrf})
        assert json.loads(r2.data)['succes'] is True


class TestImportExport:

    def setup_method(self):
        code = creer_licence_test()
        lic  = db.get_licence_par_code(code)
        self.eleve = creer_eleve_test(licence_id=lic['id'])

    def test_import_un_fichier(self, client, csrf):
        login(client, 'eleve@test.fr', 'Eleve123!', csrf)
        contenu = b'ecrire \"fichier importe\"'
        data = {
            'csrf_token': csrf,
            'fichiers': (io.BytesIO(contenu), 'mon_code.shc'),
        }
        r = client.post('/etudiant/importer', data=data,
                        content_type='multipart/form-data')
        result = json.loads(r.data)
        assert result['succes'] is True
        assert len(result['sauvegardes']) == 1
        assert result['sauvegardes'][0]['nom'] == 'mon_code'

    def test_import_plusieurs_fichiers(self, client, csrf):
        login(client, 'eleve@test.fr', 'Eleve123!', csrf)
        data = {
            'csrf_token': csrf,
            'fichiers': [
                (io.BytesIO(b'ecrire 1'), 'f1.shc'),
                (io.BytesIO(b'ecrire 2'), 'f2.shc'),
                (io.BytesIO(b'ecrire 3'), 'f3.shc'),
            ],
        }
        r = client.post('/etudiant/importer', data=data,
                        content_type='multipart/form-data')
        result = json.loads(r.data)
        assert result['succes'] is True
        assert len(result['sauvegardes']) == 3

    def test_telecharger_zip(self, client, csrf):
        login(client, 'eleve@test.fr', 'Eleve123!', csrf)
        # Sauvegarde quelques fichiers
        for i in range(3):
            client.post('/etudiant/sauvegarder',
                        data=json.dumps({'nom': f'prog_{i}', 'code': f'ecrire {i}'}),
                        content_type='application/json',
                        headers={'X-CSRF-Token': csrf})
        r = client.get('/etudiant/programmes/telecharger')
        assert r.status_code == 200
        assert r.content_type == 'application/zip'
        # Vérifie que le ZIP contient bien 3 fichiers
        buf = io.BytesIO(r.data)
        with zipfile.ZipFile(buf) as zf:
            assert len(zf.namelist()) == 3
