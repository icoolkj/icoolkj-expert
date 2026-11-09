# 灵启·故事审校官（Lingqi Story Review Officer）

「AI创艺坊」创作体系下的独立质量控制专家：以独立第三方视角对小说、短剧、动态漫和 AI 影视项目进行专业审校。

## 类型

Agent 型（单个 AI 专家）

## 功能

- **故事整体结构审校**：主线完整性、冲突升级、转折合理性、铺垫与回收、中段动力与结尾收束
- **世界观与设定一致性审校**：核对世界规则、能力体系、组织势力与已确认设定，识别设定矛盾与规则临时变动
- **人物塑造审校**：行为动机、性格连续性、人物弧线、信息知晓边界与配角逻辑
- **剧情逻辑与因果审校**：为重要事件建立因果链，指出缺失的原因或过程
- **时间线与连续性管理**：时间线、地点、伤势、道具持有、信息公开与隐藏的前后核对
- **小说/短剧/分镜专业审校**：开篇吸引力、章节节奏、钩子设计、反转铺垫、镜头可执行性与视觉资产一致性
- **问题分级与修正方案**：S/A/B/C 四级问题清单，每个问题附位置、类型、原因、影响与可执行修改建议
- **标准审校报告与百分制评分**：按标准模板输出《故事审校报告》，评分有据可依，材料不足时标注「暂定评分」

交付物：故事审校报告、S/A/B/C 分级问题清单、修改建议、bug 修复方案、百分制评分。

## 工作方式

材料接收 → 结构审校 → 世界观与设定核对 → 人物动机与因果链诊断 → 时间线连续性核对 → S/A/B/C 分级 → 标准审校报告与百分制评分；材料不足时标注「暂定评分」。

## 使用示例

- 我有一份小说或剧本，帮我做一次完整审校，指出结构、剧情逻辑、人物塑造和设定一致性问题，并按严重程度分级。
- 这段剧情我觉得不太对劲，但说不上问题在哪，帮我做一次因果链和动机诊断。
- 帮我检查这个人物的行为动机和人物弧线是否成立，以及和前文设定有没有冲突。

## 头像

官方头像：`avatars/07_灵启_故事审校官.png`（512×512 PNG）。
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
C:\Users\Administrator\.workbuddy\plugins\marketplaces\my-experts\plugins\lingqi-story-reviewer\
```

目录内应包含 `.codebuddy-plugin/plugin.json`、`agents/`、`avatars/` 和本 README。
如需在市场清单中登记，在 `my-experts/.codebuddy-plugin/marketplace.json` 的 `plugins` 数组补一条
`name` / `source` / `description` / `version`。完成后重启 WorkBuddy 让客户端重新扫描插件
（头像与配置有缓存，不重启可能看不到更新）。

## 打包分享

在 `experts/` 目录下执行：

```bash
zip -r lingqi-story-reviewer.zip lingqi-story-reviewer/
```
