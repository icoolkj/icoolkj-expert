# 灵启·短剧编剧（Lingqi Short Drama Screenwriter）

灵启逸梦（LING QI YI MENG）创作体系的商业短剧职业编剧专家：把故事转化为具有商业传播潜力、戏剧张力和影视可执行性的短剧剧本。

## 类型

Agent 型（单个 AI 专家）

## 功能

- **短剧选题与项目开发**：从创意、小说、梗概、真实事件或已有 IP 中判断短剧开发价值：题材定位、核心卖点、核心矛盾、情绪价值、商业潜力、制作可行性
- **商业短剧结构设计**：整体故事结构、分幕分集设计、人物成长弧线、情绪曲线、悬念反转、开场抓人、持续追看动力与分集结尾钩子
- **人物与关系设计**：完整人物小传体系（欲望、目标、恐惧、秘密、弱点、动机与成长），重点设计利益、情感、认知与身份四类冲突
- **分集大纲创作**：按短剧节奏拆分集数，每集含核心事件、冲突、情绪变化、高潮与结尾钩子
- **标准短剧剧本创作**：输出含场次、时间、地点、人物、场景描述、动作与对白的专业剧本，标注 OS/VO/景别/音效/转场
- **小说与 IP 短剧改编**：原作分析、改编方案、可压缩支线与可合并人物处理、重要改编说明
- **剧本诊断与连续性管理**：项目诊断报告、剧情优化方案、伏笔与时间线连续性记录

交付物：短剧成片剧本、项目诊断报告、整体大纲、分集大纲、改编方案、剧本连续性记录。

## 工作方式

项目诊断 → 商业结构设计 → 人物与关系 → 分集大纲 → 标准剧本 → 剧本诊断与连续性管理；每集必须落在核心事件、冲突升级、情绪变化与结尾钩子上。

## 使用示例

- 开始短剧开发：这是我的故事创意（或小说/梗概/已有剧本），请先帮我诊断项目并确定开发方案，再搭建整体大纲。
- 按已确认的整体大纲，创作第1集的标准短剧剧本（含场次、动作说明与人物对白）。
- 这是我的小说（或 IP 素材），请分析原作并输出短剧化改编方案与分集大纲。

## 头像

官方头像：`avatars/04_灵启_短剧编剧.png`（512×512 PNG）。
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
C:\Users\Administrator\.workbuddy\plugins\marketplaces\my-experts\plugins\lingqi-shortdrama-writer\
```

目录内应包含 `.codebuddy-plugin/plugin.json`、`agents/`、`avatars/` 和本 README。
如需在市场清单中登记，在 `my-experts/.codebuddy-plugin/marketplace.json` 的 `plugins` 数组补一条
`name` / `source` / `description` / `version`。完成后重启 WorkBuddy 让客户端重新扫描插件
（头像与配置有缓存，不重启可能看不到更新）。

## 打包分享

在 `experts/` 目录下执行：

```bash
zip -r lingqi-shortdrama-writer.zip lingqi-shortdrama-writer/
```
