# Skill 小头标图标库

来源：`灵启逸梦 · AI创艺坊` 官方海报中「12 项核心 Skill」区域的 12 枚蓝色图标。
原始海报留存为 `source-poster.jpg`，图标经抠底、等比缩放后统一为 256×256 透明 PNG。

## 文件说明

| 文件 | 说明 |
|---|---|
| `Sxx-*.png` | 12 枚透明图标（按海报编号命名） |
| `contact-sheet.png` | 12 宫格总览图，便于快速核对 |
| `source-poster.jpg` | 海报原图（1254×1254），用于复现 |
| `extract_icons.py` | 提取脚本，海报改版后改坐标重跑即可 |

同时，S01–S10 的图标各复制了一份到对应技能目录下，命名为 `skills/<技能名>/icon.png`，
与专家包 `avatars/` 目录的用法保持一致（放文件，不改 SKILL.md frontmatter）。

## 编号对照

| 编号 | 名称 | 图标文件 | 对应技能目录 |
|---|---|---|---|
| S01 | 项目规划 | `S01-project-planning.png` | `original-ip-project-planning` |
| S02 | 世界观构建 | `S02-worldbuilding.png` | `story-worldbuilding` |
| S03 | 小说创作 | `S03-novel-writing.png` | `ai-novel-writing-studio` |
| S04 | 章节续写 | `S04-chapter-continuation.png` | `novel-continuity-and-continuation` |
| S05 | 小说→短剧 | `S05-novel-to-shortdrama.png` | `ai-short-drama-adaptation-studio` |
| S06 | 短剧剧本 | `S06-screenplay.png` | `short-drama-script-standardization` |
| S07 | 分镜脚本 | `S07-storyboard.png` | `cinematic-storyboard-design` |
| S08 | 视效素材 | `S08-visual-assets.png` | `ai-character-environment-asset-design` |
| S09 | 逻辑审核 | `S09-logic-review.png` | `story-logic-and-continuity-review` |
| S10 | IP运营 | `S10-ip-operations.png` | `ip-commercial-operations-planning` |
| S11 | 数据分析 | `S11-data-analysis.png` | 暂无，仅存图标库 |
| S12 | 内容策划 | `S12-content-strategy.png` | 暂无，仅存图标库 |

> S11 数据分析、S12 内容策划目前项目里没有对应技能，图标先留在库中备用。
> 后续若新增这两个技能，在脚本的 `SKILLS` 里补上目录名重跑，图标会自动分发过去。

## 复现

```bash
python assets/skill-icons/extract_icons.py
```

需要 Pillow。若海报尺寸或排版变化，更新脚本里的 `ICON_BOXES`（12 个图标包围盒坐标）即可。
