# ─────────────────────────────────────────────────────────────
#  FrLang — Interpréteur (exécution de l'AST)
#
#  Rôle : parcourir l'arbre syntaxique nœud par nœud et
#  exécuter les instructions.
#
#  Concepts clés :
#   • Environnement : stocke les variables (comme un dictionnaire)
#   • Portée (scope) : chaque fonction a sa propre portée
#   • ValeurRetour   : exception utilisée pour implémenter 'retourner'
# ─────────────────────────────────────────────────────────────

from .noeud    import *
from .lexer    import TT
from .erreurs  import ErreurExecution, ErreurVariable, ErreurType


# ── Signal de retour (pour les fonctions) ─────────────────────

class ValeurRetour(Exception):
    """
    Levée par 'retourner expr' pour remonter la valeur
    jusqu'à l'appelant de la fonction.
    """
    def __init__(self, valeur):
        self.valeur = valeur


# ── Environnement (portée des variables) ─────────────────────

class Environnement:
    """
    Stocke les variables sous forme de dictionnaire.
    Chaque environnement peut avoir un parent (portée englobante).
    """
    def __init__(self, parent=None):
        self._vars  = {}
        self.parent = parent

    def lire(self, nom: str, ligne: int = None):
        """Retourne la valeur de la variable, cherche dans les portées parentes si besoin."""
        if nom in self._vars:
            return self._vars[nom]
        if self.parent:
            return self.parent.lire(nom, ligne)
        raise ErreurVariable(
            f"La variable '{nom}' n'existe pas. As-tu pensé à l'initialiser ?",
            ligne
        )

    def ecrire(self, nom: str, valeur):
        """Crée ou modifie une variable dans la portée courante."""
        self._vars[nom] = valeur

    def __repr__(self):
        return f'Env({list(self._vars.keys())})'


# ── Représentation d'une fonction définie par l'utilisateur ──

class FonctionUtilisateur:
    def __init__(self, noeud: NoeudFonction, env_definition: Environnement):
        self.noeud          = noeud
        self.env_definition = env_definition   # portée où la fonction a été définie


# ── Interpréteur principal ────────────────────────────────────

class Interpreteur:
    def __init__(self, input_fn=None):
        self.env_global = Environnement()
        self._builtins  = self._creer_builtins()
        # input_fn permet de remplacer input() dans un contexte web
        self._input_fn  = input_fn if input_fn is not None else input

    # ── Fonctions natives ─────────────────────────────────────

    def _creer_builtins(self) -> dict:
        """
        Fonctions disponibles nativement dans FrLang.
        Ajoutez ici autant de fonctions que vous voulez !
        """
        def _verif(args, n, nom):
            if len(args) < n:
                raise ErreurExecution(f"'{nom}' requiert au moins {n} argument(s)")
            return args

        return {
            # Conversion de types
            'nombre':   lambda args, l: float(_verif(args,1,'nombre')[0]),
            'texte':    lambda args, l: self._vers_texte(_verif(args,1,'texte')[0]),
            'booleen':  lambda args, l: bool(_verif(args,1,'booleen')[0]),

            # Mathématiques
            'arrondir': lambda args, l: round(_verif(args,1,'arrondir')[0],
                                               int(args[1]) if len(args) > 1 else 0),
            'absolu':   lambda args, l: abs(_verif(args,1,'absolu')[0]),
            'minimum':  lambda args, l: min(_verif(args,1,'minimum')),
            'maximum':  lambda args, l: max(_verif(args,1,'maximum')),
            'racine':   lambda args, l: _verif(args,1,'racine')[0] ** 0.5,
            'puissance':lambda args, l: _verif(args,2,'puissance')[0] ** args[1],

            # Chaînes
            'taille':   lambda args, l: len(_verif(args,1,'taille')[0]),
            'majuscules': lambda args, l: str(_verif(args,1,'majuscules')[0]).upper(),
            'minuscules': lambda args, l: str(_verif(args,1,'minuscules')[0]).lower(),
            'contient':   lambda args, l: str(_verif(args,2,'contient')[1]) in str(args[0]),
        }

    # ── Exécution du programme ────────────────────────────────

    def executer(self, programme: NoeudProgramme):
        for instr in programme.instructions:
            self._exec(instr, self.env_global)

    # ── Dispatch principal ────────────────────────────────────

    def _exec(self, noeud, env: Environnement):
        """Exécute un nœud et retourne sa valeur."""

        if isinstance(noeud, NoeudNombre):
            return noeud.valeur

        elif isinstance(noeud, NoeudChaine):
            return noeud.valeur

        elif isinstance(noeud, NoeudBooleen):
            return noeud.valeur

        elif isinstance(noeud, NoeudRien):
            return None

        elif isinstance(noeud, NoeudIdentifiant):
            return env.lire(noeud.nom, noeud.ligne)

        elif isinstance(noeud, NoeudAffectation):
            valeur = self._exec(noeud.valeur, env)
            env.ecrire(noeud.nom, valeur)
            return valeur

        elif isinstance(noeud, NoeudOperationBinaire):
            return self._operation(noeud, env)

        elif isinstance(noeud, NoeudNegation):
            return self._negation(noeud, env)

        elif isinstance(noeud, NoeudComparaison):
            return self._comparaison(noeud, env)

        elif isinstance(noeud, NoeudEtOu):
            return self._et_ou(noeud, env)

        elif isinstance(noeud, NoeudEcrire):
            valeur = self._exec(noeud.expression, env)
            print(self._afficher(valeur))
            return None

        elif isinstance(noeud, NoeudLire):
            invite = self._exec(noeud.invite, env)
            return self._input_fn(str(invite))

        elif isinstance(noeud, NoeudSi):
            return self._si(noeud, env)

        elif isinstance(noeud, NoeudTantQue):
            return self._tant_que(noeud, env)

        elif isinstance(noeud, NoeudPour):
            return self._pour(noeud, env)

        elif isinstance(noeud, NoeudFonction):
            # Enregistre la fonction dans l'environnement courant
            env.ecrire(noeud.nom, FonctionUtilisateur(noeud, env))
            return None

        elif isinstance(noeud, NoeudAppelFonction):
            return self._appel(noeud, env)

        elif isinstance(noeud, NoeudRetourner):
            valeur = self._exec(noeud.valeur, env)
            raise ValeurRetour(valeur)

        else:
            raise ErreurExecution(f"Nœud inconnu : {type(noeud).__name__}")

    # ── Opérations arithmétiques ──────────────────────────────

    def _operation(self, noeud: NoeudOperationBinaire, env: Environnement):
        g = self._exec(noeud.gauche, env)
        d = self._exec(noeud.droite, env)
        op = noeud.operateur

        if op == TT.PLUS:
            # Si l'un des deux est une chaîne → concaténation
            if isinstance(g, str) or isinstance(d, str):
                return self._vers_texte(g) + self._vers_texte(d)
            if not isinstance(g, (int, float)) or not isinstance(d, (int, float)):
                raise ErreurType(
                    f"Impossible d'additionner '{self._vers_texte(g)}' et '{self._vers_texte(d)}'",
                    noeud.ligne
                )
            return g + d

        elif op == TT.MOINS:
            self._verif_nombres(g, d, 'soustraire', noeud.ligne)
            return g - d

        elif op == TT.FOIS:
            self._verif_nombres(g, d, 'multiplier', noeud.ligne)
            return g * d

        elif op == TT.DIVISE_PAR:
            self._verif_nombres(g, d, 'diviser', noeud.ligne)
            if d == 0:
                raise ErreurExecution("Division par zéro impossible !", noeud.ligne)
            return g / d

        elif op == TT.MODULO:
            self._verif_nombres(g, d, 'calculer le modulo de', noeud.ligne)
            if d == 0:
                raise ErreurExecution("Modulo par zéro impossible !", noeud.ligne)
            return g % d

        raise ErreurExecution(f"Opérateur inconnu : {op}", noeud.ligne)

    def _verif_nombres(self, g, d, action: str, ligne: int):
        if not isinstance(g, (int, float)) or not isinstance(d, (int, float)):
            raise ErreurType(
                f"Impossible de {action} des valeurs non numériques",
                ligne
            )

    # ── Négation (non / moins) ────────────────────────────────

    def _negation(self, noeud: NoeudNegation, env: Environnement):
        val = self._exec(noeud.operande, env)
        if isinstance(val, bool):
            return not val
        if isinstance(val, (int, float)):
            return -val
        raise ErreurType(
            f"Impossible de nier '{self._vers_texte(val)}'",
            noeud.ligne
        )

    # ── Comparaisons ──────────────────────────────────────────

    def _comparaison(self, noeud: NoeudComparaison, env: Environnement):
        g  = self._exec(noeud.gauche, env)
        d  = self._exec(noeud.droite, env)
        op = noeud.operateur

        if op == TT.EST_EGAL_A:        return g == d
        if op == TT.EST_DIFFERENT_DE:  return g != d
        if op == TT.EST_INFERIEUR_A:   return g < d
        if op == TT.EST_SUPERIEUR_A:   return g > d
        if op == TT.EST_INF_OU_EGAL_A: return g <= d
        if op == TT.EST_SUP_OU_EGAL_A: return g >= d

        raise ErreurExecution(f"Comparateur inconnu : {op}", noeud.ligne)

    # ── Opérateurs logiques ───────────────────────────────────

    def _et_ou(self, noeud: NoeudEtOu, env: Environnement):
        g = self._exec(noeud.gauche, env)
        if noeud.operateur == 'et':
            # Court-circuit : si g est faux, on n'évalue pas d
            return bool(g) and bool(self._exec(noeud.droite, env))
        else:
            # Court-circuit : si g est vrai, on n'évalue pas d
            return bool(g) or  bool(self._exec(noeud.droite, env))

    # ── Structures de contrôle ────────────────────────────────

    def _si(self, noeud: NoeudSi, env: Environnement):
        if self._exec(noeud.condition, env):
            self._exec_bloc(noeud.bloc_alors, env)
            return None

        for condition, bloc in noeud.sinon_si:
            if self._exec(condition, env):
                self._exec_bloc(bloc, env)
                return None

        if noeud.bloc_sinon is not None:
            self._exec_bloc(noeud.bloc_sinon, env)
        return None

    def _tant_que(self, noeud: NoeudTantQue, env: Environnement):
        iterations = 0
        while self._exec(noeud.condition, env):
            self._exec_bloc(noeud.corps, env)
            iterations += 1
            if iterations > 1_000_000:
                raise ErreurExecution(
                    "Boucle infinie détectée (plus d'un million de tours) !",
                    noeud.ligne
                )

    def _pour(self, noeud: NoeudPour, env: Environnement):
        debut = self._exec(noeud.debut, env)
        fin   = self._exec(noeud.fin,   env)

        if not isinstance(debut, (int, float)) or not isinstance(fin, (int, float)):
            raise ErreurType(
                "La boucle 'pour' requiert des nombres entiers comme bornes",
                noeud.ligne
            )

        for i in range(int(debut), int(fin) + 1):
            env.ecrire(noeud.variable, i)
            self._exec_bloc(noeud.corps, env)

    # ── Appel de fonction ─────────────────────────────────────

    def _appel(self, noeud: NoeudAppelFonction, env: Environnement):
        nom    = noeud.nom
        ligne  = noeud.ligne
        args   = [self._exec(a, env) for a in noeud.arguments]

        # Fonctions natives ?
        if nom in self._builtins:
            return self._builtins[nom](args, ligne)

        # Fonction utilisateur
        fn = env.lire(nom, ligne)
        if not isinstance(fn, FonctionUtilisateur):
            raise ErreurExecution(f"'{nom}' n'est pas une fonction", ligne)

        if len(args) != len(fn.noeud.parametres):
            raise ErreurExecution(
                f"La fonction '{nom}' attend {len(fn.noeud.parametres)} "
                f"argument(s), mais {len(args)} ont été fourni(s)",
                ligne
            )

        # Nouvelle portée (fermeture : voit la portée de définition)
        env_fn = Environnement(parent=fn.env_definition)
        for param, arg in zip(fn.noeud.parametres, args):
            env_fn.ecrire(param, arg)

        try:
            self._exec_bloc(fn.noeud.corps, env_fn)
            return None
        except ValeurRetour as r:
            return r.valeur

    # ── Utilitaires ───────────────────────────────────────────

    def _exec_bloc(self, bloc: list, env: Environnement):
        for instr in bloc:
            self._exec(instr, env)

    def _vers_texte(self, valeur) -> str:
        """Convertit une valeur en chaîne (pour les concaténations)."""
        if isinstance(valeur, bool):
            return 'vrai' if valeur else 'faux'
        if valeur is None:
            return 'rien'
        if isinstance(valeur, float) and valeur == int(valeur):
            return str(int(valeur))
        return str(valeur)

    def _afficher(self, valeur) -> str:
        """Convertit une valeur pour l'affichage avec 'ecrire'."""
        if isinstance(valeur, bool):
            return 'vrai' if valeur else 'faux'
        if valeur is None:
            return 'rien'
        if isinstance(valeur, float) and valeur == int(valeur):
            return str(int(valeur))
        return str(valeur)
