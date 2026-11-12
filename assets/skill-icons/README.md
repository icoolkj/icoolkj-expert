# Skill 小头标图标库

按项目统一的蓝色渐变图形规范独立绘制的 Skill 图标库。当前正式核心范围为 S01–S10；S11、S12 为备用图标，不代表已发布的核心 Skill。
不做位图抠图：SVG 是源文件，PNG 由 SVG 渲染导出，任意尺寸都不会糊。

## 文件说明

| 文件 | 说明 |
|---|---|
| `svg/Sxx-*.svg` | 12 枚矢量源文件（S01–S10 正式核心，S11–S12 备用；64×64 viewBox） |
| `Sxx-*.png` | 由 SVG 渲染的 256×256 透明 PNG |
| `contact-sheet.png` | 12 宫格总览图（含 2 枚备用图标） |
| `gallery.html` | 展示页：内联 SVG，双击即可查看全套图标及深色底效果 |
| `build_icons.py` | 生成脚本：改 SVG 内容后重跑，SVG / PNG / 总览 / 展示页 / 技能目录会一起刷新 |
| `source-poster.jpg` | 历史参考海报；仅作内部历史设计参考，来源证据待补齐，默认不进入商业交付包 |

S01–S10 的图标各复制了一份到对应技能目录，命名为 `skills/<技能名>/icon.svg` 与 `icon.png`，
与专家包 `avatars/` 目录的用法保持一致（只放文件，不改 `SKILL.md` frontmatter）。

## 编号对照

| 编号 | 名称 | 图标 | 对应技能目录 |
|---|---|---|---|
| S01 | 项目规划 | 剪贴板 + 对勾 | `original-ip-project-planning` |
| S02 | 世界观构建 | 地球经纬 | `story-worldbuilding` |
| S03 | 小说创作 | 羽毛笔 | `ai-novel-writing-studio` |
| S04 | 章节续写 | 文档 + 循环箭头 | `novel-continuity-and-continuation` |
| S05 | 小说→短剧 | 播放按钮 | `ai-short-drama-adaptation-studio` |
| S06 | 短剧剧本 | 场记板 | `short-drama-script-standardization` |
| S07 | 分镜脚本 | 分镜格 + 画面 | `cinematic-storyboard-design` |
| S08 | 视效素材 | 叠放图片 | `ai-character-environment-asset-design` |
| S09 | 逻辑审核 | 盾牌对勾 | `story-logic-and-continuity-review` |
| S10 | IP运营 | 上升柱状 + 箭头 | `ip-commercial-operations-planning` |
| S11 | 数据分析 | 报表 + 放大镜 | 暂无，仅存图标库 |
| S12 | 内容策划 | 灯泡（唯一暖色） | 暂无，仅存图标库 |

> S11 数据分析、S12 内容策划目前项目里没有对应技能，图标先留在库中备用。
> 后续新增时，在脚本 `ICONS` 里补上目录名重跑即可自动分发。

## 图形规范

- 画布 64×64，主渐变 `#57A0FF → #2D6BEF → #123FCF`，描边 `#0E3BB8`，内部细节纯白
- 线宽 2.6，端点圆角；图标主体控制在 8–56 的安全区内
- S12 备用灯泡使用金黄色 `#FFDC5C → #F59E0B`，不属于 S01–S10 正式核心图标体系

## 复现

```bash
python assets/skill-icons/build_icons.py
```

需要 Pillow + 本机 Chrome（用于无头渲染 SVG → 透明 PNG）。
改设计只需编辑脚本 `ICONS` 里的 SVG 片段，重跑会重建 SVG、PNG、总览图与 10 个技能目录的图标。
