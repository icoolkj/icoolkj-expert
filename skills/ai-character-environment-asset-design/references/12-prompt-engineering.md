# 12｜AI 视觉 Prompt 设计

## 1. Prompt 的目标

Prompt 不是"描述一张好看的图"，而是**下达一份可执行的视觉工单**。判断标准：另一名制作者照此 Prompt 能否产出可用的、可复用的一致性资产。

## 2. 结构化写法（七段式）

```
1 主体（谁/什么）
2 身份锁定（识别特征，逐条复现）
3 形态（角度、姿态、服装、状态）
4 环境（空间、材质、陈设）
5 光影（方向、色温、光比）
6 镜头（焦段、景别、构图、画幅）
7 风格（媒介、质感、参照锚点）
```

顺序有意义：越靠前权重越高，把不可妥协的内容放前面。

## 3. 各类型模板

### 3.1 角色基础形象
```
[年龄感/性别/族群] [脸型与骨相] [三个识别特征] [发型发色] [体型] [服装] [姿态] [光位] [景别] [风格] [画幅]
negative: extra fingers, deformed hands, asymmetric eyes, text, watermark, logo
```

### 3.2 三视图
```
character turnaround sheet, four views from left to right: front, three-quarter,
side, back. full body, consistent scale, standing on the same baseline,
A-pose, neutral expression, soft frontal light, plain mid-gray background,
orthographic, no perspective distortion, [身份锁定], [服装], [风格]
negative: perspective, dramatic lighting, cropping, different outfits per view
```

### 3.3 表情
```
[身份锁定] close-up portrait, expression: [肌肉描述 + 强度], eye direction [x],
head tilt [x], soft frontal light, neutral background, [风格]
```

### 3.4 场景主视觉
```
[空间类型] [尺寸与结构] [材质与颜色] [家具陈设] [光源与色温] [时间天气] [焦段与构图] [风格] [画幅]
```

### 3.5 场景多视角
```
same room as reference, reversed angle from [方位], showing [新增可见元素],
consistent materials and lighting direction from [方位], [焦段]
```

### 3.6 道具
```
[道具名] [尺寸] [材质] [颜色] [磨损与标记] [视角] [背景] [光位] [摄影风格]
```

### 3.7 镜头级视觉 Prompt
```
[场景编号] + [角色编号与状态] + [构图与景别] + [动作瞬间] + [光位] + [镜头语言] + [风格锁定]
```

## 4. 关键词选择的三个陷阱

1. **堆叠风格词**：`masterpiece, best quality, 8k, ultra detailed` 对一致性毫无帮助，占位浪费。
2. **抽象形容词**：`beautiful, cinematic, moody` 不可复现。换成可观测描述：`single hard key from camera left, deep falloff, 4:1 ratio`。
3. **时代错乱词**：`cyberpunk` 用在民国剧会污染服装与材质判断。

## 5. 一致性控制手段（按可靠性排序）

| 手段 | 可靠性 | 说明 |
|------|--------|------|
| 参考图 / 图生图 | 高 | 用同一张基础图作输入，最稳 |
| 角色微调（LoRA / 角色训练） | 高 | 需 15–30 张多角度素材 |
| 固定种子 + 固定参数 | 中高 | 仅在同一模型同一版本内有效 |
| 局部重绘（inpaint） | 中高 | 保持身体、只改服装/表情 |
| ControlNet / 姿态约束 | 中高 | 锁构图与姿态 |
| 结构化文字 Prompt | 中 | 必须配合上述手段 |
| 负面词排除 | 低中 | 减少错误，不保证正确 |

**结论：文字 Prompt 是基础，不是保证。** 向用户说明这一点，并给出配套方案。

## 6. 模型适配

不同模型对 Prompt 的响应差异明显，交付时注明：

- **自然语言型**（如 GPT-image / Seedream 类）：写完整句子，逻辑连贯，少用逗号堆词。
- **标签型**（如 SD 系列）：逗号分隔关键词 + 权重括号 + 强负面词。
- **参考图驱动型**：文字只写"改动部分"，其余交给参考图，文字越少越稳。
- 明确写出：模型名、版本、采样步数/CFG/种子（若用户提供）。

## 7. 负面词库（按项目取用）

```
通用：text, watermark, logo, signature, extra fingers, deformed hands,
      extra limbs, mutated, blurry, low resolution, jpeg artifacts
人物：asymmetric eyes, crossed eyes, plastic skin, over-smoothed face,
      different person, inconsistent facial features
场景：impossible geometry, floating objects, warped perspective, tilted horizon
时代：modern clothing, contemporary props, wrong-era footwear, printed graphics
```

## 8. Prompt 库交付格式

| 编号 | 用途 | Prompt | 负面词 | 参数 | 参考图 | 输出文件 | 状态 |
|------|------|--------|--------|------|--------|----------|------|
| CHAR-001-P01 | 基础形象 | ... | ... | seed 12345 / cfg 7 | ref/char001_base.png | out/char001_p01.png | Approved |

Prompt 必须与资产编号绑定，便于追溯与复用。
