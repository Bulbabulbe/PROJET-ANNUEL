#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║            SharCode — Interpréteur v1.0                      ║
║    Le premier langage de programmation en français naturel   ║
╠══════════════════════════════════════════════════════════════╣
║  Usage :                                                     ║
║    python main.py              → Mode interactif (REPL)      ║
║    python main.py fichier.shc  → Exécuter un fichier         ║
╚══════════════════════════════════════════════════════════════╝
"""

import sys
import os

# Forcer l'encodage UTF-8 sur Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from frLang.lexer        import Lexer
from frLang.parseur      import Parseur
from frLang.interpreteur import Interpreteur
from frLang.erreurs      import ErreurFrLang


BANNIERE = """
╔══════════════════════════════════════════╗
║        SharCode 1.0  — Mode interactif  ║
║  Tapez votre code, puis Entrée.          ║
║  Tapez  quitter  pour sortir.            ║
╚══════════════════════════════════════════╝
"""


# ── Exécuter un bloc de code ──────────────────────────────────

def executer_source(source: str, interpreteur: Interpreteur) -> bool:
    """
    Retourne True si l'exécution s'est bien passée, False sinon.
    """
    try:
        tokens = Lexer(source).tokeniser()
        ast    = Parseur(tokens).analyser()
        interpreteur.executer(ast)
        return True
    except ErreurFrLang as e:
        print(f"\n  ❌ {e}\n", file=sys.stderr)
        return False
    except RecursionError:
        print("\n  ❌ Erreur : récursion trop profonde (fonction qui s'appelle trop souvent)\n",
              file=sys.stderr)
        return False


# ── Mode fichier ──────────────────────────────────────────────

def mode_fichier(chemin: str):
    if not os.path.exists(chemin):
        print(f"  ❌ Fichier introuvable : '{chemin}'", file=sys.stderr)
        sys.exit(1)

    with open(chemin, 'r', encoding='utf-8') as f:
        source = f.read()

    interpreteur = Interpreteur()
    ok = executer_source(source, interpreteur)
    sys.exit(0 if ok else 1)


# ── Mode interactif (REPL) ────────────────────────────────────

def mode_interactif():
    print(BANNIERE)
    interpreteur = Interpreteur()

    while True:
        try:
            ligne = input(">>> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  Au revoir !")
            break

        if not ligne:
            continue

        if ligne.lower() in ('quitter', 'quit', 'exit', 'q'):
            print("  Au revoir !")
            break

        executer_source(ligne, interpreteur)


# ── Point d'entrée ────────────────────────────────────────────

def main():
    if len(sys.argv) > 1:
        mode_fichier(sys.argv[1])
    else:
        mode_interactif()


if __name__ == '__main__':
    main()
