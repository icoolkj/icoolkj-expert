# 8 位专家头像 · 编号映射

官方头像按 **01–08** 编号与 8 位专家一一对应，顺序与根目录 README 的「专家清单」一致。
头像原图保存在各自的 `experts/<目录>/avatars/` 下，**`plugin.json` 的 `avatar` 字段直接指向带编号的文件名**，不再使用通用的 `expert.png`。

| 编号 | 专家 | 目录 | 头像文件 | 绑定 Skill |
| --- | --- | --- | --- | --- |
| 01 | 灵启·总编策划官 | `lingqi-chief-editor` | `01_灵启_总编策划官.png` | S01、S10 |
| 02 | 灵启·世界观架构师 | `lingqi-worldbuilding-architect` | `02_灵启_世界观架构师.png` | S02 |
| 03 | 灵启·小说主笔 | `lingqi-novel-writer` | `03_灵启_小说主笔.png` | S03、S04 |
| 04 | 灵启·短剧编剧 | `lingqi-shortdrama-writer` | `04_灵启_短剧编剧.png` | S05、S06 |
| 05 | 灵启·影视导演 | `lingqi-film-director` | `05_灵启_影视导演.png` | S07 |
| 06 | 灵启·AI视觉设计师 | `lingqi-ai-visual-designer` | `06_灵启_AI视觉设计师.png` | S08 |
| 07 | 灵启·故事审校官 | `lingqi-story-reviewer` | `07_灵启_故事审校官.png` | S09 |
| 08 | 灵启·IP运营官 | `lingqi-ip-operations-officer` | `08_灵启_IP运营官.png` | S10 |

规格：512×512 PNG，单张 350–410KB。

## 文件说明

| 文件 | 用途 |
| --- | --- |
| `gallery.html` | 展示页：8 张头像卡片 + 深色界面效果 + 映射表。512 PNG 压成 320 JPEG 内联，无脚本无外部依赖，单文件即可打开或分享 |
| `contact-sheet.png` | 4×2 总览图，单文件可直接分享 |
| `build_gallery.py` | 生成脚本，数据源是 8 个 `plugin.json` 的 `avatar` / `displayName` / `profession` |

## 换头像的正确姿势

1. 把新图片放进对应专家的 `avatars/`，文件名沿用 `<编号>_灵启_<角色名>.png`
2. 更新该专家 `.codebuddy-plugin/plugin.json` 的 `avatar` 字段指向新文件名
3. 重跑生成脚本，展示页与总览图一起刷新：

```bash
python assets/expert-avatars/build_gallery.py
```

4. 同步到本机专家目录后，重启 WorkBuddy 让客户端重新扫描插件

> 关联的唯一真相是 `plugin.json` 的 `avatar` 字段。只换文件、不改字段会导致头像断链。

## 本机安装位置

```
C:\Users\Administrator\.workbuddy\plugins\marketplaces\my-experts\plugins\<专家目录>\
```

另外 `marketplaces\experts\plugins\` 下还有一份 `lingqi-shortdrama-writer`，同步时需要一并更新，否则列表里可能出现旧头像。
