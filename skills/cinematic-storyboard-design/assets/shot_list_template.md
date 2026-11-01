# 镜头表（18 字段）

> 用法：每集一份。可复制为 CSV 供 `scripts/shotlist_lint.py` 检查。
> 未知项填"待确认"或"待估"，**不留空、不编造**。

## 表 A：技术参数

| shot_id | episode | scene_id | duration | shot_function | shot_size | camera_angle | composition | camera_movement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EP01-SC01-SH01 | EP01 | SC01 | 5.0s | 建立 | 远景 | 平视 | 三分 | 固定 |
| | | | | | | | | |
| | | | | | | | | |

**允许值**

- `shot_function`：建立 / 推进 / 揭示 / 反应 / 强调 / 过渡 / 停留
- `shot_size`：大远景 / 远景 / 全景 / 中全 / 中景 / 中近 / 近景 / 特写 / 大特写
- `camera_angle`：平视 / 俯 / 仰 / 侧 / 背 / 主观 / 过肩 / 荷兰角
- `composition`：三分 / 中心 / 对称 / 框架 / 遮挡 / 引导线 / 留白
- `camera_movement`：固定 / 推 / 拉 / 摇 / 移 / 跟 / 升降 / 手持 / 组合
- `duration`：`3.5s` 格式，或 `待估`

## 表 B：内容与执行

| shot_id | visual_description | character_blocking | performance | lighting | dialogue_audio | transition | continuity | visual_prompt | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EP01-SC01-SH01 | | | | | | 切 | | | |
| | | | | | | | | | |

**填写要点**

- `visual_description`：六段式（起始/主体/动作/摄影/结束/声音），不写抽象心理
- `character_blocking`：初始位置 → 过程 → 终态
- `performance`：外部可执行（下颌收紧，不是"悲伤"）
- `lighting`：方向 + 质量 + 明暗比（例：窗光左侧，柔，1:4）
- `dialogue_audio`：分列对白 / OS / VO / 环境 / 音效 / 音乐，无则写"无"
- `transition`：切 / 叠化 / 淡入淡出 / 划 / 匹配剪辑 / 硬切对撞
- `continuity`：本镜必须维持的状态（手持物、湿痕、伤势、朝向）
- `visual_prompt`：见 references/12，含画幅、景别、机位、光、构图
- `notes`：`[待确认]` / `[建议]` 事项

## 场次统计块（每场末尾必填）

```
SC__ 统计：
镜头 __ 个 ｜ 总时长 __s ｜ 平均 __s
景别分布：大远景_ / 远景_ / 全景_ / 中全_ / 中景_ / 中近_ / 近景_ / 特写_ / 大特写_
动镜 __ 个（__%）｜ 最长镜 __（_s）｜ 最短镜 __（_s）
功能分布：建立_ / 推进_ / 揭示_ / 反应_ / 强调_ / 过渡_ / 停留_
```

## 集末汇总

```
EP__ 共 __ 场，__ 镜，总时长 __
与集目标时长差异：__
连续性冲突：P0 __ / P1 __ / P2 __
待确认事项：__ 条
```

## CSV 表头（可直接使用）

```csv
shot_id,episode,scene_id,duration,shot_function,shot_size,camera_angle,composition,camera_movement,visual_description,character_blocking,performance,lighting,dialogue_audio,transition,continuity,visual_prompt,notes
```
