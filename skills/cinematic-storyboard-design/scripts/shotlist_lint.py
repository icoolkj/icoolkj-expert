#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""镜头表体检工具（S07 影视分镜设计）

对镜头表做确定性检查，输出可复核的问题清单。只检查，不改稿。

支持输入：
  - CSV / TSV（首行为表头）
  - Markdown 表格（可含多张表，自动识别表头行）

表头可用中文字段名或英文字段键名。

用法：
  python shotlist_lint.py shotlist.csv
  python shotlist_lint.py shotlist.md --format json --out report.json
  python shotlist_lint.py shotlist.csv --strict
  python shotlist_lint.py shotlist.csv --ai      # 要求 visual_prompt 必填
"""

import argparse
import csv
import io
import json
import os
import re
import sys

# ---------- 字段定义 ----------

FIELD_ALIASES = {
    "shot_id": ["shot_id", "镜头编号", "镜号"],
    "episode": ["episode", "集数", "集"],
    "scene_id": ["scene_id", "所属场次", "场次", "场号"],
    "duration": ["duration", "预计时长", "时长"],
    "shot_function": ["shot_function", "镜头功能", "功能"],
    "shot_size": ["shot_size", "景别"],
    "camera_angle": ["camera_angle", "机位角度", "机位"],
    "composition": ["composition", "构图"],
    "camera_movement": ["camera_movement", "摄影机运动", "运镜"],
    "visual_description": ["visual_description", "画面描述", "画面"],
    "character_blocking": ["character_blocking", "人物调度", "调度"],
    "performance": ["performance", "表演要求", "表演"],
    "lighting": ["lighting", "光影", "光线"],
    "dialogue_audio": ["dialogue_audio", "对白和声音", "对白声音", "声音", "对白"],
    "transition": ["transition", "转场"],
    "continuity": ["continuity", "连续性要求", "连续性"],
    "visual_prompt": ["visual_prompt", "视觉提示", "视觉提示词", "提示词"],
    "notes": ["notes", "备注"],
}

REQUIRED = [
    "shot_id", "episode", "scene_id", "duration", "shot_function",
    "shot_size", "camera_angle", "composition", "camera_movement",
    "visual_description", "transition", "continuity",
]

# 有人物时才强制（用是否存在人物相关列来判定，这里仅提示）
CONDITIONAL = ["character_blocking", "performance", "lighting", "dialogue_audio"]

ENUMS = {
    "shot_function": ["建立", "推进", "揭示", "反应", "强调", "过渡", "停留"],
    "shot_size": ["大远景", "远景", "全景", "中全", "中景", "中近", "近景", "特写", "大特写"],
    "camera_angle": ["平视", "俯", "仰", "侧", "背", "主观", "过肩", "荷兰角"],
    "composition": ["三分", "中心", "对称", "框架", "遮挡", "引导线", "留白"],
    "camera_movement": ["固定", "推", "拉", "摇", "移", "跟", "升降", "手持", "组合"],
    "transition": ["切", "叠化", "淡入淡出", "划", "匹配剪辑", "硬切对撞", "黑场", "白场"],
}

ENUM_FUZZY_HINTS = {
    "shot_size": {"中近景": "中近", "中全景": "中全", "大特": "大特写", "中近景/近景": "中近"},
    "camera_angle": {"平": "平视", "俯拍": "俯", "仰拍": "仰", "侧拍": "侧", "背拍": "背"},
    "shot_function": {"情绪停留": "停留", "过渡镜": "过渡"},
}

PLACEHOLDER_OK = {"待确认", "待估", "-", "—", "无", "/"}
SHOT_ID_RE = re.compile(r"^(EP\d{1,3})-(SC\d{1,3})-SH(\d{1,3})([A-Z])?$", re.IGNORECASE)
DUR_RE = re.compile(r"^(\d+(?:\.\d+)?)s?$", re.IGNORECASE)
ABSTRACT_WORDS = ["氛围", "气氛", "情绪感", "感觉很", "充满", "弥漫", "仿佛", "似乎", "压抑感", "张力"]


class Issue:
    __slots__ = ("level", "code", "shot", "msg")

    def __init__(self, level, code, shot, msg):
        self.level = level
        self.code = code
        self.shot = shot
        self.msg = msg

    def as_dict(self):
        return {"level": self.level, "code": self.code, "shot": self.shot, "message": self.msg}


# ---------- 读取 ----------

def normalize_header(cell):
    c = (cell or "").strip().strip("*").strip().lower()
    for key, alts in FIELD_ALIASES.items():
        if c == key.lower() or c in [a.lower() for a in alts]:
            return key
    return c


def read_csv(text, delim):
    reader = csv.reader(io.StringIO(text), delimiter=delim)
    rows = [r for r in reader if any((c or "").strip() for c in r)]
    if not rows:
        return []
    header = [normalize_header(c) for c in rows[0]]
    out = []
    for r in rows[1:]:
        rec = {}
        for i, key in enumerate(header):
            rec[key] = (r[i] if i < len(r) else "").strip()
        out.append(rec)
    return out


def read_markdown(text):
    """解析 Markdown 表格，并按镜头编号跨表合并。

    模板默认把 18 个字段拆成表 A（技术参数）与表 B（内容执行），
    两张表共用 shot_id。若不合并，会误报"缺少列"与"字段为空"。
    """
    tables = []
    lines = text.splitlines()
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i].strip()
        if line.startswith("|") and i + 1 < n:
            nxt = lines[i + 1].strip()
            if re.match(r"^\|[\s:\-\|]+\|?$", nxt) and "-" in nxt:
                header = [normalize_header(c) for c in split_row(line)]
                rows = []
                i += 2
                while i < n and lines[i].strip().startswith("|"):
                    cells = split_row(lines[i].strip())
                    if any(c for c in cells):
                        rec = {}
                        for j, key in enumerate(header):
                            rec[key] = cells[j] if j < len(cells) else ""
                        if any(v for v in rec.values()):
                            rows.append(rec)
                    i += 1
                if rows:
                    tables.append((header, rows))
                continue
        i += 1

    if not tables:
        return []

    merged = {}
    order = []
    loose = []
    for header, rows in tables:
        has_id = "shot_id" in header
        table_seen = set()
        for rec in rows:
            sid = (rec.get("shot_id") or "").strip()
            if has_id and sid:
                if sid in table_seen:
                    # 同一张表内重复：保留为独立行，交给 DUP_ID 检出
                    loose.append(rec)
                    continue
                table_seen.add(sid)
                if sid not in merged:
                    merged[sid] = {"shot_id": sid}
                    order.append(sid)
                for k, v in rec.items():
                    if k == "shot_id":
                        continue
                    if v or k not in merged[sid]:
                        merged[sid][k] = v
            else:
                loose.append(rec)

    return [merged[s] for s in order] + loose


def split_row(line):
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return [c.strip() for c in s.split("|")]


def load(path):
    with open(path, "r", encoding="utf-8-sig", errors="replace") as f:
        text = f.read()
    ext = os.path.splitext(path)[1].lower()
    if ext in (".md", ".markdown"):
        return read_markdown(text)
    if ext == ".tsv":
        return read_csv(text, "\t")
    return read_csv(text, ",")


# ---------- 检查 ----------

def is_placeholder(v):
    v = (v or "").strip()
    return v == "" or v in PLACEHOLDER_OK or v.startswith("待确认") or v.startswith("待估")


def check(records, require_ai=False):
    issues = []
    if not records:
        issues.append(Issue("error", "EMPTY", "-", "未解析到任何镜头行，请检查表头与表格格式"))
        return issues, {}

    present = set()
    for rec in records:
        present.update(rec.keys())

    for key in REQUIRED:
        if key not in present:
            issues.append(Issue("error", "MISSING_COLUMN", "-", "缺少必需列：%s" % key))

    seen_ids = {}
    timed_scenes = {}
    prev_size = None
    size_run = 0
    prev_size_shot = None

    for idx, rec in enumerate(records, start=2):
        sid = (rec.get("shot_id") or "").strip()
        label = sid or ("第%d行" % idx)

        # 空行跳过
        if not any((v or "").strip() for v in rec.values()):
            continue

        # 必需字段空值
        for key in REQUIRED:
            if key in present and is_placeholder(rec.get(key)):
                if key == "shot_id":
                    issues.append(Issue("error", "EMPTY_SHOT_ID", label, "镜头编号为空"))
                else:
                    issues.append(Issue("warn", "EMPTY_FIELD", label, "字段为空或待填：%s" % key))

        # 编号格式
        m = SHOT_ID_RE.match(sid) if sid else None
        if sid and not m:
            issues.append(Issue("error", "BAD_ID_FORMAT", label,
                                "镜头编号格式应为 EP01-SC03-SH07，当前为 %s" % sid))
        if m:
            ep, sc = m.group(1).upper(), m.group(2).upper()
            rep_ep = (rec.get("episode") or "").strip().upper()
            rep_sc = (rec.get("scene_id") or "").strip().upper()
            if rep_ep and rep_ep != ep:
                issues.append(Issue("error", "ID_EP_MISMATCH", label,
                                    "编号中的集号 %s 与 episode 字段 %s 不一致" % (ep, rep_ep)))
            if rep_sc and rep_sc != sc:
                issues.append(Issue("error", "ID_SC_MISMATCH", label,
                                    "编号中的场号 %s 与 scene_id 字段 %s 不一致" % (sc, rep_sc)))

        # 重复编号
        if sid:
            if sid in seen_ids:
                issues.append(Issue("error", "DUP_ID", label,
                                    "镜头编号重复（首次出现于第 %d 行）" % seen_ids[sid]))
            else:
                seen_ids[sid] = idx

        # 时长
        dur = (rec.get("duration") or "").strip()
        if dur and not is_placeholder(dur):
            dm = DUR_RE.match(dur)
            if not dm:
                issues.append(Issue("warn", "BAD_DURATION", label,
                                    "时长格式应为 3.5s 或待估，当前为 %s" % dur))
            else:
                val = float(dm.group(1))
                if val <= 0:
                    issues.append(Issue("warn", "BAD_DURATION", label, "时长必须大于 0"))
                elif val > 30:
                    issues.append(Issue("warn", "LONG_SHOT", label,
                                        "单镜时长 %.1fs 偏长，确认是否为刻意长镜" % val))
                sc_key = (rec.get("scene_id") or ep or "-").strip() or "-"
                timed_scenes[sc_key] = timed_scenes.get(sc_key, 0.0) + val

        # 枚举
        for key, allowed in ENUMS.items():
            if key not in present:
                continue
            v = (rec.get(key) or "").strip()
            if is_placeholder(v):
                continue
            ok = any(v == a or v.startswith(a) for a in allowed)
            if not ok:
                hint = ""
                for bad, good in ENUM_FUZZY_HINTS.get(key, {}).items():
                    if bad in v:
                        hint = "（疑似应为“%s”）" % good
                        break
                issues.append(Issue("warn", "BAD_ENUM", label,
                                    "%s 使用了非规范值“%s”，允许值：%s%s"
                                    % (key, v, "/".join(allowed), hint)))

        # 连续性空话
        cont = (rec.get("continuity") or "").strip()
        if cont and cont in ("无", "-", "—", "/", "无特殊", "同上"):
            issues.append(Issue("info", "WEAK_CONTINUITY", label,
                                "continuity 内容过简（“%s”），建议写明需维持的具体状态" % cont))

        # 抽象词
        desc = (rec.get("visual_description") or "")
        hits = [w for w in ABSTRACT_WORDS if w in desc]
        if hits:
            issues.append(Issue("warn", "ABSTRACT_WORD", label,
                                "画面描述含抽象词：%s，建议改为可见信息" % "、".join(hits)))

        # 提示词
        vp = (rec.get("visual_prompt") or "").strip()
        if require_ai and is_placeholder(vp):
            issues.append(Issue("error", "MISSING_PROMPT", label,
                                "AI 衔接模式要求 visual_prompt 必填"))

        # 景别连排
        size = (rec.get("shot_size") or "").strip()
        if size and not is_placeholder(size):
            if size == prev_size:
                size_run += 1
                if size_run == 4:
                    issues.append(Issue("warn", "SIZE_RUN", label,
                                        "景别“%s”已连续出现 4 次（自 %s 起），建议跳变"
                                        % (size, prev_size_shot)))
            else:
                prev_size = size
                prev_size_shot = label
                size_run = 1
        else:
            prev_size, size_run, prev_size_shot = None, 0, None

        # 光影三要素粗检
        light = (rec.get("lighting") or "").strip()
        if light and not is_placeholder(light):
            missing = []
            if not re.search(r"左|右|上|下|顶|底|背|逆|侧|顺|窗|灯|光", light):
                missing.append("方向")
            if not re.search(r"比|:\d|1:\d|柔|硬", light):
                missing.append("明暗比或光质")
            if missing:
                issues.append(Issue("info", "LIGHT_INCOMPLETE", label,
                                    "光影描述缺少：%s" % "、".join(missing)))

    return issues, timed_scenes


# ---------- 输出 ----------

def summarize(records, timed_scenes):
    sizes, funcs, moves = {}, {}, 0
    total = 0
    for rec in records:
        s = (rec.get("shot_size") or "").strip()
        if s:
            sizes[s] = sizes.get(s, 0) + 1
        f = (rec.get("shot_function") or "").strip()
        if f:
            funcs[f] = funcs.get(f, 0) + 1
        mv = (rec.get("camera_movement") or "").strip()
        if mv and "固定" not in mv:
            moves += 1
        d = (rec.get("duration") or "").strip()
        dm = DUR_RE.match(d) if d else None
        if dm:
            total += float(dm.group(1))
    n = len(records)
    return {
        "shots": n,
        "total_duration_s": round(total, 1),
        "avg_duration_s": round(total / n, 2) if n else 0,
        "moving_shots": moves,
        "moving_ratio": round(moves / n * 100, 1) if n else 0,
        "shot_size_dist": sizes,
        "shot_function_dist": funcs,
        "scene_duration": {k: round(v, 1) for k, v in timed_scenes.items()},
    }


def render_md(issues, stats, src):
    errs = [i for i in issues if i.level == "error"]
    warns = [i for i in issues if i.level == "warn"]
    infos = [i for i in issues if i.level == "info"]
    out = []
    out.append("# 镜头表体检报告")
    out.append("")
    out.append("- 文件：%s" % src)
    out.append("- 镜头数：%d" % stats["shots"])
    out.append("- 总时长：%ss（平均 %ss/镜）" % (stats["total_duration_s"], stats["avg_duration_s"]))
    out.append("- 动镜：%d 个（%s%%）" % (stats["moving_shots"], stats["moving_ratio"]))
    out.append("- 问题：错误 %d ／ 警告 %d ／ 提示 %d" % (len(errs), len(warns), len(infos)))
    out.append("")

    def block(title, items):
        out.append("## %s（%d）" % (title, len(items)))
        out.append("")
        if not items:
            out.append("无。")
            out.append("")
            return
        out.append("| 位置 | 问题 | 说明 |")
        out.append("| --- | --- | --- |")
        for it in items:
            out.append("| %s | %s | %s |" % (it.shot, it.code, it.msg))
        out.append("")

    block("错误（必须处理）", errs)
    block("警告（建议处理）", warns)
    block("提示（可选优化）", infos)

    out.append("## 景别分布")
    out.append("")
    for k, v in sorted(stats["shot_size_dist"].items(), key=lambda x: -x[1]):
        out.append("- %s：%d" % (k, v))
    out.append("")
    out.append("## 功能分布")
    out.append("")
    for k, v in sorted(stats["shot_function_dist"].items(), key=lambda x: -x[1]):
        out.append("- %s：%d" % (k, v))
    out.append("")
    if len(stats["scene_duration"]) > 1:
        out.append("## 场次时长")
        out.append("")
        for k, v in stats["scene_duration"].items():
            out.append("- %s：%ss" % (k, v))
        out.append("")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description="镜头表体检（S07 影视分镜设计）")
    ap.add_argument("input", help="镜头表文件（.csv/.tsv/.md）")
    ap.add_argument("--format", choices=["md", "json"], default="md", help="输出格式")
    ap.add_argument("--out", help="输出文件路径（默认打印到标准输出）")
    ap.add_argument("--strict", action="store_true", help="有警告也返回非零退出码")
    ap.add_argument("--ai", action="store_true", help="AI 衔接模式：visual_prompt 必填")
    args = ap.parse_args()

    if not os.path.exists(args.input):
        sys.stderr.write("文件不存在：%s\n" % args.input)
        return 2

    records = load(args.input)
    issues, timed = check(records, require_ai=args.ai)
    stats = summarize(records, timed)

    if args.format == "json":
        payload = {
            "file": os.path.abspath(args.input),
            "stats": stats,
            "issues": [i.as_dict() for i in issues],
            "counts": {
                "error": sum(1 for i in issues if i.level == "error"),
                "warn": sum(1 for i in issues if i.level == "warn"),
                "info": sum(1 for i in issues if i.level == "info"),
            },
        }
        text = json.dumps(payload, ensure_ascii=False, indent=2)
    else:
        text = render_md(issues, stats, args.input)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text + "\n")
        sys.stderr.write("已写入 %s\n" % args.out)
    else:
        sys.stdout.write(text + "\n")

    errs = sum(1 for i in issues if i.level == "error")
    warns = sum(1 for i in issues if i.level == "warn")
    if errs:
        return 1
    if args.strict and warns:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
