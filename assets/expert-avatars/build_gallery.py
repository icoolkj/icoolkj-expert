"""生成 8 位专家头像展示页与总览图。

唯一数据源是 experts/<name>/.codebuddy-plugin/plugin.json 的 avatar 字段，
因此换头像 / 改文件名后，只要把 plugin.json 的 avatar 指过去，重跑本脚本即可刷新。

    python assets/expert-avatars/build_gallery.py

产物：
    gallery.html        自包含展示页：512 PNG 压成 320 JPEG 内联，无脚本、无外部依赖
    contact-sheet.png   4x2 总览图
"""
from __future__ import annotations

import base64
import html
import io
import json
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
EXPERTS = ROOT / "experts"
HERE = Path(__file__).resolve().parent

# 与 README「专家 ↔ Skill 映射关系」保持一致
BINDINGS = {
    "01": "S01、S10",
    "02": "S02",
    "03": "S03、S04",
    "04": "S05、S06",
    "05": "S07",
    "06": "S08",
    "07": "S09",
    "08": "S10",
}

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:"Microsoft YaHei","PingFang SC",system-ui,sans-serif;
background:linear-gradient(160deg,#eef3ff 0%,#f7f9ff 45%,#eaf0fb 100%);color:#1a2b5c;padding:48px 24px 64px}
.wrap{max-width:1180px;margin:0 auto}
h1{font-size:30px;letter-spacing:1px}
.lead{color:#5a6890;margin:12px 0 6px;font-size:15px;line-height:1.8}
.meta{color:#8a96b4;font-size:13px;margin-bottom:34px}
.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:20px}
.card{background:#fff;border-radius:20px;padding:22px 18px 20px;text-align:center;
box-shadow:0 8px 28px rgba(30,60,130,.09);border:1px solid #e6ecfa;
transition:transform .2s ease,box-shadow .2s ease}
.card:hover{transform:translateY(-5px);box-shadow:0 16px 38px rgba(30,60,130,.16)}
.photo{width:168px;height:168px;margin:0 auto 16px;border-radius:50%;overflow:hidden;
border:3px solid #dfe8ff;box-shadow:0 6px 18px rgba(40,80,180,.18)}
.photo img{width:100%;height:100%;object-fit:cover;display:block}
.code{display:inline-block;background:#123fcf;color:#fff;font-size:12px;font-weight:700;
letter-spacing:1px;padding:3px 11px;border-radius:20px;margin-bottom:9px}
.title{font-size:18px;font-weight:700;margin-bottom:3px}
.prof{font-size:12px;color:#7a86a8;margin-bottom:12px}
.dir{font-size:11px;color:#9aa6c2;font-family:Consolas,monospace;word-break:break-all;line-height:1.5}
.file{font-size:11px;color:#5a6890;margin-top:7px;word-break:break-all;line-height:1.5}
.skills{margin-top:13px;padding-top:12px;border-top:1px dashed #e2e9f8;font-size:12px;color:#123fcf;font-weight:700}
.dark{margin-top:44px;background:linear-gradient(135deg,#101f4a,#1c357a);border-radius:22px;padding:30px 28px 34px;color:#eaf0ff}
.dark h2{font-size:19px;margin-bottom:6px}
.dark p{font-size:13px;color:#a9bce8;margin-bottom:24px}
.row{display:grid;grid-template-columns:repeat(8,1fr);gap:14px}
.cell{text-align:center}
.cell img{width:100%;border-radius:50%;border:2px solid rgba(255,255,255,.25);display:block}
.cell span{display:block;font-size:12px;color:#c3d2f5;margin-top:8px}
table{width:100%;border-collapse:collapse;margin-top:40px;background:#fff;border-radius:16px;overflow:hidden;
box-shadow:0 8px 28px rgba(30,60,130,.08);font-size:13px}
th{background:#123fcf;color:#fff;text-align:left;padding:13px 16px;font-weight:600}
td{padding:12px 16px;border-bottom:1px solid #eef2fb;color:#33446e}
tr:last-child td{border-bottom:none}
td.mono{font-family:Consolas,monospace;font-size:12px;color:#5a6890}
.ok{display:inline-block;background:#e6f2ff;color:#123fcf;border-radius:6px;padding:2px 8px;font-size:11px;font-weight:700}
.foot{margin-top:26px;color:#8a96b4;font-size:12px;line-height:1.9}
@media(max-width:900px){.grid{grid-template-columns:repeat(2,1fr)}.row{grid-template-columns:repeat(4,1fr)}}
"""


def load_items() -> list[dict]:
    items = []
    for d in sorted(EXPERTS.iterdir()):
        cfg = json.loads((d / ".codebuddy-plugin" / "plugin.json").read_text(encoding="utf-8"))
        rel = cfg["avatar"]
        f = d / rel
        if not f.exists():
            raise FileNotFoundError(f"头像断链: {d.name} -> {rel}")
        code = f.stem.split("_", 1)[0]
        items.append({
            "code": code,
            "zh": cfg["displayName"]["zh"],
            "prof": cfg.get("profession", {}).get("zh", ""),
            "dir": d.name,
            "file": f.name,
            "path": f,
            "skills": BINDINGS.get(code, "—"),
        })
    items.sort(key=lambda x: x["code"])
    assert len(items) == 8, f"应有 8 位专家，实际 {len(items)}"
    assert len({i["code"] for i in items}) == 8, "编号重复"
    return items


@lru_cache(maxsize=None)
def thumb(path_str: str) -> str:
    """把 512 PNG 压成 320 JPEG 内联，让展示页单文件可用（原图不受影响）。"""
    im = Image.open(path_str).convert("RGB")
    im.thumbnail((320, 320), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=88, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


def build_html(items: list[dict]) -> str:
    cards = "".join(
        f'<div class="card"><div class="photo"><img src="{thumb(str(i["path"]))}" alt="{html.escape(i["zh"])}"></div>'
        f'<span class="code">{i["code"]}</span>'
        f'<div class="title">{html.escape(i["zh"])}</div>'
        f'<div class="prof">{html.escape(i["prof"])}</div>'
        f'<div class="dir">{i["dir"]}</div>'
        f'<div class="file">{html.escape(i["file"])}</div>'
        f'<div class="skills">绑定 {i["skills"]}</div></div>'
        for i in items
    )
    cells = "".join(
        f'<div class="cell"><img src="{thumb(str(i["path"]))}" alt=""><span>{i["code"]}</span></div>'
        for i in items
    )
    rows = "".join(
        f'<tr><td><b>{i["code"]}</b></td><td>{html.escape(i["zh"])}</td>'
        f'<td class="mono">{i["dir"]}</td><td>{html.escape(i["file"])}</td>'
        f'<td>{i["skills"]}</td><td><span class="ok">已关联</span></td></tr>'
        for i in items
    )
    return (
        '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>灵启逸梦 · 8 位专家头像</title><style>' + CSS + '</style></head><body><div class="wrap">'
        '<h1>灵启逸梦 · 8 位专家头像</h1>'
        '<p class="lead">官方头像按 01–08 编号与 8 位专家一一关联，'
        '<code>plugin.json</code> 的 <code>avatar</code> 字段直接指向带编号的文件名。</p>'
        '<p class="meta">512×512 PNG · 单张 350–410KB · 已同步到本机 my-experts 市场</p>'
        '<div class="grid">' + cards + '</div>'
        '<div class="dark"><h2>深色界面下的效果</h2>'
        '<p>圆形头像在深蓝底的专家列表中同样清晰，无白边残留。</p>'
        '<div class="row">' + cells + '</div></div>'
        '<table><thead><tr><th>编号</th><th>专家</th><th>目录</th><th>头像文件</th>'
        '<th>绑定 Skill</th><th>关联状态</th></tr></thead><tbody>' + rows + '</tbody></table>'
        '<p class="foot">数据源：<code>experts/&lt;name&gt;/.codebuddy-plugin/plugin.json</code> 的 '
        '<code>avatar</code> 字段。替换头像后更新该字段并重跑 '
        '<code>build_gallery.py</code>，展示页与总览图会一起刷新。<br>'
        '绑定 Skill 与 README「专家 ↔ Skill 映射关系」保持一致。</p>'
        '</div></body></html>'
    )


def build_sheet(items: list[dict]) -> Image.Image:
    cw, ch = 250, 258
    sheet = Image.new("RGB", (cw * 4, ch * 2), "#F2F5FC")
    dr = ImageDraw.Draw(sheet)
    f_title = ImageFont.truetype("C:/Windows/Fonts/msyhbd.ttc", 16)
    f_code = ImageFont.truetype("C:/Windows/Fonts/msyhbd.ttc", 15)
    f_dir = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 11)
    for n, i in enumerate(items):
        cx, cy = (n % 4) * cw, (n // 4) * ch
        dr.rounded_rectangle((cx + 8, cy + 8, cx + cw - 8, cy + ch - 8), radius=16, fill="white")
        im = Image.open(i["path"]).convert("RGB")
        im.thumbnail((176, 176), Image.LANCZOS)
        sheet.paste(im, (cx + (cw - im.width) // 2, cy + 18))
        dr.text((cx + 18, cy + 200), f'{i["code"]}  {i["zh"]}', font=f_title, fill="#1A2B5C")
        dr.text((cx + 18, cy + 228), i["dir"], font=f_dir, fill="#7A86A8")
    return sheet


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    items = load_items()
    (HERE / "gallery.html").write_text(build_html(items), encoding="utf-8")
    print("已生成 gallery.html")
    build_sheet(items).save(HERE / "contact-sheet.png")
    print("已生成 contact-sheet.png")
    for i in items:
        print(f'  {i["code"]}  {i["zh"]:<16} {i["file"]}')


if __name__ == "__main__":
    main()
