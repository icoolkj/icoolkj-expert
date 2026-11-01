# 灵启·AI视觉设计师 (Lingqi AI Visual Designer)

灵启逸梦 LING QI YI MENG 原创故事工作室的 AI 视觉设计师专家：将文字设定、导演构想和剧本需求，转化为具有统一艺术风格、明确设计规范和可供 AI 影视生产使用的视觉资产。

## 类型

Agent 型（单个 AI 专家）

## 功能

- **项目视觉定位与艺术指导**：建立项目整体视觉风格、色彩体系、光影规则与统一规范（支持电影级写实 CG、3D/2D 动画、国风、赛博朋克、仙侠玄幻等多种风格）
- **角色资产设计**：基础身份、外貌特征、服装造型、表情、动作与三视图等完整角色视觉资产，保证多镜头一致性
- **场景资产设计**：城市街道、室内空间、自然环境、科幻空间等各类场景的结构、色彩、光影与氛围设定
- **道具与特殊视觉元素设计**：武器、信物、机械装置、特殊生物等叙事道具的独立设定
- **AI 图像生成 Prompt 工程**：面向 Midjourney / Stable Diffusion / FLUX / DALL·E 等模型的提示词设计与适配
- **AI 视频视觉资产适配**：为 AI 视频制作提前设计可复用、可衔接的角色、场景与道具资产
- **视觉资产管理与版本控制**：CHAR/SCENE/PROP/CREATURE/FX/STYLE 资产编号体系、版本记录与一致性检查

## 使用示例

- 这是我的项目资料（世界观/人物设定/剧本/导演阐述），请先做视觉需求分析并建立项目整体视觉规范。
- 请为我的主角设计角色视觉资产（三视图、表情、服装、动作），并输出可复用的 AI 图像生成 Prompt。
- 请检查这些生成图片的视觉一致性（角色外貌、服装、场景结构、道具），并输出一致性检查报告。

## 头像

头像已由用户提供的图片生成（512×512，约 447KB）。如需替换为自定义头像，要求：
- 格式：PNG（推荐）或 JPG
- 尺寸：512×512 px
- 大小：单张不超过 500KB

## 安装

将专家包目录放到专家目录下：

```
C:\Users\Administrator\.workbuddy\plugins\marketplaces\my-experts\plugins/lingqi-ai-visual-designer/
```

然后运行注册命令使其可见：

```bash
python3 scripts/register_expert.py <expert-dir>
```

## 打包分享

```bash
zip -r lingqi-ai-visual-designer.zip lingqi-ai-visual-designer/
```
