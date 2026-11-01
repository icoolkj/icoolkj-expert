#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""story_state.py —— 长篇小说创作台账

维护 novel/story-state.json：章节索引、人物当前状态、伏笔台账、待解决问题。
只记录正文中实际发生的事，不记录计划。

用法：
    python story_state.py init    --dir ./novel --title "书名" --genre "玄幻" --pov "第三人称限知"
    python story_state.py chapter --dir ./novel --no 12 --title "夜渡" \
        --summary "苏瑾夜渡，船夫死，匣子在身" \
        --chars "苏瑾:右臂伤重,河心|船夫:死" \
        --events "巡夜队封锁渡口;船夫认出匣子" \
        --fore-add "巡夜队受谁指使" --fore-close "FORE-004" \
        --open "陆沉下落"
    python story_state.py status --dir ./novel
    python story_state.py brief  --dir ./novel
    python story_state.py fore   --dir ./novel --stale 20
"""

import argparse
import io
import json
import os
import sys
from datetime import datetime

STATE_FILE = "story-state.json"


# ---------------------------------------------------------------- 基础工具

def _fix_stdout():
    """Windows 控制台默认非 UTF-8，统一改成 UTF-8，失败则忽略。"""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            try:
                sys.stdout = io.TextIOWrapper(stream.buffer, encoding="utf-8", errors="replace")
            except Exception:
                pass


def state_path(target_dir):
    return os.path.join(target_dir, STATE_FILE)


def load(target_dir):
    path = state_path(target_dir)
    if not os.path.exists(path):
        fail("未找到台账：%s\n请先运行 init。" % path)
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def save(target_dir, data):
    data["meta"]["updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    path = state_path(target_dir)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def fail(msg):
    print("[错误] " + msg, file=sys.stderr)
    sys.exit(1)


def split_list(raw, sep):
    """把 'a;b;c' 拆成列表，去空。"""
    if not raw:
        return []
    return [x.strip() for x in raw.split(sep) if x.strip()]


def parse_chars(raw):
    """'苏瑾:右臂伤重,河心|陆沉:失踪' -> {name: status}"""
    result = {}
    for item in split_list(raw, "|"):
        if ":" in item or "：" in item:
            item = item.replace("：", ":")
            name, _, status = item.partition(":")
            name, status = name.strip(), status.strip()
        else:
            name, status = item, ""
        if name:
            result[name] = status
    return result


def next_fore_id(data):
    nums = []
    for key in data.get("foreshadow", {}):
        digits = "".join(ch for ch in key if ch.isdigit())
        if digits:
            nums.append(int(digits))
    return "FORE-%03d" % (max(nums) + 1 if nums else 1)


def resolve_fore(data, token):
    """按编号或描述片段查找伏笔，返回 key。"""
    table = data.get("foreshadow", {})
    token = token.strip()
    if token in table:
        return token
    upper = token.upper()
    if upper in table:
        return upper
    for key, item in table.items():
        if token and token in item.get("desc", ""):
            return key
    return None


# ---------------------------------------------------------------- 命令实现

def cmd_init(args):
    target = args.dir
    os.makedirs(target, exist_ok=True)
    path = state_path(target)
    if os.path.exists(path) and not args.force:
        fail("台账已存在：%s\n如需覆盖请加 --force。" % path)

    data = {
        "meta": {
            "title": args.title or "未命名",
            "genre": args.genre or "",
            "pov": args.pov or "",
            "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "updated": "",
            "last_chapter": 0,
            "total_chapters": 0,
        },
        "chapters": [],
        "characters": {},
        "foreshadow": {},
        "open_questions": [],
    }
    save(target, data)
    print("已创建台账：%s" % path)
    print("书名：%s｜题材：%s｜视角：%s" % (data["meta"]["title"], data["meta"]["genre"] or "—", data["meta"]["pov"] or "—"))
    print("下一步：写完一章后运行 chapter 命令追加记录。")


def cmd_chapter(args):
    data = load(args.dir)
    no = int(args.no)
    if any(ch["no"] == no for ch in data["chapters"]):
        fail("第 %d 章已存在。如需修改请先手动编辑 %s。" % (no, state_path(args.dir)))

    time_note = args.time or ""
    chars = parse_chars(args.chars)
    events = split_list(args.events, ";")
    opened = split_list(args.open, ";")

    record = {
        "no": no,
        "title": args.title or "",
        "summary": args.summary or "",
        "time": time_note,
        "loc": args.loc or "",
        "events": events,
        "chars": chars,
        "word_count": int(args.words) if args.words else None,
        "recorded": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    data["chapters"].append(record)
    data["chapters"].sort(key=lambda c: c["no"])

    for name, status in chars.items():
        entry = data["characters"].setdefault(name, {"status": "", "last_chapter": 0, "history": []})
        entry["status"] = status
        entry["last_chapter"] = no
        entry["history"].append({"chapter": no, "status": status})

    for desc in (args.fore_add or []):
        key = next_fore_id(data)
        data["foreshadow"][key] = {
            "desc": desc.strip(),
            "planted": no,
            "reminders": [],
            "planned": None,
            "status": "open",
            "closed_at": None,
        }
        print("  新增伏笔 %s：%s" % (key, desc))

    for token in (args.fore_close or []):
        key = resolve_fore(data, token)
        if not key:
            print("  [提示] 未找到伏笔「%s」，已跳过。" % token)
            continue
        data["foreshadow"][key]["status"] = "closed"
        data["foreshadow"][key]["closed_at"] = no
        print("  回收伏笔 %s：%s" % (key, data["foreshadow"][key]["desc"]))

    for token in (args.fore_note or []):
        key = resolve_fore(data, token)
        if not key:
            print("  [提示] 未找到伏笔「%s」，已跳过。" % token)
            continue
        data["foreshadow"][key]["reminders"].append(no)
        print("  提醒伏笔 %s（第 %d 章）" % (key, no))

    for question in opened:
        data["open_questions"].append({"q": question, "chapter": no, "closed": False})

    for token in (args.resolve or []):
        hit = False
        for item in data["open_questions"]:
            if not item["closed"] and token in item["q"]:
                item["closed"] = True
                item["closed_chapter"] = no
                hit = True
        if not hit:
            print("  [提示] 未找到待解决问题「%s」，已跳过。" % token)

    data["meta"]["last_chapter"] = max(data["meta"]["last_chapter"], no)
    data["meta"]["total_chapters"] = len(data["chapters"])
    save(args.dir, data)

    print("已记录 CH-%04d《%s》" % (no, record["title"] or "无题"))
    if events:
        print("  事件：%s" % "；".join(events))
    if chars:
        print("  人物：%s" % "；".join("%s（%s）" % (k, v or "—") for k, v in chars.items()))
    open_count = sum(1 for f in data["foreshadow"].values() if f["status"] == "open")
    q_count = sum(1 for q in data["open_questions"] if not q["closed"])
    print("  在途伏笔 %d 条｜未解决问题 %d 条" % (open_count, q_count))


def cmd_status(args):
    data = load(args.dir)
    meta = data["meta"]
    chapters = data["chapters"]
    print("=" * 52)
    print("《%s》｜%s｜%s" % (meta["title"], meta["genre"] or "未标题材", meta["pov"] or "未标视角"))
    print("=" * 52)
    if not chapters:
        print("尚无章节记录。")
        return
    words = sum(c["word_count"] or 0 for c in chapters)
    print("进度：%d 章｜%s 字｜最后更新 %s" % (
        len(chapters),
        ("%d" % words) if words else "未统计",
        meta.get("updated", "—"),
    ))
    last = chapters[-1]
    print("最新：CH-%04d《%s》%s" % (last["no"], last["title"], ("　" + last["time"]) if last["time"] else ""))
    if last["summary"]:
        print("       %s" % last["summary"])

    print("\n-- 人物当前状态 --")
    if data["characters"]:
        for name, item in sorted(data["characters"].items(), key=lambda kv: -kv[1]["last_chapter"]):
            print("  %-6s %-22s （最后出现 CH-%04d）" % (name, item["status"] or "—", item["last_chapter"]))
    else:
        print("  无记录")

    print("\n-- 未解决问题 --")
    pending = [q for q in data["open_questions"] if not q["closed"]]
    if pending:
        for item in pending:
            print("  · %s（CH-%04d 起）" % (item["q"], item["chapter"]))
    else:
        print("  无")

    print("\n-- 伏笔 --")
    table = data["foreshadow"]
    open_fore = {k: v for k, v in table.items() if v["status"] == "open"}
    closed_fore = {k: v for k, v in table.items() if v["status"] == "closed"}
    print("  在途 %d 条｜已收 %d 条" % (len(open_fore), len(closed_fore)))
    for key, item in sorted(open_fore.items()):
        last_touch = max([item["planted"]] + item["reminders"])
        age = meta["last_chapter"] - last_touch
        flag = "  <注意>" if age >= 20 else ""
        print("  %-9s 埋 CH-%04d｜提醒 %s｜已 %d 章未触碰%s  %s" % (
            key, item["planted"],
            ",".join("CH-%04d" % r for r in item["reminders"]) or "无",
            age, flag, item["desc"],
        ))


def cmd_brief(args):
    data = load(args.dir)
    meta = data["meta"]
    chapters = data["chapters"]
    if not chapters:
        fail("尚无章节记录，无法生成承接单。")
    last = chapters[-1]
    nxt = last["no"] + 1

    print("## 下一章承接单｜CH-%04d" % nxt)
    print("作品：《%s》" % meta["title"])
    print()
    print("### 此刻局面")
    print(last["summary"] or "（上一章未写摘要，请补）")
    if last["time"] or last["loc"]:
        print("时间/地点：%s｜%s" % (last["time"] or "—", last["loc"] or "—"))
    print()
    print("### 人物状态")
    if data["characters"]:
        for name, item in sorted(data["characters"].items(), key=lambda kv: -kv[1]["last_chapter"]):
            print("- %s：%s" % (name, item["status"] or "—"))
    else:
        print("- （未记录）")
    print()
    print("### 上一章事件")
    if last["events"]:
        for event in last["events"]:
            print("- %s" % event)
    else:
        print("- （未记录）")
    print()
    print("### 未解决冲突")
    pending = [q for q in data["open_questions"] if not q["closed"]]
    if pending:
        for item in pending:
            print("- %s（CH-%04d 起）" % (item["q"], item["chapter"]))
    else:
        print("- （无，可考虑新开冲突）")
    print()
    print("### 在途伏笔（可承接的）")
    open_fore = {k: v for k, v in data["foreshadow"].items() if v["status"] == "open"}
    if open_fore:
        for key, item in sorted(open_fore.items()):
            age = meta["last_chapter"] - max([item["planted"]] + item["reminders"])
            print("- %s %s（埋 CH-%04d，已 %d 章）" % (key, item["desc"], item["planted"], age))
    else:
        print("- （无）")
    print()
    print("### 动笔前须确认")
    print("1. 本章的核心目标是什么？（写到可失败）")
    print("2. 本章的不可逆变化是什么？（写不出就删掉本章）")
    print("3. 哪些信息本章不得提前揭露？")


def cmd_fore(args):
    data = load(args.dir)
    meta = data["meta"]
    table = data["foreshadow"]
    if not table:
        print("尚无伏笔记录。")
        return
    rows = []
    for key, item in sorted(table.items()):
        last_touch = max([item["planted"]] + item["reminders"])
        age = meta["last_chapter"] - last_touch
        rows.append((key, item, age))
    if args.stale:
        rows = [r for r in rows if r[1]["status"] == "open" and r[2] >= args.stale]
        if not rows:
            print("没有超过 %d 章未触碰的在途伏笔。" % args.stale)
            return
        print("超过 %d 章未触碰的在途伏笔：" % args.stale)
    for key, item, age in rows:
        state = "在途" if item["status"] == "open" else "已收(CH-%04d)" % (item["closed_at"] or 0)
        print("  %-9s [%s] 埋 CH-%04d｜提醒 %s｜%d 章未触碰｜%s" % (
            key, state, item["planted"],
            ",".join("CH-%04d" % r for r in item["reminders"]) or "无",
            age, item["desc"],
        ))
    if not args.stale:
        overdue = [r for r in rows if r[1]["status"] == "open" and r[2] >= 40]
        if overdue:
            print("\n建议处理（≥40 章未触碰）：%s" % "、".join(r[0] for r in overdue))


# ---------------------------------------------------------------- 入口

def build_parser():
    parser = argparse.ArgumentParser(description="长篇小说创作台账")
    sub = parser.add_subparsers(dest="command")

    p_init = sub.add_parser("init", help="初始化台账")
    p_init.add_argument("--dir", default="./novel", help="项目目录，默认 ./novel")
    p_init.add_argument("--title", default="", help="书名")
    p_init.add_argument("--genre", default="", help="题材")
    p_init.add_argument("--pov", default="", help="叙事视角")
    p_init.add_argument("--force", action="store_true", help="覆盖已有台账")
    p_init.set_defaults(func=cmd_init)

    p_ch = sub.add_parser("chapter", help="追加一章记录")
    p_ch.add_argument("--dir", default="./novel")
    p_ch.add_argument("--no", required=True, help="章节号")
    p_ch.add_argument("--title", default="", help="章名")
    p_ch.add_argument("--summary", default="", help="三句摘要：发生了什么/改变了什么/留下了什么")
    p_ch.add_argument("--time", default="", help="故事内时间，如 D0 子时—寅时")
    p_ch.add_argument("--loc", default="", help="地点")
    p_ch.add_argument("--chars", default="", help="人物状态：'苏瑾:右臂伤|陆沉:失踪'")
    p_ch.add_argument("--events", default="", help="重要事件，分号分隔")
    p_ch.add_argument("--words", default="", help="本章字数")
    p_ch.add_argument("--fore-add", action="append", help="新增伏笔（可多次）")
    p_ch.add_argument("--fore-close", action="append", help="回收伏笔：编号或描述片段（可多次）")
    p_ch.add_argument("--fore-note", action="append", help="提醒伏笔（可多次）")
    p_ch.add_argument("--open", default="", help="新增未解决问题，分号分隔")
    p_ch.add_argument("--resolve", action="append", help="关闭未解决问题：关键词（可多次）")
    p_ch.set_defaults(func=cmd_chapter)

    p_st = sub.add_parser("status", help="查看进度、人物状态、伏笔")
    p_st.add_argument("--dir", default="./novel")
    p_st.set_defaults(func=cmd_status)

    p_br = sub.add_parser("brief", help="生成下一章承接单")
    p_br.add_argument("--dir", default="./novel")
    p_br.set_defaults(func=cmd_brief)

    p_fo = sub.add_parser("fore", help="查看伏笔台账")
    p_fo.add_argument("--dir", default="./novel")
    p_fo.add_argument("--stale", type=int, default=0, help="只列出 ≥N 章未触碰的在途伏笔")
    p_fo.set_defaults(func=cmd_fore)

    return parser


def main():
    _fix_stdout()
    parser = build_parser()
    args = parser.parse_args()
    if not getattr(args, "func", None):
        parser.print_help()
        return
    args.func(args)


if __name__ == "__main__":
    main()
