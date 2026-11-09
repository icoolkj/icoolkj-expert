# 灵启·小说主笔（Lingqi Fiction Head Writer）

灵启逸梦原创小说创作体系的核心专家——职业小说主笔，负责把故事创意转化为有吸引力、有情感、有逻辑、有阅读价值的原创小说作品。

## 类型

Agent 型（单个 AI 专家）

## 功能

- **小说创意与选题分析**：题材定位、卖点提炼、目标读者判断、改进建议
- **小说大纲设计**：核心概念、主线支线、核心矛盾、转折、高潮结局、伏笔及回收计划
- **章节规划与创作**：每章目标、事件、冲突、情绪、结尾钩子与下章衔接
- **小说正文写作**：叙事、人物、场景、对话四大核心写作能力
- **商业网文节奏设计**：开篇吸引力、悬念、爽点、反转、章节钩子、阶段性高潮
- **人物塑造与情感表达**：目标、动机、性格、内在矛盾与成长弧线
- **长篇连续性管理**：维护人物状态、世界观规则、事件顺序与伏笔档案
- **小说修改与文学润色**：语言、叙事、对话、节奏、逻辑优化，尊重原始文风

交付物：小说项目策划案、整体大纲、分卷章节大纲、小说正文、剧情连续性档案、修改与审校报告。

## 工作方式

按八层创作方法推进：题材定位 → 大纲设计 → 章节规划 → 正文创作 → 连续性管理 → 修改润色；长篇项目持续维护人物状态、世界观规则与伏笔档案，修改时尊重作者原始文风。

## 使用示例

- 开始小说创作：这是我的故事创意（或素材/原稿），请先帮我定位题材并设计大纲，然后开始创作。
- 按已确认的大纲写第一章（或继续下一章），输出完整正文，不要只给摘要。
- 润色并修改这一章：保持我的原始文风，修正逻辑和节奏问题，并给出修改报告。

## 头像

官方头像：`avatars/03_灵启_小说主笔.png`（512×512 PNG）。
`.codebuddy-plugin/plugin.json` 的 `avatar` 字段指向该文件——更换头像时须同步更新字段，
再重跑 `python scripts/build_expert_readmes.py` 与 `python assets/expert-avatars/build_gallery.py`
同步本 README 与头像展示页。

自定义头像要求：
- 格式：PNG（推荐）或 JPG
- 尺寸：512×512 px
- 大小：单张不超过 500KB
- 文件名沿用 `<编号>_灵启_<角色名>.png`，保持 01–08 编号与专家一一对应

## 安装

将整个专家包目录放到本机专家市场目录下：

```
C:\Users\Administrator\.workbuddy\plugins\marketplaces\my-experts\plugins\lingqi-novel-writer\
```

目录内应包含 `.codebuddy-plugin/plugin.json`、`agents/`、`avatars/` 和本 README。
如需在市场清单中登记，在 `my-experts/.codebuddy-plugin/marketplace.json` 的 `plugins` 数组补一条
`name` / `source` / `description` / `version`。完成后重启 WorkBuddy 让客户端重新扫描插件
（头像与配置有缓存，不重启可能看不到更新）。

## 打包分享

在 `experts/` 目录下执行：

```bash
zip -r lingqi-novel-writer.zip lingqi-novel-writer/
```
