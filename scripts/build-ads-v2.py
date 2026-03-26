"""
BTL MN Ads — V2 Image Builder (Updated with new source images)
Creates fresh ad images for 3 campaigns: Main (4 variants), Retargeting (2), Interest-based (2)
Plus a new carousel set (6 cards)

Output specs per playbook:
- Static ads: 1080x1350 (4:5 vertical)
- Carousel cards: 1080x1080 (square)
- No text on images — all copy goes in Ads Manager
- Dark overlay + BTL logo pill top-right
"""

from PIL import Image, ImageDraw, ImageFilter
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "ads", "v2")
os.makedirs(OUT, exist_ok=True)

SRC = os.path.join(BASE, "assets", "v2-sources")

ASSETS = {
    # New sources
    "hotel_twilight": f"{SRC}/hotel-landing-twilight.jpg",
    "hotel_daytime": f"{SRC}/hotel-landing-daytime.jpg",
    "physician_dark": f"{SRC}/physician-dark.jpg",
    "physician_light": f"{SRC}/physician-light.jpg",
    "emsella": f"{SRC}/emsella-treatment.jpg",
    "emsculpt_treatment": f"{SRC}/emsculpt-treatment.jpg",
    "emsculpt_model": f"{SRC}/emsculpt-neo-model.jpg",
    "data_dashboard": f"{SRC}/data-dashboard-1.jpg",
    "data_dashboard_2": f"{SRC}/data-dashboard-2.jpg",
    # Existing good sources
    "wayzata": f"{BASE}/../btl-minnesota/shared/assets/wayzata-lake-minnetonka.jpg",
    "ballroom": f"{BASE}/assets/ballroom.jpg",
    "networking": f"{BASE}/assets/networking.jpg",
    "emsculpt_neo_hero": f"{BASE}/shared/assets/products/emsculpt-neo/hero.jpg",
    "emsculpt_neo_product": f"{BASE}/shared/assets/products/emsculpt-neo/product-1.jpg",
    "emface_closeup": f"{BASE}/shared/assets/products/emface/product-2.jpg",
    "logo": f"{BASE}/shared/assets/btl-logo-white.png",
}

STATIC_SIZE = (1080, 1350)  # 4:5 vertical
SQUARE_SIZE = (1080, 1080)  # 1:1 carousel


def center_crop(img, target_w, target_h):
    """Resize and center-crop to exact dimensions."""
    iw, ih = img.size
    scale = max(target_w / iw, target_h / ih)
    img = img.resize((int(iw * scale), int(ih * scale)), Image.LANCZOS)
    iw, ih = img.size
    left = (iw - target_w) // 2
    top = (ih - target_h) // 2
    return img.crop((left, top, left + target_w, top + target_h))


def add_overlay(img, opacity=0.55, gradient=True):
    """Dark overlay with optional bottom gradient for readability."""
    overlay = Image.new("RGBA", img.size, (0, 40, 60, int(255 * opacity)))
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    img = Image.alpha_composite(img, overlay)

    if gradient:
        grad = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(grad)
        w, h = img.size
        gradient_start = int(h * 0.6)
        for y in range(gradient_start, h):
            alpha = int(120 * ((y - gradient_start) / (h - gradient_start)))
            draw.line([(0, y), (w, y)], fill=(0, 20, 40, alpha))
        img = Image.alpha_composite(img, grad)

    return img


def add_logo(img, size=38):
    """BTL logo in a dark pill, top-right."""
    logo_img = Image.open(ASSETS["logo"]).convert("RGBA")
    lw, lh = logo_img.size
    scale = size / lh
    logo_resized = logo_img.resize((int(lw * scale), int(lh * scale)), Image.LANCZOS)

    pw = logo_resized.width + 24
    ph = logo_resized.height + 16
    pill = Image.new("RGBA", (pw, ph), (0, 0, 0, 140))

    lx = (pw - logo_resized.width) // 2
    ly = (ph - logo_resized.height) // 2
    pill.paste(logo_resized, (lx, ly), logo_resized)

    margin = 24
    pos = (img.width - pw - margin, margin)
    img.paste(pill, pos, pill)

    return img


def add_accent(img, color=(0, 130, 200), width=6, position="bottom"):
    """Subtle accent line."""
    draw = ImageDraw.Draw(img)
    w, h = img.size
    if position == "bottom":
        draw.rectangle([(0, h - width), (w, h)], fill=color + (200,))
    elif position == "top":
        draw.rectangle([(0, 0), (w, width)], fill=color + (200,))
    return img


def build_image(source_key, target_size, overlay_opacity=0.55, gradient=True, accent=None, blur=0):
    """Full pipeline: crop -> blur -> overlay -> logo -> accent."""
    img = Image.open(ASSETS[source_key]).convert("RGB")
    img = center_crop(img, *target_size)

    if blur > 0:
        img = img.filter(ImageFilter.GaussianBlur(radius=blur))

    img = img.convert("RGBA")
    img = add_overlay(img, overlay_opacity, gradient)
    img = add_logo(img)

    if accent:
        img = add_accent(img, **accent)

    return img


# ============================================================
# MAIN CAMPAIGN — 4 static ads (4:5 vertical)
# ============================================================

print("Building Main Campaign statics...")

# 1. Revenue Model — Hotel Landing twilight (the venue, aspirational)
img = build_image("hotel_twilight", STATIC_SIZE, overlay_opacity=0.42,
                  accent={"color": (0, 160, 80), "width": 5, "position": "bottom"})
img.convert("RGB").save(os.path.join(OUT, "main-1-revenue-model.jpg"), quality=92)
print("  main-1-revenue-model.jpg — Hotel Landing twilight")

# 2. Financing — Emsculpt treatment in action (shows the product being used)
img = build_image("emsculpt_treatment", STATIC_SIZE, overlay_opacity=0.45,
                  accent={"color": (0, 120, 200), "width": 5, "position": "bottom"})
img.convert("RGB").save(os.path.join(OUT, "main-2-financing.jpg"), quality=92)
print("  main-2-financing.jpg — Emsculpt treatment in action")

# 3. New Technology — Emsculpt Neo product hero (device reveal)
img = build_image("emsculpt_neo_product", STATIC_SIZE, overlay_opacity=0.35, gradient=False,
                  accent={"color": (0, 100, 180), "width": 5, "position": "top"})
img.convert("RGB").save(os.path.join(OUT, "main-3-new-tech.jpg"), quality=92)
print("  main-3-new-tech.jpg — Emsculpt Neo product hero")

# 4. Peer Proof — Physician with stethoscope (speaks to ICP identity)
img = build_image("physician_dark", STATIC_SIZE, overlay_opacity=0.40,
                  accent={"color": (0, 160, 80), "width": 5, "position": "bottom"})
img.convert("RGB").save(os.path.join(OUT, "main-4-peer-proof.jpg"), quality=92)
print("  main-4-peer-proof.jpg — Physician (dark bg)")


# ============================================================
# RETARGETING CAMPAIGN — 2 static ads (4:5 vertical)
# ============================================================

print("Building Retargeting statics...")

# 1. Model Waiting — Emface close-up treatment (personal, device on face)
img = build_image("emface_closeup", STATIC_SIZE, overlay_opacity=0.45,
                  accent={"color": (255, 180, 0), "width": 5, "position": "bottom"})
img.convert("RGB").save(os.path.join(OUT, "retarget-1-model-waiting.jpg"), quality=92)
print("  retarget-1-model-waiting.jpg — Emface close-up")

# 2. Financing Reminder — Data dashboard (numbers, analysis)
img = build_image("data_dashboard", STATIC_SIZE, overlay_opacity=0.48,
                  accent={"color": (0, 120, 200), "width": 5, "position": "bottom"})
img.convert("RGB").save(os.path.join(OUT, "retarget-2-financing.jpg"), quality=92)
print("  retarget-2-financing.jpg — Data dashboard")


# ============================================================
# INTEREST-BASED CAMPAIGN — 2 static ads (4:5 vertical)
# ============================================================

print("Building Interest-Based statics...")

# 1. Clinical — Emsella provider + patient (device in action, provider present)
img = build_image("emsella", STATIC_SIZE, overlay_opacity=0.48,
                  accent={"color": (0, 160, 80), "width": 6, "position": "top"})
img.convert("RGB").save(os.path.join(OUT, "interest-1-clinical.jpg"), quality=92)
print("  interest-1-clinical.jpg — Emsella treatment")

# 2. Experience — Hotel Landing daytime (venue, lush, inviting)
img = build_image("hotel_daytime", STATIC_SIZE, overlay_opacity=0.45,
                  accent={"color": (0, 120, 200), "width": 5, "position": "bottom"})
img.convert("RGB").save(os.path.join(OUT, "interest-2-experience.jpg"), quality=92)
print("  interest-2-experience.jpg — Hotel Landing daytime")


# ============================================================
# NEW CAROUSEL — 6 cards (1:1 square)
# ============================================================

print("Building New Carousel...")

carousel_specs = [
    # (source, opacity, accent, description)
    ("hotel_twilight", 0.42, {"color": (0, 120, 200), "width": 4, "position": "bottom"}, "Hotel Landing twilight"),
    ("emsculpt_treatment", 0.45, {"color": (0, 160, 80), "width": 4, "position": "bottom"}, "Emsculpt treatment"),
    ("emsculpt_neo_product", 0.35, {"color": (0, 100, 180), "width": 4, "position": "top"}, "Emsculpt Neo device"),
    ("emsella", 0.48, {"color": (0, 160, 80), "width": 4, "position": "bottom"}, "Emsella consultation"),
    ("wayzata", 0.48, {"color": (0, 120, 200), "width": 4, "position": "bottom"}, "Lake Minnetonka"),
    ("ballroom", 0.48, {"color": (255, 180, 0), "width": 4, "position": "bottom"}, "Evening party"),
]

for i, (src, opacity, accent, desc) in enumerate(carousel_specs, 1):
    img = build_image(src, SQUARE_SIZE, overlay_opacity=opacity, accent=accent)
    fname = f"carousel-v2-{i:02d}.jpg"
    img.convert("RGB").save(os.path.join(OUT, fname), quality=92)
    print(f"  {fname} — {desc}")


# ============================================================
# Summary
# ============================================================

files = sorted(os.listdir(OUT))
print(f"\nDone! {len(files)} images in {OUT}/")
for f in files:
    size = os.path.getsize(os.path.join(OUT, f))
    img = Image.open(os.path.join(OUT, f))
    print(f"  {f} — {img.size[0]}x{img.size[1]} — {size//1024}KB")
