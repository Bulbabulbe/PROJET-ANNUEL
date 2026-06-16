"""
Fixtures partagées pour tous les tests SharCode.
Chaque test reçoit une base SQLite temporaire fraîche et isolée.
"""

import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ['SECRET_KEY'] = 'test-secret-key'

# Base temporaire pour l'import initial (app.py appelle db.init_db() au niveau module)
_init_fd, _init_path = tempfile.mkstemp(suffix='.db')
os.close(_init_fd)
os.environ['DATABASE_PATH'] = _init_path

import database as db
from app import app as flask_app


@pytest.fixture(scope='function', autouse=True)
def _fresh_db(tmp_path):
    """Crée une base fraîche pour chaque test via un fichier temp unique."""
    path = str(tmp_path / 'test.db')
    db.DB_PATH = path
    db.init_db()
    yield


@pytest.fixture(scope='function')
def app(_fresh_db):
    flask_app.config['TESTING'] = True
    flask_app.config['WTF_CSRF_ENABLED'] = False
    flask_app.config['SECRET_KEY'] = 'test-secret-key'
    yield flask_app


@pytest.fixture(scope='function')
def client(app):
    return app.test_client()


@pytest.fixture(scope='function')
def client_admin(client, csrf):
    """Client déjà connecté en tant qu'admin."""
    with client.session_transaction() as sess:
        sess['csrf_token'] = csrf
    resp = client.post('/login', data={
        'email': 'admin@sharcode.fr',
        'mot_de_passe': 'Admin2024!',
        'csrf_token': csrf,
    }, follow_redirects=True)
    assert resp.status_code == 200
    return client


@pytest.fixture(scope='function')
def csrf(client):
    """Retourne un token CSRF valide pour la session du client."""
    with client.session_transaction() as sess:
        sess['csrf_token'] = 'test-csrf'
    return 'test-csrf'


