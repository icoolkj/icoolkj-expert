"""从「灵启逸梦」海报中提取 12 枚 Skill 小头标，生成透明 PNG 并分发到各 skill 目录。

用法：
    python assets/skill-icons/extract_icons.py

输入：同目录下的 source-poster.jpg（1254x1254 原始海报）
输出：
    assets/skill-icons/Sxx-*.png          12 枚透明图标，256x256
    assets/skill-icons/contact-sheet.png  12 宫格总览图
    skills/<name>/icon.png                S01-S10 对应的 10 个技能各一枚

海报改版时：只需按新海报更新 ICON_BOXES 坐标，重跑本脚本即可。
"""

from __future__ import annotations

import math
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
POSTER = HERE / "source-poster.jpg"

# 每张卡片内图标的像素包围盒（原图 1254x1254，亮度阈值投影 + 非背景像素自动检测）
# 顺序：第一行 S01-S06，第二行 S07-S12
ICON_BOXES = [
    (109, 811, 162, 872),   # S01 项目规划 · 剪贴板清单
    (296, 813, 357, 875),   # S02 世界观构建 · 地球经纬
    (491, 812, 552, 871),   # S03 小说创作 · 羽毛笔
    (704, 818, 765, 873),   # S04 章节续写 · 文档与齿轮
    (899, 818, 967, 870),   # S05 小说→短剧 · 播放按钮
    (1098, 808, 1159, 874), # S06 短剧剧本 · 场记板
    (101, 957, 174, 1012),  # S07 分镜脚本 · 分镜格
    (294, 957, 368, 1016),  # S08 视效素材 · 图片山峰
    (502, 951, 562, 1018),  # S09 逻辑审核 · 盾牌对勾
    (704, 955, 762, 1014),  # S10 IP运营 · 上升柱状图
    (904, 956, 965, 1016),  # S11 数据分析 · 报表清单
    (1097, 949, 1157, 1021),# S12 内容策划 · 灯泡
]

PAD = 5          # 在图标包围盒外多留几像素，避免切掉抗锯齿边缘
CANVAS = 96      # 统一画布边长（图标按最长边等比缩放后居中）
ICON_MAX = 84    # 图标在画布内最长边
OUT_SIZE = 256   # 最终输出尺寸

# 编号 → (英文短名, 中文名, 对应技能目录名)；目录名 None 表示项目里暂无对应技能
SKILLS = [
    ("S01", "project-planning", "项目规划", "original-ip-project-planning"),
    ("S02", "worldbuilding", "世界观构建", "story-worldbuilding"),
    ("S03", "novel-writing", "小说创作", "ai-novel-writing-studio"),
    ("S04", "chapter-continuation", "章节续写", "novel-continuity-and-continuation"),
    ("S05", "novel-to-shortdrama", "小说→短剧", "ai-short-drama-adaptation-studio"),
    ("S06", "screenplay", "短剧剧本", "short-drama-script-standardization"),
    ("S07", "storyboard", "分镜脚本", "cinematic-storyboard-design"),
    ("S08", "visual-assets", "视效素材", "ai-character-environment-asset-design"),
    ("S09", "logic-review", "逻辑审核", "story-logic-and-continuity-review"),
    ("S10", "ip-operations", "IP运营", "ip-commercial-operations-planning"),
    ("S11", "data-analysis", "数据分析", None),
    ("S12", "content-strategy", "内容策划", None),
]

FONT_CANDIDATES = [
    Path("C:/Windows/Fonts/msyh.ttc"),
    Path("C:/Windows/Fonts/simhei.ttf"),
    Path("C:/Windows/Fonts/Deng.ttf"),
]


def load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for p in FONT_CANDIDATES:
        if p.exists():
            return ImageFont.truetype(str(p), size)
    return ImageFont.load_default()


def extract_icon(poster: Image.Image, box: tuple[int, int, int, int]) -> Image.Image:
    """按图标包围盒裁切、抠掉卡片底色，等比缩放并居中到统一透明画布。"""
    x1, y1, x2, y2 = box
    tile = poster.crop((x1 - PAD, y1 - PAD, x2 + 1 + PAD, y2 + 1 + PAD)).convert("RGB")
    w, h = tile.size

    # 卡片底色取四角小块均值，消除淡紫渐变与 JPG 噪点
    s = 8
    corners = []
    for ox, oy in ((0, 0), (w - s, 0), (0, h - s), (w - s, h - s)):
        patch = list(tile.crop((ox, oy, ox + s, oy + s)).get_flattened_data())
        corners.append(tuple(sum(c[i] for c in patch) / len(patch) for i in range(3)))
    bg = tuple(sum(c[i] for c in corners) / len(corners) for i in range(3))

    smooth = tile.filter(ImageFilter.GaussianBlur(0.4))
    alpha = []
    for r, g, b in smooth.get_flattened_data():
        dist = math.sqrt((r - bg[0]) ** 2 + (g - bg[1]) ** 2 + (b - bg[2]) ** 2)
        # dist<26 视为纯背景（含淡紫雾），dist>78 视为纯图标，中间为抗锯齿过渡
        a = max(0.0, min(1.0, (dist - 26) / 52))
        alpha.append(int(a * 255))

    rgba = tile.convert("RGBA")
    rgba.putalpha(Image.frombytes("L", (w, h), bytes(alpha)))

    # 等比缩放到最长边 ICON_MAX，居中放进 CANVAS 画布，保证 12 枚视觉大小一致
    scale = ICON_MAX / max(w, h)
    nw, nh = round(w * scale), round(h * scale)
    icon = rgba.resize((nw, nh), Image.LANCZOS)
    canvas = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    canvas.paste(icon, ((CANVAS - nw) // 2, (CANVAS - nh) // 2), icon)
    return canvas.resize((OUT_SIZE, OUT_SIZE), Image.LANCZOS)


def build_contact_sheet(icons: list[Image.Image]) -> Image.Image:
    """浅色底 12 宫格总览，便于核对图标与编号。"""
    cell_w, cell_h, cols = 260, 250, 4
    rows = math.ceil(len(icons) / cols)
    sheet = Image.new("RGB", (cell_w * cols, cell_h * rows), "#F4F5FB")
    d = ImageDraw.Draw(sheet)
    f_title, f_sub = load_font(17), load_font(13)
    for i, (icon, (code, _, zh, target)) in enumerate(zip(icons, SKILLS)):
        cx = (i % cols) * cell_w
        cy = (i // cols) * cell_h
        d.rounded_rectangle((cx + 12, cy + 12, cx + cell_w - 12, cy + cell_h - 12),
                            radius=16, fill="#FFFFFF", outline="#DDE2F2", width=2)
        thumb = icon.resize((128, 128), Image.LANCZOS)
        sheet.paste(thumb, (cx + (cell_w - 128) // 2, cy + 20), thumb)
        d.text((cx + 20, cy + 160), f"{code}  {zh}", font=f_title, fill="#2A3560")
        label = target or "暂无对应技能"
        # 长目录名自动降字号，避免溢出卡片
        size = 13
        while size > 8 and d.textlength(label, font=load_font(size)) > cell_w - 40:
            size -= 1
        d.text((cx + 20, cy + 190), label, font=load_font(size), fill="#7A86A8")
    return sheet


def main() -> None:
    if not POSTER.exists():
        raise SystemExit(f"缺少海报原图：{POSTER}")
    poster = Image.open(POSTER).convert("RGB")
    if poster.size != (1254, 1254):
        print(f"提示：海报尺寸 {poster.size} 与预设坐标 (1254,1254) 不一致，请检查 ICON_BOXES")

    icons = []
    for (code, slug, zh, target), box in zip(SKILLS, ICON_BOXES):
        icon = extract_icon(poster, box)
        out = HERE / f"{code}-{slug}.png"
        icon.save(out)
        icons.append(icon)
        if target:
            shutil.copyfile(out, ROOT / "skills" / target / "icon.png")
            print(f"{code} {zh:<8} -> {out.name}  +  skills/{target}/icon.png")
        else:
            print(f"{code} {zh:<8} -> {out.name}  (项目暂无对应技能，仅存图标库)")

    build_contact_sheet(icons).save(HERE / "contact-sheet.png")
    print("已生成 contact-sheet.png")


if __name__ == "__main__":
    main()
