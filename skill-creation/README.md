# Skill 创作与使用

本目录保存 Shelah Compact 的中英文技能源文件，用于维护、复制和安装。两版都包含“广义等价概念合并”和“数学记号、公式优先”的最新规则，仅在用户显式调用时启用。

## 目录

```text
skill-creation/
├── README.md
├── shelah-compact/
│   ├── SKILL.md
│   └── agents/openai.yaml
└── shelah-compact-en/
    ├── SKILL.md
    └── agents/openai.yaml
```

| 版本 | 规则文件 | 调用名 |
| --- | --- | --- |
| 中文 | [SKILL.md](shelah-compact/SKILL.md) | `$shelah-compact` |
| 英文 | [SKILL.md](shelah-compact-en/SKILL.md) | `$shelah-compact-en` |

`SKILL.md` 保存名称、适用范围和写作规则；`agents/openai.yaml` 保存界面名称与调用策略。每个技能文件夹可独立安装，无需加载原始 style 或下载论文。

## 创作过程

1. **选取基础。** 阅读已有的 [Saharon Shelah style](../styles/saharon-shelah.txt)，保留数学密度、稳定记号和明确依赖。这次工作直接改编已有指南，未重新采集论文或提炼学者风格。
2. **压缩重复讲解。** 生成 [中文精简 TXT](../styles/saharon-shelah-compact.txt)：共同概念定义一次，通式写一次，特例只交代参数、条件或替换项；共同预算、流程和指标集中说明。
3. **加入广义等价。** 将不同术语、记号、参数化或实现中的同一核心机制合并讲解，只补对应关系与实质差异。严格等价、单向蕴含、近似和类比仍须区分。
4. **封装为技能。** 把完整规则放进 `SKILL.md`，添加 YAML 元数据、显式调用范围和 `agents/openai.yaml`；不增加运行脚本或外部依赖。
5. **制作英文版。** 翻译规则及调用范围，使用独立名称 `shelah-compact-en`，并保留 [英文精简 TXT](../styles/saharon-shelah-compact-en.txt)。英文版指规则语言，回答语言仍由用户请求决定。
6. **补充表达优先级。** 在两版开头加入“优先使用数学记号和公式，除非文字表达更简洁”，同时保留正确性与可读性要求。
7. **校验并安装。** 使用 `skill-creator` 的 `quick_validate.py` 检查技能格式，单独解析调用策略，确认 `allow_implicit_invocation` 为布尔值 `false`；安装后核对文件哈希。本目录由已安装的最新版本复制而来。

## 如何封装同类技能

先写清可独立执行的规则，再创建与技能同名的文件夹。`SKILL.md` 的开头使用 YAML 元数据，例如：

```yaml
---
name: "shelah-compact"
description: "仅在用户显式调用 $shelah-compact 时使用：精简解释与改写，合并广义等价概念，变体只写差异。"
---
```

随后写入正文，说明本次调用的作用范围。仅显式调用的技能还须在 `agents/openai.yaml` 中设置：

```yaml
policy:
  allow_implicit_invocation: false
```

该设置关闭基于任务内容的自动选择；正文中的范围约束要求后续未调用的请求不自动沿用。技能名称、文件夹名称和调用名应一致。校验工具依赖 Python 与 PyYAML，技能使用本身不依赖它们。

## 安装与发现

本次已将两个技能安装到当前电脑的个人目录：

```text
C:\Users\Administrator\.codex\skills\shelah-compact\
C:\Users\Administrator\.codex\skills\shelah-compact-en\
```

在其他环境安装时，将所需的完整技能文件夹复制到该环境支持的技能目录。官方文档列出的个人目录为 `~/.agents/skills/`，项目目录为 `.agents/skills/`。必须保留 `agents/openai.yaml`，才能保留显式调用策略。

`skill-creation/` 用于存放源码；仅把文件放在这里不会自动注册技能。避免将同名技能同时安装到多个发现目录。Codex 通常会自动发现变更；若调用列表未更新，重启 Codex。

## 使用方法

在需要应用规则的请求中，输入 `$` 并选择对应技能，或显式写出调用名。

中文示例：

```text
$shelah-compact 请解释下面这段内容：
……
```

英文示例：

```text
$shelah-compact-en Explain the following passage:
…
```

调用只作用于当前请求及完成它所需的步骤。后续请求需要使用这套规则时，再次调用。需要详细推导或指定输出语言时，在同一请求中说明。

## 后续维护

先修改本目录中的技能源文件，再同步对应语言版本、`styles/` 中的精简 TXT 和个人安装副本；这些文件不会自动同步。保留名称和显式调用设置，更新后重新校验格式与策略。

完整规范与技能发现规则见 [OpenAI 官方技能文档](https://learn.chatgpt.com/docs/build-skills)。
