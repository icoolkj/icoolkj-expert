#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""故事逻辑与连续性审校 —— 问题台账管理工具。

用于在多次审校/复审之间保持问题编号唯一、状态可追踪、统计可复现。
台账为单个 JSON 文件，只保存问题元数据（不保存原文全文）。

用法示例：
    python review_ledger.py init --project "长夜" --scope "第1-40章" --ledger ledger.json
    python review_ledger.py add --ledger ledger.json --prefix TIME --severity P1 \
        --title "行程三日不可达" --location "第13章" --module M04
    python review_ledger.py set-status --ledger ledger.json --id TIME-001 --status 待复审
    python review_ledger.py summary --ledger ledger.json
    python review_ledger.py export-md --ledger ledger.json --out report-issues.md
"""

import argparse
import json
import os
import sys
from collections import Counter, OrderedDict
from datetime import datetime

try:  # 保证在 Windows 控制台也能正确输出中文
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:  # pragma: no cover
    pass

PREFIXES = OrderedDict([
    ("LOGIC", "M01 故事因果逻辑"),
    ("CHAR", "M02/M10 人物动机与情绪成长"),
    ("RULE", "M03 世界观规则"),
    ("TIME", "M04 时间线连续性"),
    ("STATE", "M05 人物状态连续性"),
    ("KNOW", "M06 人物认知边界"),
    ("PLOT", "M07 情节衔接"),
    ("FORESHADOW", "M07 伏笔与回收"),
    ("SPACE", "M08 空间与道具"),
    ("MEDIA", "M09 跨媒介一致性"),
])

SEVERITIES = ["P0", "P1", "P2", "P3", "P4"]

STATUSES = ["待确认", "已确认", "修复中", "待复审", "已关闭", "保留原设计"]

SEVERITY_LABEL = {
    "P0": "致命逻辑错误",
    "P1": "严重连续性错误",
    "P2": "重要逻辑风险",
    "P3": "一般叙事问题",
    "P4": "表达与体验问题",
}


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def die(msg):
    print("错误：" + msg, file=sys.stderr)
    sys.exit(1)


def load(path):
    if not os.path.exists(path):
        die("台账文件不存在：%s（先运行 init）" % path)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    data.setdefault("issues", [])
    return data


def save(path, data):
    data["updated"] = now()
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def next_id(data, prefix):
    nums = []
    for it in data["issues"]:
        iid = it.get("id", "")
        if iid.startswith(prefix + "-"):
            tail = iid[len(prefix) + 1:]
            if tail.isdigit():
                nums.append(int(tail))
    n = (max(nums) + 1) if nums else 1
    return "%s-%03d" % (prefix, n)


def cmd_init(args):
    if os.path.exists(args.ledger) and not args.force:
        die("台账已存在：%s（如需覆盖请加 --force）" % args.ledger)
    data = {
        "project": args.project,
        "scope": args.scope or "",
        "created": now(),
        "updated": now(),
        "issues": [],
    }
    save(args.ledger, data)
    print("已初始化台账：%s" % os.path.abspath(args.ledger))
    print("  项目：%s" % data["project"])
    print("  范围：%s" % (data["scope"] or "（未填写）"))


def cmd_add(args):
    data = load(args.ledger)
    prefix = args.prefix.upper()
    if prefix not in PREFIXES:
        die("未知前缀 %s，可选：%s" % (prefix, ", ".join(PREFIXES)))
    severity = args.severity.upper()
    if severity not in SEVERITIES:
        die("未知等级 %s，可选：%s" % (severity, ", ".join(SEVERITIES)))
    status = args.status
    if status not in STATUSES:
        die("未知状态 %s，可选：%s" % (status, ", ".join(STATUSES)))
    if not args.title.strip():
        die("标题不能为空")

    iid = args.id or next_id(data, prefix)
    if any(it.get("id") == iid for it in data["issues"]):
        die("编号已存在：%s（编号不可复用）" % iid)

    issue = {
        "id": iid,
        "prefix": prefix,
        "module": args.module or "",
        "severity": severity,
        "status": status,
        "title": args.title.strip(),
        "location": args.location or "",
        "basis": args.basis or "",
        "fix": args.fix or "",
        "impact": args.impact or "",
        "note": args.note or "",
        "created": now(),
        "updated": now(),
    }
    data["issues"].append(issue)
    save(args.ledger, data)
    print("已登记 %s [%s] %s" % (iid, severity, issue["title"]))


def cmd_set_status(args):
    data = load(args.ledger)
    if args.status not in STATUSES:
        die("未知状态 %s，可选：%s" % (args.status, ", ".join(STATUSES)))
    hit = [it for it in data["issues"] if it.get("id") == args.id]
    if not hit:
        die("未找到编号：%s" % args.id)
    it = hit[0]
    old = it.get("status", "")
    it["status"] = args.status
    it["updated"] = now()
    if args.note:
        prev = it.get("note", "")
        it["note"] = (prev + " | " if prev else "") + args.note
    save(args.ledger, data)
    print("%s 状态：%s → %s" % (args.id, old, args.status))


def cmd_set_severity(args):
    data = load(args.ledger)
    sev = args.severity.upper()
    if sev not in SEVERITIES:
        die("未知等级 %s" % sev)
    hit = [it for it in data["issues"] if it.get("id") == args.id]
    if not hit:
        die("未找到编号：%s" % args.id)
    it = hit[0]
    old = it.get("severity")
    it["severity"] = sev
    it["updated"] = now()
    if args.note:
        prev = it.get("note", "")
        it["note"] = (prev + " | " if prev else "") + args.note
    save(args.ledger, data)
    print("%s 等级：%s → %s" % (args.id, old, sev))


def filtered(data, args):
    out = data["issues"]
    if getattr(args, "status", None):
        out = [it for it in out if it.get("status") == args.status]
    if getattr(args, "severity", None):
        out = [it for it in out if it.get("severity") == args.severity.upper()]
    if getattr(args, "prefix", None):
        out = [it for it in out if it.get("prefix") == args.prefix.upper()]
    return out


def cmd_list(args):
    data = load(args.ledger)
    items = filtered(data, args)
    if not items:
        print("（无匹配记录）")
        return
    print("%-14s %-3s %-8s %-10s %s" % ("编号", "等级", "状态", "位置", "标题"))
    print("-" * 78)
    for it in items:
        print("%-14s %-3s %-8s %-10s %s" % (
            it.get("id", ""), it.get("severity", ""), it.get("status", ""),
            (it.get("location") or "-")[:10], it.get("title", "")))
    print("-" * 78)
    print("合计 %d 条" % len(items))


def cmd_summary(args):
    data = load(args.ledger)
    issues = data["issues"]
    print("项目：%s" % data.get("project", ""))
    print("范围：%s" % (data.get("scope") or "（未填写）"))
    print("台账更新：%s" % data.get("updated", ""))
    print("问题总数：%d\n" % len(issues))

    if not issues:
        return

    print("按等级：")
    sev_count = Counter(it.get("severity", "?") for it in issues)
    for s in SEVERITIES:
        c = sev_count.get(s, 0)
        if c:
            pct = 100.0 * c / len(issues)
            print("  %s %-12s %3d 条  %5.1f%%" % (s, SEVERITY_LABEL[s], c, pct))
    others = {k: v for k, v in sev_count.items() if k not in SEVERITIES}
    for k, v in others.items():
        print("  %-3s %-12s %3d 条" % (k, "（非法等级）", v))

    print("\n按模块：")
    mod_count = Counter(it.get("module") or "未标注" for it in issues)
    for m, c in sorted(mod_count.items()):
        print("  %-6s %3d 条" % (m, c))

    print("\n按状态：")
    st_count = Counter(it.get("status", "?") for it in issues)
    for s in STATUSES:
        if st_count.get(s):
            print("  %-8s %3d 条" % (s, st_count[s]))

    open_items = [it for it in issues if it.get("status") not in ("已关闭", "保留原设计")]
    print("\n未关闭：%d 条" % len(open_items))

    critical = [it for it in issues if it.get("severity") in ("P0", "P1")]
    if critical:
        print("\nP0/P1 清单：")
        for it in critical:
            print("  %-14s %-3s %-8s %s" % (
                it.get("id"), it.get("severity"), it.get("status"), it.get("title")))

    # 健康度提示
    p0 = sev_count.get("P0", 0)
    if len(issues) >= 5 and p0 > 0 and 100.0 * p0 / len(issues) > 10:
        print("\n[提示] P0 占比超过 10%，请复核是否存在定级通胀（参见 references/10）。")
    if p0 > 3:
        print("[提示] P0 超过 3 条，建议逐条复核冲突基准是否建立有误。")


def cmd_export_md(args):
    data = load(args.ledger)
    items = data["issues"]
    lines = []
    lines.append("# 问题索引：%s" % data.get("project", ""))
    lines.append("")
    lines.append("- 审校范围：%s" % (data.get("scope") or "（未填写）"))
    lines.append("- 台账更新：%s" % data.get("updated", ""))
    lines.append("- 问题总数：%d" % len(items))
    lines.append("")
    lines.append("| 编号 | 等级 | 状态 | 模块 | 位置 | 标题 |")
    lines.append("|---|---|---|---|---|---|")
    for it in items:
        lines.append("| %s | %s | %s | %s | %s | %s |" % (
            it.get("id", ""), it.get("severity", ""), it.get("status", ""),
            it.get("module", ""), it.get("location", ""), it.get("title", "")))
    text = "\n".join(lines) + "\n"
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text)
        print("已导出：%s" % os.path.abspath(args.out))
    else:
        print(text)


def cmd_prefixes(args):
    print("可用前缀：")
    for p, desc in PREFIXES.items():
        print("  %-11s %s" % (p, desc))
    print("\n可用状态：%s" % "、".join(STATUSES))
    print("可用等级：%s" % "、".join(SEVERITIES))


def build_parser():
    p = argparse.ArgumentParser(
        description="故事逻辑与连续性审校 —— 问题台账管理",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="前缀与状态的取值可用 `prefixes` 子命令查看。",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    pi = sub.add_parser("init", help="初始化台账")
    pi.add_argument("--ledger", required=True)
    pi.add_argument("--project", required=True)
    pi.add_argument("--scope", default="")
    pi.add_argument("--force", action="store_true", help="覆盖已存在的台账")
    pi.set_defaults(func=cmd_init)

    pa = sub.add_parser("add", help="登记问题（自动分配编号）")
    pa.add_argument("--ledger", required=True)
    pa.add_argument("--prefix", required=True)
    pa.add_argument("--severity", required=True)
    pa.add_argument("--title", required=True)
    pa.add_argument("--location", default="")
    pa.add_argument("--module", default="")
    pa.add_argument("--status", default="待确认")
    pa.add_argument("--basis", default="", help="冲突基准")
    pa.add_argument("--fix", default="", help="最小修复方案")
    pa.add_argument("--impact", default="", help="影响范围")
    pa.add_argument("--note", default="")
    pa.add_argument("--id", default="", help="手动指定编号（默认自动）")
    pa.set_defaults(func=cmd_add)

    ps = sub.add_parser("set-status", help="更新问题状态")
    ps.add_argument("--ledger", required=True)
    ps.add_argument("--id", required=True)
    ps.add_argument("--status", required=True)
    ps.add_argument("--note", default="")
    ps.set_defaults(func=cmd_set_status)

    pv = sub.add_parser("set-severity", help="调整问题等级")
    pv.add_argument("--ledger", required=True)
    pv.add_argument("--id", required=True)
    pv.add_argument("--severity", required=True)
    pv.add_argument("--note", default="")
    pv.set_defaults(func=cmd_set_severity)

    pl = sub.add_parser("list", help="列出问题")
    pl.add_argument("--ledger", required=True)
    pl.add_argument("--status", default="")
    pl.add_argument("--severity", default="")
    pl.add_argument("--prefix", default="")
    pl.set_defaults(func=cmd_list)

    pm = sub.add_parser("summary", help="统计汇总")
    pm.add_argument("--ledger", required=True)
    pm.set_defaults(func=cmd_summary)

    pe = sub.add_parser("export-md", help="导出 Markdown 问题索引")
    pe.add_argument("--ledger", required=True)
    pe.add_argument("--out", default="")
    pe.set_defaults(func=cmd_export_md)

    pp = sub.add_parser("prefixes", help="查看可选前缀/状态/等级")
    pp.set_defaults(func=cmd_prefixes)

    return p


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
