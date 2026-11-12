"""生成 10 枚正式核心 Skill 图标及 2 枚备用图标，统一采用项目蓝色渐变图形规范。历史参考海报仅作为内部设计记录，不作为商业交付素材。

不做位图抠图：直接生成 SVG，再由本机 Chrome 无头渲染导出透明 PNG。
用法：
    python assets/skill-icons/build_icons.py

输出：
    assets/skill-icons/svg/Sxx-*.svg       12 枚矢量源文件
    assets/skill-icons/Sxx-*.png          256x256 透明 PNG（由 SVG 渲染）
    assets/skill-icons/contact-sheet.png  12 宫格总览
    skills/<name>/icon.svg + icon.png     S01-S10 对应技能各一套
"""

from __future__ import annotations

import math
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SVG_DIR = HERE / "svg"
CHROME = Path("C:/Program Files/Google/Chrome/Application/chrome.exe")

# 统一图形语言：64x64 画布、蓝色竖向渐变、深蓝描边、白色内部细节
DEFS = """<defs>
  <linearGradient id="b" x1="0" y1="0" x2="0.25" y2="1">
    <stop offset="0" stop-color="#57A0FF"/>
    <stop offset="0.5" stop-color="#2D6BEF"/>
    <stop offset="1" stop-color="#123FCF"/>
  </linearGradient>
  <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#FFDC5C"/>
    <stop offset="1" stop-color="#F59E0B"/>
  </linearGradient>
</defs>"""
STROKE = '#0E3BB8'

# 编号 → (英文短名, 中文名, SVG 内容, 对应技能目录名)
ICONS = [
    ("S01", "project-planning", "项目规划", """
<rect x="11" y="12" width="36" height="45" rx="5" fill="url(#b)" stroke="S" stroke-width="2.6"/>
<rect x="23" y="7" width="13" height="9" rx="3" fill="#EAF2FF" stroke="S" stroke-width="2.6"/>
<g stroke="#FFFFFF" stroke-width="3" stroke-linecap="round">
  <line x1="19" y1="26" x2="38" y2="26"/><line x1="19" y1="34" x2="38" y2="34"/><line x1="19" y1="42" x2="31" y2="42"/>
</g>
<circle cx="47" cy="47" r="10.5" fill="#FFFFFF" stroke="S" stroke-width="2.6"/>
<path d="M42 47.5 l3.5 3.5 l6.5 -7" fill="none" stroke="#1747D6" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/>
""", "original-ip-project-planning"),

    ("S02", "worldbuilding", "世界观构建", """
<circle cx="32" cy="32" r="23" fill="url(#b)" stroke="S" stroke-width="2.6"/>
<g fill="none" stroke="#FFFFFF" stroke-width="2" opacity="0.92">
  <ellipse cx="32" cy="32" rx="10" ry="23"/>
  <line x1="9" y1="32" x2="55" y2="32"/>
  <path d="M13.5 20 Q32 28 50.5 20"/><path d="M13.5 44 Q32 36 50.5 44"/>
</g>
<path d="M20 17 l7 -2 4 4 -1 6 -7 1 -4 -5z" fill="#FFFFFF" opacity="0.95"/>
<path d="M36 36 l8 -2 5 5 -3 7 -8 -1 -3 -5z" fill="#FFFFFF" opacity="0.95"/>
""", "story-worldbuilding"),

    ("S03", "novel-writing", "小说创作", """
<path d="M52 7 C34 11 20 24 16 40 L13 50 L23 47 C39 43 51 29 52 7 Z" fill="url(#b)" stroke="S" stroke-width="2.6" stroke-linejoin="round"/>
<path d="M16 40 Q30 28 45 14" fill="none" stroke="#FFFFFF" stroke-width="2.6" stroke-linecap="round"/>
<g stroke="#FFFFFF" stroke-width="1.9" opacity="0.85" stroke-linecap="round">
  <line x1="27" y1="31" x2="22" y2="25"/><line x1="33" y1="26" x2="29" y2="19"/>
  <line x1="39" y1="21" x2="37" y2="14"/><line x1="24" y1="37" x2="19" y2="33"/>
</g>
<path d="M9 55 Q22 50 35 55" fill="none" stroke="#1747D6" stroke-width="3.4" stroke-linecap="round"/>
""", "ai-novel-writing-studio"),

    ("S04", "chapter-continuation", "章节续写", """
<rect x="9" y="8" width="35" height="47" rx="5" fill="url(#b)" stroke="S" stroke-width="2.6"/>
<path d="M34 8 v8 a3 3 0 0 0 3 3 h7" fill="#EAF2FF" stroke="S" stroke-width="2.2" stroke-linejoin="round"/>
<g stroke="#FFFFFF" stroke-width="3" stroke-linecap="round">
  <line x1="17" y1="28" x2="36" y2="28"/><line x1="17" y1="36" x2="34" y2="36"/><line x1="17" y1="44" x2="27" y2="44"/>
</g>
<circle cx="47" cy="44" r="10.5" fill="#FFFFFF" stroke="S" stroke-width="2.6"/>
<path d="M42 42 a5.5 5.5 0 0 1 9 -3" fill="none" stroke="#1747D6" stroke-width="2.8" stroke-linecap="round"/>
<path d="M52 46 a5.5 5.5 0 0 1 -9 3" fill="none" stroke="#1747D6" stroke-width="2.8" stroke-linecap="round"/>
<path d="M50 36.5 v3.2 h-3.2" fill="none" stroke="#1747D6" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>
""", "novel-continuity-and-continuation"),

    ("S05", "novel-to-shortdrama", "小说→短剧", """
<rect x="8" y="10" width="48" height="44" rx="10" fill="url(#b)" stroke="S" stroke-width="2.6"/>
<rect x="12" y="14" width="40" height="36" rx="7" fill="none" stroke="#FFFFFF" stroke-width="1.6" opacity="0.45"/>
<path d="M27 22 L44 32 L27 42 Z" fill="#FFFFFF" stroke="#EAF2FF" stroke-width="1" stroke-linejoin="round"/>
""", "ai-short-drama-adaptation-studio"),

    ("S06", "screenplay", "短剧剧本", """
<path d="M8 21 L14 8 H56 L50 21 Z" fill="url(#b)" stroke="S" stroke-width="2.6" stroke-linejoin="round"/>
<g stroke="#FFFFFF" stroke-width="3.2" stroke-linecap="round">
  <line x1="21" y1="9" x2="17" y2="20"/><line x1="33" y1="9" x2="29" y2="20"/><line x1="45" y1="9" x2="41" y2="20"/>
</g>
<rect x="8" y="21" width="48" height="33" rx="5" fill="url(#b)" stroke="S" stroke-width="2.6"/>
<line x1="8" y1="28" x2="56" y2="28" stroke="#FFFFFF" stroke-width="2.6"/>
<line x1="18" y1="40" x2="46" y2="40" stroke="#FFFFFF" stroke-width="3.2" stroke-linecap="round"/>
""", "short-drama-script-standardization"),

    ("S07", "storyboard", "分镜脚本", """
<rect x="22" y="7" width="12" height="7" rx="2.5" fill="url(#b)" stroke="S" stroke-width="2.4"/>
<rect x="7" y="12" width="50" height="43" rx="6" fill="url(#b)" stroke="S" stroke-width="2.6"/>
<rect x="13" y="20" width="21" height="17" rx="2" fill="#FFFFFF"/>
<circle cx="19" cy="25" r="2.4" fill="#4C8DFF"/>
<path d="M13 35 l6 -7 4.5 4.5 3.5 -3.5 7 6 v2 h-21z" fill="#9CC2FF"/>
<g stroke="#FFFFFF" stroke-width="3" stroke-linecap="round">
  <line x1="39" y1="24" x2="51" y2="24"/><line x1="39" y1="31" x2="51" y2="31"/>
  <line x1="13" y1="45" x2="51" y2="45"/>
</g>
""", "cinematic-storyboard-design"),

    ("S08", "visual-assets", "视效素材", """
<rect x="20" y="7" width="37" height="33" rx="5" fill="#8DB8FF" stroke="S" stroke-width="2.6"/>
<rect x="7" y="20" width="41" height="37" rx="5" fill="url(#b)" stroke="S" stroke-width="2.6"/>
<circle cx="18" cy="31" r="4" fill="#FFFFFF"/>
<path d="M8 53 l13 -15 8 8 6 -6 12 13 v2 h-39z" fill="#C6DEFF"/>
""", "ai-character-environment-asset-design"),

    ("S09", "logic-review", "逻辑审核", """
<path d="M32 6 L52 13 V30 C52 43 43 52 32 58 C21 52 12 43 12 30 V13 Z" fill="url(#b)" stroke="S" stroke-width="2.6" stroke-linejoin="round"/>
<path d="M22 31 l8 8 l14 -15" fill="none" stroke="#FFFFFF" stroke-width="5.2" stroke-linecap="round" stroke-linejoin="round"/>
""", "story-logic-and-continuity-review"),

    ("S10", "ip-operations", "IP运营", """
<g fill="url(#b)" stroke="S" stroke-width="2.2">
  <rect x="10" y="38" width="10" height="19" rx="2"/><rect x="25" y="30" width="10" height="27" rx="2"/><rect x="40" y="22" width="10" height="35" rx="2"/>
</g>
<path d="M10 26 L24 18 L36 23 L51 8" fill="none" stroke="#1747D6" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M43 8 h9 v9" fill="none" stroke="#1747D6" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round"/>
""", "ip-commercial-operations-planning"),

    ("S11", "data-analysis", "数据分析", """
<rect x="9" y="9" width="36" height="47" rx="5" fill="url(#b)" stroke="S" stroke-width="2.6"/>
<rect x="19" y="5" width="16" height="8" rx="3" fill="#EAF2FF" stroke="S" stroke-width="2.4"/>
<g stroke="#FFFFFF" stroke-width="3" stroke-linecap="round">
  <line x1="17" y1="25" x2="37" y2="25"/><line x1="17" y1="33" x2="37" y2="33"/><line x1="17" y1="41" x2="29" y2="41"/>
</g>
<circle cx="46" cy="44" r="9" fill="#FFFFFF" stroke="S" stroke-width="2.6"/>
<line x1="52" y1="50" x2="59" y2="57" stroke="S" stroke-width="3.2" stroke-linecap="round"/>
""", None),

    ("S12", "content-strategy", "内容策划", """
<g stroke="#F0A500" stroke-width="2.8" stroke-linecap="round">
  <line x1="32" y1="3" x2="32" y2="9"/><line x1="11" y1="13" x2="15" y2="17"/><line x1="53" y1="13" x2="49" y2="17"/>
  <line x1="4" y1="31" x2="10" y2="31"/><line x1="60" y1="31" x2="54" y2="31"/>
</g>
<path d="M32 10 C21 10 14 18 14 28 C14 35 18 40 23 44 V48 H41 V44 C46 40 50 35 50 28 C50 18 43 10 32 10 Z" fill="url(#g)" stroke="#E08A00" stroke-width="2.6" stroke-linejoin="round"/>
<path d="M26 44 v-8 a6 6 0 0 1 12 0 v8" fill="none" stroke="#FFFFFF" stroke-width="2.6" stroke-linecap="round"/>
<rect x="24" y="48" width="16" height="4.5" rx="2" fill="#E08A00"/>
<path d="M26 56 h12" stroke="#E08A00" stroke-width="3.2" stroke-linecap="round"/>
""", None),
]

FONT_CANDIDATES = [Path("C:/Windows/Fonts/msyh.ttc"), Path("C:/Windows/Fonts/simhei.ttf")]


def font(size: int):
    for p in FONT_CANDIDATES:
        if p.exists():
            return ImageFont.truetype(str(p), size)
    return ImageFont.load_default()


def build_svg(body: str) -> str:
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" '
        'width="64" height="64" fill="none">'
        + DEFS + body.replace('stroke="S"', f'stroke="{STROKE}"') + "</svg>"
    )


def render_pngs() -> list[Image.Image]:
    """用一个透明底 HTML 页面一次性渲染 12 枚 SVG，再裁成独立 PNG。"""
    if not CHROME.exists():
        raise SystemExit(f"未找到 Chrome：{CHROME}")

    cell = 512
    pad = 32
    cells = "\n".join(
        f'<div class="c"><img src="svg/{code}-{slug}.svg"></div>'
        for code, slug, *_ in ICONS
    )
    html = f"""<!doctype html><html><head><meta charset="utf-8"><style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{background:transparent}}
.g{{display:grid;grid-template-columns:repeat(4,{cell}px);grid-template-rows:repeat(3,{cell}px)}}
.c{{width:{cell}px;height:{cell}px;display:flex;align-items:center;justify-content:center}}
img{{width:{cell - pad * 2}px;height:{cell - pad * 2}px}}
</style></head><body><div class="g">{cells}</div></body></html>"""
    page = HERE / "_render.html"
    shot = HERE / "_render.png"
    page.write_text(html, encoding="utf-8")

    cmd = [
        str(CHROME), "--headless=new", "--disable-gpu", "--no-sandbox",
        "--hide-scrollbars", "--force-device-scale-factor=1",
        "--default-background-color=00000000",
        f"--window-size={cell * 4},{cell * 3}",
        f"--screenshot={shot.as_posix()}",
        page.as_uri(),
    ]
    subprocess.run(cmd, check=True, capture_output=True, timeout=120)
    sheet = Image.open(shot).convert("RGBA")

    icons = []
    for i in range(len(ICONS)):
        x = (i % 4) * cell
        y = (i // 4) * cell
        tile = sheet.crop((x, y, x + cell, y + cell)).resize((256, 256), Image.LANCZOS)
        icons.append(unpremultiply(tile))
    page.unlink(missing_ok=True)
    shot.unlink(missing_ok=True)
    return icons


def unpremultiply(im: Image.Image) -> Image.Image:
    """Chrome 透明截图的 RGB 是按 alpha 预乘到黑底上的，还原真实颜色以消除深色描边。"""
    src = list(im.getdata())
    out = []
    for r, g, b, a in src:
        if a == 0:
            out.append((0, 0, 0, 0))
        elif a == 255:
            out.append((r, g, b, 255))
        else:
            k = 255 / a
            out.append((min(255, round(r * k)), min(255, round(g * k)),
                        min(255, round(b * k)), a))
    fixed = Image.new("RGBA", im.size)
    fixed.putdata(out)
    return fixed


def build_contact_sheet(icons: list[Image.Image]) -> Image.Image:
    cell_w, cell_h, cols = 260, 250, 4
    rows = math.ceil(len(icons) / cols)
    sheet = Image.new("RGB", (cell_w * cols, cell_h * rows), "#F4F5FB")
    d = ImageDraw.Draw(sheet)
    for i, (icon, item) in enumerate(zip(icons, ICONS)):
        code, _, zh, _, target = item
        cx, cy = (i % cols) * cell_w, (i // cols) * cell_h
        d.rounded_rectangle((cx + 12, cy + 12, cx + cell_w - 12, cy + cell_h - 12),
                            radius=16, fill="#FFFFFF", outline="#DDE2F2", width=2)
        thumb = icon.resize((128, 128), Image.LANCZOS)
        sheet.paste(thumb, (cx + (cell_w - 128) // 2, cy + 20), thumb)
        d.text((cx + 20, cy + 160), f"{code}  {zh}", font=font(17), fill="#2A3560")
        label = target or "暂无对应技能"
        size = 13
        while size > 8 and d.textlength(label, font=font(size)) > cell_w - 40:
            size -= 1
        d.text((cx + 20, cy + 190), label, font=font(size), fill="#7A86A8")
    return sheet


def main() -> None:
    SVG_DIR.mkdir(exist_ok=True)
    for code, slug, _, body, _ in ICONS:
        (SVG_DIR / f"{code}-{slug}.svg").write_text(build_svg(body), encoding="utf-8")

    icons = render_pngs()
    alpha0 = icons[0].getchannel("A").getextrema()
    print(f"渲染完成，首枚 alpha 范围 {alpha0}（含 0 表示透明底生效）")

    for (code, slug, zh, _, target), icon in zip(ICONS, icons):
        png = HERE / f"{code}-{slug}.png"
        icon.save(png)
        if target:
            shutil.copyfile(SVG_DIR / f"{code}-{slug}.svg", ROOT / "skills" / target / "icon.svg")
            shutil.copyfile(png, ROOT / "skills" / target / "icon.png")
            print(f"{code} {zh:<8} -> svg + png  +  skills/{target}/")
        else:
            print(f"{code} {zh:<8} -> svg + png  (暂无对应技能)")

    build_contact_sheet(icons).save(HERE / "contact-sheet.png")
    (HERE / "gallery.html").write_text(build_gallery(), encoding="utf-8")
    print("已生成 contact-sheet.png / gallery.html")


GALLERY_CSS = """
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:"Microsoft YaHei","PingFang SC",system-ui,sans-serif;background:#F5F7FD;color:#1E2A4A;padding:40px 28px 56px}
.wrap{max-width:1120px;margin:0 auto}
h1{font-size:26px;letter-spacing:.5px}
.lead{margin:10px 0 6px;color:#64719A;font-size:14px;line-height:1.8}
.meta{color:#8A96B8;font-size:12.5px;margin-bottom:28px}
.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}
.card{background:#fff;border:1px solid #E2E8F5;border-radius:16px;padding:22px 18px 18px;
      box-shadow:0 2px 10px rgba(30,52,110,.04);transition:transform .18s,box-shadow .18s}
.card:hover{transform:translateY(-3px);box-shadow:0 10px 24px rgba(30,52,110,.12)}
.icon{height:76px;display:flex;align-items:center;justify-content:center;margin-bottom:14px}
.icon svg{width:76px;height:76px}
.code{font-size:12px;color:#8A96B8;letter-spacing:1px}
.title{font-size:16px;font-weight:600;margin:3px 0 8px}
.slug{font-size:11.5px;color:#7A86A8;word-break:break-all;line-height:1.5;min-height:34px}
.badge{display:inline-block;margin-top:10px;padding:3px 10px;border-radius:99px;font-size:11px}
.on{background:#E8F1FF;color:#1D57C8}.off{background:#F1F2F7;color:#8A90A8}
.dark{margin-top:34px;background:#141B32;border-radius:18px;padding:24px 26px}
.dark h2{font-size:15px;color:#DCE5FF;font-weight:600;margin-bottom:4px}
.dark p{font-size:12px;color:#8794BC;margin-bottom:18px}
.row{display:flex;flex-wrap:wrap;gap:14px}
.cell{width:74px;text-align:center}
.cell svg{width:46px;height:46px}
.cell span{display:block;color:#7E8CB8;font-size:10.5px;margin-top:4px}
.foot{margin-top:26px;font-size:12px;color:#8A96B8;line-height:1.8}
"""


def build_gallery() -> str:
    """生成静态展示页：内联 SVG，不依赖外部文件，双击即可看。"""
    def inline(code: str, slug: str, suffix: str = "") -> str:
        svg = (SVG_DIR / f"{code}-{slug}.svg").read_text(encoding="utf-8")
        # 同一文档内 24 个 SVG（卡片区 + 深色区），渐变 id 需全局唯一
        for key in ("b", "g"):
            svg = svg.replace(f'id="{key}"', f'id="{key}{code}{suffix}"')
            svg = svg.replace(f"url(#{key})", f"url(#{key}{code}{suffix})")
        return svg

    cards = []
    for code, slug, zh, _, target in ICONS:
        badge = "已安装到本机技能" if target else "图标库备用"
        cls = "on" if target else "off"
        cards.append(
            f'<div class="card"><div class="icon">{inline(code, slug)}</div>'
            f'<div class="code">{code}</div><div class="title">{zh}</div>'
            f'<div class="slug">{target or "暂无对应技能"}</div>'
            f'<span class="badge {cls}">{badge}</span></div>'
        )
    cells = "".join(
        f'<div class="cell">{inline(code, slug, "-dark")}<span>{code}</span></div>'
        for code, slug, *_ in ICONS
    )
    return (
        '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>AI创艺坊 · Skill 小头标</title><style>' + GALLERY_CSS + '</style></head><body><div class="wrap">'
        '<h1>AI创艺坊 · Skill 小头标</h1>'
        '<p class="lead">当前正式产品包含 10 项核心 Skill（S01–S10）；S11、S12 为备用图标，不代表已发布技能。SVG 源文件 + 透明 PNG，任意尺寸清晰。</p>'
        '<p class="meta">64×64 画布 · 蓝色渐变 #57A0FF → #123FCF · 描边 #0E3BB8 · S12 灯泡保留金色强调</p>'
        '<div class="grid">' + "".join(cards) + '</div>'
        '<div class="dark"><h2>深色界面下的透明底效果</h2>'
        '<p>透明 PNG / SVG 无白底残留，深色背景同样干净。</p>'
        '<div class="row">' + cells + '</div></div>'
        '<p class="foot">S01–S10 已同步到仓库中对应技能目录（icon.svg + icon.png）'
        'S11 数据分析、S12 内容策划为备用图标，当前暂无对应技能。<br>'
        '改设计请编辑 build_icons.py 的 ICONS 片段后重跑。</p>'
        '</div></body></html>'
    )


if __name__ == "__main__":
    main()
