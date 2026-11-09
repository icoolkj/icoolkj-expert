# 灵启·AI视觉设计师（Lingqi AI Visual Designer）

灵启逸梦 LING QI YI MENG 原创故事工作室的 AI 视觉设计师专家：将文字设定、导演构想和剧本需求，转化为具有统一艺术风格、明确设计规范和可供 AI 影视生产使用的视觉资产。

## 类型

Agent 型（单个 AI 专家）

## 功能

- **项目视觉定位与艺术指导**：建立项目整体视觉风格、色彩体系、光影规则与统一规范，支持电影级写实 CG、3D/2D 动画、国风、赛博朋克、仙侠玄幻等风格
- **角色资产设计**：基础身份、外貌特征、服装造型、表情、动作与三视图等完整角色视觉资产，保证多镜头一致性
- **场景资产设计**：城市街道、室内空间、自然环境、科幻空间等各类场景的结构、色彩、光影与氛围设定
- **道具与特殊视觉元素设计**：武器、信物、机械装置、特殊生物等叙事道具的独立设定
- **AI 图像生成 Prompt 工程**：面向 Midjourney / Stable Diffusion / FLUX / DALL·E 等模型的提示词设计与适配
- **AI 视频视觉资产适配**：为 AI 视频制作提前设计可复用、可衔接的角色、场景与道具资产
- **视觉资产管理与版本控制**：CHAR/SCENE/PROP/CREATURE/FX/STYLE 资产编号体系、版本记录与一致性检查

交付物：角色立绘与三视图、场景素材、道具设定、AI 绘图 Prompt 库、视觉规范文档、资产一致性检查报告。

## 工作方式

视觉需求分析 → 项目视觉规范 → 角色/场景/道具资产设计 → AI 图像生成 Prompt → 多镜头一致性检查 → 资产编号与版本管理。

## 使用示例

- 这是我的项目资料（世界观/人物设定/剧本/导演阐述），请先做视觉需求分析并建立项目整体视觉规范。
- 请为我的主角设计角色视觉资产（三视图、表情、服装、动作），并输出可复用的AI图像生成Prompt。
- 请检查这些生成图片的视觉一致性（角色外貌、服装、场景结构、道具），并输出一致性检查报告。

## 头像

官方头像：`avatars/06_灵启_AI视觉设计师.png`（512×512 PNG）。
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
C:\Users\Administrator\.workbuddy\plugins\marketplaces\my-experts\plugins\lingqi-ai-visual-designer\
```

目录内应包含 `.codebuddy-plugin/plugin.json`、`agents/`、`avatars/` 和本 README。
如需在市场清单中登记，在 `my-experts/.codebuddy-plugin/marketplace.json` 的 `plugins` 数组补一条
`name` / `source` / `description` / `version`。完成后重启 WorkBuddy 让客户端重新扫描插件
（头像与配置有缓存，不重启可能看不到更新）。

## 打包分享

在 `experts/` 目录下执行：

```bash
zip -r lingqi-ai-visual-designer.zip lingqi-ai-visual-designer/
```
