# Pixel Art Game Studio

[← README principal](../../README.md) · Français · Traduction assistée par machine, en attente de relecture par des locuteurs natifs.

<!-- section: overview -->
## Présentation

Pixel Art Game Studio est une skill pour Claude Code accompagnée d'une équipe de huit sous-agents
spécialisés, destinée à créer des jeux 2D originaux en pixel art. Vous décrivez le jeu que vous
imaginez, ce qui vous déplaît dans le résultat actuel et ce qu'il faut changer ensuite. Claude planifie
le travail, écrit le code, génère les graphismes, lance les tests, corrige les bogues qu'il parvient à
reproduire et ne rapporte que ce qu'il a réellement vérifié.

L'outil vise les aventures narratives douillettes, les simulations de vie et de ferme, les jeux de rôle
riches en dialogues, les jeux d'exploration en vue de dessus et les jeux de réflexion, mais il convient
aussi à d'autres idées 2D originales. Quatre éléments restent séparés : la **skill** (les
instructions), les **agents** (les spécialistes), les **scripts** (des outils déterministes) et
**votre jeu** (son propre répertoire de projet).

<!-- section: features -->
## Fonctionnalités

- Un déroulé de Game Director qui transforme une idée vague en une conception courte et une boucle
  jouable minimale.
- Huit spécialistes aux responsabilités claires, avec des listes d'outils limitées et des rapports
  structurés.
- Du pixel art procédural : des spécifications JSON deviennent de vraies planches de sprites PNG, des
  métadonnées et des aperçus. La même spécification produit toujours les mêmes octets.
- Un contrat de données pour les cartes, le décor, les dialogues, les quêtes, les objets et les
  traductions, avec un validateur qui repère les sorties inaccessibles, les branches de dialogue
  impossibles et les clés de texte manquantes.
- Une assurance qualité avec niveaux de gravité, rapports de défauts reproductibles et corrections
  vérifiées par des tests de régression.
- Un installateur sûr avec simulation, détection des conflits, sauvegardes et désinstallation prudente.

<!-- section: agents -->
## L'équipe d'agents

Il y a neuf rôles. Le **Game Director** est la skill elle-même ; il s'exécute dans votre session
principale de Claude Code : il tient la conception, rédige les consignes, vérifie chaque résultat et
décide quand une tâche est terminée. Les huit sous-agents sont :

| Agent | Responsabilité |
| --- | --- |
| `pixel-artist` | direction artistique, spécifications des ressources, sprites et tuiles générés |
| `npc-story-engineer` | personnages, dialogues à embranchements, drapeaux, quêtes |
| `world-builder-level-design` | structure des cartes, collisions, points d'apparition, sorties |
| `world-builder-environmental-content` | décor, lieux d'intérêt, ambiance de chaque région |
| `ui-engineer` | menus, HUD, boîte de dialogue, écrans d'inventaire et de sauvegarde |
| `gameplay-engineer` | déplacement, état du jeu, inventaire, quêtes, sauvegarde |
| `qa-tester` | tests, exécutions de tests, rapports de défauts |
| `bug-fixer` | corrections de la cause profonde avec tests de régression |

Plus de détails : [AGENTS.md](../AGENTS.md).

<!-- section: architecture -->
## Architecture

Le Director est la skill et non un sous-agent, car il doit voir vos demandes et conserver une source de
vérité unique (`design/GAME_DESIGN.md`, `ART_DIRECTION.md` et cinq autres documents courts). Les
spécialistes reçoivent des consignes précises, travaillent sur les fichiers dont ils ont la charge et
rendent un rapport ; ils ne peuvent pas lancer d'autres agents. Le contenu du jeu se trouve dans un
dossier `data/` indépendant du moteur, ce qui permet d'avancer en parallèle sur l'histoire, les niveaux
et l'environnement et de tout vérifier sans démarrer le moteur. Si les sous-agents ne sont pas
disponibles, le Director effectue lui-même les mêmes étapes, l'une après l'autre. Voir
[ARCHITECTURE.md](../ARCHITECTURE.md).

<!-- section: prerequisites -->
## Prérequis

- Claude Code (vérifié avec la version 2.1.312).
- Python 3.9 ou plus récent ; aucun paquet supplémentaire n'est nécessaire.
- Pour de vrais jeux, le moteur de votre choix, par exemple Godot 4 ou le SDK .NET pour MonoGame. La
  skill vérifie ce qui est installé et demande avant d'installer quoi que ce soit.

<!-- section: installation -->
## Installation

Le plus simple est de l'installer comme plugin depuis Claude Code. La skill s'appelle alors `/pixel-art-game-studio:pixel-art-game-studio` et les agents prennent le préfixe `pixel-art-game-studio:` :

```text
/plugin marketplace add Rodinyamert48/pixel-art-game-studio
/plugin install pixel-art-game-studio@pixel-art-game-studio
```

Ou bien, sans le système de plugins : Clonez le dépôt, puis choisissez le mode d'installation. Prévisualisez toujours les changements avec
`--dry-run` :

```bash
python scripts/install.py --scope project --project-dir ../my-game --dry-run
python scripts/install.py --scope project --project-dir ../my-game
python scripts/install.py --scope user
```

La portée projet écrit dans `<project>/.claude/`, la portée utilisateur dans `~/.claude/`. Les fichiers
existants que l'installateur n'a pas créés ne sont jamais remplacés. Utilisez `--update` pour mettre à
jour une installation (les anciens fichiers sont sauvegardés) et `--uninstall` pour supprimer
uniquement les fichiers non modifiés qu'il a installés. Vous pouvez aussi lancer Claude Code
directement dans ce dépôt ou copier les dossiers à la main. Toutes les options sont décrites dans
[INSTALLATION.md](../INSTALLATION.md).

<!-- section: quick-start -->
## Démarrage rapide

Ouvrez Claude Code dans le dossier de votre projet et tapez :

```text
/pixel-art-game-studio Crée un jeu original et douillet en pixel art vu de dessus, avec un petit village, une forêt, trois personnages, des dialogues à embranchements, un cycle jour/nuit et la sauvegarde.
```

Le Director choisit des valeurs par défaut raisonnables, rédige une conception courte et construit
d'abord une petite version jouable. Pour appeler directement un spécialiste, mentionnez-le, par exemple
`@agent-qa-tester`.

<!-- section: examples -->
## Exemples de demandes

```text
/pixel-art-game-studio Ajoute une région de marais brumeux avec deux personnages et une quête à deux fins.
/pixel-art-game-studio Le village paraît vide. Ajoute des détails et de petites découvertes, mais garde les chemins dégagés.
/pixel-art-game-studio Examine ce jeu, lance tous les tests disponibles et corrige les bogues reproductibles.
```

Vous pouvez écrire vos demandes dans n'importe quelle langue. Un exemple complet se trouve dans
[examples](../../examples/example-game-idea.md).

<!-- section: workflows -->
## Méthodes de travail

- **Créer un jeu** : de l'idée à la livraison en 14 étapes, en commençant par une boucle jouable
  minimale.
- **Étendre un jeu** : examiner le projet existant, faire le plus petit changement cohérent, vérifier
  l'absence de régressions.
- **Tester et corriger** : lancer de vrais tests, signaler les défauts, corriger ceux qui sont
  confirmés avec un nombre limité de tentatives.
- **Générer des ressources** : d'abord la direction artistique, puis les spécifications, les fichiers
  PNG et les aperçus.
- **Vérification avant publication** : un verdict appuyé par des preuves : prêt, prêt avec problèmes
  connus ou pas prêt.

Vue d'ensemble : [WORKFLOWS.md](../WORKFLOWS.md).

<!-- section: testing -->
## Tests et correction des bogues

Le testeur QA découvre quels outils le jeu possède réellement, transforme les critères d'acceptation en
tests, les exécute et rédige des rapports de défauts avec gravité, étapes et preuves. Le correcteur de
bogues reproduit chaque défaut, corrige la cause profonde, ajoute un test de régression et relance les
vérifications. Il est toujours interdit d'affaiblir ou de supprimer des tests. Pour tester ce dépôt :

```bash
python -m unittest discover -s tests -v
python scripts/validate_repository.py
```

Détails : [TESTING.md](../TESTING.md).

<!-- section: limitations -->
## Limites

- L'outil ne crée pas à lui seul des jeux commerciaux finis ; attendez-vous à une base fonctionnelle
  qui grandit avec vos retours.
- Sans moteur installé, seules les données, les ressources et la logique indépendante du moteur
  peuvent être vérifiées.
- Les contrôles structurels ne peuvent pas dire si les graphismes sont beaux ou si un jeu est amusant ;
  il faut pour cela un regard humain.
- Les traductions sont assistées par machine et attendent une relecture par des locuteurs natifs.

<!-- section: troubleshooting -->
## Dépannage

Si la skill n'apparaît pas, vérifiez que `SKILL.md` se trouve dans `.claude/skills/pixel-art-game-studio/`.
Si les agents sont introuvables, redémarrez Claude Code après avoir créé `.claude/agents/`. Si
l'installateur se termine avec le code 2, il a trouvé un fichier qu'il n'a pas créé ; lisez le plan
qu'il a affiché. D'autres réponses figurent dans [TROUBLESHOOTING.md](../TROUBLESHOOTING.md).

<!-- section: contributing -->
## Contribuer

Les contributions sont les bienvenues, en particulier les relectures de ces traductions par des
locuteurs natifs. Lisez [CONTRIBUTING.md](../CONTRIBUTING.md) et le [code de conduite](../CODE_OF_CONDUCT.md)
avant d'ouvrir une pull request.

<!-- section: license -->
## Licence

Pixel Art Game Studio est publié sous une [licence d'utilisation seule](../../LICENSE) : vous pouvez l'utiliser
gratuitement, mais pas le vendre, le modifier ni le redistribuer. Les jeux que vous créez avec lui vous
appartiennent.
