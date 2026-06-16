"""
Fonctions utilitaires partagées entre les tests.
"""
import database as db


def creer_licence_test(label='École Test'):
    return db.creer_licence(label, max_profs=5)


def creer_prof_test(email='prof@test.fr', mdp='Prof1234!', licence_id=None):
    ok, _ = db.creer_utilisateur('Prof', 'Test', email, mdp, role='prof',
                                 licence_id=licence_id)
    assert ok
    return db.verifier_login(email, mdp)


def creer_eleve_test(email='eleve@test.fr', mdp='Eleve123!', licence_id=None):
    ok, _ = db.creer_utilisateur('Eleve', 'Test', email, mdp, role='etudiant',
                                 licence_id=licence_id)
    assert ok
    return db.verifier_login(email, mdp)
