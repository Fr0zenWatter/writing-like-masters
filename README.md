<p align="center">
  <strong>简体中文</strong> · <a href="./README_EN.md">English</a>
</p>

# Writing Like Masters

从一位学者的公开研究论文中提炼学术写作风格，生成一份可以直接交给 AI agent 使用的实用写作指南。

你只需要告诉 agent 作者是谁。它会先确认找对了人，再收集公开的论文源文件，观察作者怎样组织文字、公式和论证，最后把结果保存成一个简单的 TXT 文件。

## 最简单的用法

在这个文件夹里对 agent 说：

```text
请为 <作者名> 整理一份写作风格。先确认作者身份，然后按照 AGENTS.md 完成整个流程。
```

如果论文已经下载过，可以说：

```text
请直接使用 corpora/<作者代号>/，不要重新下载，生成最终 style。
```

agent 会按顺序做四件事：

1. 确认作者，并寻找公开论文源文件。
2. 论文准备好后，让你选择“简洁版”或“标准版”风格提炼。
3. 按所选版本总结作者的写作选择；简洁版不分析时间演化。
4. 把最终结果保存到 `styles/<作者代号>.txt`。

如果公开源文件太少，agent 会先问你是否允许使用 PDF，不会自行决定。

## 文件放在哪里

- `styles/`：最终成果，可以上传 Git。
- `corpora/`：下载的论文，只留在本机，不上传 Git。
- `scripts/`：帮 agent 下载、检查和整理材料的小工具。
- `SCHOLAR_TEX_ACQUISITION_SKILL.md`：如何找到并整理论文。
- `SCHOLAR_STYLE_DISTILLATION_LITE_SKILL.md`：简洁、非时间维度的风格整理流程。
- `SCHOLAR_STYLE_DISTILLATION_SKILL.md`：包含完整证据和时间维度的标准流程。
- `AGENTS.md`：告诉 agent 先做什么、后做什么。

下载记录、临时文件和中间分析也只留在本机，已经由 `.gitignore` 排除。

## 已有风格

这些风格都以数学正确性为先，主要区别在于如何组织问题、解释概念和推进论证：

- [Grigori Perelman](styles/grigori-perelman.txt)：研究几何分析、微分几何与拓扑，尤其 Ricci flow；整体是**冷峻极简**的文风，少铺垫、直入证明，按逻辑依赖推进，对假设、缺口和未完成之处表述得很克制。
- [Noga Alon](styles/noga-alon.txt)：研究组合数学、图论、概率方法与理论计算机科学；整体是**精确经济**的文风，问题先行，迅速进入定理与证明，篇幅紧凑，几乎没有多余铺陈。
- [Peter Scholze](styles/peter-scholze.txt)：研究算术几何、代数几何、p-进几何、上同调与 Langlands；整体是**概念架构型**文风，先识别核心障碍，再引入恰好解决障碍的新对象，在形式陈述与概念直觉之间切换。
- [Saharon Shelah](styles/saharon-shelah.txt)：研究数理逻辑、模型论与集合论；整体是**高密度构造型**文风，编号、记号和依赖关系极强，常把长证明拆成一系列可定位的局部任务与技术障碍。
- [Sourav Chatterjee](styles/sourav-chatterjee.txt)：研究概率论、统计、数学物理与分析；整体是**直觉解释型**文风，强调机制和动机，常从具体问题或简单模型切入，再逐步抽象，并解释每一步为什么需要。
- [Terence Tao](styles/terence-tao.txt)：研究调和分析、偏微分方程、组合数学、数论等多个领域；整体是**教学式导航**文风，层次清晰，不断交替严格陈述与直观解释，把复杂证明组织成一连串有明确动机的 reduction。

## 同一原稿的风格示例

下面两份文稿使用同一份数学原稿生成，分别展示 Peter Scholze 和 Terence Tao 风格下的组织方式。

### Peter Scholze

<p align="center">
  <img src="assets/readme/peter-scholze-blueprint-example.png" alt="Peter Scholze 风格的单页数学文稿" width="760">
</p>

### Terence Tao

<p align="center">
  <img src="assets/readme/terence-tao-blueprint-example.png" alt="Terence Tao 风格的无 section 单页数学文稿" width="760">
</p>

## 准备环境

需要 Python 3.10 或更新版本。安装依赖：

```powershell
python -m pip install -r requirements.txt
```

通常只处理论文源文件即可。只有在不得不读取 PDF 时，才可能需要额外的 PDF 文字识别工具。

## 使用提醒

- 只使用公开来源，并先确认作者身份。
- 最终 TXT 是写作参考，不是数学正确性的保证。
- 本项目是独立整理，与风格所涉及的学者本人无隶属、合作或背书关系。
- 不要上传下载的论文、网页缓存或中间文件。
- 发布前检查最终 TXT，避免保留大段原文、私人信息或第三方模板内容。

## 许可证

本仓库中的代码、工作流说明和风格文件采用 [MIT License](LICENSE) 发布。下载的论文、语料库、网页缓存及其他第三方材料不属于本仓库，也不在此许可证的授权范围内。

想了解规则，可以阅读[论文收集说明](SCHOLAR_TEX_ACQUISITION_SKILL.md)、[简洁版风格整理说明](SCHOLAR_STYLE_DISTILLATION_LITE_SKILL.md)和[标准版风格整理说明](SCHOLAR_STYLE_DISTILLATION_SKILL.md)。
