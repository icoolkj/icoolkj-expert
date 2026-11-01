#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""资产登记表工具（asset registry）。

用于 AI 角色与场景资产设计项目：
分配唯一资产编号、登记状态资产、校验编号唯一性、导出资产清单。

示例：
    python asset_registry.py init --project ./art --name "项目名"
    python asset_registry.py add --project ./art --type char --name "林晚" --priority P0
    python asset_registry.py add --project ./art --type env  --name "法医中心·解剖室" --priority P0
    python asset_registry.py state --project ./art --base CHAR-001 --dim C --name "冷灰长风衣通勤装"
    python asset_registry.py status --project ./art --id CHAR-001-C01 --set Review
    python asset_registry.py link --project ./art --id CHAR-001 --shot SHOT-012-003
    python asset_registry.py list --project ./art
    python asset_registry.py validate --project ./art
    python asset_registry.py report --project ./art --out ./art/assets.md
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from datetime import datetime

REGISTRY_NAME = "asset_registry.json"

TYPE_PREFIX = {
    "char": "CHAR",
    "env": "ENV",
    "prop": "PROP",
    "style": "STYLE",
    "shot": "SHOT",
}

STATUSES = ["Draft", "Review", "Approved", "Deprecated", "Superseded"]

ALLOWED_TRANSITIONS = {
    "Draft": {"Draft", "Review", "Deprecated"},
    "Review": {"Draft", "Review", "Approved", "Deprecated"},
    "Approved": {"Approved", "Superseded", "Deprecated"},
    "Deprecated": {"Deprecated"},
    "Superseded": {"Superseded", "Deprecated"},
}

# 状态维度后缀：-A 年龄 -C 服装 -M 妆造 -I 伤势 -G 成长 -X 特殊状态 -E 表情 -S 场景状态
STATE_DIMS = {"A", "C", "M", "I", "G", "X", "E", "S"}

ID_PATTERNS = {
    "CHAR": re.compile(r"^CHAR-\d{3}(-[A-Z]\d{2})?$"),
    "ENV": re.compile(r"^ENV-\d{3}(-S\d{2})?$"),
    "PROP": re.compile(r"^PROP-\d{3}(-[A-Z]\d{2})?$"),
    "STYLE": re.compile(r"^STYLE-\d{3}$"),
    "SHOT": re.compile(r"^SHOT-\d{3}-\d{3}$"),
}


# ---------------------------------------------------------------- 基础读写

def now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def registry_path(project: str) -> str:
    return os.path.join(project, REGISTRY_NAME)


def load(project: str) -> dict:
    path = registry_path(project)
    if not os.path.exists(path):
        die(f"未找到登记表：{path}\n请先执行 init。")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save(project: str, data: dict) -> None:
    path = registry_path(project)
    data["updated"] = now()
    # 原子写入，避免中断导致登记表损坏
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path) or ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def die(msg: str) -> None:
    print(f"[错误] {msg}", file=sys.stderr)
    sys.exit(1)


def warn(msg: str) -> None:
    print(f"[提示] {msg}", file=sys.stderr)


def find(data: dict, asset_id: str) -> dict | None:
    for a in data["assets"]:
        if a["id"] == asset_id:
            return a
    return None


# ---------------------------------------------------------------- 命令实现

def cmd_init(args) -> None:
    os.makedirs(args.project, exist_ok=True)
    path = registry_path(args.project)
    if os.path.exists(path) and not args.force:
        die(f"登记表已存在：{path}\n如需重建请加 --force。")
    data = {
        "project": args.name or os.path.basename(os.path.abspath(args.project)),
        "created": now(),
        "updated": now(),
        "counters": {p: 0 for p in TYPE_PREFIX.values()},
        "assets": [],
    }
    save(args.project, data)
    print(f"已创建登记表：{path}")


def cmd_add(args) -> None:
    data = load(args.project)
    prefix = TYPE_PREFIX[args.type]

    if prefix == "SHOT":
        if not args.scene_no:
            die("登记 SHOT 需要 --scene-no（场次号）。")
        num = args.scene_no
        counters = data["counters"]
        key = f"SHOT-{num}"
        counters[key] = counters.get(key, 0) + 1
        asset_id = f"SHOT-{int(num):03d}-{counters[key]:03d}"
    else:
        counters = data["counters"]
        counters[prefix] = counters.get(prefix, 0) + 1
        asset_id = f"{prefix}-{counters[prefix]:03d}"

    if find(data, asset_id):
        die(f"编号冲突：{asset_id} 已存在，请检查登记表 counters。")

    asset = {
        "id": asset_id,
        "type": prefix,
        "name": args.name,
        "priority": args.priority,
        "status": args.status,
        "version": 1,
        "parent": None,
        "note": args.note or "",
        "shots": [],
        "created": now(),
        "updated": now(),
    }
    data["assets"].append(asset)
    save(args.project, data)
    print(f"已登记 {asset_id}｜{args.name}｜{args.priority}｜{args.status}")


def cmd_state(args) -> None:
    data = load(args.project)
    base = find(data, args.base)
    if not base:
        die(f"找不到基础资产：{args.base}")
    if base["type"] not in ("CHAR", "ENV", "PROP"):
        die("只有 CHAR / ENV / PROP 支持状态资产。")

    dim = args.dim.upper()
    if dim not in STATE_DIMS:
        die(f"未知状态维度：{dim}，可选 {sorted(STATE_DIMS)}")

    if base["type"] == "ENV" and dim != "S":
        die("场景状态统一使用 -S 后缀。")
    if base["type"] != "ENV" and dim == "S":
        die("只有 ENV 使用 -S 后缀。")

    siblings = [a for a in data["assets"] if a.get("parent") == base["id"]]
    seq = len(siblings) + 1
    asset_id = f"{base['id']}-{dim}{seq:02d}"
    while find(data, asset_id):
        seq += 1
        asset_id = f"{base['id']}-{dim}{seq:02d}"

    asset = {
        "id": asset_id,
        "type": base["type"],
        "name": args.name,
        "priority": base["priority"],
        "status": args.status,
        "version": 1,
        "parent": base["id"],
        "note": args.note or "",
        "shots": [],
        "created": now(),
        "updated": now(),
    }
    data["assets"].append(asset)
    save(args.project, data)
    print(f"已登记状态资产 {asset_id}（父级 {base['id']}）｜{args.name}")


def cmd_status(args) -> None:
    data = load(args.project)
    asset = find(data, args.id)
    if not asset:
        die(f"找不到资产：{args.id}")
    cur, new = asset["status"], args.set
    if new not in STATUSES:
        die(f"未知状态：{new}，可选 {STATUSES}")
    if new not in ALLOWED_TRANSITIONS.get(cur, set()):
        die(f"非法状态流转：{cur} → {new}")
    if cur == "Approved" and new == "Approved" and not args.force:
        warn("资产已是 Approved，未做变更。")
        return
    asset["status"] = new
    asset["updated"] = now()
    save(args.project, data)
    print(f"{args.id}：{cur} → {new}")


def cmd_update(args) -> None:
    data = load(args.project)
    asset = find(data, args.id)
    if not asset:
        die(f"找不到资产：{args.id}")
    if asset["status"] == "Approved" and not args.force:
        die(
            f"{args.id} 已确认（Approved），禁止直接覆盖。\n"
            "如需修改请加 --force（将自动生成新版本），或先降级为 Review。"
        )
    changed = []
    if args.name:
        asset["name"] = args.name
        changed.append("name")
    if args.note is not None:
        asset["note"] = args.note
        changed.append("note")
    if args.priority:
        asset["priority"] = args.priority
        changed.append("priority")
    if args.force:
        asset["version"] += 1
        changed.append(f"version→{asset['version']}")
    asset["updated"] = now()
    save(args.project, data)
    print(f"已更新 {args.id}：{', '.join(changed) or '无变更'}")


def cmd_link(args) -> None:
    data = load(args.project)
    asset = find(data, args.id)
    if not asset:
        die(f"找不到资产：{args.id}")
    if not re.match(r"^SHOT-\d{3}-\d{3}$", args.shot):
        die("镜头号格式应为 SHOT-XXX-XXX。")
    if args.shot not in asset["shots"]:
        asset["shots"].append(args.shot)
        asset["shots"].sort()
        asset["updated"] = now()
        save(args.project, data)
    print(f"{args.id} 关联 {args.shot}（共 {len(asset['shots'])} 个镜头）")


def cmd_list(args) -> None:
    data = load(args.project)
    rows = data["assets"]
    if args.type:
        rows = [a for a in rows if a["type"] == TYPE_PREFIX[args.type]]
    if args.priority:
        rows = [a for a in rows if a["priority"] == args.priority]
    if args.status:
        rows = [a for a in rows if a["status"] == args.status]
    if not rows:
        print("（无匹配资产）")
        return
    print(f"{'编号':<16}{'名称':<24}{'优先级':<8}{'状态':<12}{'版本':<6}镜头数")
    for a in rows:
        print(
            f"{a['id']:<16}{a['name'][:22]:<24}{a['priority']:<8}"
            f"{a['status']:<12}v{a['version']:<5}{len(a['shots'])}"
        )
    print(f"\n共 {len(rows)} 项")


def cmd_validate(args) -> None:
    data = load(args.project)
    problems: list[str] = []
    seen: dict[str, str] = {}

    for a in data["assets"]:
        aid = a["id"]
        if aid in seen:
            problems.append(f"编号重复：{aid}")
        seen[aid] = a["name"]

        pattern = ID_PATTERNS.get(a["type"])
        if pattern and not pattern.match(aid):
            problems.append(f"编号格式不符：{aid}（类型 {a['type']}）")

        if a["status"] not in STATUSES:
            problems.append(f"{aid} 状态非法：{a['status']}")
        if a["status"] == "Approved" and a["type"] in ("CHAR", "ENV") and not a["shots"]:
            problems.append(f"{aid} 已确认但未关联任何镜头（可能尚未进入生产）")
        if a.get("parent") and not find(data, a["parent"]):
            problems.append(f"{aid} 的父级不存在：{a['parent']}")

    for prefix, count in data["counters"].items():
        if prefix.startswith("SHOT"):
            continue
        existing = [a for a in data["assets"] if a["type"] == prefix and a.get("parent") is None]
        if count < len(existing):
            problems.append(f"{prefix} 计数器（{count}）小于实际资产数（{len(existing)}）")

    if problems:
        print(f"校验未通过，发现 {len(problems)} 个问题：")
        for p in problems:
            print(f"  - {p}")
        sys.exit(1)

    total = len(data["assets"])
    by_status = {}
    for a in data["assets"]:
        by_status[a["status"]] = by_status.get(a["status"], 0) + 1
    print(f"校验通过：共 {total} 项资产")
    for s in STATUSES:
        if s in by_status:
            print(f"  {s}: {by_status[s]}")


def cmd_report(args) -> None:
    data = load(args.project)
    lines = [
        f"# 资产清单｜{data['project']}",
        "",
        f"生成时间：{now()}　资产总数：{len(data['assets'])}",
        "",
        "## 角色（CHAR）",
        "",
        "| 编号 | 名称 | 优先级 | 状态 | 版本 | 关联镜头 |",
        "|------|------|--------|------|------|----------|",
    ]

    def block(prefix: str) -> list[str]:
        out = []
        for a in data["assets"]:
            if a["type"] != prefix:
                continue
            indent = "　└ " if a.get("parent") else ""
            shots = ", ".join(a["shots"]) if a["shots"] else "—"
            out.append(
                f"| {a['id']} | {indent}{a['name']} | {a['priority']} | "
                f"{a['status']} | v{a['version']} | {shots} |"
            )
        if not out:
            out.append("| — | （无） | — | — | — | — |")
        return out

    lines += block("CHAR")
    lines += ["", "## 场景（ENV）", "",
              "| 编号 | 名称 | 优先级 | 状态 | 版本 | 关联镜头 |",
              "|------|------|--------|------|------|----------|"]
    lines += block("ENV")
    lines += ["", "## 道具（PROP）", "",
              "| 编号 | 名称 | 优先级 | 状态 | 版本 | 关联镜头 |",
              "|------|------|--------|------|------|----------|"]
    lines += block("PROP")
    lines += ["", "## 风格（STYLE）", "",
              "| 编号 | 名称 | 优先级 | 状态 | 版本 | 关联镜头 |",
              "|------|------|--------|------|------|----------|"]
    lines += block("STYLE")

    pending = [a for a in data["assets"] if a["status"] in ("Draft", "Review")]
    lines += ["", "## 待确认资产", ""]
    if pending:
        for a in pending:
            lines.append(f"- {a['id']}｜{a['name']}｜{a['status']}")
    else:
        lines.append("- 无")

    text = "\n".join(lines) + "\n"
    if args.out:
        os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"已导出：{args.out}")
    else:
        print(text)


# ---------------------------------------------------------------- 入口

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="AI 角色与场景资产登记表工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("init", help="初始化登记表")
    s.add_argument("--project", required=True, help="项目资产目录")
    s.add_argument("--name", help="项目名")
    s.add_argument("--force", action="store_true", help="覆盖已有登记表")
    s.set_defaults(func=cmd_init)

    s = sub.add_parser("add", help="新增基础资产并分配编号")
    s.add_argument("--project", required=True)
    s.add_argument("--type", required=True, choices=list(TYPE_PREFIX.keys()))
    s.add_argument("--name", required=True)
    s.add_argument("--priority", default="P1", choices=["P0", "P1", "P2", "P3"])
    s.add_argument("--status", default="Draft", choices=STATUSES)
    s.add_argument("--note", default="")
    s.add_argument("--scene-no", help="SHOT 类型必填：场次号")
    s.set_defaults(func=cmd_add)

    s = sub.add_parser("state", help="为资产新增状态变体")
    s.add_argument("--project", required=True)
    s.add_argument("--base", required=True, help="父级资产编号，如 CHAR-001")
    s.add_argument("--dim", required=True, help="状态维度：A/C/M/I/G/X/E/S")
    s.add_argument("--name", required=True, help="状态名称，如 冷灰长风衣通勤装")
    s.add_argument("--status", default="Draft", choices=STATUSES)
    s.add_argument("--note", default="")
    s.set_defaults(func=cmd_state)

    s = sub.add_parser("status", help="变更资产状态")
    s.add_argument("--project", required=True)
    s.add_argument("--id", required=True)
    s.add_argument("--set", required=True, choices=STATUSES)
    s.add_argument("--force", action="store_true")
    s.set_defaults(func=cmd_status)

    s = sub.add_parser("update", help="修改资产字段（Approved 需 --force）")
    s.add_argument("--project", required=True)
    s.add_argument("--id", required=True)
    s.add_argument("--name")
    s.add_argument("--note")
    s.add_argument("--priority", choices=["P0", "P1", "P2", "P3"])
    s.add_argument("--force", action="store_true", help="强制修改并升级版本号")
    s.set_defaults(func=cmd_update)

    s = sub.add_parser("link", help="关联镜头")
    s.add_argument("--project", required=True)
    s.add_argument("--id", required=True)
    s.add_argument("--shot", required=True, help="SHOT-XXX-XXX")
    s.set_defaults(func=cmd_link)

    s = sub.add_parser("list", help="列出资产")
    s.add_argument("--project", required=True)
    s.add_argument("--type", choices=list(TYPE_PREFIX.keys()))
    s.add_argument("--priority", choices=["P0", "P1", "P2", "P3"])
    s.add_argument("--status", choices=STATUSES)
    s.set_defaults(func=cmd_list)

    s = sub.add_parser("validate", help="校验编号唯一性与状态合法性")
    s.add_argument("--project", required=True)
    s.set_defaults(func=cmd_validate)

    s = sub.add_parser("report", help="导出 Markdown 资产清单")
    s.add_argument("--project", required=True)
    s.add_argument("--out", help="输出文件路径，缺省打印到 stdout")
    s.set_defaults(func=cmd_report)

    return p


def main() -> None:
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
