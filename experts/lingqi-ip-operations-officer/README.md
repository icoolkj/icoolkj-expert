# Lingqi Ip Operations Officer

[TODO: 一句话描述]

## 类型

Agent 型（单个 AI 专家）

## 功能

[TODO: 详细功能说明]

## 使用示例

- [TODO: 示例提示词1]
- [TODO: 示例提示词2]
- [TODO: 示例提示词3]

## 头像

官方头像：`avatars/08_灵启_IP运营官.png`（512×512 PNG）。
`.codebuddy-plugin/plugin.json` 的 `avatar` 字段指向该文件——更换头像时须同步更新字段，
并重跑 `python assets/expert-avatars/build_gallery.py` 刷新展示页与总览图。

自定义头像要求：
- 格式：PNG（推荐）或 JPG
- 尺寸：512×512 px
- 大小：单张不超过 500KB
- 文件名沿用 `<编号>_灵启_<角色名>.png`，保持 01–08 编号与专家一一对应


## 安装

将专家包目录放到专家目录下：

```
C:\Users\Administrator\.workbuddy\plugins\marketplaces\my-experts\plugins/lingqi-ip-operations-officer/
```

然后运行注册命令使其可见：

```bash
python3 scripts/register_expert.py <expert-dir>
```

## 打包分享

```bash
zip -r lingqi-ip-operations-officer.zip lingqi-ip-operations-officer/
```
