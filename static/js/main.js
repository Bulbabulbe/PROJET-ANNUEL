// ─────────────────────────────────────────────────────────────
//  SharCode — Interface web
// ─────────────────────────────────────────────────────────────

// ── Contenu des leçons ────────────────────────────────────────
const LECONS = [
  {
    numero: 'Leçon 1',
    titre: 'Les variables',
    desc: 'Stocker des informations',
    contenu: `
      <p>Une <strong>variable</strong>, c'est une boîte dans laquelle on range une information. On lui donne un nom, et on lui assigne une valeur avec le mot <strong>vaut</strong>.</p>
      <div class="highlight"><strong>nom</strong>  vaut  <strong>valeur</strong></div>
      <p>Il existe plusieurs types de valeurs :</p>
      <p>• <strong>Nombre</strong> &nbsp;&nbsp;— <code style="background:#f1f5f9;padding:2px 6px;border-radius:4px">age vaut 15</code></p>
      <p>• <strong>Texte</strong> &nbsp;&nbsp;&nbsp;&nbsp;— <code style="background:#f1f5f9;padding:2px 6px;border-radius:4px">prenom vaut "Alice"</code> (toujours entre guillemets)</p>
      <p>• <strong>Vrai/Faux</strong> — <code style="background:#f1f5f9;padding:2px 6px;border-radius:4px">connecte vaut vrai</code></p>
      <p>Pour afficher une variable, on utilise <strong>ecrire</strong>. Pour combiner texte et variables, on utilise <strong>+</strong>.</p>
    `,
    code: `# Mes premières variables
prenom vaut "Alice"
age vaut 15
taille vaut 1.68

ecrire prenom
ecrire age
ecrire "Taille : " + taille + " m"`
  },
  {
    numero: 'Leçon 2',
    titre: 'Afficher et saisir',
    desc: 'Communiquer avec l\'utilisateur',
    contenu: `
      <p>Pour <strong>afficher</strong> quelque chose à l'écran :</p>
      <div class="highlight">ecrire "Bonjour !"<br>ecrire "Age : " + age</div>
      <p>Pour <strong>demander</strong> une saisie à l'utilisateur :</p>
      <div class="highlight">prenom vaut lire "Comment tu t'appelles ? "</div>
      <p>Si tu saisis un nombre, il faut le convertir avec <strong>nombre()</strong> :</p>
      <div class="highlight">age vaut nombre(lire "Quel age as-tu ? ")</div>
      <p>Attention : dans cet éditeur, si ton programme utilise <em>lire</em>, écris tes réponses dans la zone <strong>Entrées du programme</strong>, une par ligne.</p>
    `,
    code: `# Afficher et saisir
prenom vaut lire "Quel est ton prénom ? "
age vaut nombre(lire "Quel est ton age ? ")

ecrire "Bonjour " + prenom + " !"
ecrire "Tu as " + age + " ans."`,
    entrees: 'Alice\n15'
  },
  {
    numero: 'Leçon 3',
    titre: 'L\'indentation',
    desc: 'Organiser le code lisiblement',
    contenu: `
      <p>L'<strong>indentation</strong>, c'est les espaces au début de certaines lignes. En SharCode, le code qui est <em>à l'intérieur</em> d'un bloc (condition, boucle, fonction) doit être décalé vers la droite.</p>
      <p>Utilise la touche <strong>Tab</strong> pour indenter (4 espaces).</p>
      <div class="highlight">si age >= 18 alors<br><span style="color:#0077b6">    </span>ecrire "Majeur"   <span style="color:#999"># décalé = à l'intérieur du si</span><br>fin<br><br>ecrire "Fin"   <span style="color:#999"># pas décalé = en dehors du si</span></div>
      <p>SharCode utilise le mot <strong>fin</strong> pour fermer chaque bloc. L'indentation ne change pas le résultat pour l'ordinateur, mais elle rend le code <strong>beaucoup plus lisible</strong> pour toi et tes camarades.</p>
      <p>Règle simple : chaque fois que tu ouvres un bloc (<em>alors</em>, <em>tant que</em>, <em>pour</em>, <em>fonction</em>), tu indentes. Quand tu écris <em>fin</em>, tu reviens en arrière.</p>
    `,
    code: `# Exemple d'indentation
x vaut 10

si x > 5 alors
    ecrire "x est grand"    # indenté : à l'intérieur du si
    si x > 8 alors
        ecrire "x est très grand"   # double indentation
    fin
sinon
    ecrire "x est petit"    # indenté : à l'intérieur du sinon
fin

ecrire "Terminé"    # pas indenté : en dehors du si`
  },
  {
    numero: 'Leçon 4',
    titre: 'Les conditions',
    desc: 'Prendre des décisions',
    contenu: `
      <p>Une <strong>condition</strong> permet d'exécuter du code différent selon une situation.</p>
      <div class="highlight">si condition alors<br>    ...<br>sinon<br>    ...<br>fin</div>
      <p>Les opérateurs de comparaison :</p>
      <p>• <strong>==</strong> &nbsp;— égal à</p>
      <p>• <strong>!=</strong> &nbsp;— différent de</p>
      <p>• <strong>&lt;</strong> &nbsp;&nbsp;— inférieur à</p>
      <p>• <strong>&gt;</strong> &nbsp;&nbsp;— supérieur à</p>
      <p>• <strong>&lt;=</strong> — inférieur ou égal</p>
      <p>• <strong>&gt;=</strong> — supérieur ou égal</p>
      <p>On peut combiner avec <strong>et</strong> / <strong>ou</strong>, et enchaîner avec <strong>sinon si</strong>.</p>
    `,
    code: `# Les conditions
note vaut 14

si note >= 16 alors
    ecrire "Mention Très Bien !"
sinon si note >= 14 alors
    ecrire "Mention Bien"
sinon si note >= 10 alors
    ecrire "Admis"
sinon
    ecrire "Insuffisant"
fin

# Combiner deux conditions
age vaut 17
permis vaut faux

si age >= 18 et permis alors
    ecrire "Tu peux conduire"
sinon
    ecrire "Tu ne peux pas conduire"
fin`
  },
  {
    numero: 'Leçon 5',
    titre: 'Les boucles',
    desc: 'Répéter des instructions',
    contenu: `
      <p>Il y a deux types de boucles en SharCode.</p>
      <p><strong>La boucle pour</strong> — quand on sait combien de fois on répète :</p>
      <div class="highlight">pour i de 1 a 10<br>    ...<br>fin</div>
      <p><strong>La boucle tant que</strong> — quand on répète jusqu'à ce qu'une condition soit fausse :</p>
      <div class="highlight">tant que condition<br>    ...<br>fin</div>
      <p>Attention : dans une boucle <em>tant que</em>, il faut que la condition devienne fausse à un moment, sinon le programme tourne indéfiniment.</p>
    `,
    code: `# Boucle pour : table de 7
pour i de 1 a 10
    ecrire "7 x " + i + " = " + 7 * i
fin

ecrire ""

# Boucle tant que : compte à rebours
i vaut 5
tant que i > 0
    ecrire i
    i vaut i - 1
fin
ecrire "Partez !"`
  },
  {
    numero: 'Leçon 6',
    titre: 'Les fonctions',
    desc: 'Organiser et réutiliser son code',
    contenu: `
      <p>Une <strong>fonction</strong> est un bloc de code qu'on nomme pour pouvoir le réutiliser.</p>
      <div class="highlight">fonction nom(parametre1, parametre2)<br>    ...<br>    retourner resultat<br>fin</div>
      <p>On appelle une fonction en écrivant son nom avec des parenthèses :</p>
      <div class="highlight">resultat vaut additionner(3, 4)</div>
      <p>Les fonctions permettent d'<strong>éviter les répétitions</strong> : au lieu d'écrire le même code plusieurs fois, on l'écrit une fois dans une fonction.</p>
      <p>C'est la base des <strong>bonnes pratiques</strong> en programmation.</p>
    `,
    code: `# Les fonctions
fonction saluer(prenom)
    ecrire "Bonjour " + prenom + " !"
fin

fonction est_pair(n)
    retourner n % 2 == 0
fin

saluer("Alice")
saluer("Bob")

ecrire ""
pour i de 1 a 10
    si est_pair(i) alors
        ecrire i + " est pair"
    sinon
        ecrire i + " est impair"
    fin
fin`
  }
];

// ── Exemples prêts à l'emploi ─────────────────────────────────
const EXEMPLES = [
  {
    titre: 'Deviner un nombre',
    desc: 'Jeu avec boucle et conditions',
    entrees: '10\n30\n42',
    code: `# Jeu : deviner le nombre secret
secret vaut 42
essais vaut 0
gagne vaut faux

ecrire "=== Jeu du nombre secret (1 à 100) ==="
ecrire ""

tant que non gagne
    reponse vaut nombre(lire "Propose un nombre : ")
    essais vaut essais + 1

    si reponse == secret alors
        gagne vaut vrai
    sinon si reponse < secret alors
        ecrire "Trop petit !"
    sinon
        ecrire "Trop grand !"
    fin
fin

ecrire ""
ecrire "Bravo ! Trouvé en " + essais + " essai(s) !"`
  },
  {
    titre: 'Table de multiplication',
    desc: 'Boucles imbriquées',
    code: `# Tables de multiplication de 1 à 5
pour table de 1 a 5
    ecrire "=== Table de " + table + " ==="
    pour i de 1 a 10
        ecrire table + " x " + i + " = " + table * i
    fin
    ecrire ""
fin`
  },
  {
    titre: 'Factorielle (récursif)',
    desc: 'Fonctions récursives',
    code: `# Calcul de factorielle par récursivité
fonction factorielle(n)
    si n <= 1 alors
        retourner 1
    fin
    retourner n * factorielle(n - 1)
fin

pour i de 1 a 12
    ecrire texte(i) + "! = " + factorielle(i)
fin`
  },
  {
    titre: 'Calculatrice simple',
    desc: 'Saisie, conditions, opérations',
    entrees: '10\n3',
    code: `# Calculatrice simple
a vaut nombre(lire "Premier nombre : ")
b vaut nombre(lire "Deuxième nombre : ")

ecrire ""
ecrire "=== Résultats ==="
ecrire a + " + " + b + " = " + (a + b)
ecrire a + " - " + b + " = " + (a - b)
ecrire a + " x " + b + " = " + (a * b)

si b != 0 alors
    ecrire a + " / " + b + " = " + arrondir(a / b, 2)
sinon
    ecrire "Division impossible"
fin`
  },
  {
    titre: 'Nombres premiers',
    desc: 'Algorithme classique',
    code: `# Nombres premiers jusqu'à 50
fonction est_premier(n)
    si n < 2 alors
        retourner faux
    fin
    i vaut 2
    tant que i * i <= n
        si n % i == 0 alors
            retourner faux
        fin
        i vaut i + 1
    fin
    retourner vrai
fin

ecrire "Nombres premiers jusqu'à 50 :"
pour n de 2 a 50
    si est_premier(n) alors
        ecrire n
    fin
fin`
  }
];


// ── Initialisation ────────────────────────────────────────────
let leconActive = 0;
let programmeCourantId = null;   // fichier élève actuellement ouvert (null = nouveau)

document.addEventListener('DOMContentLoaded', () => {
  construireLecons();
  construireExemples();
  updateLineNumbers();
});

function construireLecons() {
  const container = document.getElementById('lecons-list');
  LECONS.forEach((l, i) => {
    const card = document.createElement('div');
    card.className = 'lecon-card';
    card.innerHTML = `
      <div class="lecon-numero">${l.numero}</div>
      <div class="lecon-titre">${l.titre}</div>
      <div class="lecon-desc">${l.desc}</div>
    `;
    card.onclick = () => ouvrirLecon(i);
    container.appendChild(card);
  });
}

function construireExemples() {
  const container = document.getElementById('exemples-list');
  EXEMPLES.forEach((ex, i) => {
    const card = document.createElement('div');
    card.className = 'exemple-card';
    card.innerHTML = `
      <div class="exemple-card-titre">${ex.titre}</div>
      <div class="exemple-card-desc">${ex.desc}</div>
    `;
    card.onclick = () => chargerExemple(ex);
    container.appendChild(card);
  });
}


// ── Navigation sidebar ────────────────────────────────────────
function showPanel(nom) {
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
  const panel = document.getElementById('panel-' + nom);
  if (panel) panel.classList.add('active');
  const btn = document.querySelector('.nav-btn[data-panel="' + nom + '"]');
  if (btn) btn.classList.add('active');
}


// ── Modal Leçon ───────────────────────────────────────────────
function ouvrirLecon(index) {
  leconActive = index;
  const l = LECONS[index];
  document.getElementById('modal-titre').textContent   = `${l.numero} — ${l.titre}`;
  document.getElementById('modal-contenu').innerHTML   = l.contenu;
  document.getElementById('modal-code').textContent    = l.code;
  document.getElementById('modal-progress').textContent = `${index + 1} / ${LECONS.length}`;

  const btnPrev = document.getElementById('btn-prev-lecon');
  const btnNext = document.getElementById('btn-next-lecon');
  btnPrev.disabled = index === 0;
  btnNext.textContent = index === LECONS.length - 1 ? 'Terminer' : 'Suivant →';

  document.getElementById('modal-lecon').classList.add('open');
  document.getElementById('modal-overlay').classList.add('open');
}

function fermerLecon() {
  document.getElementById('modal-lecon').classList.remove('open');
  document.getElementById('modal-overlay').classList.remove('open');
}

function navLecon(direction) {
  const next = leconActive + direction;
  // Marquer la leçon actuelle comme complétée
  const l = LECONS[leconActive];
  fetch('/etudiant/lecon', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ lecon_id: leconActive + 1, lecon_titre: l.titre })
  }).catch(() => {});
  if (next < 0 || next >= LECONS.length) { fermerLecon(); return; }
  ouvrirLecon(next);
}

function chargerExempleLecon() {
  const l = LECONS[leconActive];
  document.getElementById('editor').value = l.code;
  if (l.entrees) document.getElementById('entrees').value = l.entrees;
  programmeCourantId = null;
  const fn = document.getElementById('filename');
  if (fn) fn.textContent = 'mon_programme.shc';
  updateLineNumbers();
  fermerLecon();
}

function chargerExemple(ex) {
  document.getElementById('editor').value = ex.code;
  document.getElementById('entrees').value = ex.entrees || '';
  programmeCourantId = null;
  const fn = document.getElementById('filename');
  if (fn) fn.textContent = 'mon_programme.shc';
  updateLineNumbers();
  showPanel('apprendre');
}


// ── Éditeur ───────────────────────────────────────────────────
function handleTab(e) {
  if (e.key !== 'Tab') return;
  e.preventDefault();
  const ta    = e.target;
  const start = ta.selectionStart;
  const end   = ta.selectionEnd;
  ta.value = ta.value.substring(0, start) + '    ' + ta.value.substring(end);
  ta.selectionStart = ta.selectionEnd = start + 4;
}

function updateLineNumbers() {
  const editor  = document.getElementById('editor');
  const lines   = editor.value.split('\n');
  const nums    = lines.map((_, i) => i + 1).join('\n');
  document.getElementById('line-numbers').textContent = nums || '1';
}

function syncScroll() {
  const editor = document.getElementById('editor');
  const ln     = document.getElementById('line-numbers');
  ln.scrollTop = editor.scrollTop;
}

function clearEditor() {
  if (document.getElementById('editor').value &&
      !confirm('Effacer tout le code ?')) return;
  document.getElementById('editor').value = '';
  document.getElementById('entrees').value = '';
  updateLineNumbers();
  clearConsole();
}


// ── Exécution ─────────────────────────────────────────────────
async function lancerCode() {
  const code    = document.getElementById('editor').value.trim();
  const entrees = document.getElementById('entrees').value;
  const btn     = document.getElementById('btn-run');
  const output  = document.getElementById('console-output');

  if (!code) {
    afficherConsole('Rien à exécuter. Écris du code d\'abord !', 'console-error');
    return;
  }

  btn.disabled = true;
  btn.textContent = 'En cours...';
  afficherConsole('Exécution en cours...', 'console-running loading');

  try {
    const res  = await fetch('/executer', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ code, entrees })
    });
    const data = await res.json();

    if (data.succes) {
      const texte = data.sortie || '(Aucune sortie)';
      afficherConsole(texte, 'console-success');
    } else {
      afficherConsole('Erreur — ' + data.erreur, 'console-error');
    }
  } catch (err) {
    afficherConsole('Impossible de contacter le serveur.', 'console-error');
  } finally {
    btn.disabled = false;
    btn.textContent = '&#9654; Lancer';
  }
}

function afficherConsole(texte, classe = 'console-success') {
  const output = document.getElementById('console-output');
  output.innerHTML = '';
  const span = document.createElement('span');
  span.className = classe;
  span.textContent = texte;
  output.appendChild(span);
}

function clearConsole() {
  document.getElementById('console-output').innerHTML =
    '<span class="console-welcome">Console effacée.</span>';
}

// Raccourci clavier : Ctrl+Entrée pour lancer
document.addEventListener('keydown', e => {
  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
    e.preventDefault();
    lancerCode();
  }
});


// ── Mes fichiers (programmes sauvegardés de l'élève) ──────────
function escapeHtml(s) {
  return String(s == null ? '' : s).replace(/[&<>"']/g, c => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[c]));
}

async function chargerMesProgrammes() {
  const container = document.getElementById('programmes-list');
  if (!container) return;
  container.innerHTML = '<p class="panel-subtitle">Chargement...</p>';
  try {
    const rep  = await fetch('/etudiant/programmes');
    const data = await rep.json();
    const progs = data.programmes || [];
    if (progs.length === 0) {
      container.innerHTML = '<p class="panel-subtitle">Aucun fichier sauvegardé pour l\'instant.</p>';
      return;
    }
    container.innerHTML = '';
    progs.forEach(p => {
      const card = document.createElement('div');
      card.className = 'exemple-card';
      const date = (p.date_sauvegarde || '').substring(0, 16).replace('T', ' ');
      card.innerHTML =
        '<div class="exemple-card-titre">' + escapeHtml(p.nom) + '</div>' +
        '<div class="exemple-card-desc">' + escapeHtml(date) + '</div>';

      const actions = document.createElement('div');
      actions.className = 'table-actions';
      actions.style.marginTop = '0.5rem';

      const bOpen = document.createElement('button');
      bOpen.className = 'btn-secondary btn-small';
      bOpen.textContent = 'Ouvrir';
      bOpen.onclick = () => ouvrirProgramme(p.id, p.nom, p.code);

      const bDel = document.createElement('button');
      bDel.className = 'btn-danger btn-small';
      bDel.textContent = 'Supprimer';
      bDel.onclick = () => supprimerMonProgramme(p.id, p.nom);

      actions.appendChild(bOpen);
      actions.appendChild(bDel);
      card.appendChild(actions);
      container.appendChild(card);
    });
  } catch (e) {
    container.innerHTML = '<p class="panel-subtitle">Erreur de chargement.</p>';
  }
}

function ouvrirProgramme(id, nom, code) {
  programmeCourantId = id;
  document.getElementById('editor').value = code || '';
  document.getElementById('filename').textContent = (nom || 'mon_programme') + '.shc';
  updateLineNumbers();
  showPanel('apprendre');  // retour à l'éditeur
}

function nouveauProgramme() {
  programmeCourantId = null;
  document.getElementById('editor').value = '';
  document.getElementById('entrees').value = '';
  document.getElementById('filename').textContent = 'mon_programme.shc';
  updateLineNumbers();
}

async function supprimerMonProgramme(id, nom) {
  if (!confirm('Supprimer le fichier "' + nom + '" ?')) return;
  await fetch('/etudiant/programme/' + id + '/supprimer', { method: 'POST' });
  if (programmeCourantId === id) nouveauProgramme();
  chargerMesProgrammes();
}
