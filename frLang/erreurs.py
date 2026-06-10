# ─────────────────────────────────────────────────────────────
#  FrLang — Gestion des erreurs
# ─────────────────────────────────────────────────────────────


class ErreurFrLang(Exception):
    """Erreur de base du langage FrLang."""
    def __init__(self, message: str, ligne: int = None):
        self.ligne = ligne
        if ligne is not None:
            super().__init__(f"Ligne {ligne} — {message}")
        else:
            super().__init__(message)


class ErreurSyntaxe(ErreurFrLang):
    """Erreur détectée lors de l'analyse du code (mauvaise écriture)."""
    pass


class ErreurExecution(ErreurFrLang):
    """Erreur survenue pendant l'exécution du programme."""
    pass


class ErreurVariable(ErreurExecution):
    """Variable utilisée mais jamais définie."""
    pass


class ErreurType(ErreurExecution):
    """Opération impossible sur ce type de valeur."""
    pass
