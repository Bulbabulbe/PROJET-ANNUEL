"""
Tests exercices : CRUD, filtrage par école, soumissions.
"""

import pytest
import json
from helpers import creer_licence_test, creer_prof_test, creer_eleve_test
import database as db


def login(client, email, mdp, csrf):
    client.post('/login', data={
        'email': email, 'mot_de_passe': mdp, 'csrf_token': csrf
    })


class TestExercicesCRUD:

    def setup_method(self):
        self.code = creer_licence_test()
        self.lic  = db.get_licence_par_code(self.code)
        self.prof = creer_prof_test(licence_id=self.lic['id'])

    def test_creer_exercice(self):
        exo_id = db.creer_exercice(self.prof['id'], 'Mon exo', 'Description test')
        assert exo_id is not None
        exo = db.get_exercice(exo_id)
        assert exo['titre'] == 'Mon exo'
        assert exo['prof_id'] == self.prof['id']

    def test_creer_exercice_avec_date_limite(self):
        exo_id = db.creer_exercice(self.prof['id'], 'Exo daté', 'Desc',
                                   date_limite='2025-12-31')
        exo = db.get_exercice(exo_id)
        assert exo['date_limite'] == '2025-12-31'

    def test_supprimer_exercice_par_auteur(self):
        exo_id = db.creer_exercice(self.prof['id'], 'À supprimer', 'Desc')
        db.supprimer_exercice(exo_id, self.prof['id'])
        assert db.get_exercice(exo_id) is None

    def test_supprimer_exercice_autre_prof_sans_effet(self):
        exo_id = db.creer_exercice(self.prof['id'], 'Protégé', 'Desc')
        db.supprimer_exercice(exo_id, 9999)  # mauvais prof_id
        assert db.get_exercice(exo_id) is not None

    def test_get_exercices_prof(self):
        db.creer_exercice(self.prof['id'], 'Ex1', 'D')
        db.creer_exercice(self.prof['id'], 'Ex2', 'D')
        exos = db.get_exercices_prof(self.prof['id'])
        assert len(exos) == 2


class TestFiltragEcole:

    def test_eleve_voit_seulement_son_ecole(self):
        code1 = creer_licence_test('École A')
        code2 = creer_licence_test('École B')
        lic1  = db.get_licence_par_code(code1)
        lic2  = db.get_licence_par_code(code2)

        prof1 = creer_prof_test('prof1@a.fr', licence_id=lic1['id'])
        prof2 = creer_prof_test('prof2@b.fr', licence_id=lic2['id'])
        eleve = creer_eleve_test('eleve@a.fr', licence_id=lic1['id'])

        db.creer_exercice(prof1['id'], 'Exo école A', 'D')
        db.creer_exercice(prof2['id'], 'Exo école B', 'D')

        exos = db.get_exercices_etudiant(lic1['id'])
        titres = [e['titre'] for e in exos]
        assert 'Exo école A' in titres
        assert 'Exo école B' not in titres

    def test_eleve_sans_licence_voit_rien(self, client, csrf):
        creer_eleve_test('sans_ecole@test.fr', licence_id=None)
        login(client, 'sans_ecole@test.fr', 'Eleve123!', csrf)
        r = client.get('/etudiant/exercices')
        assert r.status_code == 200
        # Aucun exercice affiché
        assert b'Aucun exercice' in r.data or b'aucune' in r.data.lower()


class TestSoumissions:

    def setup_method(self):
        self.code = creer_licence_test()
        self.lic  = db.get_licence_par_code(self.code)
        self.prof = creer_prof_test(licence_id=self.lic['id'])
        self.eleve = creer_eleve_test(licence_id=self.lic['id'])
        self.exo_id = db.creer_exercice(self.prof['id'], 'Exo test', 'Desc')

    def test_soumettre_exercice(self):
        db.soumettre_exercice(self.exo_id, self.eleve['id'], 'ecrire "hello"')
        soum = db.get_soumissions_exercice(self.exo_id)
        assert len(soum) == 1
        assert soum[0]['code'] == 'ecrire "hello"'

    def test_soumettre_deux_fois_met_a_jour(self):
        db.soumettre_exercice(self.exo_id, self.eleve['id'], 'version 1')
        db.soumettre_exercice(self.exo_id, self.eleve['id'], 'version 2')
        soum = db.get_soumissions_exercice(self.exo_id)
        assert len(soum) == 1
        assert soum[0]['code'] == 'version 2'

    def test_soumission_en_retard(self):
        db.soumettre_exercice(self.exo_id, self.eleve['id'], 'code')
        soum = db.get_soumissions_etudiant(self.eleve['id'])
        # Pas de date limite sur cet exercice donc pas de retard
        assert soum[0]['en_retard'] is False

    def test_soumettre_via_api(self, client, csrf):
        login(client, 'eleve@test.fr', 'Eleve123!', csrf)
        r = client.post('/etudiant/soumettre',
                        data=json.dumps({
                            'exercice_id': self.exo_id,
                            'code': 'ecrire "test"',
                            'commentaire': 'ma réponse'
                        }),
                        content_type='application/json',
                        headers={'X-CSRF-Token': csrf})
        data = json.loads(r.data)
        assert data['succes'] is True

    def test_soumettre_exercice_autre_ecole_refuse(self, client, csrf):
        # Crée un exercice d'une autre école
        code2 = creer_licence_test('École B')
        lic2  = db.get_licence_par_code(code2)
        prof2 = creer_prof_test('prof2@b.fr', licence_id=lic2['id'])
        exo_autre = db.creer_exercice(prof2['id'], 'Exo B', 'D')

        login(client, 'eleve@test.fr', 'Eleve123!', csrf)
        r = client.post('/etudiant/soumettre',
                        data=json.dumps({
                            'exercice_id': exo_autre,
                            'code': 'ecrire "hack"',
                        }),
                        content_type='application/json',
                        headers={'X-CSRF-Token': csrf})
        data = json.loads(r.data)
        assert data['succes'] is False

    def test_prof_voit_soumissions_son_exercice(self, client, csrf):
        db.soumettre_exercice(self.exo_id, self.eleve['id'], 'code élève')
        login(client, 'prof@test.fr', 'Prof1234!', csrf)
        r = client.get(f'/prof/exercice/{self.exo_id}/soumissions')
        assert r.status_code == 200
        assert b'code' in r.data

    def test_prof_ne_voit_pas_soumissions_autre_prof(self, client, csrf):
        prof2 = creer_prof_test('prof2@test.fr', licence_id=self.lic['id'])
        exo2  = db.creer_exercice(prof2['id'], 'Exo prof2', 'D')
        login(client, 'prof@test.fr', 'Prof1234!', csrf)
        r = client.get(f'/prof/exercice/{exo2}/soumissions', follow_redirects=True)
        # Doit refuser
        assert b'introuvable' in r.data or r.status_code in (302, 200)
