# ─────────────────────────────────────────────────────────────
#  FrLang — Analyse lexicale (Lexer / Tokeniseur)
#
#  Rôle : lire le code source caractère par caractère et
#  produire une liste de « tokens » (jetons).
#
#  Exemple :
#    "age vaut 25"
#    → [Token(IDENTIFIANT,'age'), Token(VAUT,'vaut'), Token(NOMBRE,25)]
#
#  Gestion des mots-clés composés :
#    "est egal a"     → un seul token EST_EGAL_A
#    "tant que"       → un seul token TANT_QUE
#    "divise par"     → un seul token DIVISE_PAR
# ─────────────────────────────────────────────────────────────

import unicodedata
from .erreurs import ErreurSyntaxe


# ── Types de tokens ───────────────────────────────────────────

class TT:
    # Valeurs
    NOMBRE      = 'NOMBRE'
    CHAINE      = 'CHAINE'
    VRAI        = 'VRAI'
    FAUX        = 'FAUX'
    RIEN        = 'RIEN'
    IDENTIFIANT = 'IDENTIFIANT'

    # Mots-clés simples
    VAUT        = 'VAUT'
    SI          = 'SI'
    ALORS       = 'ALORS'
    SINON       = 'SINON'
    SINON_SI    = 'SINON_SI'
    FIN         = 'FIN'
    POUR        = 'POUR'
    DE          = 'DE'
    A           = 'A'
    ECRIRE      = 'ECRIRE'
    LIRE        = 'LIRE'
    FONCTION    = 'FONCTION'
    RETOURNER   = 'RETOURNER'
    ET          = 'ET'
    OU          = 'OU'
    NON         = 'NON'
    PLUS        = 'PLUS'
    MOINS       = 'MOINS'
    FOIS        = 'FOIS'
    MODULO      = 'MODULO'

    # Mots-clés composés (plusieurs mots → un seul token)
    TANT_QUE          = 'TANT_QUE'
    EST_EGAL_A        = 'EST_EGAL_A'
    EST_DIFFERENT_DE  = 'EST_DIFFERENT_DE'
    EST_INFERIEUR_A   = 'EST_INFERIEUR_A'
    EST_SUPERIEUR_A   = 'EST_SUPERIEUR_A'
    EST_INF_OU_EGAL_A = 'EST_INF_OU_EGAL_A'
    EST_SUP_OU_EGAL_A = 'EST_SUP_OU_EGAL_A'
    DIVISE_PAR        = 'DIVISE_PAR'

    # Ponctuation
    LPAREN  = 'LPAREN'
    RPAREN  = 'RPAREN'
    VIRGULE = 'VIRGULE'
    NEWLINE = 'NEWLINE'
    EOF     = 'EOF'

    # Interne — avant fusion des séquences
    _MOT = '__MOT__'


# ── Token ─────────────────────────────────────────────────────

class Token:
    __slots__ = ('type', 'valeur', 'ligne')

    def __init__(self, type_: str, valeur, ligne: int):
        self.type   = type_
        self.valeur = valeur
        self.ligne  = ligne

    def __repr__(self):
        return f'Token({self.type}, {self.valeur!r}, L{self.ligne})'


# ── Séquences multi-mots (du plus long au plus court) ─────────
#  Chaque entrée : (liste de mots normalisés, type de token résultant)

SEQUENCES = [
    (['sinon', 'si'],                          TT.SINON_SI),
    (['tant', 'que'],                          TT.TANT_QUE),
    (['est', 'inferieur', 'ou', 'egal', 'a'],  TT.EST_INF_OU_EGAL_A),
    (['est', 'superieur', 'ou', 'egal', 'a'],  TT.EST_SUP_OU_EGAL_A),
    (['est', 'egal', 'a'],                     TT.EST_EGAL_A),
    (['est', 'different', 'de'],               TT.EST_DIFFERENT_DE),
    (['est', 'inferieur', 'a'],                TT.EST_INFERIEUR_A),
    (['est', 'superieur', 'a'],                TT.EST_SUPERIEUR_A),
    (['divise', 'par'],                        TT.DIVISE_PAR),
]

# Mots-clés simples (après fusion des séquences)
MOTS_CLES = {
    'vaut':      TT.VAUT,
    'si':        TT.SI,
    'alors':     TT.ALORS,
    'sinon':     TT.SINON,
    'fin':       TT.FIN,
    'pour':      TT.POUR,
    'de':        TT.DE,
    'a':         TT.A,
    'ecrire':    TT.ECRIRE,
    'afficher':  TT.ECRIRE,    # alias
    'lire':      TT.LIRE,
    'fonction':  TT.FONCTION,
    'retourner': TT.RETOURNER,
    'vrai':      TT.VRAI,
    'faux':      TT.FAUX,
    'rien':      TT.RIEN,
    'et':        TT.ET,
    'ou':        TT.OU,
    'non':       TT.NON,
    'plus':      TT.PLUS,
    'moins':     TT.MOINS,
    'fois':      TT.FOIS,
    'modulo':    TT.MODULO,
}


def _normaliser(texte: str) -> str:
    """
    Met en minuscules et supprime les accents.
    Permet d'écrire 'écrire', 'ecrire' ou 'Ecrire' indifféremment.
    """
    sans_accent = ''.join(
        c for c in unicodedata.normalize('NFD', texte)
        if unicodedata.category(c) != 'Mn'
    )
    return sans_accent.lower()


# ── Lexer ─────────────────────────────────────────────────────

class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.pos    = 0
        self.ligne  = 1

    @property
    def _c(self) -> str:
        """Caractère courant (ou '\0' en fin de fichier)."""
        return self.source[self.pos] if self.pos < len(self.source) else '\0'

    def _suivant(self) -> str:
        """Caractère suivant (lookahead d'un cran)."""
        p = self.pos + 1
        return self.source[p] if p < len(self.source) else '\0'

    def _avancer(self):
        if self._c == '\n':
            self.ligne += 1
        self.pos += 1

    # ── Point d'entrée ────────────────────────────────────────

    def tokeniser(self) -> list:
        """
        Convertit le code source en liste de tokens.
        Étape 1 : tokenisation de base.
        Étape 2 : fusion des séquences multi-mots.
        """
        tokens = []

        while self._c != '\0':
            c = self._c

            # Espaces et tabulations ignorés
            if c in (' ', '\t', '\r'):
                self._avancer()

            # Commentaires : tout ce qui suit '#' est ignoré
            elif c == '#':
                while self._c not in ('\n', '\0'):
                    self._avancer()

            # Sauts de ligne → token NEWLINE
            elif c == '\n':
                tokens.append(Token(TT.NEWLINE, '\n', self.ligne))
                self._avancer()

            # Nombres : 42  ou  3.14
            elif c.isdigit():
                tokens.append(self._lire_nombre())

            # Chaînes : "bonjour"  ou  'bonjour'
            elif c in ('"', "'"):
                tokens.append(self._lire_chaine(c))

            # Mots (identifiants ou mots-clés)
            elif c.isalpha() or c == '_':
                tokens.append(self._lire_mot())

            # Parenthèses et virgule
            elif c == '(':
                tokens.append(Token(TT.LPAREN,  '(', self.ligne)); self._avancer()
            elif c == ')':
                tokens.append(Token(TT.RPAREN,  ')', self.ligne)); self._avancer()
            elif c == ',':
                tokens.append(Token(TT.VIRGULE, ',', self.ligne)); self._avancer()

            # ── Symboles arithmétiques ────────────────────────
            elif c == '+':
                tokens.append(Token(TT.PLUS,       '+', self.ligne)); self._avancer()
            elif c == '-':
                tokens.append(Token(TT.MOINS,      '-', self.ligne)); self._avancer()
            elif c == '*':
                tokens.append(Token(TT.FOIS,       '*', self.ligne)); self._avancer()
            elif c == '/':
                tokens.append(Token(TT.DIVISE_PAR, '/', self.ligne)); self._avancer()
            elif c == '%':
                tokens.append(Token(TT.MODULO,     '%', self.ligne)); self._avancer()

            # ── Symboles de comparaison ───────────────────────
            elif c == '<':
                if self._suivant() == '=':
                    tokens.append(Token(TT.EST_INF_OU_EGAL_A, '<=', self.ligne))
                    self._avancer(); self._avancer()
                else:
                    tokens.append(Token(TT.EST_INFERIEUR_A, '<', self.ligne))
                    self._avancer()
            elif c == '>':
                if self._suivant() == '=':
                    tokens.append(Token(TT.EST_SUP_OU_EGAL_A, '>=', self.ligne))
                    self._avancer(); self._avancer()
                else:
                    tokens.append(Token(TT.EST_SUPERIEUR_A, '>', self.ligne))
                    self._avancer()
            elif c == '=':
                if self._suivant() == '=':
                    tokens.append(Token(TT.EST_EGAL_A, '==', self.ligne))
                    self._avancer(); self._avancer()
                else:
                    raise ErreurSyntaxe(
                        "Pour comparer, utilise '==' (double égal). "
                        "Pour assigner une valeur, utilise 'vaut'.",
                        self.ligne
                    )
            elif c == '!':
                if self._suivant() == '=':
                    tokens.append(Token(TT.EST_DIFFERENT_DE, '!=', self.ligne))
                    self._avancer(); self._avancer()
                else:
                    raise ErreurSyntaxe(
                        "Caractère '!' inconnu. Pour inverser une condition, utilise 'non'.",
                        self.ligne
                    )

            else:
                raise ErreurSyntaxe(
                    f"Caractère inconnu : '{c}'",
                    self.ligne
                )

        tokens.append(Token(TT.EOF, None, self.ligne))

        # Étape 2 : fusionner les séquences multi-mots
        tokens = self._fusionner_sequences(tokens)
        return tokens

    # ── Lecture d'un nombre ───────────────────────────────────

    def _lire_nombre(self) -> Token:
        debut = self.pos
        ligne = self.ligne
        while self._c.isdigit():
            self._avancer()
        # Partie décimale optionnelle
        if self._c == '.' and self.pos + 1 < len(self.source) and self.source[self.pos + 1].isdigit():
            self._avancer()
            while self._c.isdigit():
                self._avancer()
        texte = self.source[debut:self.pos]
        valeur = float(texte) if '.' in texte else int(texte)
        return Token(TT.NOMBRE, valeur, ligne)

    # ── Lecture d'une chaîne de caractères ───────────────────

    def _lire_chaine(self, delimiteur: str) -> Token:
        ligne = self.ligne
        self._avancer()          # saute le guillemet ouvrant
        debut = self.pos
        while self._c != delimiteur and self._c != '\0':
            if self._c == '\n':
                raise ErreurSyntaxe("Chaîne de caractères non fermée (retour à la ligne inattendu)", ligne)
            self._avancer()
        if self._c == '\0':
            raise ErreurSyntaxe("Chaîne de caractères non fermée", ligne)
        texte = self.source[debut:self.pos]
        self._avancer()          # saute le guillemet fermant
        return Token(TT.CHAINE, texte, ligne)

    # ── Lecture d'un mot ──────────────────────────────────────

    def _lire_mot(self) -> Token:
        debut = self.pos
        ligne = self.ligne
        while self._c.isalnum() or self._c == '_':
            self._avancer()
        texte  = self.source[debut:self.pos]
        norme  = _normaliser(texte)
        # On stocke la forme normalisée dans un token interne __MOT__
        # La conversion en mot-clé définitif se fait après la fusion
        return Token(TT._MOT, norme, ligne)

    # ── Fusion des séquences multi-mots ──────────────────────

    def _fusionner_sequences(self, tokens: list) -> list:
        """
        Parcourt la liste de tokens et fusionne les suites de __MOT__
        correspondant à des mots-clés composés.

        Exemple :
          [__MOT__('est'), __MOT__('egal'), __MOT__('a')]
          → [EST_EGAL_A]
        """
        resultat = []
        i = 0
        while i < len(tokens):
            tok = tokens[i]

            if tok.type == TT._MOT:
                fusionne = False

                # Essai de chaque séquence (du plus long au plus court)
                for sequence, type_compose in SEQUENCES:
                    n = len(sequence)
                    mots = []
                    j = i
                    for mot_attendu in sequence:
                        if (j < len(tokens)
                                and tokens[j].type == TT._MOT
                                and tokens[j].valeur == mot_attendu):
                            mots.append(tokens[j])
                            j += 1
                        else:
                            break

                    if len(mots) == n:
                        # Séquence reconnue → token composé
                        texte = ' '.join(m.valeur for m in mots)
                        resultat.append(Token(type_compose, texte, tok.ligne))
                        i = j
                        fusionne = True
                        break

                if not fusionne:
                    # Pas de séquence → mot-clé simple ou identifiant
                    resultat.append(self._mot_vers_token(tok))
                    i += 1
            else:
                resultat.append(tok)
                i += 1

        return resultat

    def _mot_vers_token(self, tok: Token) -> Token:
        """Convertit un __MOT__ en mot-clé ou en identifiant."""
        type_ = MOTS_CLES.get(tok.valeur, TT.IDENTIFIANT)
        return Token(type_, tok.valeur, tok.ligne)
