# ─────────────────────────────────────────────────────────────
#  FrLang — Nœuds de l'arbre syntaxique abstrait (AST)
#
#  Chaque nœud représente une construction du langage.
#  L'interpréteur "marche" dans cet arbre pour exécuter
#  le programme.
# ─────────────────────────────────────────────────────────────

from dataclasses import dataclass, field
from typing import Any, List, Optional, Tuple


# ── Valeurs littérales ────────────────────────────────────────

@dataclass
class NoeudNombre:
    valeur: float
    ligne: int = 0

@dataclass
class NoeudChaine:
    valeur: str
    ligne: int = 0

@dataclass
class NoeudBooleen:
    valeur: bool
    ligne: int = 0

@dataclass
class NoeudRien:
    ligne: int = 0


# ── Variables ─────────────────────────────────────────────────

@dataclass
class NoeudIdentifiant:
    """Lecture d'une variable : mon_var"""
    nom: str
    ligne: int = 0

@dataclass
class NoeudAffectation:
    """Affectation : nom vaut expression"""
    nom: str
    valeur: Any
    ligne: int = 0


# ── Opérations ────────────────────────────────────────────────

@dataclass
class NoeudOperationBinaire:
    """plus, moins, fois, divise par, modulo"""
    gauche: Any
    operateur: str   # type de token (TT.PLUS, TT.FOIS, …)
    droite: Any
    ligne: int = 0

@dataclass
class NoeudNegation:
    """non condition  OU  moins nombre"""
    operande: Any
    ligne: int = 0

@dataclass
class NoeudComparaison:
    """est egal a, est superieur a, …"""
    gauche: Any
    operateur: str   # type de token (TT.EST_EGAL_A, …)
    droite: Any
    ligne: int = 0

@dataclass
class NoeudEtOu:
    """condition et condition  /  condition ou condition"""
    gauche: Any
    operateur: str   # 'et' ou 'ou'
    droite: Any
    ligne: int = 0


# ── Entrée / Sortie ───────────────────────────────────────────

@dataclass
class NoeudEcrire:
    """ecrire expression"""
    expression: Any
    ligne: int = 0

@dataclass
class NoeudLire:
    """lire "message"  — attend une saisie clavier"""
    invite: Any
    ligne: int = 0


# ── Structures de contrôle ────────────────────────────────────

@dataclass
class NoeudSi:
    """
    si condition alors
        …
    sinon si autre_cond alors
        …
    sinon
        …
    fin
    """
    condition: Any
    bloc_alors: List[Any]
    sinon_si: List[Tuple[Any, List[Any]]]   # liste de (condition, bloc)
    bloc_sinon: Optional[List[Any]]
    ligne: int = 0

@dataclass
class NoeudTantQue:
    """
    tant que condition
        …
    fin
    """
    condition: Any
    corps: List[Any]
    ligne: int = 0

@dataclass
class NoeudPour:
    """
    pour i de 1 a 10
        …
    fin
    """
    variable: str
    debut: Any
    fin: Any
    corps: List[Any]
    ligne: int = 0


# ── Fonctions ─────────────────────────────────────────────────

@dataclass
class NoeudFonction:
    """
    fonction nom(param1, param2)
        …
    fin
    """
    nom: str
    parametres: List[str]
    corps: List[Any]
    ligne: int = 0

@dataclass
class NoeudAppelFonction:
    """nom(arg1, arg2)"""
    nom: str
    arguments: List[Any]
    ligne: int = 0

@dataclass
class NoeudRetourner:
    """retourner expression"""
    valeur: Any
    ligne: int = 0


# ── Programme ─────────────────────────────────────────────────

@dataclass
class NoeudProgramme:
    instructions: List[Any]
