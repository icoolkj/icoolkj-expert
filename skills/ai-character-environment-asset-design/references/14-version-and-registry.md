# 14｜编号、版本与登记表管理

## 1. 编号规则

| 类型 | 格式 | 正则 | 示例 |
|------|------|------|------|
| 角色基础 | `CHAR-XXX` | `^CHAR-\d{3}$` | CHAR-001 |
| 角色状态 | `CHAR-XXX-<维度>XX` | `^CHAR-\d{3}-[A-Z]\d{2}$` | CHAR-001-C02 |
| 场景基础 | `ENV-XXX` | `^ENV-\d{3}$` | ENV-003 |
| 场景状态 | `ENV-XXX-SXX` | `^ENV-\d{3}-S\d{2}$` | ENV-003-S01 |
| 道具 | `PROP-XXX` | `^PROP-\d{3}$` | PROP-007 |
| 风格 | `STYLE-XXX` | `^STYLE-\d{3}$` | STYLE-001 |
| 镜头 | `SHOT-XXX-XXX` | `^SHOT-\d{3}-\d{3}$` | SHOT-012-003 |

### 状态维度码

| 码 | 维度 |
|----|------|
| A | 年龄阶段 |
| C | 服装 |
| M | 妆造 |
| I | 伤势 |
| G | 成长阶段 |
| X | 特殊状态（湿身、血污、幻境） |
| E | 表情 |
| S | 场景状态（昼夜、天气、停电） |

规则：编号唯一、不复用、不跳号（跳号可接受，复用不可接受）。废弃资产保留编号，状态置 Deprecated。

## 2. 版本规则

- `version` 为整数，每次对已确认资产的实质修改 +1。
- 版本记录必须包含：修改人、日期、改了什么、为什么改、影响了哪些镜头。
- **不允许静默覆盖**：Approved 资产被改动时，旧版本文件必须保留（旧文件名加 `_v1` 后缀），新版本另存。
- 版本号只增不减，回滚通过新建版本实现，不改历史。

## 3. 登记表工具：`scripts/asset_registry.py`

纯标准库，无依赖。登记表存为项目目录下的 `asset_registry.json`。

### 3.1 常用命令

```bash
# 初始化（在项目资产目录下建立登记表）
python scripts/asset_registry.py init --project ./art --name "项目名"

# 新增基础资产，自动分配编号
python scripts/asset_registry.py add --project ./art --type char --name "林晚" --priority P0
python scripts/asset_registry.py add --project ./art --type env  --name "法医中心·解剖室" --priority P0
python scripts/asset_registry.py add --project ./art --type prop --name "解剖刀组" --priority P1
python scripts/asset_registry.py add --project ./art --type style --name "冷调写实雨夜" --priority P0
python scripts/asset_registry.py add --project ./art --type shot --name "解剖台特写" --scene-no 12

# 新增状态变体（自动续号 CHAR-001-C01 / C02 ...）
python scripts/asset_registry.py state --project ./art --base CHAR-001 --dim C --name "冷灰长风衣通勤装"
python scripts/asset_registry.py state --project ./art --base ENV-003 --dim S --name "雨夜停电"

# 状态流转
python scripts/asset_registry.py status --project ./art --id CHAR-001-C01 --set Review
python scripts/asset_registry.py status --project ./art --id CHAR-001-C01 --set Approved

# 修改已确认资产（必须 --force，自动升版本）
python scripts/asset_registry.py update --project ./art --id CHAR-001 --note "新增左眉疤痕位置说明" --force

# 镜头关联与校验
python scripts/asset_registry.py link     --project ./art --id CHAR-001 --shot SHOT-012-003
python scripts/asset_registry.py validate --project ./art
python scripts/asset_registry.py list     --project ./art --priority P0

# 导出交付清单
python scripts/asset_registry.py report --project ./art --out ./art/assets.md
```

### 3.2 状态机约束（脚本强制）

| 当前 | 允许流转到 |
|------|-----------|
| Draft | Draft, Review, Deprecated |
| Review | Draft, Review, Approved, Deprecated |
| Approved | Approved, Superseded, Deprecated |
| Deprecated | Deprecated |
| Superseded | Superseded, Deprecated |

非法流转会被拒绝。Approved 资产的字段修改需 `--force`，并自动 version+1。

### 3.3 校验内容

- 编号格式与唯一性。
- 状态合法性。
- 父级状态资产是否存在。
- 计数器与实际资产数是否一致。
- 已确认的角色 / 场景是否已关联镜头（未关联会提示，用于发现"做完没用上"的资产）。

## 4. 无脚本时的替代方案

若环境无法运行 Python：

1. 使用 `references/15-templates.md` 中的 Markdown 表格手工维护。
2. 每次分配编号前在表内全局搜索该编号，确认未占用。
3. 状态变更在表内加一行「变更记录」，不删旧行。

## 5. 版本变更记录模板

```markdown
| 日期 | 资产编号 | 版本 | 变更类型 | 变更内容 | 原因 | 影响镜头 | 操作人 | 确认人 |
|------|----------|------|----------|----------|------|----------|--------|--------|
| 2026-03-02 | CHAR-001 | v2 | 特征追加 | 明确左眉疤痕长 1.5cm | 生成不统一 | SHOT-012-003～006 | 美术 | 导演 |
```

## 6. 资产交接包结构

```
project/
├── 00_style/            STYLE-001 视觉圣经、色卡、参考图
├── 01_characters/
│   ├── CHAR-001_林晚/
│   │   ├── CHAR-001_profile.md
│   │   ├── CHAR-001_turnaround/
│   │   ├── CHAR-001_expression/
│   │   └── CHAR-001-C01_costume/
├── 02_environments/
│   └── ENV-003_解剖室/
│       ├── ENV-003_plan.md
│       ├── ENV-003_main/
│       └── ENV-003-S02_night/
├── 03_props/
├── 04_prompts/          prompt 库（按编号命名）
├── 05_reports/          一致性报告、验收报告
└── asset_registry.json
```
