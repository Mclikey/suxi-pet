"""重新生成 224x350 苏汐差分图（kurocat-src 版）。
修复：shy/happy 的腮红之前用 ImageDraw 直接画（像素被替换成 alpha=75 的半透明粉），
运行时粉洞透出深色桌面变成深紫色。本版腮红用 alpha_composite 正确混合，结果不透明。
"""
from PIL import Image, ImageDraw
import os

SRC = r"G:\WorkBuddy\2026-11-26-10-59-14\suxi-pet\assets\suxi.png"
OUT = r"G:\WorkBuddy\2026-11-26-10-59-14\kurocat-src\src\assets\suxi"

im = Image.open(SRC).convert("RGBA")

# 224x350：取苏汐原图 y=0..660（耳尖到身体中段），等比缩放
crop_bottom = 660
crop = im.crop((0, 0, 422, crop_bottom))
ratio = 224 / 422
sprite = crop.resize((224, 350), Image.LANCZOS)

def pt(x, y):
    return (x * ratio, y * ratio)

LEFT_EYE = pt(157.5, 385)
RIGHT_EYE = pt(261, 385)
RX, RY = 30 * ratio, 28 * ratio
print("canvas", sprite.size, "eyes", LEFT_EYE, RIGHT_EYE, "r", round(RX, 1), round(RY, 1))

SKIN = im.getpixel((211, 430))  # 鼻下干净肤色
skin_rgba = tuple(min(255, int(c * 1.02)) for c in SKIN[:3]) + (255,)
print("skin", SKIN)

# 腮红：参考图粉色 #ffd5dc，画在脸颊两侧（嘴角外侧）
BLUSH_POS = [pt(125, 412), pt(296, 412)]
BLUSH_RX, BLUSH_RY = 13.5 * ratio * 2, 6.0 * ratio * 2  # 精灵空间半径
BLUSH_COLOR = (255, 170, 185, 115)  # 叠加在肤色后接近 #ffd5dc

def add_blush(base):
    """用独立图层 alpha_composite 混合腮红，保证结果像素不透明。"""
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    for cx, cy in BLUSH_POS:
        d.ellipse([cx - BLUSH_RX, cy - BLUSH_RY, cx + BLUSH_RX, cy + BLUSH_RY], fill=BLUSH_COLOR)
    # 两次柔和叠加让边缘更自然
    out = base.copy()
    out.alpha_composite(overlay)
    out.alpha_composite(overlay)  # 双层加深一点点
    return out

def close_eye(base, center, rx, ry, skin):
    d = ImageDraw.Draw(base, "RGBA")
    cx, cy = center
    # 肤色覆盖眼球（略微扩大盖住描边）
    d.ellipse([cx - rx - 4, cy - ry - 2, cx + rx + 4, cy + ry + 6], fill=skin)
    # 自然闭眼：一条向下弯的弧（笑眯眼）
    line = (95, 72, 52, 255)
    pts = []
    for i in range(15):
        t = i / 14
        x = cx - rx + 2 * rx * t
        y = cy - 3 - 4 * (1 - (2 * t - 1) ** 2)
        pts.append((x, y))
    d.line(pts, fill=line, width=3, joint="curve")
    # 外眼角短睫毛
    d.line([(cx + rx - 1, cy - 4), (cx + rx + 4, cy - 9)], fill=line, width=2)
    d.line([(cx - rx + 1, cy - 4), (cx - rx - 4, cy - 8)], fill=line, width=2)

idle = sprite.copy()
idle.save(os.path.join(OUT, "idle.png"))

blink = sprite.copy()
close_eye(blink, LEFT_EYE, RX, RY, skin_rgba)
close_eye(blink, RIGHT_EYE, RX, RY, skin_rgba)
blink.save(os.path.join(OUT, "blink.png"))

shy = blink.copy()
close_eye(shy, LEFT_EYE, RX, RY, skin_rgba)
close_eye(shy, RIGHT_EYE, RX, RY, skin_rgba)
shy = add_blush(shy)
shy.save(os.path.join(OUT, "shy.png"))

happy = sprite.copy()
happy = add_blush(happy)
d = ImageDraw.Draw(happy, "RGBA")
mx, my = pt(211, 420)
d.arc([mx - 9, my - 6, mx + 9, my + 6], start=10, end=170, fill=(120, 70, 55, 255), width=2)
happy.save(os.path.join(OUT, "happy.png"))

# 校验：全图不允许半透明像素（0<a<250 且非原图边缘）
for name in ["idle", "blink", "shy", "happy"]:
    p = Image.open(os.path.join(OUT, f"{name}.png")).convert("RGBA")
    semi = sum(1 for y in range(p.height) for x in range(p.width)
               if 60 < p.getpixel((x, y))[3] < 250)
    print(name, "semi-alpha px:", semi)

# 预览
preview = Image.new("RGBA", (224 * 4, 350), (40, 40, 40, 255))
for i, n in enumerate(["idle", "blink", "shy", "happy"]):
    q = Image.open(os.path.join(OUT, f"{n}.png"))
    preview.alpha_composite(q, (i * 224, 0))
preview.convert("RGB").save("G:/WorkBuddy/2026-11-26-10-59-14/suxi-sprites-v2-preview.png")
print("done")
