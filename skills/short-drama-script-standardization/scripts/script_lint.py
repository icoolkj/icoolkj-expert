#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""短剧剧本结构化体检工具（只读，不修改原稿）。

对 UTF-8 文本 / Markdown 剧本做确定性检查，输出可复核的问题清单，
用于配合 references/09-quality-check.md、10-issue-grading.md 做人工判定。

检查项：
  - 集标记、场次编号（重复 / 跳号 / 与集号不符）
  - 场景标题四要素缺失（时间 / 内外景 / 地点）
  - 人物行缺失、对白署名不在本场人物行
  - 疑似同一人物的多种署名（相似度初筛）
  - 疑似同一地点的不同写法
  - 空场、空台词
  - 标注括号不配对、成对标记（闪回 / 蒙太奇）未闭合
  - 半角/全角括号混用
  - 超长台词
  - 动作行混入景别运镜、英文技术参数

用法：
    python script_lint.py <剧本文件> [--format md|json] [--out 输出路径]
                            [--max-dialogue-len 120]
"""

import argparse
import difflib
import json
import re
import sys
from collections import Counter, OrderedDict

# ---------------------------------------------------------------- 正则

HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s*")
BOLD_RE = re.compile(r"^\s*(\*\*|__)(.+?)(\*\*|__)\s*$")
SEP_RE = re.compile(r"^\s*(?:[-*_]{3,}|={3,})\s*$")

EP_RE = re.compile(
    r"^\s*(?:第\s*([0-9]{1,3}|[一二三四五六七八九十百零]{1,4})\s*集|EP\s*0*([0-9]{1,3}))"
    r"\s*[:：.、]?\s*(.*)$",
    re.IGNORECASE,
)

SCENE_RE = re.compile(
    r"^\s*(?:场\s*)?([0-9]{1,3})\s*[-－—–]\s*([0-9]{1,3})\s*[、:：.]?\s*(.*)$"
)

CHAR_LINE_RE = re.compile(r"^\s*(?:人物|出场人物|角色|本场人物)\s*[:：]\s*(.*)$")

ACTION_RE = re.compile(r"^\s*[△▲▽▼]\s*(.*)$")

DIALOGUE_RE = re.compile(
    r"^\s*([\u4e00-\u9fa5A-Za-z][\u4e00-\u9fa5A-Za-z0-9·]{0,9})"
    r"\s*(?:[（(]([^）)]{0,40})[）)])?\s*[:：]\s*(.*)$"
)

NOTE_RE = re.compile(r"【([^】]{0,60})】")

SHOT_WORDS = (
    "特写", "近景", "中景", "全景", "远景", "大远景", "景别", "镜头", "机位",
    "推近", "推镜", "拉远", "拉开", "摇镜", "摇摄", "移镜", "跟拍", "俯拍",
    "仰拍", "过肩", "航拍", "空镜", "升格", "降格", "慢镜", "快切", "跳切",
)
PROMPT_HINT_RE = re.compile(r"[A-Za-z]{3,}[\s,][A-Za-z]{3,}")

TIME_WORDS = (
    "凌晨", "清晨", "清晨", "早晨", "早上", "上午", "中午", "下午", "傍晚",
    "黄昏", "傍晚", "夜晚", "深夜", "半夜", "日", "夜", "晨", "昼",
    "同日", "次日", "当日", "当天", "连续", "稍后", "片刻后", "同时",
    "回忆", "闪回", "梦境", "幻想", "未来", "过去",
)
TIME_ALIAS = {"日间": "日", "白天": "日", "晚上": "夜", "傍晚": "黄昏"}

INOUT_WORDS = ("内外", "内景", "外景", "内", "外", "INT./EXT.", "INT", "EXT")

META_KEYS = {
    "人物", "出场人物", "角色", "本场人物", "时间", "场景", "地点", "备注",
    "集", "集数", "场次", "标题", "项目", "项目名", "片名", "版本", "状态",
    "日期", "说明", "注", "附录", "摘要", "类型", "内外", "导演", "编剧",
    "分镜", "场号", "页码", "todo", "note", "summary",
}

VOICE_HINTS = ("OS", "VO", "画外", "旁白", "内心", "电话", "广播", "电视", "视频")

PSYCH_WORDS = (
    "心里", "内心", "心中", "暗自", "默默", "思绪", "感慨", "情绪",
    "难过", "伤心", "痛苦", "愤怒", "恐惧", "激动", "不舍", "纠结",
    "崩溃", "复杂", "五味杂陈", "百感交集", "心如", "回忆涌",
)

GROUP_SPEAKER_HINTS = (
    "旁白", "众人", "全体", "广播", "电视", "系统", "画外", "群演", "宾客",
    "记者", "观众", "众人", "大家",
)

CN_NUM = {"零": 0, "一": 1, "二": 2, "三": 3, "四": 4, "五": 5,
          "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}


def cn_to_int(text):
    """把 1-99 的中文数字转成整数，失败返回 None。"""
    if not text:
        return None
    if text.isdigit():
        return int(text)
    if text == "十":
        return 10
    if "十" in text:
        left, _, right = text.partition("十")
        tens = CN_NUM.get(left, 1) if left else 1
        ones = CN_NUM.get(right, 0) if right else 0
        return tens * 10 + ones
    if len(text) == 1:
        return CN_NUM.get(text)
    return None


# ---------------------------------------------------------------- 数据结构


class Scene:
    def __init__(self, line_no, ep_no, num, title, time_val, inout, place):
        self.line_no = line_no
        self.ep_no = ep_no
        self.num = num
        self.title = title
        self.time = time_val
        self.inout = inout
        self.place = place
        self.characters = []
        self.actions = 0
        self.dialogues = []          # (speaker, hint, body)
        self.notes = []
        self.raw_content_lines = 0

    @property
    def code(self):
        return "%s-%s" % (self.ep_no if self.ep_no is not None else "?", self.num)


class Linter:
    def __init__(self, text, max_dialogue_len=120):
        self.text = text
        self.lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
        self.max_dialogue_len = max_dialogue_len
        self.issues = []
        self.episodes = OrderedDict()   # ep_no -> {"title":..., "line":...}
        self.scenes = []
        self.speakers = Counter()
        self.speaker_hints = {}
        self.notes = Counter()
        self.half_paren = 0
        self.full_paren = 0

    # ------------------------------------------------------------ 工具

    def add(self, code, level, category, position, message, suggestion=""):
        self.issues.append({
            "code": code,
            "level": level,
            "category": category,
            "position": position,
            "message": message,
            "suggestion": suggestion,
        })

    @staticmethod
    def clean(line):
        s = HEADING_RE.sub("", line)
        m = BOLD_RE.match(s)
        if m:
            s = m.group(2)
        return s.strip()

    # ------------------------------------------------------------ 主流程

    def run(self):
        ep_no = None
        scene = None
        last_scene_num = {}
        pending_dialogue = None       # (speaker, hint, parts, scene, line_no)

        for idx, raw in enumerate(self.lines, 1):
            line = raw.rstrip()
            if SEP_RE.match(line):
                continue
            s = self.clean(line)
            if not s:
                pending_dialogue = self._flush_dialogue(pending_dialogue)
                continue

            # 集标记
            m = EP_RE.match(s)
            if m:
                pending_dialogue = self._flush_dialogue(pending_dialogue)
                num = m.group(1) or m.group(2)
                ep_no = cn_to_int(num) if num is not None else None
                title = (m.group(3) or "").strip()
                if ep_no is not None and ep_no not in self.episodes:
                    self.episodes[ep_no] = {"title": title, "line": idx}
                scene = None
                continue

            # 场次标题
            m = SCENE_RE.match(s)
            if m and s.count("：") == 0:
                pending_dialogue = self._flush_dialogue(pending_dialogue)
                num = int(m.group(2))
                rest = (m.group(3) or "").strip()
                scene = self._make_scene(idx, ep_no, num, rest)
                if ep_no is not None:
                    prev = last_scene_num.get(ep_no)
                    if prev is not None and num > prev + 1:
                        self.add(
                            "S04", "P2", "场次编号",
                            "第%d行 %s" % (idx, scene.code),
                            "场号跳号：上一场为 %s，本场为 %s" % (prev, num),
                            "补号，或在结构清单注明缺号原因",
                        )
                    last_scene_num[ep_no] = num
                self.scenes.append(scene)
                continue

            # 人物行
            m = CHAR_LINE_RE.match(s)
            if m:
                pending_dialogue = self._flush_dialogue(pending_dialogue)
                names = [x.strip() for x in re.split(r"[、,，/；;]", m.group(1)) if x.strip()]
                if scene is not None:
                    scene.characters.extend(names)
                continue

            # 动作行
            m = ACTION_RE.match(s)
            if m:
                pending_dialogue = self._flush_dialogue(pending_dialogue)
                body = m.group(1).strip()
                if scene is not None:
                    scene.actions += 1
                    scene.raw_content_lines += 1
                self._check_action(idx, scene, body)
                continue

            # 标注
            notes = NOTE_RE.findall(s)
            if notes:
                pending_dialogue = self._flush_dialogue(pending_dialogue)
                for n in notes:
                    kind = n.split("：")[0].split(":")[0].strip()
                    self.notes[kind] += 1
                if scene is not None:
                    scene.notes.extend(notes)
                    if not s.startswith("【切至"):
                        scene.raw_content_lines += 1
                continue

            # 对白
            m = DIALOGUE_RE.match(s)
            if m:
                name, hint, rest = m.group(1).strip(), (m.group(2) or "").strip(), m.group(3).strip()
                if name.lower() in META_KEYS:
                    if scene is not None:
                        scene.raw_content_lines += 1
                    continue
                pending_dialogue = self._flush_dialogue(pending_dialogue)
                body_parts = [rest] if rest else []
                half_paren = "(" in s and "（" not in s
                pending_dialogue = [name, hint, body_parts, scene, idx, half_paren]
                if scene is not None:
                    scene.raw_content_lines += 1
                continue

            # 其它文字：并入当前对白正文，或视为游离段落
            if pending_dialogue is not None:
                pending_dialogue[2].append(s)
            else:
                if scene is not None:
                    scene.raw_content_lines += 1

        self._flush_dialogue(pending_dialogue)

        self._check_structure()
        self._check_characters()
        self._check_places()
        self._check_notes()
        self._check_parens()
        return self

    def _make_scene(self, line_no, ep_no, num, rest):
        time_val, inout, place = None, None, None
        tokens = [t for t in re.split(r"[\s　]+", rest) if t]
        if tokens:
            in_idx = None
            for i, t in enumerate(tokens):
                if t in INOUT_WORDS or t.upper() in ("INT", "EXT", "INT./EXT."):
                    in_idx = i
                    break
            if in_idx is not None:
                inout = tokens[in_idx]
                before = tokens[:in_idx]
                after = tokens[in_idx + 1:]
                for t in reversed(before):
                    if t in TIME_WORDS or t in TIME_ALIAS:
                        time_val = TIME_ALIAS.get(t, t)
                        break
                place = "".join(after).strip() or None
            else:
                for t in tokens:
                    if t in TIME_WORDS or t in TIME_ALIAS:
                        time_val = TIME_ALIAS.get(t, t)
                        break
                place = rest
                if time_val:
                    place = rest.replace(time_val, "", 1).strip()
                place = place or None
        scene = Scene(line_no, ep_no, num, rest, time_val, inout, place)
        return scene

    def _flush_dialogue(self, pending):
        if not pending:
            return None
        name, hint, parts, scene, line_no, half_paren = pending
        body = "".join(p.strip() for p in parts if p.strip())
        self.speakers[name] += 1
        if hint:
            self.speaker_hints.setdefault(name, set()).add(hint)
            self._check_hint(hint, scene, line_no, half_paren)
        if scene is not None:
            scene.dialogues.append((name, hint, body))
            if name not in scene.characters and scene.characters:
                if not any(k in name for k in GROUP_SPEAKER_HINTS):
                    self.add(
                        "C03", "P1", "对白归属",
                        "第%d行 %s" % (line_no, scene.code),
                        "署名「%s」不在本场人物行（%s）中" % (name, "、".join(scene.characters)),
                        "确认是漏列人物，还是署名错误；补人物行或统一署名",
                    )
        if not body:
            self.add(
                "D02", "P1", "对白",
                "第%d行 %s" % (line_no, (scene.code if scene else "-")),
                "署名「%s」后无台词内容（空台词）" % name,
                "补「（沉默）」或改写为动作行，需作者确认",
            )
        elif len(body) > self.max_dialogue_len:
            self.add(
                "D03", "P3", "对白",
                "第%d行 %s" % (line_no, (scene.code if scene else "-")),
                "「%s」单条台词 %d 字，超过建议阈值 %d 字" % (name, len(body), self.max_dialogue_len),
                "建议按语义切分为多条（不改变语义），提交作者确认",
            )
        return None

    def _check_hint(self, hint, scene, line_no, half_paren=False):
        """检查对白表演提示（括号内容）。"""
        pos = "第%d行 %s" % (line_no, scene.code if scene else "-")
        if half_paren:
            self.add(
                "D08", "P2", "格式", pos,
                "表演提示使用半角括号",
                "统一为全角（）；英文缩写例外",
            )
        hit = [w for w in SHOT_WORDS if w in hint]
        if hit:
            self.add(
                "D04", "P1", "对白", pos,
                "表演提示含景别/运镜词：%s" % "、".join(hit),
                "提示只写语气、对象、伴随动作；镜头内容移入分镜或建议栏",
            )
        psych = [w for w in PSYCH_WORDS if w in hint]
        if psych:
            self.add(
                "D05", "P2", "对白", pos,
                "表演提示写的是心理活动：%s" % "、".join(psych),
                "改为可表演的外在表现，或保留原文并列建议，不得擅自替换",
            )
        if len(hint) > 12:
            self.add(
                "D06", "P3", "对白", pos,
                "表演提示 %d 字，偏长（建议 ≤12 字）" % len(hint),
                "过长说明写成了描述，考虑移入动作行（需作者确认）",
            )
        if hint and not re.search(r"[\u4e00-\u9fa5A-Za-z0-9]", hint):
            self.add("D07", "P3", "对白", pos, "表演提示内容为空或仅符号", "删除空括号")

    # ------------------------------------------------------------ 检查

    def _check_action(self, idx, scene, body):
        pos = "第%d行 %s" % (idx, scene.code if scene else "-")
        if not body:
            self.add("A01", "P1", "动作", pos, "动作行为空", "补动作内容或删除标记")
            return
        hit = [w for w in SHOT_WORDS if w in body]
        if hit:
            self.add(
                "A02", "P1", "动作", pos,
                "动作行混入景别/运镜词：%s" % "、".join(hit),
                "剥离到分镜或建议栏，标准剧本只保留可拍动作",
            )
        if PROMPT_HINT_RE.search(body):
            self.add(
                "A03", "P2", "动作", pos,
                "动作行疑似含英文技术参数/Prompt",
                "剥离至生成层文档，不留在标准剧本",
            )
        if not re.search(r"[\u4e00-\u9fa5]", body):
            self.add("A04", "P2", "动作", pos, "动作行不含中文，疑似非剧本内容", "核查是否误贴")

    def _check_structure(self):
        if not self.episodes:
            self.add("S01", "P0", "结构", "全稿", "未识别到集标记（第NN集 / EPxx）",
                     "补集标记，或确认该文件是否仅为片段")
        if not self.scenes:
            self.add("S02", "P0", "结构", "全稿", "未识别到场次标题（N-N 时间 内外 地点）",
                     "统一场次标题格式后重跑")

        seen = {}
        for sc in self.scenes:
            key = (sc.ep_no, sc.num)
            if key in seen:
                self.add(
                    "S03", "P0", "场次编号",
                    "第%d行 %s" % (sc.line_no, sc.code),
                    "场号重复：与第%d行 %s 相同" % (seen[key], sc.code),
                    "按出现顺序重排或加字母后缀（如 4A），记录修改依据",
                )
            else:
                seen[key] = sc.line_no

            if sc.time is None:
                self.add("S05", "P1", "场景标题", "第%d行 %s" % (sc.line_no, sc.code),
                         "场景标题缺时间（日/夜/晨/黄昏…）",
                         "可从上下文推定则补并注明依据，否则标【待确认：时间】")
            if sc.inout is None:
                self.add("S06", "P1", "场景标题", "第%d行 %s" % (sc.line_no, sc.code),
                         "场景标题缺内外景（内/外）",
                         "补内外景；直接影响灯光录音备案")
            if not sc.place:
                self.add("S07", "P1", "场景标题", "第%d行 %s" % (sc.line_no, sc.code),
                         "场景标题缺地点",
                         "补地点；原稿无则写【待确认：地点】，不得自拟")
            if not sc.characters:
                self.add("S08", "P1", "人物行", "第%d行 %s" % (sc.line_no, sc.code),
                         "本场缺人物行",
                         "按场中实际出场人物补「人物：A、B」，无法确定则标待确认")
            if sc.raw_content_lines == 0 and not sc.dialogues and sc.actions == 0:
                self.add("S09", "P0", "结构", "第%d行 %s" % (sc.line_no, sc.code),
                         "空场：仅有场次标题，无动作无对白无标注",
                         "报告作者，不得补写")

        # 集内场号顺序
        for ep_no in self.episodes:
            nums = [sc.num for sc in self.scenes if sc.ep_no == ep_no]
            if nums != sorted(nums):
                self.add("S10", "P2", "场次编号", "第%d集" % ep_no,
                         "场号出现顺序与大小不一致：%s" % "、".join(str(n) for n in nums),
                         "按阅读顺序重排场号，并同步结构清单")

    def _check_characters(self):
        names = sorted(self.speakers)
        if len(names) < 2:
            return
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                a, b = names[i], names[j]
                if a in GROUP_SPEAKER_HINTS or b in GROUP_SPEAKER_HINTS:
                    continue
                ratio = difflib.SequenceMatcher(None, a, b).ratio()
                short, long_ = (a, b) if len(a) <= len(b) else (b, a)
                if ratio >= 0.84 or (short in long_ and len(long_) - len(short) <= 2):
                    self.add(
                        "C05", "P2", "人物一致性", "全稿",
                        "疑似同一人物的不同署名：「%s」与「%s」（相似度 %.2f）" % (a, b, ratio),
                        "确认是否同一人：同一人则统一署名并建别名映射；不同人则补身份区分",
                    )

    def _check_places(self):
        places = sorted({sc.place for sc in self.scenes if sc.place})
        for i in range(len(places)):
            for j in range(i + 1, len(places)):
                a, b = places[i], places[j]
                ratio = difflib.SequenceMatcher(None, a, b).ratio()
                if ratio >= 0.85 and a != b:
                    self.add(
                        "S11", "P2", "场景一致性", "全稿",
                        "疑似同一地点的不同写法：「%s」与「%s」（相似度 %.2f）" % (a, b, ratio),
                        "统一为标准地点名，台词内的称呼可保留原样",
                    )

    def _check_notes(self):
        opens = self.text.count("【")
        closes = self.text.count("】")
        if opens != closes:
            self.add("N01", "P1", "标注", "全稿",
                     "标注括号不配对：【 %d 个，】 %d 个" % (opens, closes),
                     "逐条补齐闭合括号")
        for kind in ("闪回", "蒙太奇", "梦境"):
            starts = sum(v for k, v in self.notes.items() if k.startswith(kind) and "结束" not in k)
            ends = sum(v for k, v in self.notes.items() if k.startswith(kind) and "结束" in k)
            if starts != ends:
                self.add("N02", "P1", "标注", "全稿",
                         "成对标记【%s】未闭合：开始 %d 次，结束 %d 次" % (kind, starts, ends),
                         "补「【%s结束】」，或合并为单段标注" % kind)
        for kind, cnt in self.notes.items():
            if cnt >= 8:
                self.add("N03", "P3", "标注", "全稿",
                         "标注【%s】使用 %d 次，密度偏高" % (kind, cnt),
                         "核对是否可用动作/台词承担同类信息")

    def _check_parens(self):
        full = len(re.findall(r"[（）]", self.text))
        half = len(re.findall(r"[()]", self.text))
        if full and half:
            self.add("P01", "P2", "格式", "全稿",
                     "全角与半角括号混用：全角 %d 个，半角 %d 个" % (full, half),
                     "统一为全角（）；英文缩写与 URL 例外")

    # ------------------------------------------------------------ 输出

    def stats(self):
        dlg_total = sum(len(sc.dialogues) for sc in self.scenes)
        inner = sum(1 for sc in self.scenes if sc.inout and "内" in sc.inout)
        outer = sum(1 for sc in self.scenes if sc.inout and "外" in sc.inout)
        night = sum(1 for sc in self.scenes if sc.time and sc.time in ("夜", "深夜", "凌晨", "半夜"))
        return {
            "episodes": len(self.episodes),
            "scenes": len(self.scenes),
            "dialogues": dlg_total,
            "characters": len([n for n in self.speakers if n not in GROUP_SPEAKER_HINTS]),
            "inner": inner,
            "outer": outer,
            "night": night,
            "notes": sum(self.notes.values()),
        }

    def to_dict(self):
        levels = Counter(i["level"] for i in self.issues)
        return {
            "stats": self.stats(),
            "levels": dict(levels),
            "issues": self.issues,
            "speakers": [{"name": k, "lines": v, "hints": sorted(self.speaker_hints.get(k, []))}
                         for k, v in self.speakers.most_common()],
            "notes": dict(self.notes),
            "scenes": [{
                "code": sc.code, "line": sc.line_no, "time": sc.time,
                "inout": sc.inout, "place": sc.place,
                "characters": sc.characters,
                "actions": sc.actions, "dialogues": len(sc.dialogues),
                "notes": len(sc.notes),
            } for sc in self.scenes],
        }

    def to_markdown(self, source=""):
        st = self.stats()
        levels = Counter(i["level"] for i in self.issues)
        out = []
        out.append("# 剧本体检报告")
        out.append("")
        if source:
            out.append("源文件：`%s`" % source)
            out.append("")
        out.append("> 本报告由 `scripts/script_lint.py` 生成，仅做结构化检测，不修改原稿。")
        out.append("> 问题等级与处理方式仍需按 `references/10-issue-grading.md` 人工判定。")
        out.append("")
        out.append("## 1. 概览")
        out.append("")
        out.append("| 指标 | 数值 |")
        out.append("| --- | --- |")
        out.append("| 集数 | %d |" % st["episodes"])
        out.append("| 场次数 | %d |" % st["scenes"])
        out.append("| 对白条数 | %d |" % st["dialogues"])
        out.append("| 有署名角色 | %d |" % st["characters"])
        out.append("| 内景场次 / 外景场次 | %d / %d |" % (st["inner"], st["outer"]))
        out.append("| 夜戏场次 | %d |" % st["night"])
        out.append("| 标注条数 | %d |" % st["notes"])
        out.append("")
        out.append("## 2. 问题统计")
        out.append("")
        out.append("| 等级 | 数量 |")
        out.append("| --- | --- |")
        for lv in ("P0", "P1", "P2", "P3"):
            out.append("| %s | %d |" % (lv, levels.get(lv, 0)))
        out.append("")
        if not self.issues:
            out.append("未检出结构性问题。仍需人工完成 09-quality-check.md 中的判断项（人物关系、时间逻辑、信息揭示等）。")
            out.append("")

        for lv in ("P0", "P1", "P2", "P3"):
            group = [i for i in self.issues if i["level"] == lv]
            if not group:
                continue
            out.append("### %s（%d 条）" % (lv, len(group)))
            out.append("")
            out.append("| 编号 | 类别 | 位置 | 问题 | 建议 |")
            out.append("| --- | --- | --- | --- | --- |")
            for i in group:
                out.append("| %s | %s | %s | %s | %s |" % (
                    i["code"], i["category"], i["position"],
                    i["message"].replace("|", "／"), i["suggestion"].replace("|", "／"),
                ))
            out.append("")

        out.append("## 3. 人物署名统计")
        out.append("")
        out.append("| 署名 | 台词条数 | 声音提示 |")
        out.append("| --- | --- | --- |")
        for name, cnt in self.speakers.most_common():
            hints = "、".join(sorted(self.speaker_hints.get(name, []))) or "—"
            out.append("| %s | %d | %s |" % (name, cnt, hints))
        out.append("")

        if self.notes:
            out.append("## 4. 标注类型统计")
            out.append("")
            out.append("| 标注类型 | 次数 |")
            out.append("| --- | --- |")
            for k, v in sorted(self.notes.items(), key=lambda x: -x[1]):
                out.append("| 【%s】 | %d |" % (k, v))
            out.append("")

        out.append("## 5. 场次索引")
        out.append("")
        out.append("| 场号 | 行号 | 时间 | 内外 | 地点 | 人物 | 动作 | 对白 | 标注 |")
        out.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
        for sc in self.scenes:
            out.append("| %s | %d | %s | %s | %s | %s | %d | %d | %d |" % (
                sc.code, sc.line_no, sc.time or "—", sc.inout or "—", sc.place or "—",
                "、".join(sc.characters) or "—", sc.actions, len(sc.dialogues), len(sc.notes),
            ))
        out.append("")
        out.append("## 6. 使用建议")
        out.append("")
        out.append("1. P0/P1 逐条与 `assets/issue_report_template.md` 对齐后写入报告。")
        out.append("2. P2 中属纯格式的按 A 类直接修复并记入 `assets/change_log_template.md`。")
        out.append("3. 涉及人物关系、时间线、信息揭示的冲突，脚本无法判定，需按 `references/14-continuity-check.md` 人工核对。")
        out.append("4. 相似度提示（C05 / S11）只是初筛，必须人工确认，禁止直接合并。")
        out.append("")
        return "\n".join(out)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="短剧剧本结构化体检（只读，不修改原稿）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("script", help="剧本文件路径（UTF-8 文本或 Markdown）")
    parser.add_argument("--format", choices=["md", "json"], default="md", help="输出格式，默认 md")
    parser.add_argument("--out", help="输出文件路径，默认打印到标准输出")
    parser.add_argument("--max-dialogue-len", type=int, default=120, help="单条台词长度阈值，默认 120")
    args = parser.parse_args(argv)

    try:
        with open(args.script, "r", encoding="utf-8-sig") as f:
            text = f.read()
    except FileNotFoundError:
        sys.stderr.write("找不到文件：%s\n" % args.script)
        return 2
    except UnicodeDecodeError:
        sys.stderr.write("文件不是 UTF-8 编码，请先转换：%s\n" % args.script)
        return 2

    linter = Linter(text, max_dialogue_len=args.max_dialogue_len).run()

    if args.format == "json":
        content = json.dumps(linter.to_dict(), ensure_ascii=False, indent=2)
    else:
        content = linter.to_markdown(source=args.script)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(content)
        sys.stderr.write("报告已写入：%s\n" % args.out)
    else:
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
        sys.stdout.write(content + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
