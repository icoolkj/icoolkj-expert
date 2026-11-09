# 灵启·世界观架构师（Lingqi Worldbuilding Architect）

灵启逸梦原创故事创作体系的世界观架构师：为原创小说与影视 IP 搭建世界底层逻辑——世界背景、运行规则、力量体系、人物体系、势力组织、时间线与关系图谱，保证设定自洽、可验证、可延展。

## 类型

Agent 型（单个 AI 专家）

## 功能

- **世界观总体架构**：世界背景、地理空间、文明历史、社会制度、世界独特性
- **世界运行规则设计**：修炼/异能/魔法/科技体系、境界划分、代价与限制
- **人物体系架构**：人物档案、动机与秘密、成长弧线、人物关系
- **势力与组织架构**：国家、宗门、家族、商业与秘密组织、阵营利益关系
- **故事结构与时间线**：世界历史、主线时间线、伏笔与回收节点
- **故事关系图谱**：Mermaid 图表 / 关系表格 / 结构化数据
- **设定一致性检查**：设定冲突、逻辑漏洞、时间线问题的检测与修补方案
- **跨媒介改编支持**：小说、短剧、动态漫、动画、AI 影视、游戏的扩展性设计
- **分层架构方法**：六层分层架构：核心层 → 基础层 → 规则层 → 人物势力层 → 事件层 → 扩展应用层

交付物：世界观设定集、世界规则与力量体系文档、人物与势力档案、时间线、关系图谱、设定一致性检查报告。

## 工作方式

按六层分层架构推进七阶段标准流程，设定分层归档并做版本管理；输出六类标准交付物，交付前执行设定冲突、逻辑漏洞与时间线自检。

## 使用示例

- 我有一个故事想法（或一份原稿/设定资料），帮我搭建一套完整自洽的世界观：世界背景、运行规则、核心人物与势力组织。
- 帮这个世界设计力量体系：境界划分、能力上限、使用代价与限制规则，并说明如何约束剧情。
- 对我小说的现有设定、人物和时间线做一次一致性检查，列出设定冲突、逻辑漏洞与修补方案。

## 头像

官方头像：`avatars/02_灵启_世界观架构师.png`（512×512 PNG）。
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
C:\Users\Administrator\.workbuddy\plugins\marketplaces\my-experts\plugins\lingqi-worldbuilding-architect\
```

目录内应包含 `.codebuddy-plugin/plugin.json`、`agents/`、`avatars/` 和本 README。
如需在市场清单中登记，在 `my-experts/.codebuddy-plugin/marketplace.json` 的 `plugins` 数组补一条
`name` / `source` / `description` / `version`。完成后重启 WorkBuddy 让客户端重新扫描插件
（头像与配置有缓存，不重启可能看不到更新）。

## 打包分享

在 `experts/` 目录下执行：

```bash
zip -r lingqi-worldbuilding-architect.zip lingqi-worldbuilding-architect/
```
