"""
Tests utilisateurs : créer, modifier, changer MDP, supprimer, rôles.
"""

import pytest
from helpers import creer_licence_test, creer_prof_test, creer_eleve_test
import database as db


class TestCreerUtilisateur:

    def test_creer_prof(self):
        code = creer_licence_test()
        lic  = db.get_licence_par_code(code)
        ok, err = db.creer_utilisateur('Dupont', 'Alice', 'alice@test.fr',
                                       'Motdepasse1!', role='prof',
                                       licence_id=lic['id'])
        assert ok is True
        u = db.verifier_login('alice@test.fr', 'Motdepasse1!')
        assert u is not None
        assert u['role'] == 'prof'

    def test_creer_eleve(self):
        code = creer_licence_test()
        lic  = db.get_licence_par_code(code)
        ok, err = db.creer_utilisateur('Martin', 'Bob', 'bob@test.fr',
                                       'Mdp12345!', role='etudiant',
                                       licence_id=lic['id'])
        assert ok is True

    def test_email_unique(self):
        ok1, _  = db.creer_utilisateur('A', 'B', 'dup@test.fr', 'Mdp1234!')
        ok2, err = db.creer_utilisateur('C', 'D', 'dup@test.fr', 'Mdp1234!')
        assert ok1 is True
        assert ok2 is False
        assert 'déjà' in err

    def test_mdp_hache(self):
        db.creer_utilisateur('X', 'Y', 'hash@test.fr', 'MonMdp!')
        u = db.verifier_login('hash@test.fr', 'MonMdp!')
        assert u is not None
        # Le hash ne doit pas être en clair
        assert u['mot_de_passe'] != 'MonMdp!'
        assert u['mot_de_passe'].startswith('pbkdf2:')


class TestModifierUtilisateur:

    def setup_method(self):
        code = creer_licence_test()
        self.lic  = db.get_licence_par_code(code)
        self.prof = creer_prof_test(licence_id=self.lic['id'])
        self.eleve = creer_eleve_test(licence_id=self.lic['id'])

    def test_modifier_utilisateur_admin(self):
        ok, err = db.modifier_utilisateur_admin(
            self.prof['id'], 'NouveauNom', 'NouveauPrenom',
            'nouveau@test.fr', self.lic['id']
        )
        assert ok is True
        u = db.get_utilisateur(self.prof['id'])
        assert u['nom'] == 'NouveauNom'
        assert u['email'] == 'nouveau@test.fr'

    def test_modifier_email_duplique_refuse(self):
        ok, err = db.modifier_utilisateur_admin(
            self.prof['id'], 'A', 'B', 'eleve@test.fr'
        )
        assert ok is False
        assert 'déjà' in err

    def test_modifier_eleve_par_prof(self):
        ok, err = db.modifier_eleve(
            self.eleve['id'], self.lic['id'],
            'NomModif', 'PrenomModif', 'modif@test.fr', '6ème B'
        )
        assert ok is True
        u = db.get_utilisateur(self.eleve['id'])
        assert u['nom'] == 'NomModif'
        assert u['classe'] == '6ème B'

    def test_modifier_eleve_autre_ecole_refuse(self):
        code2 = creer_licence_test('École 2')
        lic2  = db.get_licence_par_code(code2)
        ok, err = db.modifier_eleve(
            self.eleve['id'], lic2['id'],
            'Hack', 'Hack', 'hack@test.fr'
        )
        assert ok is False
        assert 'introuvable' in err


class TestChangerMotDePasse:

    def setup_method(self):
        code = creer_licence_test()
        self.lic   = db.get_licence_par_code(code)
        self.prof  = creer_prof_test(licence_id=self.lic['id'])
        self.eleve = creer_eleve_test(licence_id=self.lic['id'])

    def test_changer_mdp_eleve_par_prof(self):
        ok, err = db.changer_mdp_eleve(
            self.eleve['id'], self.lic['id'], 'NouveauMdp1!'
        )
        assert ok is True
        u = db.verifier_login('eleve@test.fr', 'NouveauMdp1!')
        assert u is not None

    def test_changer_mdp_eleve_autre_ecole_refuse(self):
        code2 = creer_licence_test('École 2')
        lic2  = db.get_licence_par_code(code2)
        ok, err = db.changer_mdp_eleve(
            self.eleve['id'], lic2['id'], 'Hack1234!'
        )
        assert ok is False

    def test_changer_mdp_admin(self):
        ok, _ = db.changer_mdp_utilisateur(self.prof['id'], 'AdminReset1!')
        assert ok is True
        u = db.verifier_login('prof@test.fr', 'AdminReset1!')
        assert u is not None

    def test_ancien_mdp_invalide_apres_changement(self):
        db.changer_mdp_utilisateur(self.eleve['id'], 'NouveauMdp1!')
        u = db.verifier_login('eleve@test.fr', 'Eleve123!')
        assert u is None


class TestSupprimerUtilisateur:

    def setup_method(self):
        code = creer_licence_test()
        self.lic   = db.get_licence_par_code(code)
        self.prof  = creer_prof_test(licence_id=self.lic['id'])
        self.eleve = creer_eleve_test(licence_id=self.lic['id'])

    def test_supprimer_eleve_par_prof(self):
        db.supprimer_eleve(self.eleve['id'], self.lic['id'])
        assert db.get_utilisateur(self.eleve['id']) is None

    def test_supprimer_eleve_autre_ecole_sans_effet(self):
        code2 = creer_licence_test('École 2')
        lic2  = db.get_licence_par_code(code2)
        db.supprimer_eleve(self.eleve['id'], lic2['id'])
        assert db.get_utilisateur(self.eleve['id']) is not None

    def test_supprimer_eleve_supprime_ses_donnees(self):
        pid = db.sauvegarder_programme(self.eleve['id'], 'prog', 'code')
        exo = db.creer_exercice(self.prof['id'], 'Exo', 'D')
        db.soumettre_exercice(exo, self.eleve['id'], 'réponse')

        db.supprimer_eleve(self.eleve['id'], self.lic['id'])

        assert db.get_programme(pid) is None
        assert len(db.get_soumissions_exercice(exo)) == 0

    def test_supprimer_admin(self):
        db.supprimer_utilisateur_admin(self.prof['id'])
        assert db.get_utilisateur(self.prof['id']) is None

    def test_toggle_utilisateur(self):
        uid = self.eleve['id']
        assert db.get_utilisateur(uid)['actif'] == 1
        db.toggle_utilisateur(uid)
        assert db.get_utilisateur(uid)['actif'] == 0
        # Utilisateur désactivé ne peut pas se connecter
        u = db.verifier_login('eleve@test.fr', 'Eleve123!')
        assert u is None


class TestMigrationHash:

    def test_migration_sha256_vers_pbkdf2(self):
        """Un compte avec hash SHA-256 legacy doit pouvoir se connecter et être migré."""
        import hashlib
        sha_hash = hashlib.sha256('OldPass1!'.encode()).hexdigest()
        conn = db.get_db()
        conn.execute(
            "INSERT INTO utilisateurs (nom, prenom, email, mot_de_passe, role) "
            "VALUES (?, ?, ?, ?, ?)",
            ('Legacy', 'User', 'legacy@test.fr', sha_hash, 'etudiant')
        )
        conn.commit()
        conn.close()

        # Connexion avec l'ancien hash
        u = db.verifier_login('legacy@test.fr', 'OldPass1!')
        assert u is not None

        # Le hash est maintenant migré en PBKDF2
        u2 = db.get_utilisateur(u['id'])
        assert u2['mot_de_passe'].startswith('pbkdf2:')
