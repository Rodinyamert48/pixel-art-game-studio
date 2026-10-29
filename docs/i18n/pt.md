# Pixel Art Game Studio

[← README principal](../../README.md) · Português (Brasil) · Tradução assistida por máquina, aguardando revisão de falantes nativos.

<!-- section: overview -->
## Visão geral

Pixel Art Game Studio é uma skill do Claude Code com uma equipe de oito subagentes especializados para
criar jogos 2D originais em pixel art. Você descreve o jogo que imagina, o que não gosta no resultado
atual e o que quer mudar em seguida. O Claude planeja o trabalho, escreve o código, gera os gráficos,
executa os testes, corrige os bugs que consegue reproduzir e relata apenas o que realmente verificou.

Ele foi pensado para aventuras narrativas aconchegantes, simuladores de vida e de fazenda, RPGs com
muito diálogo, jogos de exploração com visão de cima e jogos de quebra-cabeça, mas também funciona para
outras ideias 2D originais. Quatro partes ficam separadas: a **skill** (instruções), os **agentes**
(especialistas), os **scripts** (ferramentas determinísticas) e **o seu jogo** (um diretório de projeto
próprio).

<!-- section: features -->
## Recursos

- Um fluxo de Game Director que transforma uma ideia solta em um design curto e em um ciclo jogável
  mínimo.
- Oito especialistas com responsabilidades claras, listas de ferramentas limitadas e relatórios
  estruturados.
- Pixel art procedural: especificações em JSON viram folhas de sprites PNG reais, metadados e
  pré-visualizações. A mesma especificação sempre gera os mesmos bytes.
- Um contrato de dados para mapas, decoração, diálogos, missões, itens e traduções, com um validador
  que encontra saídas inalcançáveis, ramos de diálogo impossíveis e chaves de texto ausentes.
- Controle de qualidade com níveis de gravidade, relatórios de defeitos reproduzíveis e correções
  verificadas com testes de regressão.
- Um instalador seguro com simulação, detecção de conflitos, cópias de segurança e uma desinstalação
  cuidadosa.

<!-- section: agents -->
## A equipe de agentes

São nove papéis. O **Game Director** é a própria skill e roda na sua sessão principal do Claude Code:
ele mantém o design, escreve as tarefas, confere cada resultado e decide quando algo está pronto. Os
oito subagentes são:

| Agente | Responsabilidade |
| --- | --- |
| `pixel-artist` | direção de arte, especificações de assets, sprites e tiles gerados |
| `npc-story-engineer` | personagens, diálogos ramificados, flags, missões |
| `world-builder-level-design` | estrutura dos mapas, colisão, pontos de surgimento, saídas |
| `world-builder-environmental-content` | decoração, pontos de interesse, atmosfera de cada região |
| `ui-engineer` | menus, HUD, caixa de diálogo, telas de inventário e de salvamento |
| `gameplay-engineer` | movimento, estado do jogo, inventário, missões, salvamento |
| `qa-tester` | testes, execuções de testes, relatórios de defeitos |
| `bug-fixer` | correções na causa raiz com testes de regressão |

Mais detalhes: [AGENTS.md](../AGENTS.md).

<!-- section: architecture -->
## Arquitetura

O Director é a skill e não um subagente, porque precisa ver os seus pedidos e manter uma única fonte de
verdade (`design/GAME_DESIGN.md`, `ART_DIRECTION.md` e mais cinco documentos curtos). Os especialistas
recebem tarefas bem definidas, trabalham nos arquivos pelos quais são responsáveis e devolvem um
relatório; eles não podem iniciar outros agentes. O conteúdo do jogo fica em uma pasta `data/`
independente do motor, então história, fases e ambientação podem avançar em paralelo e ser verificadas
sem abrir o motor. Se os subagentes não estiverem disponíveis, o Director executa os mesmos passos
sozinho, um após o outro. Veja [ARCHITECTURE.md](../ARCHITECTURE.md).

<!-- section: prerequisites -->
## Pré-requisitos

- Claude Code (verificado com a versão 2.1.312).
- Python 3.9 ou mais recente; nenhum pacote extra é necessário.
- Para jogos de verdade, o motor que você escolher, como Godot 4 ou o .NET SDK para MonoGame. A skill
  verifica o que está instalado e pergunta antes de instalar qualquer coisa.

<!-- section: installation -->
## Instalação

O jeito mais fácil é instalar como plugin de dentro do Claude Code. A skill passa a se chamar `/pixel-art-game-studio:pixel-art-game-studio` e os agentes ganham o prefixo `pixel-art-game-studio:`:

```text
/plugin marketplace add Rodinyamert48/pixel-art-game-studio
/plugin install pixel-art-game-studio@pixel-art-game-studio
```

Ou, sem o sistema de plugins: Clone o repositório e escolha como instalar. Confira cada mudança antes com `--dry-run`:

```bash
python scripts/install.py --scope project --project-dir ../my-game --dry-run
python scripts/install.py --scope project --project-dir ../my-game
python scripts/install.py --scope user
```

O escopo de projeto grava em `<project>/.claude/` e o escopo de usuário em `~/.claude/`. Arquivos
existentes que não foram criados pelo instalador nunca são substituídos. Use `--update` para atualizar
uma instalação (os arquivos antigos ganham cópia de segurança) e `--uninstall` para remover apenas os
arquivos não modificados que ele instalou. Você também pode rodar o Claude Code direto neste
repositório ou copiar as pastas manualmente. Todas as opções estão em [INSTALLATION.md](../INSTALLATION.md).

<!-- section: quick-start -->
## Início rápido

Abra o Claude Code na pasta do seu projeto e digite:

```text
/pixel-art-game-studio Crie um jogo original e aconchegante em pixel art com visão de cima, com uma pequena cidade, uma floresta, três personagens, diálogos ramificados, ciclo de dia e noite e sistema de salvamento.
```

O Director escolhe padrões sensatos, escreve um design curto e constrói primeiro uma pequena versão
jogável. Para chamar um especialista diretamente, mencione o nome dele, por exemplo `@agent-qa-tester`.

<!-- section: examples -->
## Exemplos de pedidos

```text
/pixel-art-game-studio Adicione uma região de pântano com neblina, dois personagens e uma missão com dois finais.
/pixel-art-game-studio A cidade parece vazia. Adicione detalhes e pequenas descobertas, mas mantenha os caminhos livres.
/pixel-art-game-studio Analise este jogo, rode todos os testes disponíveis e corrija os bugs reproduzíveis.
```

Você pode escrever seus pedidos em qualquer idioma. Há um exemplo completo em
[examples](../../examples/example-game-idea.md).

<!-- section: workflows -->
## Fluxos de trabalho

- **Criar um jogo**: da ideia à entrega em 14 etapas, começando por um ciclo jogável mínimo.
- **Expandir um jogo**: examinar o projeto existente, fazer a menor mudança coerente e verificar se não
  houve regressões.
- **Testar e corrigir**: executar testes reais, relatar defeitos e corrigir os confirmados com um
  número limitado de tentativas.
- **Gerar assets**: primeiro a direção de arte, depois as especificações, os arquivos PNG e as
  pré-visualizações.
- **Verificação de lançamento**: um veredito baseado em evidências: pronto, pronto com problemas
  conhecidos ou não pronto.

Visão geral: [WORKFLOWS.md](../WORKFLOWS.md).

<!-- section: testing -->
## Testes e correção de bugs

O testador de QA descobre quais ferramentas o jogo realmente tem, transforma os critérios de aceitação
em testes, executa esses testes e escreve relatórios de defeitos com gravidade, passos e evidências. O
corretor de bugs reproduz cada defeito, corrige a causa raiz, adiciona um teste de regressão e roda as
verificações de novo. Enfraquecer ou apagar testes nunca é permitido. Para testar este repositório:

```bash
python -m unittest discover -s tests -v
python scripts/validate_repository.py
```

Detalhes: [TESTING.md](../TESTING.md).

<!-- section: limitations -->
## Limitações

- Ele não cria sozinho jogos comerciais prontos; espere uma base funcional que cresce com o seu
  feedback.
- Sem um motor instalado, só é possível verificar dados, assets e lógica que não depende do motor.
- Verificações estruturais não conseguem dizer se a arte está bonita ou se o jogo é divertido; isso
  exige uma pessoa.
- As traduções são assistidas por máquina e aguardam revisão de falantes nativos.

<!-- section: troubleshooting -->
## Solução de problemas

Se a skill não aparecer, confira se o `SKILL.md` está em `.claude/skills/pixel-art-game-studio/`. Se os
agentes não forem encontrados, reinicie o Claude Code depois de criar `.claude/agents/`. Se o instalador
terminar com o código 2, ele encontrou um arquivo que não criou; leia o plano que ele exibiu. Mais
respostas em [TROUBLESHOOTING.md](../TROUBLESHOOTING.md).

<!-- section: contributing -->
## Como contribuir

Contribuições são bem-vindas, principalmente revisões destas traduções por falantes nativos. Leia o
[CONTRIBUTING.md](../CONTRIBUTING.md) e o [Código de Conduta](../CODE_OF_CONDUCT.md) antes de abrir um
pull request.

<!-- section: license -->
## Licença

Pixel Art Game Studio é distribuído sob uma [licença somente de uso](../../LICENSE): você pode usá-lo de graça,
mas não pode vendê-lo, modificá-lo nem redistribuí-lo. Os jogos que você cria com ele são seus.
