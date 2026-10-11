#!/usr/bin/env python3
"""Color Theory Visualizer — Interactive Education (single-file edition)"""

import sys
import math
from dataclasses import dataclass
from typing import List

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QSlider, QFrame, QStackedWidget, QScrollArea,
    QSizePolicy, QGroupBox, QColorDialog, QToolTip, QGridLayout, QStatusBar,
    QShortcut,
)
from PySide6.QtCore import Qt, Signal, QRectF, QPointF, QTimer, QSize
from PySide6.QtGui import (
    QFont, QPalette, QColor,
    QPainter, QPen, QBrush,
    QConicalGradient, QRadialGradient, QCursor,
    QKeySequence, QPixmap,
)

# ══════════════════════════════════════════════════════════════════════════════
#  Theme & Constants
# ══════════════════════════════════════════════════════════════════════════════

class Theme:
    BG_DARK = "#1a1a2e"
    BG_CARD = "#252540"
    BG_PANEL = "#2a2a4a"
    BORDER = "#3a3a5a"
    BORDER_LIGHT = "#4a4a6a"
    TEXT_PRIMARY = "#e0e0e0"
    TEXT_SECONDARY = "#a0a0c0"
    TEXT_MUTED = "#777"
    TEXT_HEADER = "#c0c0e0"
    ACCENT = "#7070b0"
    ACCENT_HOVER = "#3a3a5a"
    ACCENT_PRESSED = "#4a4a7a"
    PASS_GREEN = "#4CAF50"
    FAIL_RED = "#F44336"
    
    FONT_UI = "Segoe UI"
    FONT_MONO = "Consolas"
    
    BTN_STYLE = (
        f"QPushButton{{background:{BG_PANEL};color:{TEXT_PRIMARY};border:1px solid {BORDER};"
        f"border-radius:5px;padding:6px 14px;font-weight:bold;font-size:11px}}"
        f"QPushButton:hover{{background:{ACCENT_HOVER}}}"
    )

# ══════════════════════════════════════════════════════════════════════════════
#  Utility Functions & Data Classes
# ══════════════════════════════════════════════════════════════════════════════

def clamp(v, lo=0, hi=255):
    return max(lo, min(hi, int(v)))

def luminance(color: QColor) -> float:
    r, g, b = color.redF(), color.greenF(), color.blueF()
    r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
    g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
    b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

def contrast_ratio(c1: QColor, c2: QColor) -> float:
    l1, l2 = luminance(c1), luminance(c2)
    lighter, darker = max(l1, l2), min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)

def simulate_protanopia(c: QColor) -> QColor:
    r, g, b = c.redF(), c.greenF(), c.blueF()
    return QColor(clamp((0.56667 * r + 0.43333 * g) * 255), clamp((0.55833 * r + 0.44167 * g) * 255), clamp((0.24167 * g + 0.75833 * b) * 255))

def simulate_deuteranopia(c: QColor) -> QColor:
    r, g, b = c.redF(), c.greenF(), c.blueF()
    return QColor(clamp((0.62500 * r + 0.37500 * g) * 255), clamp((0.70000 * r + 0.30000 * g) * 255), clamp((0.30000 * g + 0.70000 * b) * 255))

def simulate_tritanopia(c: QColor) -> QColor:
    r, g, b = c.redF(), c.greenF(), c.blueF()
    return QColor(clamp((0.95000 * r + 0.05000 * g) * 255), clamp((0.43333 * g + 0.56667 * b) * 255), clamp((0.47500 * g + 0.52500 * b) * 255))

def simulate_achromatopsia(c: QColor) -> QColor:
    g = int(0.299 * c.red() + 0.587 * c.green() + 0.114 * c.blue())
    return QColor(g, g, g)

def copy_to_clipboard(text):
    QApplication.clipboard().setText(text)
    QToolTip.showText(QCursor.pos(), f"Copied: {text}", None, QRect(), 1500)

def draw_color_swatches(painter, x, y, colors, swatch_size=50, spacing=7, show_hex=True):
    """Reusable swatch row painter."""
    for c in colors:
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(c))
        painter.drawRoundedRect(QRectF(x, y, swatch_size, swatch_size), 5, 5)
        painter.setPen(QPen(QColor(80, 80, 100), 1))
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(QRectF(x, y, swatch_size, swatch_size), 5, 5)
        if show_hex:
            painter.setFont(QFont(Theme.FONT_UI, 8))
            painter.setPen(QColor(160, 160, 190))
            painter.drawText(QRectF(x - 2, y + swatch_size + 2, swatch_size + 4, 14), Qt.AlignCenter, c.name().upper())
        x += swatch_size + spacing

@dataclass
class HarmonyScheme:
    name: str
    description: str
    colors: List[QColor]

def compute_harmonies(base: QColor) -> List[HarmonyScheme]:
    h = base.hue() if base.hue() >= 0 else 0
    s, v = base.saturation(), base.value()
    return [
        HarmonyScheme("Complementary", "Maximum contrast & vibrancy.", [base, QColor.fromHsv((h + 180) % 360, s, v)]),
        HarmonyScheme("Analogous", "Naturally harmonious, common in nature.", [QColor.fromHsv((h - 30) % 360, s, v), QColor.fromHsv((h - 15) % 360, s, v), base, QColor.fromHsv((h + 15) % 360, s, v), QColor.fromHsv((h + 30) % 360, s, v)]),
        HarmonyScheme("Triadic", "Vibrant yet balanced.", [base, QColor.fromHsv((h + 120) % 360, s, v), QColor.fromHsv((h + 240) % 360, s, v)]),
        HarmonyScheme("Split-Complementary", "Contrast with less tension.", [base, QColor.fromHsv((h + 150) % 360, s, v), QColor.fromHsv((h + 210) % 360, s, v)]),
        HarmonyScheme("Tetradic (Rectangle)", "Rich and versatile.", [base, QColor.fromHsv((h + 60) % 360, s, v), QColor.fromHsv((h + 180) % 360, s, v), QColor.fromHsv((h + 240) % 360, s, v)]),
        HarmonyScheme("Square", "Bold and dynamic.", [base, QColor.fromHsv((h + 90) % 360, s, v), QColor.fromHsv((h + 180) % 360, s, v), QColor.fromHsv((h + 270) % 360, s, v)]),
    ]

# ══════════════════════════════════════════════════════════════════════════════
#  Reusable Custom Widgets
# ══════════════════════════════════════════════════════════════════════════════

class CopyButton(QPushButton):
    """Button that safely copies a stored value without signal disconnect issues."""
    def __init__(self, parent=None):
        super().__init__("📋 Copy", parent)
        self.copy_value = ""
        self.setFixedWidth(70)
        self.setStyleSheet(Theme.BTN_STYLE)
        self.clicked.connect(self._copy)

    def _copy(self):
        if self.copy_value:
            copy_to_clipboard(self.copy_value)

    def set_copy_value(self, v):
        self.copy_value = v

class ColorHistoryWidget(QWidget):
    """Track and display recently selected colors."""
    colorSelected = Signal(QColor)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._history = []
        self._max = 10
        self.setFixedHeight(40)
        self.setToolTip("Color History (Click to select)")

    def add_color(self, c: QColor):
        if not c.isValid():
            return
        hex_val = c.name().upper()
        self._history = [col for col in self._history if col.name().upper() != hex_val]
        self._history.insert(0, QColor(c))
        if len(self._history) > self._max:
            self._history.pop()
        self.update()

    def mousePressEvent(self, e):
        pos = e.position()
        sw = 30
        sp = 5
        for i, c in enumerate(self._history):
            x = 5 + i * (sw + sp)
            if QRectF(x, 5, sw, sw).contains(pos):
                self.colorSelected.emit(c)
                break

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        sw, sp = 30, 5
        for i, c in enumerate(self._history):
            x = 5 + i * (sw + sp)
            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(c))
            p.drawRoundedRect(QRectF(x, 5, sw, sw), 4, 4)
            p.setPen(QPen(QColor(80, 80, 100), 1))
            p.drawRoundedRect(QRectF(x, 5, sw, sw), 4, 4)
        p.end()

class SimultaneousContrastCanvas(QWidget):
    """Properly subclassed widget instead of monkey-patching paintEvent."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._inner_val = 128
        self.setFixedHeight(120)

    def set_inner_value(self, v):
        self._inner_val = v
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        half_w = w // 2
        p.setBrush(QBrush(QColor(255, 255, 255))); p.drawRect(0, 0, half_w, h)
        p.setBrush(QBrush(QColor(0, 0, 0))); p.drawRect(half_w, 0, half_w, h)
        inner_c = QColor(self._inner_val, self._inner_val, self._inner_val)
        p.setBrush(QBrush(inner_c)); p.setPen(QPen(QColor(0,0,0,50), 1))
        sq_size = 50
        p.drawRect(half_w//2 - sq_size//2, h//2 - sq_size//2, sq_size, sq_size)
        p.drawRect(half_w + half_w//2 - sq_size//2, h//2 - sq_size//2, sq_size, sq_size)
        p.end()


# ══════════════════════════════════════════════════════════════════════════════
#  Color Wheel Widget
# ══════════════════════════════════════════════════════════════════════════════

class ColorWheelWidget(QWidget):
    colorSelected = Signal(QColor)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._hue = 180
        self._sat = 255
        self._val = 255
        self._dragging = False
        self.setMinimumSize(260, 260)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setCursor(Qt.PointingHandCursor)
        
        # Caching
        self._wheel_cache = None
        self._cache_size = QSize()

    def get_color(self):
        h = self._hue if self._hue >= 0 else 0
        return QColor.fromHsv(h, self._sat, self._val)

    def set_hue(self, h):
        self._hue = h % 360; self.update()

    def set_sat_val(self, s, v):
        self._sat, self._val = s, v; self.update()

    def set_hsv(self, h, s, v):
        self._hue = h % 360 if h >= 0 else 0
        self._sat, self._val = s, v; self.update()

    def _build_wheel_cache(self):
        size = min(self.width(), self.height())
        self._wheel_cache = QPixmap(size, size)
        self._wheel_cache.fill(Qt.transparent)
        self._cache_size = self.size()
        
        p = QPainter(self._wheel_cache)
        p.setRenderHint(QPainter.Antialiasing)
        cx, cy = size / 2, size / 2
        outer_r = size / 2 - 18
        inner_r = outer_r * 0.62

        grad = QConicalGradient(QPointF(cx, cy), 0)
        for i in range(61):
            grad.setColorAt(i / 60.0, QColor.fromHsv(int(i * 6) % 360, 255, 255))
        p.setPen(Qt.NoPen); p.setBrush(QBrush(grad))
        p.drawEllipse(QPointF(cx, cy), outer_r, outer_r)

        inner_grad = QRadialGradient(QPointF(cx, cy), inner_r)
        inner_grad.setColorAt(0, QColor(35, 35, 55)); inner_grad.setColorAt(1, QColor(22, 22, 38))
        p.setBrush(QBrush(inner_grad)); p.drawEllipse(QPointF(cx, cy), inner_r, inner_r)
        
        # Hue labels
        p.setPen(QColor(180, 180, 210, 180))
        f = QFont(); f.setPointSize(7); f.setBold(False); p.setFont(f)
        labels = [(0, "0°"), (30, "30°"), (60, "60°"), (90, "90°"), (120, "120°"), (150, "150°"),
                  (180, "180°"), (210, "210°"), (240, "240°"), (270, "270°"), (300, "300°"), (330, "330°")]
        for deg, txt in labels:
            la = math.radians(deg)
            p.drawText(QRectF(cx + (outer_r + 12) * math.cos(la) - 14, cy + (outer_r + 12) * math.sin(la) - 7, 28, 14), Qt.AlignCenter, txt)
        p.end()

    def paintEvent(self, event):
        if self._wheel_cache is None or self._cache_size != self.size():
            self._build_wheel_cache()
            
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.drawPixmap(0, 0, self._wheel_cache)
        
        cx, cy = self.width() / 2, self.height() / 2
        outer_r = min(self.width(), self.height()) / 2 - 18
        inner_r = outer_r * 0.62

        # Dynamic elements
        col = self.get_color(); disc_r = inner_r * 0.52
        p.setBrush(QBrush(col)); p.setPen(QPen(QColor(255, 255, 255, 80), 2))
        p.drawEllipse(QPointF(cx, cy), disc_r, disc_r)

        p.setPen(QColor(255, 255, 255) if col.lightness() < 180 else QColor(0, 0, 0))
        f = p.font(); f.setPointSize(12); f.setBold(True); p.setFont(f)
        p.drawText(QRectF(cx - 55, cy - 12, 110, 24), Qt.AlignCenter, col.name().upper())

        hue = self._hue if self._hue >= 0 else 0
        a = math.radians(hue); mr = (outer_r + inner_r) / 2
        hx = cx + mr * math.cos(a); hy = cy + mr * math.sin(a)
        p.setPen(QPen(QColor(255, 255, 255), 3)); p.setBrush(Qt.NoBrush)
        p.drawEllipse(QPointF(hx, hy), 9, 9)
        p.setPen(QPen(QColor(0, 0, 0), 1.5)); p.drawEllipse(QPointF(hx, hy), 9, 9)
        p.end()

    def mousePressEvent(self, e):
        self._dragging = True; self._pick(e.position())

    def mouseMoveEvent(self, e):
        if self._dragging: self._pick(e.position())

    def mouseReleaseEvent(self, e):
        self._dragging = False

    def _pick(self, pos):
        cx, cy = self.width() / 2, self.height() / 2
        outer_r = min(self.width(), self.height()) / 2 - 18
        inner_r = outer_r * 0.62
        dx, dy = pos.x() - cx, pos.y() - cy
        dist = math.hypot(dx, dy)
        if inner_r <= dist <= outer_r:
            self._hue = int(math.degrees(math.atan2(dy, dx))) % 360
            self.colorSelected.emit(self.get_color()); self.update()


# ══════════════════════════════════════════════════════════════════════════════
#  Color Spaces & Formats Widget
# ══════════════════════════════════════════════════════════════════════════════

class ColorFormatsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._color = QColor(0, 200, 200)
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setSpacing(12)

        t = QLabel("Color Formats & Spaces")
        t.setFont(QFont(Theme.FONT_UI, 15, QFont.Bold)); t.setStyleSheet(f"color:{Theme.TEXT_PRIMARY}")
        lay.addWidget(t)

        d = QLabel("Different industries and technologies represent colors using various mathematical models called 'color spaces'. Understanding these helps you communicate color precisely across screens, printers, and code.")
        d.setWordWrap(True); d.setStyleSheet(f"color:{Theme.TEXT_MUTED};font-size:11px")
        lay.addWidget(d)

        self.preview_frame = QFrame()
        self.preview_frame.setFixedHeight(60)
        self.preview_frame.setAutoFillBackground(True)
        self.preview_frame.setStyleSheet("border-radius:8px; border:2px solid #777")
        lay.addWidget(self.preview_frame)

        grid = QGridLayout(); grid.setSpacing(8)
        self.formats = {}
        format_defs = [
            ("HEX", "Web standard format. Compact, representing RGB values in base-16 (00-FF)."),
            ("RGB", "Additive color model for screens. Values from 0-255 for Red, Green, and Blue light."),
            ("HSL", "Hue, Saturation, Lightness. Intuitive for designers. L=100% is always white, L=50% is pure color."),
            ("HSV", "Hue, Saturation, Value. Used in graphics software. V=100% is the brightest version of the hue."),
            ("CMYK", "Cyan, Magenta, Yellow, Key (Black). Subtractive model used in printing. Percentages of ink."),
            ("CSS RGB", "Functional notation for CSS web development."),
            ("CSS HSL", "Functional notation for CSS web development."),
        ]

        for i, (name, desc) in enumerate(format_defs):
            name_lbl = QLabel(f"{name}:")
            name_lbl.setFixedWidth(70)
            name_lbl.setStyleSheet(f"color:#b0b0e0; font-weight:bold; font-size:12px; font-family:{Theme.FONT_MONO}")
            grid.addWidget(name_lbl, i, 0)

            val_lbl = QLabel("#00C8C8")
            val_lbl.setStyleSheet(f"color:{Theme.TEXT_PRIMARY}; font-size:12px; font-family:{Theme.FONT_MONO}")
            grid.addWidget(val_lbl, i, 1)

            copy_btn = CopyButton()
            grid.addWidget(copy_btn, i, 2)

            desc_lbl = QLabel(desc)
            desc_lbl.setWordWrap(True)
            desc_lbl.setStyleSheet(f"color:{Theme.TEXT_MUTED}; font-size:10px; border: none; background: transparent;")
            grid.addWidget(desc_lbl, i, 3)

            self.formats[name] = (val_lbl, copy_btn)

        lay.addLayout(grid)

        lay.addSpacing(15)
        spaces_title = QLabel("Understanding Color Spaces")
        spaces_title.setFont(QFont(Theme.FONT_UI, 13, QFont.Bold))
        spaces_title.setStyleSheet(f"color:{Theme.TEXT_SECONDARY}; border: none; background: transparent;")
        lay.addWidget(spaces_title)

        spaces_info = [
            ("RGB (Red, Green, Blue)", "The foundation of digital screens. Pixels emit light in these three colors, combining to create the visible spectrum. It is an 'additive' space because adding light creates white. 0 light is black. Designers use hex codes (`#FF0000`) as shorthand for RGB."),
            ("CMYK (Cyan, Magenta, Yellow, Black)", "The foundation of print. Ink absorbs (subtracts) light. C+M+Y theoretically makes black, but pure black ink (Key) is added for deep contrast and to save expensive colored inks. Colors in CMYK often look duller than RGB because ink cannot emit light."),
            ("HSL & HSV (Cylindrical Models)", "Created because RGB is mathematically precise but humanly unintuitive. How do you make `#808080` brighter? Hard to guess. In HSL/HSV, you just increase the L or V slider. Both wrap RGB into a cylinder: the angle is Hue (color family), radius is Saturation (vibrancy). HSL slices vertically (L=100% is white top), HSV slices differently (V=100% is pure color top)."),
        ]

        for title, desc in spaces_info:
            f = QFrame()
            f.setStyleSheet(f"QFrame{{background:{Theme.BG_CARD};border-radius:8px;padding:12px;border:1px solid {Theme.BORDER}}}")
            fl = QVBoxLayout(f)
            h = QLabel(title); h.setFont(QFont(Theme.FONT_UI, 11, QFont.Bold))
            h.setStyleSheet(f"color:{Theme.TEXT_HEADER};border:none"); fl.addWidget(h)
            b = QLabel(desc); b.setWordWrap(True)
            b.setStyleSheet(f"color:{Theme.TEXT_SECONDARY};font-size:11px;border:none"); fl.addWidget(b)
            lay.addWidget(f)

        lay.addStretch()

    def set_color(self, c):
        if not isinstance(c, QColor) or not c.isValid():
            return
        self._color = QColor(c)
        self._update_formats()

    def _update_formats(self):
        c = self._color
        hsl_c = c.toHsl()
        h_hsl = hsl_c.hslHue() if hsl_c.hslHue() >= 0 else 0
        s_hsl = int(hsl_c.hslSaturation() / 255 * 100)
        l_hsl = int(hsl_c.lightness() / 255 * 100)

        h_hsv = c.hsvHue() if c.hsvHue() >= 0 else 0
        s_hsv = int(c.hsvSaturation() / 255 * 100)
        v_hsv = int(c.value() / 255 * 100)

        # BUG FIX: Use toCmyk() for correct percentages
        cmyk = c.toCmyk()
        c_c = int(cmyk.cyanF() * 100)
        c_m = int(cmyk.magentaF() * 100)
        c_y = int(cmyk.yellowF() * 100)
        c_k = int(cmyk.blackF() * 100)

        data = {
            "HEX": c.name().upper(),
            "RGB": f"rgb({c.red()}, {c.green()}, {c.blue()})",
            "HSL": f"hsl({h_hsl}, {s_hsl}%, {l_hsl}%)",
            "HSV": f"hsv({h_hsv}, {s_hsv}%, {v_hsv}%)",
            "CMYK": f"cmyk({c_c}%, {c_m}%, {c_y}%, {c_k}%)",
            "CSS RGB": f"rgb({c.red()} {c.green()} {c.blue()})",
            "CSS HSL": f"hsl({h_hsl} {s_hsl}% {l_hsl}%)",
        }

        pal = self.preview_frame.palette()
        pal.setColor(QPalette.Window, c)
        self.preview_frame.setPalette(pal)

        for name, value in data.items():
            if name in self.formats:
                lbl, btn = self.formats[name]
                lbl.setText(value)
                # BUG FIX: Safely update copy value without disconnecting
                btn.set_copy_value(value)


# ══════════════════════════════════════════════════════════════════════════════
#  Harmony Widget
# ══════════════════════════════════════════════════════════════════════════════

class HarmonyWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.base = QColor(0, 200, 200)
        self.setMinimumHeight(500)
        
        # Export Button
        self.export_btn = QPushButton("📋 Export as CSS Variables")
        self.export_btn.setStyleSheet(Theme.BTN_STYLE)
        self.export_btn.clicked.connect(self._export_css)

    def _export_css(self):
        css = ":root {\n"
        for scheme in compute_harmonies(self.base):
            safe_name = scheme.name.replace(" ", "-").replace("(", "").replace(")", "").lower()
            for i, c in enumerate(scheme.colors):
                css += f"  --{safe_name}-{i+1}: {c.name()};\n"
        css += "}"
        copy_to_clipboard(css)

    def set_color(self, c):
        if not isinstance(c, QColor) or not c.isValid(): return
        self.base = QColor(c); self.update()

    def paintEvent(self, event):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        
        # Draw export button area
        btn_h = 40
        self.export_btn.setGeometry(10, 8, 200, 35)
        
        y = btn_h + 10
        tf = QFont(); tf.setPointSize(11); tf.setBold(True)
        df = QFont(); df.setPointSize(8)
        
        # Responsive swatch size
        sw = min(50, (self.width() - 100) // 6)
        
        for scheme in compute_harmonies(self.base):
            p.setFont(tf); p.setPen(QColor(210, 210, 230)); p.drawText(10, y + 14, scheme.name)
            p.setFont(df); p.setPen(QColor(140, 140, 170)); p.drawText(10, y + 30, scheme.description)
            draw_color_swatches(p, 10, y + 40, scheme.colors, swatch_size=sw)
            y += sw + 65
        p.end()


# ══════════════════════════════════════════════════════════════════════════════
#  Color Mixing Widgets
# ══════════════════════════════════════════════════════════════════════════════

class StaticMixingDiagram(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent); self.setMinimumSize(420, 520)

    def _draw_mixing(self, p, cx, cy, radius, colors, labels, overlap_labels, title):
        tf = QFont(); tf.setPointSize(12); tf.setBold(True)
        p.setFont(tf); p.setPen(QColor(240, 240, 255))
        p.drawText(QRectF(cx - 180, cy - radius - 40, 360, 28), Qt.AlignCenter, title)
        offsets = [(-0.5, -0.3), (0.5, -0.3), (0.0, 0.35)]
        positions = [(cx + radius * ox, cy + radius * oy) for ox, oy in offsets]
        for i, (px, py) in enumerate(positions):
            g = QRadialGradient(px, py, radius * 0.9); c = colors[i]
            g.setColorAt(0, QColor(c.red(), c.green(), c.blue(), 180)); g.setColorAt(1, QColor(c.red(), c.green(), c.blue(), 0))
            p.setPen(Qt.NoPen); p.setBrush(QBrush(g)); p.drawEllipse(QPointF(px, py), radius * 0.65, radius * 0.65)
        lf = QFont(); lf.setPointSize(9); lf.setBold(True); p.setFont(lf)
        for i, (px, py) in enumerate(positions):
            p.setPen(QColor(240, 240, 255)); p.drawText(QRectF(px - 28, py - 8, 56, 16), Qt.AlignCenter, labels[i])
        sf = QFont(); sf.setPointSize(7); p.setFont(sf); p.setPen(QColor(200, 200, 220, 200))
        mid01 = ((positions[0][0] + positions[1][0]) / 2, (positions[0][1] + positions[1][1]) / 2 - radius * 0.2)
        mid02 = ((positions[0][0] + positions[2][0]) / 2 - radius * 0.14, (positions[0][1] + positions[2][1]) / 2 + 4)
        mid12 = ((positions[1][0] + positions[2][0]) / 2 + radius * 0.14, (positions[1][1] + positions[2][1]) / 2 + 4)
        center = (cx, cy + radius * 0.03)
        for (lx, ly), txt in zip([mid01, mid02, mid12, center], overlap_labels):
            p.drawText(QRectF(lx - 24, ly - 6, 48, 12), Qt.AlignCenter, txt)

    def paintEvent(self, event):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height(); r = min(w / 3, h / 5) * 0.68
        self._draw_mixing(p, w / 2, h * 0.24, r, [QColor(255, 0, 0), QColor(0, 255, 0), QColor(0, 0, 255)],
                          ["Red", "Green", "Blue"], ["Yellow", "Magenta", "Cyan", "White"], "Additive Mixing (Light - RGB)")
        self._draw_mixing(p, w / 2, h * 0.68, r, [QColor(220, 40, 40), QColor(230, 210, 0), QColor(30, 60, 210)],
                          ["Red", "Yellow", "Blue"], ["Orange", "Purple", "Green", "Dark"], "Subtractive Mixing (Paint - RYB)")
        p.setFont(QFont(Theme.FONT_UI, 9)); p.setPen(QColor(120, 120, 150))
        p.drawText(QRectF(10, h - 36, w - 20, 30), Qt.AlignCenter, "Additive = more light = brighter  |  Subtractive = more pigment = darker"); p.end()


class InteractiveMixerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent); self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        title = QLabel("Interactive Additive (RGB) Mixer")
        title.setFont(QFont(Theme.FONT_UI, 13, QFont.Bold)); title.setStyleSheet(f"color:{Theme.TEXT_PRIMARY}"); lay.addWidget(title)
        desc = QLabel("Drag the sliders to see how Red, Green, and Blue light combine to form other colors.")
        desc.setWordWrap(True); desc.setStyleSheet(f"color:{Theme.TEXT_MUTED};font-size:11px"); lay.addWidget(desc)

        self.sliders = {}; self.previews = {}
        slider_defs = [("Red", 0, 255, 128), ("Green", 0, 255, 128), ("Blue", 0, 255, 128)]
        for name, lo, hi, default in slider_defs:
            row = QHBoxLayout(); lbl = QLabel(name + ":"); lbl.setFixedWidth(80)
            color_hex = "#FF0000" if name == "Red" else "#00FF00" if name == "Green" else "#0000FF"
            lbl.setStyleSheet(f"color:{color_hex};font-weight:bold;font-size:11px"); row.addWidget(lbl)
            sl = QSlider(Qt.Horizontal); sl.setRange(lo, hi); sl.setValue(default); sl.valueChanged.connect(self._update_mixer); row.addWidget(sl)
            val_lbl = QLabel(""); val_lbl.setFixedWidth(40); val_lbl.setStyleSheet(f"color:#aaa;font-family:{Theme.FONT_MONO};font-size:11px"); row.addWidget(val_lbl)
            prev = QLabel(); prev.setFixedSize(30, 20); prev.setAutoFillBackground(True); prev.setStyleSheet("border-radius:3px; border:1px solid #555"); row.addWidget(prev)
            lay.addLayout(row); self.sliders[name] = (sl, val_lbl); self.previews[name] = prev

        self.result_frame = QFrame(); self.result_frame.setFixedHeight(60); self.result_frame.setAutoFillBackground(True)
        self.result_frame.setStyleSheet("border-radius:8px; border:2px solid #777"); lay.addWidget(self.result_frame)
        self.result_lbl = QLabel("Mixed Color"); self.result_lbl.setAlignment(Qt.AlignCenter)
        self.result_lbl.setFont(QFont(Theme.FONT_MONO, 12, QFont.Bold)); lay.addWidget(self.result_lbl)
        lay.addStretch(); self._update_mixer()

    def _update_mixer(self):
        r = self.sliders["Red"][0].value(); g = self.sliders["Green"][0].value(); b = self.sliders["Blue"][0].value()
        self.sliders["Red"][1].setText(str(r)); self.sliders["Green"][1].setText(str(g)); self.sliders["Blue"][1].setText(str(b))
        c_mix = QColor(r, g, b)
        for name, c in [("Red", QColor(r, 0, 0)), ("Green", QColor(0, g, 0)), ("Blue", QColor(0, 0, b))]:
            pal = self.previews[name].palette(); pal.setColor(QPalette.Window, c); self.previews[name].setPalette(pal)
        pal = self.result_frame.palette(); pal.setColor(QPalette.Window, c_mix); self.result_frame.setPalette(pal)
        fg = QColor(255, 255, 255) if c_mix.lightness() < 128 else QColor(0, 0, 0)
        self.result_lbl.setStyleSheet(f"color:{fg.name()}; font-size:12px; font-weight:bold")
        self.result_lbl.setText(f"{c_mix.name().upper()}   R:{r} G:{g} B:{b}")


class ColorMixingWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent); lay = QVBoxLayout(self); lay.setContentsMargins(0, 0, 0, 0); lay.setSpacing(20)
        self.diagram = StaticMixingDiagram(); lay.addWidget(self.diagram)
        self.mixer = InteractiveMixerWidget(); lay.addWidget(self.mixer)


# ══════════════════════════════════════════════════════════════════════════════
#  Color Properties Widgets
# ══════════════════════════════════════════════════════════════════════════════

class ColorPropertiesScales(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent); self.base = QColor(0, 200, 200); self.setMinimumHeight(500)

    def set_color(self, c):
        if not isinstance(c, QColor) or not c.isValid(): return
        self.base = QColor(c); self.update()

    def paintEvent(self, event):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        r, g, b = self.base.red(), self.base.green(), self.base.blue(); y = 8
        
        sw = min(50, (self.width() - 80) // 9) # Responsive
        
        tints = [QColor(int(r + (255 - r) * i / 8), int(g + (255 - g) * i / 8), int(b + (255 - b) * i / 8)) for i in range(9)]
        tf = QFont(); tf.setPointSize(11); tf.setBold(True); p.setFont(tf); p.setPen(QColor(210, 210, 230)); p.drawText(10, y + 14, "Tints  (adding white)")
        df = QFont(); df.setPointSize(8); p.setFont(df); p.setPen(QColor(140, 140, 170)); p.drawText(10, y + 30, "Lighter, softer versions")
        draw_color_swatches(p, 10, y + 40, tints, sw); y += sw + 65
        
        shades = [QColor(int(r * (1 - i / 8)), int(g * (1 - i / 8)), int(b * (1 - i / 8))) for i in range(9)]
        p.setFont(tf); p.setPen(QColor(210, 210, 230)); p.drawText(10, y + 14, "Shades  (adding black)")
        p.setFont(df); p.setPen(QColor(140, 140, 170)); p.drawText(10, y + 30, "Darker, richer versions")
        draw_color_swatches(p, 10, y + 40, shades, sw); y += sw + 65
        
        gr = 128; tones = [QColor(int(r + (gr - r) * i / 8), int(g + (gr - g) * i / 8), int(b + (gr - b) * i / 8)) for i in range(9)]
        p.setFont(tf); p.setPen(QColor(210, 210, 230)); p.drawText(10, y + 14, "Tones  (adding gray)")
        p.setFont(df); p.setPen(QColor(140, 140, 170)); p.drawText(10, y + 30, "Muted, subtle versions")
        draw_color_swatches(p, 10, y + 40, tones, sw); y += sw + 65

        p.setFont(tf); p.setPen(QColor(210, 210, 230)); p.drawText(10, y + 14, "Color Temperature Spectrum")
        p.setFont(df); p.setPen(QColor(140, 140, 170)); p.drawText(10, y + 30, "Warm (red-yellow) advance & energize - Cool (blue-green) recede & calm")
        tw = max(1, (min(800, self.width()) - 20) / 12)
        for i in range(12):
            c = QColor.fromHsv(i * 30, 200, 220); p.setPen(Qt.NoPen); p.setBrush(QBrush(c))
            p.drawRoundedRect(QRectF(10 + i * tw, y + 44, tw - 2, 30), 3, 3)
        p.setFont(QFont(Theme.FONT_UI, 8)); p.setPen(QColor(255, 160, 110)); p.drawText(10, y + 92, "<- Warm")
        p.setPen(QColor(110, 160, 255)); p.drawText(int(10 + 11 * tw), y + 92, "Cool ->"); y += 110
        
        h = self.base.hue() if self.base.hue() >= 0 else 0
        sat_colors = [QColor.fromHsv(h, int(255 * i / 8), self.base.value()) for i in range(9)]
        p.setFont(tf); p.setPen(QColor(210, 210, 230)); p.drawText(10, y + 14, "Saturation Scale")
        p.setFont(df); p.setPen(QColor(140, 140, 170)); p.drawText(10, y + 30, "From desaturated (gray) to fully saturated (vivid)")
        draw_color_swatches(p, 10, y + 40, sat_colors, sw)
        p.end()


class SimultaneousContrastWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self); lay.setSpacing(8)
        title = QLabel("Simultaneous Contrast Illusion"); title.setFont(QFont(Theme.FONT_UI, 12, QFont.Bold))
        title.setStyleSheet(f"color:{Theme.TEXT_PRIMARY}; border:none"); lay.addWidget(title)
        desc = QLabel("Both inner squares have the EXACT SAME RGB values. They look different because our perception shifts based on the surrounding color.")
        desc.setWordWrap(True); desc.setStyleSheet(f"color:#aaa;font-size:10px; border:none"); lay.addWidget(desc)
        
        # BUG FIX: Use proper subclass
        self.canvas = SimultaneousContrastCanvas(); lay.addWidget(self.canvas)
        
        slider_row = QHBoxLayout(); lbl = QLabel("Inner Gray Value:"); lbl.setStyleSheet("color:#ccc; font-weight:bold; border:none"); slider_row.addWidget(lbl)
        self.slider = QSlider(Qt.Horizontal); self.slider.setRange(0, 255); self.slider.setValue(128); self.slider.valueChanged.connect(self.canvas.set_inner_value); slider_row.addWidget(self.slider)
        self.val_lbl = QLabel("128"); self.val_lbl.setFixedWidth(30); self.val_lbl.setStyleSheet(f"color:#aaa; font-family:{Theme.FONT_MONO}; border:none"); slider_row.addWidget(self.val_lbl)
        self.slider.valueChanged.connect(lambda v: self.val_lbl.setText(str(v)))
        lay.addLayout(slider_row)


class ColorPropertiesWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent); lay = QVBoxLayout(self); lay.setContentsMargins(0, 0, 0, 0); lay.setSpacing(10)
        self.scales = ColorPropertiesScales(); lay.addWidget(self.scales)
        self.contrast_demo = SimultaneousContrastWidget(); lay.addWidget(self.contrast_demo)
    def set_color(self, c): self.scales.set_color(c)


# ══════════════════════════════════════════════════════════════════════════════
#  HSL Explorer Widget
# ══════════════════════════════════════════════════════════════════════════════

class HSLExplorerWidget(QWidget):
    colorChanged = Signal(QColor)
    def __init__(self, parent=None):
        super().__init__(parent)
        # Debounce timer
        self._timer = QTimer()
        self._timer.setSingleShot(True)
        self._timer.setInterval(16)
        self._timer.timeout.connect(self._do_update)
        self._build()

    def _build(self):
        lay = QVBoxLayout(self); lay.setSpacing(12)
        t = QLabel("HSL / HSV Color Explorer"); t.setFont(QFont(Theme.FONT_UI, 15, QFont.Bold)); t.setStyleSheet(f"color:{Theme.TEXT_PRIMARY}"); lay.addWidget(t)
        d = QLabel("Drag the sliders to see how Hue, Saturation, and Value interact.\nH = which color  |  S = intensity / purity  |  V = brightness / lightness")
        d.setWordWrap(True); d.setStyleSheet(f"color:{Theme.TEXT_MUTED};font-size:11px"); lay.addWidget(d)
        prev_row = QHBoxLayout()
        self.preview = QLabel("Selected"); self.preview.setFixedSize(180, 80); self.preview.setAutoFillBackground(True); self.preview.setAlignment(Qt.AlignCenter); self.preview.setFont(QFont(Theme.FONT_MONO, 10, QFont.Bold)); self.preview.setStyleSheet("border-radius:8px;border:2px solid #555"); prev_row.addWidget(self.preview, alignment=Qt.AlignCenter)
        arrow = QLabel("↔"); arrow.setFont(QFont(Theme.FONT_UI, 18)); arrow.setStyleSheet("color:#666"); prev_row.addWidget(arrow, alignment=Qt.AlignCenter)
        self.comp_preview = QLabel("Complement"); self.comp_preview.setFixedSize(180, 80); self.comp_preview.setAutoFillBackground(True); self.comp_preview.setAlignment(Qt.AlignCenter); self.comp_preview.setFont(QFont(Theme.FONT_MONO, 10, QFont.Bold)); self.comp_preview.setStyleSheet("border-radius:8px;border:2px solid #555"); prev_row.addWidget(self.comp_preview, alignment=Qt.AlignCenter)
        lay.addLayout(prev_row)
        self.hex_lbl = QLabel("#00C8C8"); self.hex_lbl.setFont(QFont(Theme.FONT_MONO, 14, QFont.Bold)); self.hex_lbl.setAlignment(Qt.AlignCenter); self.hex_lbl.setStyleSheet("color:#aaa"); lay.addWidget(self.hex_lbl)
        self.rgb_lbl = QLabel("R: 0  G: 200  B: 200"); self.rgb_lbl.setAlignment(Qt.AlignCenter); self.rgb_lbl.setStyleSheet(f"color:#777;font-size:10px;font-family:{Theme.FONT_MONO}"); lay.addWidget(self.rgb_lbl)
        self.hsl_lbl = QLabel("H: 180  S: 100%  L: 39%"); self.hsl_lbl.setAlignment(Qt.AlignCenter); self.hsl_lbl.setStyleSheet(f"color:#777;font-size:10px;font-family:{Theme.FONT_MONO}"); lay.addWidget(self.hsl_lbl)
        self.hsv_lbl = QLabel("HSV: 180 100% 100%"); self.hsv_lbl.setAlignment(Qt.AlignCenter); self.hsv_lbl.setStyleSheet(f"color:#777;font-size:10px;font-family:{Theme.FONT_MONO}"); lay.addWidget(self.hsv_lbl)
        self.sliders = {}
        slider_defs = [("Hue (H)", 0, 359, 180), ("Saturation (S)", 0, 255, 255), ("Value / Brightness (V)", 0, 255, 255)]
        for name, lo, hi, default in slider_defs:
            r = QHBoxLayout(); lbl = QLabel(name + ":"); lbl.setFixedWidth(150); lbl.setStyleSheet("color:#ccc;font-weight:bold;font-size:11px"); r.addWidget(lbl)
            sl = QSlider(Qt.Horizontal); sl.setRange(lo, hi); sl.setValue(default); sl.valueChanged.connect(self._request_update); r.addWidget(sl)
            val = QLabel(""); val.setFixedWidth(50); val.setStyleSheet(f"color:#aaa;font-family:{Theme.FONT_MONO};font-size:11px"); r.addWidget(val)
            lay.addLayout(r); self.sliders[name] = (sl, val)
        concept = QLabel("HSV vs HSL: In HSV, V=100% means the brightest version of that hue. In HSL, L=50% is the purest hue; L=100% is always white. HSV is used in color pickers; HSL is common in CSS.")
        concept.setWordWrap(True); concept.setStyleSheet(f"color:#999;font-size:10px;background:{Theme.BG_CARD};padding:10px;border-radius:6px"); lay.addWidget(concept)
        lay.addStretch(); self._do_update()

    def _request_update(self):
        self._timer.start()

    def set_color(self, c):
        if not isinstance(c, QColor) or not c.isValid(): return
        h = c.hue() if c.hue() >= 0 else 0
        for s, _ in self.sliders.values(): s.blockSignals(True)
        self.sliders["Hue (H)"][0].setValue(h); self.sliders["Saturation (S)"][0].setValue(c.saturation()); self.sliders["Value / Brightness (V)"][0].setValue(c.value())
        self._do_update()
        for s, _ in self.sliders.values(): s.blockSignals(False)

    def _do_update(self):
        h = self.sliders["Hue (H)"][0].value(); s = self.sliders["Saturation (S)"][0].value(); v = self.sliders["Value / Brightness (V)"][0].value()
        c = QColor.fromHsv(h, s, v)
        pal = self.preview.palette(); pal.setColor(QPalette.Window, c); self.preview.setPalette(pal)
        fg = QColor(255, 255, 255) if c.lightness() < 150 else QColor(0, 0, 0); self.preview.setStyleSheet(f"border-radius:8px;border:2px solid #555;color:{fg.name()}"); self.preview.setText(c.name().upper())
        comp = QColor.fromHsv((h + 180) % 360, s, v); pal2 = self.comp_preview.palette(); pal2.setColor(QPalette.Window, comp); self.comp_preview.setPalette(pal2)
        fg2 = QColor(255, 255, 255) if comp.lightness() < 150 else QColor(0, 0, 0); self.comp_preview.setStyleSheet(f"border-radius:8px;border:2px solid #555;color:{fg2.name()}"); self.comp_preview.setText(comp.name().upper())
        self.hex_lbl.setText(f"{c.name().upper()}  |  Complement: {comp.name().upper()}")
        self.rgb_lbl.setText(f"R: {c.red():3d}   G: {c.green():3d}   B: {c.blue():3d}")
        
        # BUG FIX: Use Qt's native HSL conversion
        hsl_c = c.toHsl()
        h_hsl = hsl_c.hslHue() if hsl_c.hslHue() >= 0 else 0
        s_hsl_pct = int(hsl_c.hslSaturation() / 255 * 100)
        l_hsl_pct = int(hsl_c.lightness() / 255 * 100)
        self.hsl_lbl.setText(f"HSL:  H: {h_hsl}   S: {s_hsl_pct}%  L: {l_hsl_pct}%")
        self.hsv_lbl.setText(f"HSV:  H: {h}   S: {int(s / 255 * 100)}%  V: {int(v / 255 * 100)}%")
        self.sliders["Hue (H)"][1].setText(f"{h}°"); self.sliders["Saturation (S)"][1].setText(f"{int(s / 255 * 100)}%"); self.sliders["Value / Brightness (V)"][1].setText(f"{int(v / 255 * 100)}%")
        self.colorChanged.emit(c)


# ══════════════════════════════════════════════════════════════════════════════
#  Contrast Checker Widget
# ══════════════════════════════════════════════════════════════════════════════

class ContrastCheckerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent); self.fg = QColor(255, 255, 255); self.bg = QColor(30, 30, 60); self._selected_color = QColor(0, 200, 200); self._build()

    def _build(self):
        lay = QVBoxLayout(self); lay.setSpacing(14)
        t = QLabel("WCAG Contrast Ratio Checker"); t.setFont(QFont(Theme.FONT_UI, 15, QFont.Bold)); t.setStyleSheet(f"color:{Theme.TEXT_PRIMARY}"); lay.addWidget(t)
        info = QLabel("Contrast measures the luminance difference between text and background.\nWCAG 2.1 AA requires >= 4.5:1 for normal text, >= 3:1 for large text.\nWCAG 2.1 AAA requires >= 7:1 for normal text, >= 4.5:1 for large text.")
        info.setWordWrap(True); info.setStyleSheet(f"color:{Theme.TEXT_MUTED};font-size:11px"); lay.addWidget(info)
        sel_row = QHBoxLayout(); sel_row.addWidget(QLabel("App selected color:"))
        self._sel_prev = QLabel(); self._sel_prev.setFixedSize(28, 28); self._sel_prev.setAutoFillBackground(True); self._sel_prev.setStyleSheet("border-radius:4px;border:1px solid #555"); sel_row.addWidget(self._sel_prev)
        self._sel_hex = QLabel("#00C8C8"); self._sel_hex.setStyleSheet(f"color:#aaa;font-family:{Theme.FONT_MONO};font-size:11px"); sel_row.addWidget(self._sel_hex); sel_row.addStretch()
        btn_fg = QPushButton("Use as Text ->"); btn_fg.setStyleSheet(Theme.BTN_STYLE); btn_fg.clicked.connect(self._use_selected_as_fg); sel_row.addWidget(btn_fg)
        btn_bg = QPushButton("Use as Background ->"); btn_bg.setStyleSheet(Theme.BTN_STYLE); btn_bg.clicked.connect(self._use_selected_as_bg); sel_row.addWidget(btn_bg); lay.addLayout(sel_row)
        row = QHBoxLayout()
        for attr, label, color in [("fg", "Foreground (Text)", self.fg), ("bg", "Background", self.bg)]:
            grp = QGroupBox(label); grp.setStyleSheet(f"QGroupBox{{color:#bbb;border:1px solid #444;border-radius:8px;margin-top:14px;padding-top:20px;font-weight:bold}}QGroupBox::title{{subcontrol-position:top left;padding:0 8px}}")
            gl = QVBoxLayout(grp); prev = QLabel(); prev.setFixedSize(80, 80); prev.setAutoFillBackground(True); pal = prev.palette(); pal.setColor(QPalette.Window, color); prev.setPalette(pal); gl.addWidget(prev, alignment=Qt.AlignCenter)
            hx = QLabel(color.name().upper()); hx.setAlignment(Qt.AlignCenter); hx.setStyleSheet(f"color:#aaa;font-family:{Theme.FONT_MONO}"); gl.addWidget(hx)
            btn = QPushButton("Pick Color..."); btn.setStyleSheet(Theme.BTN_STYLE)
            if attr == "fg": self._fg_prev, self._fg_hx = prev, hx; btn.clicked.connect(self._pick_fg)
            else: self._bg_prev, self._bg_hx = prev, hx; btn.clicked.connect(self._pick_bg)
            gl.addWidget(btn); preset_row = QHBoxLayout()
            if attr == "fg":
                for pc in [QColor(255, 255, 255), QColor(0, 0, 0), QColor(200, 200, 200), QColor(50, 50, 50)]:
                    pb = QPushButton(); pb.setFixedSize(24, 24); pb.setStyleSheet(f"background:{pc.name()};border:1px solid #666;border-radius:3px"); pb.clicked.connect(lambda _, c=pc: self._set_fg(c)); preset_row.addWidget(pb)
            else:
                for pc in [QColor(0, 0, 0), QColor(255, 255, 255), QColor(30, 30, 60), QColor(240, 240, 240)]:
                    pb = QPushButton(); pb.setFixedSize(24, 24); pb.setStyleSheet(f"background:{pc.name()};border:1px solid #666;border-radius:3px"); pb.clicked.connect(lambda _, c=pc: self._set_bg(c)); preset_row.addWidget(pb)
            gl.addLayout(preset_row); row.addWidget(grp)
        lay.addLayout(row)
        swap_btn = QPushButton("Swap Foreground / Background"); swap_btn.setStyleSheet(Theme.BTN_STYLE); swap_btn.clicked.connect(self._swap); lay.addWidget(swap_btn)
        self.result = QFrame(); self.result.setStyleSheet(f"QFrame{{background:{Theme.BG_CARD};border-radius:10px;padding:14px}}"); rl = QVBoxLayout(self.result)
        self.ratio_lbl = QLabel("21.0 : 1"); self.ratio_lbl.setFont(QFont(Theme.FONT_UI, 30, QFont.Bold)); self.ratio_lbl.setAlignment(Qt.AlignCenter); self.ratio_lbl.setStyleSheet(f"color:{Theme.PASS_GREEN}"); rl.addWidget(self.ratio_lbl)
        self.preview_lbl = QLabel("The quick brown fox jumps over the lazy dog. 0123456789"); self.preview_lbl.setFont(QFont(Theme.FONT_UI, 14)); self.preview_lbl.setAlignment(Qt.AlignCenter); self.preview_lbl.setWordWrap(True); self.preview_lbl.setStyleSheet("padding:12px;border-radius:6px"); rl.addWidget(self.preview_lbl)
        self.preview_large = QLabel("Large Text Sample"); self.preview_large.setFont(QFont(Theme.FONT_UI, 22, QFont.Bold)); self.preview_large.setAlignment(Qt.AlignCenter); self.preview_large.setStyleSheet("padding:10px;border-radius:6px"); rl.addWidget(self.preview_large)
        badges = QHBoxLayout(); self.badges = {}
        for key in ("AA Normal", "AA Large", "AAA Normal", "AAA Large"):
            l = QLabel(f"{key}: -"); l.setAlignment(Qt.AlignCenter); l.setStyleSheet("color:#aaa;font-weight:bold;font-size:11px;padding:5px 8px;border-radius:4px;background:#1a1a30"); badges.addWidget(l); self.badges[key] = l
        rl.addLayout(badges); lay.addWidget(self.result); lay.addStretch(); self._refresh(); self._refresh_selected_preview()

    def set_selected_color(self, c): self._selected_color = QColor(c) if c.isValid() else self._selected_color; self._refresh_selected_preview()
    def _refresh_selected_preview(self): c = self._selected_color; pal = self._sel_prev.palette(); pal.setColor(QPalette.Window, c); self._sel_prev.setPalette(pal); self._sel_hex.setText(c.name().upper())
    def _use_selected_as_fg(self): self.fg = QColor(self._selected_color); self._refresh()
    def _use_selected_as_bg(self): self.bg = QColor(self._selected_color); self._refresh()
    def _pick_color(self, attr_name, title):
        current_color = getattr(self, attr_name)
        color = QColorDialog.getColor(current_color, self, title)
        if color.isValid():
            setattr(self, attr_name, color)
            self._refresh()

    def _pick_fg(self):
        self._pick_color('fg', "Foreground Color")

    def _pick_bg(self):
        self._pick_color('bg', "Background Color")
    def _set_fg(self, c): self.fg = QColor(c); self._refresh()
    def _set_bg(self, c): self.bg = QColor(c); self._refresh()
    def _swap(self): self.fg, self.bg = self.bg, self.fg; self._refresh()

    def _refresh(self):
        for prev, hx, c in [(self._fg_prev, self._fg_hx, self.fg), (self._bg_prev, self._bg_hx, self.bg)]:
            pal = prev.palette(); pal.setColor(QPalette.Window, c); prev.setPalette(pal); hx.setText(c.name().upper())
        ratio = contrast_ratio(self.fg, self.bg); self.ratio_lbl.setText(f"{ratio:.2f} : 1")
        colour = Theme.PASS_GREEN if ratio >= 7 else "#8BC34A" if ratio >= 4.5 else "#FF9800" if ratio >= 3 else Theme.FAIL_RED
        self.ratio_lbl.setStyleSheet(f"color:{colour};font-size:30px;font-weight:bold")
        self.preview_lbl.setStyleSheet(f"color:{self.fg.name()};background:{self.bg.name()};padding:12px;border-radius:6px")
        self.preview_large.setStyleSheet(f"color:{self.fg.name()};background:{self.bg.name()};padding:10px;border-radius:6px")
        checks = {"AA Normal": ratio >= 4.5, "AA Large": ratio >= 3, "AAA Normal": ratio >= 7, "AAA Large": ratio >= 4.5}
        for k, v in checks.items():
            sym = "PASS" if v else "FAIL"; c = Theme.PASS_GREEN if v else Theme.FAIL_RED; bg = "#1a3a1a" if v else "#3a1a1a"
            self.badges[k].setText(f"{k}: {sym}"); self.badges[k].setStyleSheet(f"color:{c};font-weight:bold;font-size:11px;padding:5px 8px;border-radius:4px;background:{bg}")


# ══════════════════════════════════════════════════════════════════════════════
#  Color Blindness Widgets
# ══════════════════════════════════════════════════════════════════════════════

class ColorBlindnessWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent); self.base = QColor(0, 200, 200); self.setMinimumHeight(350)
    def set_color(self, c): 
        if not isinstance(c, QColor) or not c.isValid(): return
        self.base = QColor(c); self.update()

    def paintEvent(self, event):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing); sw, sh = 110, 70
        sims = [("Normal Vision", self.base, "Trichromatic - 3 cone types"), ("Protanopia", simulate_protanopia(self.base), "Red-blind - ~1.3% of males"),
                ("Deuteranopia", simulate_deuteranopia(self.base), "Green-blind - ~1.2% of males"), ("Tritanopia", simulate_tritanopia(self.base), "Blue-blind - ~0.001%"),
                ("Achromatopsia", simulate_achromatopsia(self.base), "Total color blindness - ~0.003%")]
        tf = QFont(); tf.setPointSize(10); tf.setBold(True); df = QFont(); df.setPointSize(8)
        for i, (name, col, desc) in enumerate(sims):
            row, column = i // 3, i % 3; x = 10 + column * (max(320, self.width()) // 3); y = 8 + row * 150
            p.setPen(Qt.NoPen); p.setBrush(QBrush(QColor(0, 0, 0, 40))); p.drawRoundedRect(QRectF(x + 3, y + 3, sw, sh), 8, 8)
            p.setBrush(QBrush(col)); p.drawRoundedRect(QRectF(x, y, sw, sh), 8, 8); p.setPen(QPen(QColor(90, 90, 110), 1)); p.setBrush(Qt.NoBrush)
            p.drawRoundedRect(QRectF(x, y, sw, sh), 8, 8); p.setFont(tf); p.setPen(QColor(210, 210, 230)); p.drawText(x + sw + 12, y + 18, name)
            p.setFont(df); p.setPen(QColor(140, 140, 170)); p.drawText(x + sw + 12, y + 36, desc); p.setPen(QColor(170, 170, 200)); p.drawText(x + sw + 12, y + 54, f"Simulated: {col.name().upper()}")
            p.setFont(df); fg = QColor(255, 255, 255) if col.lightness() < 128 else QColor(0, 0, 0); p.setPen(fg); p.drawText(QRectF(x, y + sh - 16, sw, 14), Qt.AlignCenter, col.name().upper())
        p.end()


class PaletteBlindnessWidget(QWidget):
    def __init__(self, parent=None): super().__init__(parent); self.setMinimumHeight(330)
    def paintEvent(self, event):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        ui_colors = [("Success", QColor(76, 175, 80)), ("Warning", QColor(255, 193, 7)), ("Error", QColor(244, 67, 54)), ("Info", QColor(33, 150, 243)), ("Link", QColor(103, 58, 183))]
        sims = [("Normal", lambda c: c), ("Protanopia", simulate_protanopia), ("Deuteranopia", simulate_deuteranopia), ("Tritanopia", simulate_tritanopia), ("Achromat.", simulate_achromatopsia)]
        sw, sh = 72, 28; tf = QFont(); tf.setPointSize(8); tf.setBold(True); hf = QFont(); hf.setPointSize(7); row_h = sh + 24
        for ri, (sname, sfn) in enumerate(sims):
            y = ri * row_h; p.setFont(tf); p.setPen(QColor(160, 160, 180)); p.drawText(0, y + 14, sname); x = 82
            for name, col in ui_colors:
                sc = sfn(col); p.setPen(Qt.NoPen); p.setBrush(QBrush(sc)); p.drawRoundedRect(QRectF(x, y, sw, sh), 4, 4)
                p.setFont(hf); p.setPen(QColor(190, 190, 210)); p.drawText(QRectF(x, y + sh + 2, sw, 14), Qt.AlignCenter, name); x += sw + 10
        p.end()


# ══════════════════════════════════════════════════════════════════════════════
#  Theory Page Widget
# ══════════════════════════════════════════════════════════════════════════════

class TheoryPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent); lay = QVBoxLayout(self); lay.setContentsMargins(0, 0, 0, 0)
        header = QLabel("Understanding Color Theory"); header.setFont(QFont(Theme.FONT_UI, 18, QFont.Bold)); header.setStyleSheet(f"color:{Theme.TEXT_PRIMARY};padding:14px 14px 4px 14px"); lay.addWidget(header)
        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setStyleSheet("QScrollArea{border:none;background:transparent}")
        content = QWidget(); cl = QVBoxLayout(content); cl.setSpacing(14)
        sections = [
            ("The Color Wheel", "The color wheel arranges hues in a circle showing their relationships. Isaac Newton created the first circular diagram in 1666 by splitting sunlight through a prism."),
            ("Primary Colors", "Primary colors cannot be mixed from other colors - they are the building blocks.\n\nRGB (Additive / Light): Red, Green, Blue. Used in screens.\nRYB (Subtractive / Paint): Red, Yellow, Blue. Used in traditional art.\nCMYK (Print): Cyan, Magenta, Yellow, Key (Black)."),
            ("Secondary Colors", "Made by mixing two primary colors in equal proportion.\n\nRGB model: Cyan, Magenta, Yellow\nRYB model: Orange, Green, Purple"),
            ("Tertiary Colors", "Made by mixing a primary with an adjacent secondary. There are 6 tertiary colors per model, filling the wheel to 12 distinct segments."),
            ("Color Temperature", "Warm colors (red to yellow) advance toward the viewer and evoke energy. Cool colors (blue to green) recede and evoke calm. Temperature is relative."),
            ("Value, Saturation & Chroma", "Value: How light or dark a color is. Tints = hue + white. Shades = hue + black.\nSaturation: Intensity or purity. Tones = hue + gray."),
            ("Simultaneous Contrast", "A color appears different depending on its neighbors. Grey on yellow looks purplish; grey on blue looks orange-ish. Discovered by Michel Eugene Chevreul in 1839."),
            ("The 60-30-10 Rule", "A classic interior design and branding guideline:\n60% Dominant color\n30% Secondary color\n10% Accent color"),
            ("Accessibility & Color", "About 8% of men and 0.5% of women have color-vision deficiency (CVD). Never rely on color alone to convey meaning. Use contrast ratios >= 4.5:1 for body text (WCAG AA)."),
            ("Color Psychology", "Red: Passion, urgency. Blue: Trust, calm. Yellow: Optimism, warmth. Green: Nature, growth. Purple: Luxury. Orange: Energy. Black: Elegance."),
        ]
        for title, body in sections:
            f = QFrame(); f.setStyleSheet(f"QFrame{{background:{Theme.BG_CARD};border-radius:10px;padding:16px;border:1px solid {Theme.BORDER}}}")
            fl = QVBoxLayout(f); h = QLabel(title); h.setFont(QFont(Theme.FONT_UI, 12, QFont.Bold)); h.setStyleSheet(f"color:{Theme.TEXT_HEADER};border:none"); fl.addWidget(h)
            b = QLabel(body); b.setWordWrap(True); b.setStyleSheet(f"color:{Theme.TEXT_SECONDARY};font-size:11px;border:none"); fl.addWidget(b); cl.addWidget(f)
        cl.addStretch(); scroll.setWidget(content); lay.addWidget(scroll)


# ══════════════════════════════════════════════════════════════════════════════
#  Main Window
# ══════════════════════════════════════════════════════════════════════════════

class MainWindow(QMainWindow):
    PAGES = [
        ("Color Wheel", "wheel"), ("Harmonies", "harmonies"), ("Color Mixing", "mixing"),
        ("Color Properties", "properties"), ("Color Spaces", "spaces"), ("HSL Explorer", "hsl"),
        ("Accessibility", "access"), ("Color Blindness", "blind"), ("Theory Guide", "theory"),
    ]

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Color Theory Visualizer - Interactive Education")
        self.setMinimumSize(1020, 700); self.resize(1250, 830)
        self._color = QColor(0, 200, 200)
        self._apply_theme(); self._build()
        self._setup_shortcuts()

    def _apply_theme(self):
        self.setStyleSheet(f"""
            QMainWindow {{ background: {Theme.BG_DARK}; }}
            QWidget {{ background: {Theme.BG_DARK}; color: {Theme.TEXT_PRIMARY}; }}
            QPushButton {{
                background: {Theme.BG_PANEL}; color: {Theme.TEXT_PRIMARY};
                border: 1px solid {Theme.BORDER}; border-radius: 8px;
                padding: 10px 14px; font-size: 12px; font-weight: bold; text-align: left;
            }}
            QPushButton:hover {{ background: {Theme.ACCENT_HOVER}; border-color: #5a5a8a; }}
            QPushButton:checked {{ background: {Theme.ACCENT_PRESSED}; border-color: {Theme.ACCENT}; color: white; }}
            QSlider::groove:horizontal {{ height: 8px; background: #333; border-radius: 4px; }}
            QSlider::handle:horizontal {{ background: {Theme.ACCENT}; border: none; width: 18px; height: 18px; margin: -5px 0; border-radius: 9px; }}
            QSlider::handle:horizontal:hover {{ background: #9090d0; }}
            QSlider::sub-page:horizontal {{ background: #5050a0; border-radius: 4px; }}
            QScrollBar:vertical {{ background: {Theme.BG_DARK}; width: 10px; border-radius: 5px; }}
            QScrollBar::handle:vertical {{ background: #444; border-radius: 5px; min-height: 30px; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
            QScrollBar:horizontal {{ background: {Theme.BG_DARK}; height: 10px; border-radius: 5px; }}
            QScrollBar::handle:horizontal {{ background: #444; border-radius: 5px; min-width: 30px; }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}
        """)

    def _setup_shortcuts(self):
        for i in range(min(len(self.PAGES), 9)):
            QShortcut(QKeySequence(f"Ctrl+{i+1}"), self, lambda idx=i: self._switch_page(idx))

    def _switch_page(self, idx):
        if 0 <= idx < len(self.PAGES):
            self.stack.setCurrentIndex(idx)
            for btn in self.nav_buttons: btn.setChecked(False)
            self.nav_buttons[idx].setChecked(True)

    def _build(self):
        central = QWidget(); self.setCentralWidget(central)
        main_lay = QHBoxLayout(central); main_lay.setContentsMargins(10, 10, 10, 10); main_lay.setSpacing(12)

        # Left Sidebar
        sidebar = QVBoxLayout(); sidebar.setSpacing(8)
        
        logo = QLabel("🎨 Color Theory")
        logo.setFont(QFont(Theme.FONT_UI, 16, QFont.Bold)); logo.setStyleSheet("color:white;padding:10px 5px")
        sidebar.addWidget(logo)

        # Color Wheel Section
        self.wheel = ColorWheelWidget()
        self.wheel.colorSelected.connect(self._on_color_selected)
        sidebar.addWidget(self.wheel, 1)

        # Color History
        self.history = ColorHistoryWidget()
        self.history.colorSelected.connect(self._on_color_selected)
        sidebar.addWidget(self.history)

        # SV Sliders
        sv_lay = QHBoxLayout()
        self.sat_sl = QSlider(Qt.Horizontal); self.sat_sl.setRange(0, 255); self.sat_sl.setValue(255)
        self.sat_sl.setToolTip("Saturation"); self.sat_sl.valueChanged.connect(lambda v: self.wheel.set_sat_val(v, self.val_sl.value()))
        sv_lay.addWidget(QLabel("S:")); sv_lay.addWidget(self.sat_sl)

        self.val_sl = QSlider(Qt.Horizontal); self.val_sl.setRange(0, 255); self.val_sl.setValue(255)
        self.val_sl.setToolTip("Value/Brightness"); self.val_sl.valueChanged.connect(lambda v: self.wheel.set_sat_val(self.sat_sl.value(), v))
        sv_lay.addWidget(QLabel("V:")); sv_lay.addWidget(self.val_sl)
        sidebar.addLayout(sv_lay)

        # Navigation
        self.nav_buttons = []
        for i, (name, _) in enumerate(self.PAGES):
            btn = QPushButton(name); btn.setCheckable(True); btn.setChecked(i == 0)
            btn.clicked.connect(lambda checked, idx=i: self._switch_page(idx))
            sidebar.addWidget(btn); self.nav_buttons.append(btn)

        main_lay.addLayout(sidebar, 2)

        # Right Content Area
        right_lay = QVBoxLayout(); right_lay.setContentsMargins(0,0,0,0)
        
        # Header
        self.header_lbl = QLabel("Color Wheel")
        self.header_lbl.setFont(QFont(Theme.FONT_UI, 20, QFont.Bold)); self.header_lbl.setStyleSheet("color:white;padding:5px 0 15px 0")
        right_lay.addWidget(self.header_lbl)

        self.stack = QStackedWidget()
        right_lay.addWidget(self.stack)

        # Status Bar
        self.status_bar = QStatusBar(); self.setStatusBar(self.status_bar)
        self.status_bar.setStyleSheet(f"QStatusBar{{background:{Theme.BG_DARK};border-top:1px solid {Theme.BORDER}}}")
        self.status_color_prev = QLabel(); self.status_color_prev.setFixedSize(14, 14); self.status_color_prev.setAutoFillBackground(True)
        self.status_bar.addWidget(self.status_color_prev)
        self.status_hex = QLabel("#00C8C8"); self.status_hex.setStyleSheet(f"font-family:{Theme.FONT_MONO};font-size:11px")
        self.status_bar.addWidget(self.status_hex)
        self.status_rgb = QLabel("R:0 G:200 B:200"); self.status_rgb.setStyleSheet(f"font-family:{Theme.FONT_MONO};font-size:11px;color:#666")
        self.status_bar.addPermanentWidget(self.status_rgb)

        main_lay.addLayout(right_lay, 5)

        # Init Pages
        self.pages = {}
        self._add_page(ColorWheelWidget, "wheel") # Dummy for index, we use the sidebar one mostly
        self.pages["harmonies"] = HarmonyWidget(); self.stack.addWidget(self.pages["harmonies"])
        
        mix_w = ColorMixingWidget(); self.pages["mixing"] = mix_w; self.stack.addWidget(mix_w)
        
        prop_w = ColorPropertiesWidget(); self.pages["properties"] = prop_w; self.stack.addWidget(prop_w)
        
        fmt_w = ColorFormatsWidget(); self.pages["spaces"] = fmt_w; self.stack.addWidget(fmt_w)
        
        hsl_w = HSLExplorerWidget(); self.pages["hsl"] = hsl_w; hsl_w.colorChanged.connect(self._on_color_selected); self.stack.addWidget(hsl_w)
        
        acc_w = ContrastCheckerWidget(); self.pages["access"] = acc_w; self.stack.addWidget(acc_w)
        
        blind_lay = QVBoxLayout()
        blind_w1 = ColorBlindnessWidget(); blind_w2 = PaletteBlindnessWidget()
        blind_lay.addWidget(blind_w1); blind_lay.addWidget(blind_w2)
        blind_container = QWidget(); blind_container.setLayout(blind_lay)
        blind_scroll = QScrollArea(); blind_scroll.setWidgetResizable(True); blind_scroll.setWidget(blind_container)
        self.pages["blind"] = blind_w1; self.stack.addWidget(blind_scroll) # Only tracking base widget for color updates
        
        theory_w = TheoryPage(); self.pages["theory"] = theory_w; self.stack.addWidget(theory_w)

        # Sync initial color
        self._on_color_selected(self._color)

    def _add_page(self, cls, key):
        w = cls(); self.pages[key] = w; self.stack.addWidget(w)

    def _on_color_selected(self, c):
        if not isinstance(c, QColor) or not c.isValid():
            return
        self._color = c
        
        # Update Wheel (prevent loop if event came from HSL explorer)
        self.wheel.blockSignals(True)
        self.wheel.set_hsv(c.hue(), c.saturation(), c.value())
        self.wheel.blockSignals(False)
        self.sat_sl.setValue(c.saturation())
        self.val_sl.setValue(c.value())

        # Update History
        self.history.add_color(c)

        # Update Pages
        for key, page in self.pages.items():
            if key == "hsl":
                page.blockSignals(True)
                page.set_color(c)
                page.blockSignals(False)
            elif hasattr(page, 'set_color'):
                page.set_color(c)
            elif hasattr(page, 'set_selected_color'): # Contrast checker
                page.set_selected_color(c)

        # Update Status Bar
        pal = self.status_color_prev.palette(); pal.setColor(QPalette.Window, c); self.status_color_prev.setPalette(pal)
        self.status_hex.setText(c.name().upper())
        self.status_rgb.setText(f"R:{c.red()} G:{c.green()} B:{c.blue()}")

    def _switch_page(self, idx):
        if 0 <= idx < len(self.PAGES):
            self.stack.setCurrentIndex(idx)
            for i, btn in enumerate(self.nav_buttons): btn.setChecked(i == idx)
            self.header_lbl.setText(self.PAGES[idx][0])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = MainWindow()
    win.show()
    sys.exit(app.exec())