# Pixel Art Game Studio

[← 返回主 README](../../README.md) · 简体中文 · 本译文由机器辅助生成，正在等待母语者审校。

<!-- section: overview -->
## 概述

Pixel Art Game Studio 是一个 Claude Code 技能（skill），并配有一支由八个专业子代理组成的团队，用于开发原创的 2D 像素风游戏。你只需描述心中想要的游戏、对当前结果不满意的地方，以及下一步想改什么。Claude 会规划工作、编写代码、生成图像、运行测试、修复能够复现的缺陷，并且只汇报真正验证过的内容。

它主要面向温馨的叙事冒险、生活与农场模拟、对话丰富的角色扮演游戏、俯视角探索游戏和解谜游戏，也适用于其他原创 2D 创意。四个部分彼此分开：**技能**（说明与流程）、**代理**（专家）、**脚本**（确定性工具）以及**你的游戏**（独立的项目目录）。

<!-- section: features -->
## 功能

- Game Director 工作流程：把模糊的想法整理成简短的设计和一个最小可玩循环。
- 八位专家，职责清晰，工具列表受限，并以统一的格式提交报告。
- 程序化像素美术：JSON 描述会生成真实的 PNG 精灵图、元数据和预览图。相同的描述总是生成相同的字节。
- 针对地图、装饰、对话、任务、物品和翻译的数据约定，以及一个校验器，可以发现无法到达的出口、不可能触发的对话分支和缺失的文本键。
- 质量保证：包含严重程度分级、可复现的缺陷报告，以及经过回归测试验证的修复。
- 安全的安装程序：支持预演、冲突检测、备份，并且卸载时非常谨慎。

<!-- section: agents -->
## 代理团队

一共有九个角色。**Game Director** 就是技能本身，运行在你的 Claude Code 主会话中：它维护设计文档、编写任务说明、检查每一个结果，并决定什么时候算完成。八个子代理如下：

| 代理 | 职责 |
| --- | --- |
| `pixel-artist` | 美术方向、素材描述、生成的精灵和图块 |
| `npc-story-engineer` | 角色、分支对话、剧情标记、任务 |
| `world-builder-level-design` | 地图布局、碰撞、出生点、出口 |
| `world-builder-environmental-content` | 装饰、兴趣点、各区域的氛围 |
| `ui-engineer` | 菜单、HUD、对话框、背包和存档界面 |
| `gameplay-engineer` | 移动、游戏状态、背包、任务、存档 |
| `qa-tester` | 编写测试、运行测试、缺陷报告 |
| `bug-fixer` | 从根本原因修复问题，并添加回归测试 |

详情请见 [AGENTS.md](../AGENTS.md)。

<!-- section: architecture -->
## 架构

Director 是技能而不是子代理，因为它需要看到你的请求，并维护唯一的事实来源（`design/GAME_DESIGN.md`、`ART_DIRECTION.md` 以及另外五份简短文档）。专家接收任务说明，只修改自己负责的文件，然后提交报告；它们不能再启动其他代理。游戏内容存放在与引擎无关的 `data/` 文件夹中，因此剧情、关卡和环境可以并行制作，并且无需启动引擎就能检查。如果子代理不可用，Director 会自己按顺序完成同样的步骤。参见 [ARCHITECTURE.md](../ARCHITECTURE.md)。

<!-- section: prerequisites -->
## 前提条件

- Claude Code（已在 2.1.312 版本上检查）。
- Python 3.9 或更高版本；不需要额外的软件包。
- 如果要制作真正的游戏，还需要你选择的引擎，例如 Godot 4 或用于 MonoGame 的 .NET SDK。技能会检查已经安装了什么，并且在安装任何东西之前先征求你的同意。

<!-- section: installation -->
## 安装

先克隆仓库，然后选择安装方式。每次改动前都可以用 `--dry-run` 预览：

```bash
python scripts/install.py --scope project --project-dir ../my-game --dry-run
python scripts/install.py --scope project --project-dir ../my-game
python scripts/install.py --scope user
```

项目范围会写入 `<project>/.claude/`，用户范围会写入 `~/.claude/`。不是由安装程序创建的已有文件永远不会被替换。使用 `--update` 更新安装（旧文件会先备份），使用 `--uninstall` 只删除由它安装且未被修改的文件。你也可以直接在本仓库中运行 Claude Code，或者手动复制文件夹。所有选项都在 [INSTALLATION.md](../INSTALLATION.md) 中。

<!-- section: quick-start -->
## 快速开始

在项目文件夹中打开 Claude Code，然后输入：

```text
/pixel-art-game-studio 创建一个原创、温馨的俯视角像素风游戏，包含一个小镇、一片森林、三个 NPC、分支对话、昼夜循环和存档功能。
```

Director 会选择合理的默认值，写出简短的设计，并先做出一个可以游玩的小版本。如果想直接调用某位专家，可以提到它的名字，例如 `@agent-qa-tester`。

<!-- section: examples -->
## 示例请求

```text
/pixel-art-game-studio 添加一个雾气弥漫的沼泽区域，里面有两个 NPC 和一个拥有两种结局的任务。
/pixel-art-game-studio 小镇看起来太空了。添加细节和一些小发现，但要保持道路通畅。
/pixel-art-game-studio 检查这个游戏，运行所有可用的测试，并修复可以复现的缺陷。
```

你可以用任何语言写请求。完整示例见 [examples](../../examples/example-game-idea.md)。

<!-- section: workflows -->
## 工作流程

- **创建游戏**：从想法到交付共 14 个阶段，先做出最小可玩循环。
- **扩展游戏**：先检查现有项目，做出最小且一致的改动，再检查是否出现回归。
- **测试与修复**：运行真实的测试，报告缺陷，在有限的尝试次数内修复已确认的问题。
- **生成素材**：先确定美术方向，再写描述、生成 PNG 文件和预览图。
- **发布检查**：给出有证据支持的结论：可以发布、带已知问题可以发布，或尚未准备好。

概览见 [WORKFLOWS.md](../WORKFLOWS.md)。

<!-- section: testing -->
## 测试与缺陷修复

QA 测试员会先弄清游戏实际拥有哪些工具，把验收标准转换成测试并运行，然后写出包含严重程度、复现步骤和证据的缺陷报告。缺陷修复员会先复现每个缺陷，修复根本原因，添加回归测试，再重新运行检查。任何时候都不允许削弱或删除测试。测试本仓库本身：

```bash
python -m unittest discover -s tests -v
python scripts/validate_repository.py
```

详情见 [TESTING.md](../TESTING.md)。

<!-- section: limitations -->
## 局限

- 它不能独自做出完整的商业游戏；你会得到一个能运行、并随着你的反馈不断成长的基础。
- 如果没有安装引擎，只能验证数据、素材和不依赖引擎的逻辑。
- 结构检查无法判断美术是否好看、游戏是否好玩；这需要人来判断。
- 各语言译文由机器辅助生成，仍在等待母语者审校。

<!-- section: troubleshooting -->
## 故障排除

如果技能没有出现，请确认 `SKILL.md` 位于 `.claude/skills/pixel-art-game-studio/`。如果找不到代理，请在创建 `.claude/agents/` 之后重启 Claude Code。如果安装程序以代码 2 退出，说明它发现了一个不是由它创建的文件；请阅读它输出的计划。更多答案见 [TROUBLESHOOTING.md](../TROUBLESHOOTING.md)。

<!-- section: contributing -->
## 参与贡献

欢迎任何贡献，尤其欢迎母语者审校这些译文。提交 pull request 之前，请阅读 [CONTRIBUTING.md](../CONTRIBUTING.md) 和[行为准则](../CODE_OF_CONDUCT.md)。

<!-- section: license -->
## 许可证

Pixel Art Game Studio 采用 [MIT 许可证](../../LICENSE) 发布。你用它制作的游戏归你所有。
