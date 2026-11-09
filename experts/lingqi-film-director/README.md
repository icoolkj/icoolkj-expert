# 灵启·影视导演（Lingqi Film Director）

灵启·影视导演：把剧本转化为具有明确视觉风格、完整镜头逻辑、可执行拍摄方案和 AI 制作适配能力的影视作品方案。

## 类型

Agent 型（单个 AI 专家）

## 功能

- **导演视角的剧本分析**：识别主题、人物动机、戏剧冲突、关键剧情节点与视觉化重点
- **导演阐述与整体视觉定位**：创作理念、影像风格、摄影与画面设计、视听设计
- **场景拆解与场面调度**：空间布局、人物走位、轴线原则、镜头衔接
- **专业分镜设计**：景别、机位、运镜、构图、光影、音效与转场的完整镜头表
- **镜头语言与情绪表达**：用视听语言表现人物心理与故事氛围
- **AI 影视制作适配**：角色/场景一致性、镜头可生成性、镜头衔接、生成成本控制
- **AI 视频 Prompt 设计**：适配 Seedance / Sora / Kling / Veo 等工具的中英文提示词
- **剪辑与后期指导**：剪辑节奏、转场、音乐音效、色彩校正与 AI 镜头质检

交付物：分镜脚本、导演阐述、场景拆解表、AI 视频生成方案、剪辑与后期指导。

## 工作方式

导演分析 → 导演阐述与视觉定位 → 场景拆解与场面调度 → 分镜设计 → AI 视频生成方案 → 剪辑与后期质检；镜头设计始终校验可生成性与跨镜头一致性。

## 使用示例

- 这是我的剧本（或小说/分集大纲），请先做导演分析并输出导演阐述与整体视觉方案。
- 请把第X集剧本拆解为专业分镜脚本（含景别、运镜、画面动作、台词声音与转场）。
- 请为这些镜头输出AI视频生成方案（中文Prompt、一致性要求、生成难点与备选方案）。

## 头像

官方头像：`avatars/05_灵启_影视导演.png`（512×512 PNG）。
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
C:\Users\Administrator\.workbuddy\plugins\marketplaces\my-experts\plugins\lingqi-film-director\
```

目录内应包含 `.codebuddy-plugin/plugin.json`、`agents/`、`avatars/` 和本 README。
如需在市场清单中登记，在 `my-experts/.codebuddy-plugin/marketplace.json` 的 `plugins` 数组补一条
`name` / `source` / `description` / `version`。完成后重启 WorkBuddy 让客户端重新扫描插件
（头像与配置有缓存，不重启可能看不到更新）。

## 打包分享

在 `experts/` 目录下执行：

```bash
zip -r lingqi-film-director.zip lingqi-film-director/
```
