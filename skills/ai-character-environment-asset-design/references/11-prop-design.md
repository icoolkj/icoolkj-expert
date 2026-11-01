# 11｜关键道具设计

## 1. 什么道具值得建资产

满足任一条件即建资产：
- 特写镜头出现。
- 推动剧情（证据、信件、武器、钥匙、信物）。
- 角色标志物（反复出现，构成识别）。
- 状态会变化（损坏、被血污染、被拆解）。
- 需要跨场景保持同一外观（否则观众会以为是两个东西）。

纯背景陈设不建独立资产，归入场景材质表。

## 2. 道具档案字段

```
道具编号：PROP-007
名称：法医解剖刀组（七件套）
类型：职业工具 / 剧情道具
归属角色：CHAR-001
出现场景：ENV-003, ENV-011
尺寸：收纳卷 32cm × 18cm 展开；最长刀 18cm
外观：深灰帆布卷，边缘磨损；刀具为不锈钢，刀柄为黑色电木，末端有编号刻印
材质：帆布 / 316 不锈钢 / 电木
颜色：卷 #3A3D40，刀身 #C9CCCE，刀柄 #141517
使用状态：闭合卷起 / 展开平铺 / 单刀持握
损坏状态：第 14 集有一把刀缺失（空位可见）
识别特征：卷外侧用白色记号笔写有"L.W."
```

## 3. 多视角要求

重要道具（尤其特写出现）需：正面、侧面、45°、使用中的手部视角、收纳/关闭状态。

小物件不必做六视图，但必须给：**尺寸参照**（与手或硬币同框）、**关键识别面**（刻字、磨损、标签所在面）。

## 4. 道具与角色的关系

- **持有方式**：握持部位、手法（专业/生疏）、放置习惯。
- **使用痕迹**：磨损位置说明使用方式（刀柄内侧磨损 = 常用）。
- **情感重量**：道具在镜头里的时长与光位反映其重要性，资产需支持特写级别精度。

## 5. 道具与场景的关系

- 位置一致性：同一道具在不同镜头中的相对位置需符合人物动线。
- 光源响应：金属与玻璃道具必须给反射描述，否则生成结果在不同场景中质感漂移。

## 6. 状态管理

`PROP-007-S01` 完整、`-S02` 单刀缺失、`-S03` 沾血、`-S04` 被拆解。

状态变化必须在登记表标注触发场次，并与角色状态的伤势地图交叉核对（血迹位置与伤口位置一致）。

## 7. Prompt 示例

```
A rolled dark gray canvas tool wrap for forensic instruments, 32cm wide when
closed, edges frayed, white marker handwriting "L.W." on the outer flap.
Unrolled view shows seven stainless steel scalpels with black bakelite handles,
each handle stamped with a small serial number, one slot empty.
Brushed steel blades with subtle scratches. Neutral gray background, top-down
studio light, product photography, high detail, no text overlay.
```

## 8. 验收标准

- 关键识别面清晰可读（刻字、标签、磨损）。
- 尺寸与手部比例正确（AI 常把道具画得过大或过小）。
- 材质反光特性与场景光源匹配。
- 状态变体的差异明确且可辨（观众能看出"少了一把刀"）。
- 同一道具在特写与全景中的外观一致。
