# ─────────────────────────────────────────────────────────────
#  FrLang — Analyse syntaxique (Parser)
#
#  Rôle : lire la liste de tokens produite par le lexer et
#  construire un Arbre Syntaxique Abstrait (AST).
#
#  Grammaire (simplifiée) :
#    programme   → instruction*
#    instruction → affectation | si | tant_que | pour
#                | fonction | retourner | ecrire | lire
#                | appel_fonction
#    expression  → ou_expr
#    ou_expr     → et_expr  (OU et_expr)*
#    et_expr     → non_expr (ET non_expr)*
#    non_expr    → NON non_expr | comparaison
#    comparaison → addition  (comparateur addition)?
#    addition    → multiplic ((PLUS|MOINS) multiplic)*
#    multiplic   → primaire  ((FOIS|DIVISE_PAR|MODULO) primaire)*
#    primaire    → NOMBRE | CHAINE | VRAI | FAUX | RIEN
#                | IDENTIFIANT | appel | LIRE | '(' expr ')'
#                | MOINS primaire
# ─────────────────────────────────────────────────────────────

from .lexer    import TT, Token
from .noeud    import *
from .erreurs  import ErreurSyntaxe


class Parseur:
    def __init__(self, tokens: list):
        self.tokens = tokens
        self.pos    = 0

    # ── Utilitaires ───────────────────────────────────────────

    @property
    def _tok(self) -> Token:
        return self.tokens[self.pos]

    def _avancer(self) -> Token:
        tok = self.tokens[self.pos]
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return tok

    def _consommer(self, type_: str, libelle: str = None) -> Token:
        """Consomme le token courant s'il correspond au type attendu, sinon erreur."""
        if self._tok.type == type_:
            return self._avancer()
        attendu = libelle or f"'{type_}'"
        raise ErreurSyntaxe(
            f"Attendu {attendu}, mais j'ai trouvé '{self._tok.valeur}'",
            self._tok.ligne
        )

    # Mots-clés qui peuvent aussi servir de noms de variables
    # (prépositions ou mots courts fréquemment utilisés comme identifiants)
    _SOFT_KEYWORDS = {TT.A, TT.DE, TT.ET, TT.OU}

    def _consommer_nom(self, libelle: str = "nom de variable") -> Token:
        """
        Consomme un identifiant OU un mot-clé 'soft' (a, de, et, ou)
        qui peut légitimement servir de nom de variable.
        """
        if self._tok.type in (TT.IDENTIFIANT, *self._SOFT_KEYWORDS):
            tok = self._avancer()
            # On le retourne comme IDENTIFIANT peu importe son type original
            return Token(TT.IDENTIFIANT, tok.valeur, tok.ligne)
        raise ErreurSyntaxe(
            f"Attendu {libelle}, mais j'ai trouvé '{self._tok.valeur}'",
            self._tok.ligne
        )

    def _sauter_newlines(self):
        while self._tok.type == TT.NEWLINE:
            self._avancer()

    def _fin_instruction(self):
        """Consomme le saut de ligne (ou EOF) en fin d'instruction."""
        if self._tok.type == TT.NEWLINE:
            self._avancer()
        elif self._tok.type == TT.EOF:
            pass  # Fin de fichier : acceptable
        else:
            raise ErreurSyntaxe(
                f"Fin de ligne attendue après l'instruction, trouvé '{self._tok.valeur}'",
                self._tok.ligne
            )

    # ── Point d'entrée ────────────────────────────────────────

    def analyser(self) -> NoeudProgramme:
        instructions = []
        self._sauter_newlines()
        while self._tok.type != TT.EOF:
            instr = self._instruction()
            if instr is not None:
                instructions.append(instr)
            self._sauter_newlines()
        return NoeudProgramme(instructions=instructions)

    # ── Dispatch principal ────────────────────────────────────

    def _instruction(self):
        self._sauter_newlines()
        tok = self._tok

        if tok.type == TT.ECRIRE:
            return self._instr_ecrire()
        elif tok.type == TT.SI:
            return self._instr_si()
        elif tok.type == TT.TANT_QUE:
            return self._instr_tant_que()
        elif tok.type == TT.POUR:
            return self._instr_pour()
        elif tok.type == TT.FONCTION:
            return self._instr_fonction()
        elif tok.type == TT.RETOURNER:
            return self._instr_retourner()
        elif tok.type in (TT.IDENTIFIANT, *self._SOFT_KEYWORDS):
            return self._instr_identifiant()
        elif tok.type == TT.NEWLINE:
            self._avancer()
            return None
        elif tok.type == TT.EOF:
            return None
        else:
            raise ErreurSyntaxe(
                f"Instruction inconnue : '{tok.valeur}'",
                tok.ligne
            )

    # ── Instructions ──────────────────────────────────────────

    def _instr_ecrire(self):
        ligne = self._tok.ligne
        self._avancer()              # consomme 'ecrire'
        expr = self._expression()
        self._fin_instruction()
        return NoeudEcrire(expression=expr, ligne=ligne)

    def _instr_si(self):
        ligne = self._tok.ligne
        self._avancer()              # consomme 'si'
        condition = self._expression()
        self._consommer(TT.ALORS, "'alors'")
        self._sauter_newlines()

        bloc_alors = self._bloc()
        sinon_si   = []
        bloc_sinon = None

        # Zéro ou plusieurs 'sinon si'
        while self._tok.type == TT.SINON_SI:
            self._avancer()
            cond = self._expression()
            self._consommer(TT.ALORS, "'alors'")
            self._sauter_newlines()
            bloc = self._bloc()
            sinon_si.append((cond, bloc))

        # Un 'sinon' optionnel
        if self._tok.type == TT.SINON:
            self._avancer()
            self._sauter_newlines()
            bloc_sinon = self._bloc()

        self._consommer(TT.FIN, "'fin'")
        self._fin_instruction()
        return NoeudSi(
            condition  = condition,
            bloc_alors = bloc_alors,
            sinon_si   = sinon_si,
            bloc_sinon = bloc_sinon,
            ligne      = ligne,
        )

    def _instr_tant_que(self):
        ligne = self._tok.ligne
        self._avancer()              # consomme 'tant que'
        condition = self._expression()
        self._sauter_newlines()
        corps = self._bloc()
        self._consommer(TT.FIN, "'fin'")
        self._fin_instruction()
        return NoeudTantQue(condition=condition, corps=corps, ligne=ligne)

    def _instr_pour(self):
        ligne = self._tok.ligne
        self._avancer()              # consomme 'pour'
        var = self._consommer_nom("nom de variable").valeur
        self._consommer(TT.DE, "'de'")
        debut = self._expression()
        self._consommer(TT.A, "'a'")
        fin   = self._expression()
        self._sauter_newlines()
        corps = self._bloc()
        self._consommer(TT.FIN, "'fin'")
        self._fin_instruction()
        return NoeudPour(variable=var, debut=debut, fin=fin, corps=corps, ligne=ligne)

    def _instr_fonction(self):
        ligne = self._tok.ligne
        self._avancer()              # consomme 'fonction'
        nom = self._consommer_nom("nom de la fonction").valeur
        self._consommer(TT.LPAREN, "'('")
        params = []
        if self._tok.type != TT.RPAREN:
            params.append(self._consommer_nom("nom de paramètre").valeur)
            while self._tok.type == TT.VIRGULE:
                self._avancer()
                params.append(self._consommer_nom("nom de paramètre").valeur)
        self._consommer(TT.RPAREN, "')'")
        self._sauter_newlines()
        corps = self._bloc()
        self._consommer(TT.FIN, "'fin'")
        self._fin_instruction()
        return NoeudFonction(nom=nom, parametres=params, corps=corps, ligne=ligne)

    def _instr_retourner(self):
        ligne = self._tok.ligne
        self._avancer()              # consomme 'retourner'
        valeur = self._expression()
        self._fin_instruction()
        return NoeudRetourner(valeur=valeur, ligne=ligne)

    def _instr_identifiant(self):
        """Affectation  ou  appel de fonction utilisé comme instruction."""
        ligne = self._tok.ligne
        nom   = self._consommer_nom().valeur   # consomme IDENTIFIANT (ou soft keyword)

        if self._tok.type == TT.VAUT:
            # nom vaut expression
            self._avancer()
            valeur = self._expression()
            self._fin_instruction()
            return NoeudAffectation(nom=nom, valeur=valeur, ligne=ligne)

        elif self._tok.type == TT.LPAREN:
            # nom(arg, arg, …)  utilisé comme instruction
            appel = self._appel_fonction(nom, ligne)
            self._fin_instruction()
            return appel

        else:
            raise ErreurSyntaxe(
                f"Attendu 'vaut' ou '(' après '{nom}'",
                ligne
            )

    # ── Bloc d'instructions ───────────────────────────────────

    def _bloc(self) -> list:
        """
        Lit des instructions jusqu'à trouver 'fin', 'sinon',
        'sinon si' ou la fin de fichier.
        """
        instructions = []
        self._sauter_newlines()
        while self._tok.type not in (TT.FIN, TT.SINON, TT.SINON_SI, TT.EOF):
            instr = self._instruction()
            if instr is not None:
                instructions.append(instr)
            self._sauter_newlines()
        return instructions

    # ── Expressions (avec priorités) ──────────────────────────
    #
    #  Priorité (de la plus faible à la plus forte) :
    #  ou → et → non → comparaison → addition → multiplication → primaire

    def _expression(self):
        return self._ou_expr()

    def _ou_expr(self):
        gauche = self._et_expr()
        while self._tok.type == TT.OU:
            op = self._avancer()
            droite = self._et_expr()
            gauche = NoeudEtOu(gauche=gauche, operateur='ou', droite=droite, ligne=op.ligne)
        return gauche

    def _et_expr(self):
        gauche = self._non_expr()
        while self._tok.type == TT.ET:
            op = self._avancer()
            droite = self._non_expr()
            gauche = NoeudEtOu(gauche=gauche, operateur='et', droite=droite, ligne=op.ligne)
        return gauche

    def _non_expr(self):
        if self._tok.type == TT.NON:
            ligne = self._tok.ligne
            self._avancer()
            return NoeudNegation(operande=self._non_expr(), ligne=ligne)
        return self._comparaison()

    _COMPARATEURS = {
        TT.EST_EGAL_A,
        TT.EST_DIFFERENT_DE,
        TT.EST_INFERIEUR_A,
        TT.EST_SUPERIEUR_A,
        TT.EST_INF_OU_EGAL_A,
        TT.EST_SUP_OU_EGAL_A,
    }

    def _comparaison(self):
        gauche = self._addition()
        if self._tok.type in self._COMPARATEURS:
            op     = self._avancer()
            droite = self._addition()
            return NoeudComparaison(gauche=gauche, operateur=op.type, droite=droite, ligne=op.ligne)
        return gauche

    def _addition(self):
        gauche = self._multiplication()
        while self._tok.type in (TT.PLUS, TT.MOINS):
            op     = self._avancer()
            droite = self._multiplication()
            gauche = NoeudOperationBinaire(gauche=gauche, operateur=op.type, droite=droite, ligne=op.ligne)
        return gauche

    def _multiplication(self):
        gauche = self._primaire()
        while self._tok.type in (TT.FOIS, TT.DIVISE_PAR, TT.MODULO):
            op     = self._avancer()
            droite = self._primaire()
            gauche = NoeudOperationBinaire(gauche=gauche, operateur=op.type, droite=droite, ligne=op.ligne)
        return gauche

    def _primaire(self):
        tok  = self._tok
        ligne = tok.ligne

        if tok.type == TT.NOMBRE:
            self._avancer()
            return NoeudNombre(valeur=tok.valeur, ligne=ligne)

        elif tok.type == TT.CHAINE:
            self._avancer()
            return NoeudChaine(valeur=tok.valeur, ligne=ligne)

        elif tok.type == TT.VRAI:
            self._avancer()
            return NoeudBooleen(valeur=True, ligne=ligne)

        elif tok.type == TT.FAUX:
            self._avancer()
            return NoeudBooleen(valeur=False, ligne=ligne)

        elif tok.type == TT.RIEN:
            self._avancer()
            return NoeudRien(ligne=ligne)

        elif tok.type == TT.MOINS:
            # Négation arithmétique : moins 5  →  -5
            self._avancer()
            return NoeudNegation(operande=self._primaire(), ligne=ligne)

        elif tok.type == TT.LPAREN:
            self._avancer()
            expr = self._expression()
            self._consommer(TT.RPAREN, "')'")
            return expr

        elif tok.type == TT.LIRE:
            # lire "message"  utilisé comme expression (dans une affectation)
            self._avancer()
            if self._tok.type == TT.CHAINE:
                invite = NoeudChaine(valeur=self._avancer().valeur, ligne=ligne)
            else:
                invite = NoeudChaine(valeur='', ligne=ligne)
            return NoeudLire(invite=invite, ligne=ligne)

        elif tok.type in (TT.IDENTIFIANT, *self._SOFT_KEYWORDS):
            nom = self._avancer().valeur
            if self._tok.type == TT.LPAREN:
                return self._appel_fonction(nom, ligne)
            return NoeudIdentifiant(nom=nom, ligne=ligne)

        else:
            raise ErreurSyntaxe(
                f"Expression attendue, mais j'ai trouvé '{tok.valeur}'",
                ligne
            )

    def _appel_fonction(self, nom: str, ligne: int) -> NoeudAppelFonction:
        """Analyse les arguments : nom(arg1, arg2, …)"""
        self._consommer(TT.LPAREN, "'('")
        args = []
        if self._tok.type != TT.RPAREN:
            args.append(self._expression())
            while self._tok.type == TT.VIRGULE:
                self._avancer()
                args.append(self._expression())
        self._consommer(TT.RPAREN, "')'")
        return NoeudAppelFonction(nom=nom, arguments=args, ligne=ligne)
