# Lingqi Film Director

灵启·影视导演：把剧本转化为具有明确视觉风格、完整镜头逻辑、可执行拍摄方案和 AI 制作适配能力的影视作品方案。

## 类型

Agent 型（单个 AI 专家）

## 功能

- 导演视角的剧本分析：识别主题、人物动机、戏剧冲突、关键剧情节点与视觉化重点
- 导演阐述与整体视觉定位：创作理念、影像风格、摄影与画面设计、视听设计
- 场景拆解与场面调度：空间布局、人物走位、轴线原则、镜头衔接
- 专业分镜设计：景别、机位、运镜、构图、光影、音效与转场的完整镜头表
- 镜头语言与情绪表达：用视听语言表现人物心理与故事氛围
- AI 影视制作适配：角色/场景一致性、镜头可生成性、镜头衔接、生成成本控制
- AI 视频 Prompt 设计：适配 Seedance / Sora / Kling / Veo 等工具的中英文提示词
- 剪辑与后期指导：剪辑节奏、转场、音乐音效、色彩校正与 AI 镜头质检

## 使用示例

- 这是我的剧本（或小说/分集大纲），请先做导演分析并输出导演阐述与整体视觉方案。
- 请把第X集剧本拆解为专业分镜脚本（含景别、运镜、画面动作、台词声音与转场）。
- 请为这些镜头输出AI视频生成方案（中文Prompt、一致性要求、生成难点与备选方案）。

## 头像

头像已自动生成在 `avatars/` 目录下。如需替换为自定义头像，要求：
- 格式：PNG（推荐）或 JPG
- 尺寸：512×512 px
- 大小：单张不超过 500KB

## 安装

将专家包目录放到专家目录下：

```
C:\Users\Administrator\.workbuddy\plugins\marketplaces\my-experts\plugins/lingqi-film-director/
```

然后运行注册命令使其可见：

```bash
python3 scripts/register_expert.py <expert-dir>
```

## 打包分享

```bash
zip -r lingqi-film-director.zip lingqi-film-director/
```
