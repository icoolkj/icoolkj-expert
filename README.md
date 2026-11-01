# icoolkj-expert
灵启逸梦 · AI创艺坊专家工作室
> 面向网文、短剧IP全链路创作的 WorkBuddy 专家 & Skill 能力仓库

官网：https://icoolkj.com  

## 🧩 定位说明
专家 = 业务角色Agent；Skill = 可复用能力单元
一个专家可以挂载多个Skill，同一个Skill支持多专家复用，实现IP创作流水线协同。

## 👥 专家清单
| 专家名称 | 核心职责 | 交付物 |
| ---- | ---- | ---- |
| 灵启·总编策划官 | 项目决策、选题立项 | IP项目策划案 |
| 灵启·世界观架构师 | 世界规则、势力、力量体系 | 世界观设定集 |
| 灵启·小说主笔 | 长篇小说创作、章节续写 | 小说正文 |
| 灵启·短剧编剧 | 网文转短剧、剧本标准化 | 短剧成片剧本 |
| 灵启·影视导演 | 剧本影视化、镜头设计 | 分镜脚本、导演阐述 |
| 灵启·AI视觉设计师 | 角色、场景美术资产生成 | 角色立绘、场景素材、绘图Prompt |
| 灵启·故事审校官 | 剧情逻辑、人设、时间线校验 | 审校报告、bug修复建议 |
| 灵启·IP运营官 | IP包装、传播、商业化方案 | IP运营策划方案 |

## 🛠️ Skill清单（第一批10个核心Skill）
| 编号 | Skill名称 | 领域 |
| ---- | ---- | ---- |
| S01 | 原创IP项目策划 Skill | 项目策划 |
| S02 | 故事世界观构建 Skill | 世界观 |
| S03 | 长篇小说创作 Skill | 小说 |
| S04 | 小说章节续写与连续性 Skill | 小说 |
| S05 | 小说转短剧改编 Skill | 短剧 |
| S06 | 短剧剧本标准化 Skill | 短剧 |
| S07 | 影视分镜设计 Skill | 导演 |
| S08 | AI角色与场景资产设计 Skill | 视觉 |
| S09 | 故事逻辑与连续性审校 Skill | 审校 |
| S10 | IP商业运营策划 Skill | 运营 |

### 专家 ↔ Skill 映射关系
| 专家 | 绑定Skill |
| ---- | ---- |
| 灵启·总编策划官 | S01、S10 |
| 灵启·世界观架构师 | S02 |
| 灵启·小说主笔 | S03、S04 |
| 灵启·短剧编剧 | S05、S06 |
| 灵启·影视导演 | S07 |
| 灵启·AI视觉设计师 | S08 |
| 灵启·故事审校官 | S09 |
| 灵启·IP运营官 | S10 |

## 📂 目录结构
```text
icoolkj-expert/
├── experts/                # 8 位专家角色配置
│   ├── lingqi-ai-visual-designer/        # 灵启・AI 视觉设计师
│   ├── lingqi-chief-editor/              # 灵启・总编策划官
│   ├── lingqi-film-director/             # 灵启・影视导演
│   ├── lingqi-ip-operations-officer/     # 灵启・IP 运营官
│   ├── lingqi-novel-writer/              # 灵启・小说主笔
│   ├── lingqi-shortdrama-writer/         # 灵启・短剧编剧
│   ├── lingqi-story-reviewer/            # 灵启・故事审校官
│   └── lingqi-worldbuilding-architect/   # 灵启・世界观架构师
├── skills/                 # 10 个 Skill 能力包
├── assets/
│   └── avatars/            # 专家头像原图、绘图提示词
├── docs/                   # 工作流、规范文档
├── LICENSE
└── README.md
```

## 📜 版权与授权
作者：icoolkj｜灵启逸梦 · AI创艺坊  
官网：https://icoolkj.com  
联系：icoolkj@163.com / QQ：594047667  

授权协议：**CC BY-NC-SA 4.0**
- ✅ 个人学习、自用创作、二次修改衍生
- ✅ 衍生作品必须沿用 CC BY-NC-SA 4.0 协议开源
- ❌ 禁止商用、打包售卖、付费服务、商业接单
- ✅ 分发、改编必须标注原项目来源

> 协议官方地址：https://creativecommons.org/licenses/by-nc-sa/4.0/
