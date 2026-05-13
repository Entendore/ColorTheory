#!/usr/bin/env python3
"""
Color Theory Visualizer — An Interactive Educational Application
Built with PySide6

Run:  pip install PySide6 && python color_theory_visualizer.py
"""

import sys
import math
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QSlider, QFrame, QStackedWidget, QScrollArea,
    QGroupBox, QColorDialog, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QRectF, QPointF
from PySide6.QtGui import (
    QPainter, QColor, QPen, QBrush, QFont, QConicalGradient,
    QRadialGradient, QPainterPath, QPalette
)


# ═══════════════════════════════════════════════════════════════════════
#  UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════

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
    return QColor(clamp((0.56667 * r + 0.43333 * g) * 255),
                  clamp((0.55833 * r + 0.44167 * g) * 255),
                  clamp((0.24167 * g + 0.75833 * b) * 255))


def simulate_deuteranopia(c: QColor) -> QColor:
    r, g, b = c.redF(), c.greenF(), c.blueF()
    return QColor(clamp((0.62500 * r + 0.37500 * g) * 255),
                  clamp((0.70000 * r + 0.30000 * g) * 255),
                  clamp((0.30000 * g + 0.70000 * b) * 255))


def simulate_tritanopia(c: QColor) -> QColor:
    r, g, b = c.redF(), c.greenF(), c.blueF()
    return QColor(clamp((0.95000 * r + 0.05000 * g) * 255),
                  clamp((0.43333 * g + 0.56667 * b) * 255),
                  clamp((0.47500 * g + 0.52500 * b) * 255))


def simulate_achromatopsia(c: QColor) -> QColor:
    g = int(0.299 * c.red() + 0.587 * c.green() + 0.114 * c.blue())
    return QColor(g, g, g)


# ═══════════════════════════════════════════════════════════════════════
#  INTERACTIVE COLOR WHEEL
# ═══════════════════════════════════════════════════════════════════════

class ColorWheelWidget(QWidget):
    colorSelected = Signal(QColor)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._hue = 180
        self._sat = 255
        self._val = 255
        self._dragging = False
        self.setMinimumSize(260, 260)
        self.setMaximumSize(400, 400)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def get_color(self):
        h = self._hue if self._hue >= 0 else 0
        return QColor.fromHsv(h, self._sat, self._val)

    def set_hue(self, h):
        self._hue = h % 360
        self.update()

    def set_sat_val(self, s, v):
        self._sat, self._val = s, v
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        cx, cy = self.width() / 2, self.height() / 2
        outer_r = min(self.width(), self.height()) / 2 - 18
        inner_r = outer_r * 0.62

        # Hue ring
        grad = QConicalGradient(QPointF(cx, cy), 0)
        for i in range(361):
            grad.setColorAt(i / 360.0, QColor.fromHsv(i % 360, 255, 255))
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(grad))
        p.drawEllipse(QPointF(cx, cy), outer_r, outer_r)

        # Inner mask
        inner_grad = QRadialGradient(QPointF(cx, cy), inner_r)
        inner_grad.setColorAt(0, QColor(35, 35, 55))
        inner_grad.setColorAt(1, QColor(22, 22, 38))
        p.setBrush(QBrush(inner_grad))
        p.drawEllipse(QPointF(cx, cy), inner_r, inner_r)

        # Selected colour disc
        col = self.get_color()
        disc_r = inner_r * 0.52
        p.setBrush(QBrush(col))
        p.setPen(QPen(QColor(255, 255, 255, 80), 2))
        p.drawEllipse(QPointF(cx, cy), disc_r, disc_r)

        # Hex inside disc
        p.setPen(QColor(255, 255, 255) if col.lightness() < 180 else QColor(0, 0, 0))
        f = p.font(); f.setPointSize(12); f.setBold(True); p.setFont(f)
        p.drawText(QRectF(cx - 55, cy - 12, 110, 24), Qt.AlignCenter, col.name().upper())

        # Selector handle
        hue = self._hue if self._hue >= 0 else 0
        a = math.radians(hue)
        mr = (outer_r + inner_r) / 2
        hx = cx + mr * math.cos(a)
        hy = cy + mr * math.sin(a)
        p.setPen(QPen(QColor(255, 255, 255), 3)); p.setBrush(Qt.NoBrush)
        p.drawEllipse(QPointF(hx, hy), 9, 9)
        p.setPen(QPen(QColor(0, 0, 0), 1.5))
        p.drawEllipse(QPointF(hx, hy), 9, 9)

        # Labels around wheel
        p.setPen(QColor(180, 180, 210, 180))
        f.setPointSize(7); f.setBold(False); p.setFont(f)
        labels = [(0, "0°"), (30, "30°"), (60, "60°"), (90, "90°"),
                  (120, "120°"), (150, "150°"), (180, "180°"), (210, "210°"),
                  (240, "240°"), (270, "270°"), (300, "300°"), (330, "330°")]
        for deg, txt in labels:
            la = math.radians(deg)
            lx = cx + (outer_r + 12) * math.cos(la)
            ly = cy + (outer_r + 12) * math.sin(la)
            p.drawText(QRectF(lx - 14, ly - 7, 28, 14), Qt.AlignCenter, txt)
        p.end()

    def mousePressEvent(self, e):
        self._dragging = True
        self._pick(e.position())

    def mouseMoveEvent(self, e):
        if self._dragging:
            self._pick(e.position())

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
            self.colorSelected.emit(self.get_color())
            self.update()


# ═══════════════════════════════════════════════════════════════════════
#  HARMONY DISPLAY
# ═══════════════════════════════════════════════════════════════════════

class HarmonyWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.base = QColor(0, 200, 200)
        self.setMinimumHeight(500)

    def set_color(self, c):
        self.base = c
        self.update()

    def _harmonies(self):
        h = self.base.hue() if self.base.hue() >= 0 else 0
        s, v = self.base.saturation(), self.base.value()
        return [
            ("Complementary",
             "Two colors opposite on the wheel — maximum contrast & vibrancy. Great for call-to-action buttons.",
             [self.base, QColor.fromHsv((h + 180) % 360, s, v)]),
            ("Analogous",
             "3-5 adjacent hues — naturally harmonious, common in nature. Use one dominant, others as accents.",
             [QColor.fromHsv((h - 30) % 360, s, v),
              QColor.fromHsv((h - 15) % 360, s, v), self.base,
              QColor.fromHsv((h + 15) % 360, s, v),
              QColor.fromHsv((h + 30) % 360, s, v)]),
            ("Triadic",
             "Three equally-spaced hues (120 deg apart) — vibrant yet balanced. Let one colour dominate.",
             [self.base,
              QColor.fromHsv((h + 120) % 360, s, v),
              QColor.fromHsv((h + 240) % 360, s, v)]),
            ("Split-Complementary",
             "Base + two neighbours of its complement — contrast with less tension than pure complementary.",
             [self.base,
              QColor.fromHsv((h + 150) % 360, s, v),
              QColor.fromHsv((h + 210) % 360, s, v)]),
            ("Tetradic (Rectangle)",
             "Four colours in two complementary pairs — rich and versatile. Balance warm & cool tones.",
             [self.base,
              QColor.fromHsv((h + 60) % 360, s, v),
              QColor.fromHsv((h + 180) % 360, s, v),
              QColor.fromHsv((h + 240) % 360, s, v)]),
            ("Square",
             "Four evenly-spaced hues (90 deg apart) — bold and dynamic. Best with one dominant colour.",
             [self.base,
              QColor.fromHsv((h + 90) % 360, s, v),
              QColor.fromHsv((h + 180) % 360, s, v),
              QColor.fromHsv((h + 270) % 360, s, v)]),
        ]

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        sw, sh, sp = 50, 50, 7
        y = 8
        tf = QFont(); tf.setPointSize(11); tf.setBold(True)
        df = QFont(); df.setPointSize(8)
        hf = QFont(); hf.setPointSize(8)

        for name, desc, colors in self._harmonies():
            p.setFont(tf); p.setPen(QColor(210, 210, 230))
            p.drawText(10, y + 14, name)
            p.setFont(df); p.setPen(QColor(140, 140, 170))
            p.drawText(10, y + 30, desc)
            x = 10
            for c in colors:
                p.setPen(Qt.NoPen); p.setBrush(QBrush(c))
                p.drawRoundedRect(QRectF(x, y + 40, sw, sh), 5, 5)
                p.setPen(QPen(QColor(80, 80, 100), 1)); p.setBrush(Qt.NoBrush)
                p.drawRoundedRect(QRectF(x, y + 40, sw, sh), 5, 5)
                p.setFont(hf); p.setPen(QColor(160, 160, 190))
                p.drawText(QRectF(x - 2, y + 40 + sh + 2, sw + 4, 14), Qt.AlignCenter, c.name().upper())
                x += sw + sp
            y += sh + 65
        p.end()


# ═══════════════════════════════════════════════════════════════════════
#  COLOR MIXING VISUALIZATION
# ═══════════════════════════════════════════════════════════════════════

class ColorMixingWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(420, 520)

    def _draw_mixing(self, p, cx, cy, radius, colors, labels, overlap_labels, title):
        tf = QFont(); tf.setPointSize(12); tf.setBold(True)
        p.setFont(tf); p.setPen(QColor(240, 240, 255))
        p.drawText(QRectF(cx - 180, cy - radius - 40, 360, 28), Qt.AlignCenter, title)

        offsets = [(-0.5, -0.3), (0.5, -0.3), (0.0, 0.35)]
        positions = [(cx + radius * ox, cy + radius * oy) for ox, oy in offsets]

        for i, (px, py) in enumerate(positions):
            g = QRadialGradient(px, py, radius * 0.9)
            c = colors[i]
            g.setColorAt(0, QColor(c.red(), c.green(), c.blue(), 180))
            g.setColorAt(1, QColor(c.red(), c.green(), c.blue(), 0))
            p.setPen(Qt.NoPen); p.setBrush(QBrush(g))
            p.drawEllipse(QPointF(px, py), radius * 0.65, radius * 0.65)

        lf = QFont(); lf.setPointSize(9); lf.setBold(True)
        p.setFont(lf)
        for i, (px, py) in enumerate(positions):
            p.setPen(QColor(240, 240, 255))
            p.drawText(QRectF(px - 28, py - 8, 56, 16), Qt.AlignCenter, labels[i])

        sf = QFont(); sf.setPointSize(7)
        p.setFont(sf); p.setPen(QColor(200, 200, 220, 200))
        mid01 = ((positions[0][0] + positions[1][0]) / 2,
                 (positions[0][1] + positions[1][1]) / 2 - radius * 0.2)
        mid02 = ((positions[0][0] + positions[2][0]) / 2 - radius * 0.14,
                 (positions[0][1] + positions[2][1]) / 2 + 4)
        mid12 = ((positions[1][0] + positions[2][0]) / 2 + radius * 0.14,
                 (positions[1][1] + positions[2][1]) / 2 + 4)
        center = (cx, cy + radius * 0.03)
        for (lx, ly), txt in zip([mid01, mid02, mid12, center], overlap_labels):
            p.drawText(QRectF(lx - 24, ly - 6, 48, 12), Qt.AlignCenter, txt)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        r = min(w / 3, h / 5) * 0.68

        self._draw_mixing(p, w / 2, h * 0.24, r,
                          [QColor(255, 0, 0), QColor(0, 255, 0), QColor(0, 0, 255)],
                          ["Red", "Green", "Blue"],
                          ["Yellow", "Magenta", "Cyan", "White"],
                          "Additive Mixing (Light - RGB Model)")

        self._draw_mixing(p, w / 2, h * 0.68, r,
                          [QColor(220, 40, 40), QColor(230, 210, 0), QColor(30, 60, 210)],
                          ["Red", "Yellow", "Blue"],
                          ["Orange", "Purple", "Green", "Dark"],
                          "Subtractive Mixing (Paint - RYB Model)")

        p.setFont(QFont("Segoe UI", 9))
        p.setPen(QColor(120, 120, 150))
        p.drawText(QRectF(10, h - 36, w - 20, 30), Qt.AlignCenter,
                   "Additive = more light = brighter  |  Subtractive = more pigment = darker")
        p.end()


# ═══════════════════════════════════════════════════════════════════════
#  COLOR PROPERTIES (tints / shades / tones / temperature / saturation)
# ═══════════════════════════════════════════════════════════════════════

class ColorPropertiesWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.base = QColor(0, 200, 200)
        self.setMinimumHeight(500)

    def set_color(self, c):
        self.base = c; self.update()

    def _draw_scale(self, p, y, title, desc, colors):
        sw, sh, sp = 50, 50, 7
        tf = QFont(); tf.setPointSize(11); tf.setBold(True)
        df = QFont(); df.setPointSize(8)
        hf = QFont(); hf.setPointSize(8)
        p.setFont(tf); p.setPen(QColor(210, 210, 230)); p.drawText(10, y + 14, title)
        p.setFont(df); p.setPen(QColor(140, 140, 170)); p.drawText(10, y + 30, desc)
        x = 10
        for c in colors:
            p.setPen(Qt.NoPen); p.setBrush(QBrush(c))
            p.drawRoundedRect(QRectF(x, y + 40, sw, sh), 4, 4)
            p.setPen(QPen(QColor(70, 70, 90), 1)); p.setBrush(Qt.NoBrush)
            p.drawRoundedRect(QRectF(x, y + 40, sw, sh), 4, 4)
            p.setFont(hf); p.setPen(QColor(155, 155, 180))
            p.drawText(QRectF(x - 2, y + 40 + sh + 2, sw + 4, 13), Qt.AlignCenter, c.name().upper())
            x += sw + sp

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        r, g, b = self.base.red(), self.base.green(), self.base.blue()
        y = 8

        tints = [QColor(int(r + (255 - r) * i / 8),
                        int(g + (255 - g) * i / 8),
                        int(b + (255 - b) * i / 8)) for i in range(9)]
        self._draw_scale(p, y, "Tints  (adding white)",
                         "Lighter, softer versions - increase value, reduce contrast", tints)
        y += 115

        shades = [QColor(int(r * (1 - i / 8)),
                         int(g * (1 - i / 8)),
                         int(b * (1 - i / 8))) for i in range(9)]
        self._draw_scale(p, y, "Shades  (adding black)",
                         "Darker, richer versions - deepen and add drama", shades)
        y += 115

        gr = 128
        tones = [QColor(int(r + (gr - r) * i / 8),
                        int(g + (gr - g) * i / 8),
                        int(b + (gr - b) * i / 8)) for i in range(9)]
        self._draw_scale(p, y, "Tones  (adding gray)",
                         "Muted, subtle versions - reduced intensity, sophisticated feel", tones)
        y += 115

        # Temperature bar
        tf = QFont(); tf.setPointSize(11); tf.setBold(True)
        p.setFont(tf); p.setPen(QColor(210, 210, 230))
        p.drawText(10, y + 14, "Color Temperature Spectrum")
        df = QFont(); df.setPointSize(8); p.setFont(df)
        p.setPen(QColor(140, 140, 170))
        p.drawText(10, y + 30,
                   "Warm (red-yellow) advance & energize - Cool (blue-green) recede & calm - Temperature is relative")
        tw = max(1, (min(800, self.width()) - 20) / 12)
        for i in range(12):
            c = QColor.fromHsv(i * 30, 200, 220)
            p.setPen(Qt.NoPen); p.setBrush(QBrush(c))
            p.drawRoundedRect(QRectF(10 + i * tw, y + 44, tw - 2, 30), 3, 3)
        p.setFont(QFont("Segoe UI", 8))
        p.setPen(QColor(255, 160, 110)); p.drawText(10, y + 92, "<- Warm")
        p.setPen(QColor(110, 160, 255)); p.drawText(int(10 + 11 * tw), y + 92, "Cool ->")

        # Saturation scale
        y += 110
        h = self.base.hue() if self.base.hue() >= 0 else 0
        sat_colors = [QColor.fromHsv(h, int(255 * i / 8), self.base.value()) for i in range(9)]
        self._draw_scale(p, y, "Saturation Scale",
                         "From fully desaturated (gray) to fully saturated (vivid)", sat_colors)
        p.end()


# ═══════════════════════════════════════════════════════════════════════
#  COLOR BLINDNESS SIMULATION
# ═══════════════════════════════════════════════════════════════════════

class ColorBlindnessWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.base = QColor(0, 200, 200)
        self.setMinimumHeight(350)

    def set_color(self, c):
        self.base = c; self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        sw, sh = 110, 70

        sims = [
            ("Normal Vision", self.base, "Trichromatic - 3 cone types (most common)"),
            ("Protanopia", simulate_protanopia(self.base), "Red-blind - ~1.3% of males - No L-cones"),
            ("Deuteranopia", simulate_deuteranopia(self.base), "Green-blind - ~1.2% of males - No M-cones"),
            ("Tritanopia", simulate_tritanopia(self.base), "Blue-blind - ~0.001% - No S-cones"),
            ("Achromatopsia", simulate_achromatopsia(self.base), "Total colour blindness - ~0.003% - No cones"),
        ]

        tf = QFont(); tf.setPointSize(10); tf.setBold(True)
        df = QFont(); df.setPointSize(8)

        for i, (name, col, desc) in enumerate(sims):
            row, column = i // 3, i % 3
            x = 10 + column * (max(320, self.width()) // 3)
            y = 8 + row * 150

            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(QColor(0, 0, 0, 40)))
            p.drawRoundedRect(QRectF(x + 3, y + 3, sw, sh), 8, 8)

            p.setBrush(QBrush(col))
            p.drawRoundedRect(QRectF(x, y, sw, sh), 8, 8)
            p.setPen(QPen(QColor(90, 90, 110), 1)); p.setBrush(Qt.NoBrush)
            p.drawRoundedRect(QRectF(x, y, sw, sh), 8, 8)

            p.setFont(tf); p.setPen(QColor(210, 210, 230))
            p.drawText(x + sw + 12, y + 18, name)
            p.setFont(df); p.setPen(QColor(140, 140, 170))
            p.drawText(x + sw + 12, y + 36, desc)
            p.setPen(QColor(170, 170, 200))
            p.drawText(x + sw + 12, y + 54, f"Simulated: {col.name().upper()}")
        p.end()


# ═══════════════════════════════════════════════════════════════════════
#  PALETTE BLINDNESS CHECK
# ═══════════════════════════════════════════════════════════════════════

class PaletteBlindnessWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(180)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        ui_colors = [("Success", QColor(76, 175, 80)), ("Warning", QColor(255, 193, 7)),
                     ("Error", QColor(244, 67, 54)), ("Info", QColor(33, 150, 243)),
                     ("Link", QColor(103, 58, 183))]
        sims = [("Normal", lambda c: c), ("Protanopia", simulate_protanopia),
                ("Deuteranopia", simulate_deuteranopia), ("Tritanopia", simulate_tritanopia),
                ("Achromat.", simulate_achromatopsia)]
        sw, sh = 72, 28
        tf = QFont(); tf.setPointSize(8); tf.setBold(True)
        hf = QFont(); hf.setPointSize(7)

        for ri, (sname, sfn) in enumerate(sims):
            y = ri * (sh + 24)
            p.setFont(tf); p.setPen(QColor(160, 160, 180))
            p.drawText(0, y + 14, sname)
            x = 82
            for name, col in ui_colors:
                sc = sfn(col)
                p.setPen(Qt.NoPen); p.setBrush(QBrush(sc))
                p.drawRoundedRect(QRectF(x, y, sw, sh), 4, 4)
                p.setFont(hf); p.setPen(QColor(190, 190, 210))
                p.drawText(QRectF(x, y + sh + 2, sw, 14), Qt.AlignCenter, name)
                x += sw + 10
        p.end()


# ═══════════════════════════════════════════════════════════════════════
#  CONTRAST CHECKER
# ═══════════════════════════════════════════════════════════════════════

class ContrastCheckerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.fg = QColor(255, 255, 255)
        self.bg = QColor(30, 30, 60)
        self._build()

    def _btn_style(self):
        return ("QPushButton{background:#2e2e50;color:#ddd;border:1px solid #4a4a6a;"
                "border-radius:5px;padding:6px 14px;font-weight:bold;font-size:11px}"
                "QPushButton:hover{background:#3e3e60}")

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setSpacing(14)

        t = QLabel("WCAG Contrast Ratio Checker")
        t.setFont(QFont("Segoe UI", 15, QFont.Bold))
        t.setStyleSheet("color:#ddd")
        lay.addWidget(t)

        info = QLabel(
            "Contrast measures the luminance difference between text and background.\n"
            "WCAG 2.1 AA requires >= 4.5:1 for normal text, >= 3:1 for large text.\n"
            "WCAG 2.1 AAA requires >= 7:1 for normal text, >= 4.5:1 for large text.")
        info.setWordWrap(True)
        info.setStyleSheet("color:#888;font-size:11px")
        lay.addWidget(info)

        row = QHBoxLayout()
        for attr, label, color in [("fg", "Foreground (Text)", self.fg),
                                    ("bg", "Background", self.bg)]:
            grp = QGroupBox(label)
            grp.setStyleSheet(
                "QGroupBox{color:#bbb;border:1px solid #444;border-radius:8px;"
                "margin-top:14px;padding-top:20px;font-weight:bold}"
                "QGroupBox::title{subcontrol-position:top left;padding:0 8px}")
            gl = QVBoxLayout(grp)
            prev = QLabel()
            prev.setFixedSize(80, 80)
            prev.setAutoFillBackground(True)
            pal = prev.palette(); pal.setColor(QPalette.Window, color); prev.setPalette(pal)
            gl.addWidget(prev, alignment=Qt.AlignCenter)
            hx = QLabel(color.name().upper())
            hx.setAlignment(Qt.AlignCenter); hx.setStyleSheet("color:#aaa;font-family:Consolas")
            gl.addWidget(hx)
            btn = QPushButton("Pick Color...")
            btn.setStyleSheet(self._btn_style())
            if attr == "fg":
                self._fg_prev, self._fg_hx = prev, hx
                btn.clicked.connect(self._pick_fg)
            else:
                self._bg_prev, self._bg_hx = prev, hx
                btn.clicked.connect(self._pick_bg)
            gl.addWidget(btn)

            # Quick presets
            preset_row = QHBoxLayout()
            if attr == "fg":
                for pc in [QColor(255, 255, 255), QColor(0, 0, 0),
                           QColor(200, 200, 200), QColor(50, 50, 50)]:
                    pb = QPushButton()
                    pb.setFixedSize(24, 24)
                    pb.setStyleSheet(f"background:{pc.name()};border:1px solid #666;border-radius:3px")
                    pb.clicked.connect(lambda _, c=pc: self._set_fg(c))
                    preset_row.addWidget(pb)
            else:
                for pc in [QColor(0, 0, 0), QColor(255, 255, 255),
                           QColor(30, 30, 60), QColor(240, 240, 240)]:
                    pb = QPushButton()
                    pb.setFixedSize(24, 24)
                    pb.setStyleSheet(f"background:{pc.name()};border:1px solid #666;border-radius:3px")
                    pb.clicked.connect(lambda _, c=pc: self._set_bg(c))
                    preset_row.addWidget(pb)
            gl.addLayout(preset_row)
            row.addWidget(grp)
        lay.addLayout(row)

        # Swap button
        swap_btn = QPushButton("Swap Foreground / Background")
        swap_btn.setStyleSheet(self._btn_style())
        swap_btn.clicked.connect(self._swap)
        lay.addWidget(swap_btn)

        self.result = QFrame()
        self.result.setStyleSheet("QFrame{background:#252540;border-radius:10px;padding:14px}")
        rl = QVBoxLayout(self.result)

        self.ratio_lbl = QLabel("21.0 : 1")
        self.ratio_lbl.setFont(QFont("Segoe UI", 30, QFont.Bold))
        self.ratio_lbl.setAlignment(Qt.AlignCenter)
        self.ratio_lbl.setStyleSheet("color:#4CAF50")
        rl.addWidget(self.ratio_lbl)

        self.preview_lbl = QLabel("The quick brown fox jumps over the lazy dog. 0123456789")
        self.preview_lbl.setFont(QFont("Segoe UI", 14))
        self.preview_lbl.setAlignment(Qt.AlignCenter)
        self.preview_lbl.setWordWrap(True)
        self.preview_lbl.setStyleSheet("padding:12px;border-radius:6px")
        rl.addWidget(self.preview_lbl)

        self.preview_large = QLabel("Large Text Sample")
        self.preview_large.setFont(QFont("Segoe UI", 22, QFont.Bold))
        self.preview_large.setAlignment(Qt.AlignCenter)
        self.preview_large.setStyleSheet("padding:10px;border-radius:6px")
        rl.addWidget(self.preview_large)

        badges = QHBoxLayout()
        self.badges = {}
        for key in ("AA Normal", "AA Large", "AAA Normal", "AAA Large"):
            l = QLabel(f"{key}: -")
            l.setAlignment(Qt.AlignCenter)
            l.setStyleSheet("color:#aaa;font-weight:bold;font-size:11px;padding:5px 8px;"
                            "border-radius:4px;background:#1a1a30")
            badges.addWidget(l)
            self.badges[key] = l
        rl.addLayout(badges)
        lay.addWidget(self.result)
        lay.addStretch()
        self._refresh()

    def _pick_fg(self):
        c = QColorDialog.getColor(self.fg, self, "Foreground Colour")
        if c.isValid():
            self.fg = c; self._refresh()

    def _pick_bg(self):
        c = QColorDialog.getColor(self.bg, self, "Background Colour")
        if c.isValid():
            self.bg = c; self._refresh()

    def _set_fg(self, c):
        self.fg = c; self._refresh()

    def _set_bg(self, c):
        self.bg = c; self._refresh()

    def _swap(self):
        self.fg, self.bg = self.bg, self.fg; self._refresh()

    def _refresh(self):
        for prev, hx, c in [(self._fg_prev, self._fg_hx, self.fg),
                             (self._bg_prev, self._bg_hx, self.bg)]:
            pal = prev.palette(); pal.setColor(QPalette.Window, c); prev.setPalette(pal)
            hx.setText(c.name().upper())

        ratio = contrast_ratio(self.fg, self.bg)
        self.ratio_lbl.setText(f"{ratio:.2f} : 1")
        colour = "#4CAF50" if ratio >= 7 else "#8BC34A" if ratio >= 4.5 else "#FF9800" if ratio >= 3 else "#F44336"
        self.ratio_lbl.setStyleSheet(f"color:{colour};font-size:30px;font-weight:bold")

        self.preview_lbl.setStyleSheet(
            f"color:{self.fg.name()};background:{self.bg.name()};padding:12px;border-radius:6px")
        self.preview_large.setStyleSheet(
            f"color:{self.fg.name()};background:{self.bg.name()};padding:10px;border-radius:6px")

        checks = {"AA Normal": ratio >= 4.5, "AA Large": ratio >= 3,
                  "AAA Normal": ratio >= 7, "AAA Large": ratio >= 4.5}
        for k, v in checks.items():
            sym = "PASS" if v else "FAIL"
            c = "#4CAF50" if v else "#F44336"
            bg = "#1a3a1a" if v else "#3a1a1a"
            self.badges[k].setText(f"{k}: {sym}")
            self.badges[k].setStyleSheet(
                f"color:{c};font-weight:bold;font-size:11px;padding:5px 8px;"
                f"border-radius:4px;background:{bg}")


# ═══════════════════════════════════════════════════════════════════════
#  HSL / HSV EXPLORER
# ═══════════════════════════════════════════════════════════════════════

class HSLExplorerWidget(QWidget):
    colorChanged = Signal(QColor)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setSpacing(12)

        t = QLabel("HSL / HSV Colour Explorer")
        t.setFont(QFont("Segoe UI", 15, QFont.Bold)); t.setStyleSheet("color:#ddd")
        lay.addWidget(t)
        d = QLabel(
            "Drag the sliders to see how Hue, Saturation, and Value interact.\n"
            "H = which colour  |  S = intensity / purity  |  V = brightness / lightness")
        d.setWordWrap(True); d.setStyleSheet("color:#888;font-size:11px")
        lay.addWidget(d)

        # Preview + complementary
        prev_row = QHBoxLayout()
        self.preview = QLabel("Selected"); self.preview.setFixedSize(180, 80)
        self.preview.setAutoFillBackground(True); self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setFont(QFont("Consolas", 10, QFont.Bold))
        self.preview.setStyleSheet("border-radius:8px;border:2px solid #555")
        prev_row.addWidget(self.preview, alignment=Qt.AlignCenter)

        arrow = QLabel("<->"); arrow.setFont(QFont("Segoe UI", 18)); arrow.setStyleSheet("color:#666")
        prev_row.addWidget(arrow, alignment=Qt.AlignCenter)

        self.comp_preview = QLabel("Complement"); self.comp_preview.setFixedSize(180, 80)
        self.comp_preview.setAutoFillBackground(True); self.comp_preview.setAlignment(Qt.AlignCenter)
        self.comp_preview.setFont(QFont("Consolas", 10, QFont.Bold))
        self.comp_preview.setStyleSheet("border-radius:8px;border:2px solid #555")
        prev_row.addWidget(self.comp_preview, alignment=Qt.AlignCenter)
        lay.addLayout(prev_row)

        # Info labels
        self.hex_lbl = QLabel("#00C8C8")
        self.hex_lbl.setFont(QFont("Consolas", 14, QFont.Bold))
        self.hex_lbl.setAlignment(Qt.AlignCenter); self.hex_lbl.setStyleSheet("color:#aaa")
        lay.addWidget(self.hex_lbl)

        self.rgb_lbl = QLabel("R: 0  G: 200  B: 200")
        self.rgb_lbl.setAlignment(Qt.AlignCenter)
        self.rgb_lbl.setStyleSheet("color:#777;font-size:10px;font-family:Consolas")
        lay.addWidget(self.rgb_lbl)

        self.hsl_lbl = QLabel("H: 180  S: 100%  L: 39%")
        self.hsl_lbl.setAlignment(Qt.AlignCenter)
        self.hsl_lbl.setStyleSheet("color:#777;font-size:10px;font-family:Consolas")
        lay.addWidget(self.hsl_lbl)

        self.hsv_lbl = QLabel("HSV: 180 100% 100%")
        self.hsv_lbl.setAlignment(Qt.AlignCenter)
        self.hsv_lbl.setStyleSheet("color:#777;font-size:10px;font-family:Consolas")
        lay.addWidget(self.hsv_lbl)

        # Sliders
        self.sliders = {}
        slider_defs = [("Hue (H)", 0, 359, 180),
                       ("Saturation (S)", 0, 255, 255),
                       ("Value / Brightness (V)", 0, 255, 255)]
        for name, lo, hi, default in slider_defs:
            r = QHBoxLayout()
            lbl = QLabel(name + ":"); lbl.setFixedWidth(150)
            lbl.setStyleSheet("color:#ccc;font-weight:bold;font-size:11px"); r.addWidget(lbl)
            sl = QSlider(Qt.Horizontal); sl.setRange(lo, hi); sl.setValue(default)
            sl.valueChanged.connect(self._update); r.addWidget(sl)
            val = QLabel(""); val.setFixedWidth(50)
            val.setStyleSheet("color:#aaa;font-family:Consolas;font-size:11px"); r.addWidget(val)
            lay.addLayout(r)
            self.sliders[name] = (sl, val)

        # Explanation
        concept = QLabel(
            "HSV vs HSL: In HSV, V=100% means the brightest version of that hue. "
            "In HSL, L=50% is the purest hue; L=100% is always white. "
            "HSV is used in color pickers; HSL is common in CSS.")
        concept.setWordWrap(True)
        concept.setStyleSheet("color:#999;font-size:10px;background:#252540;padding:10px;border-radius:6px")
        lay.addWidget(concept)

        lay.addStretch()
        self._update()

    def set_color(self, c):
        h = c.hue() if c.hue() >= 0 else 0
        for s, _ in self.sliders.values():
            s.blockSignals(True)
        self.sliders["Hue (H)"][0].setValue(h)
        self.sliders["Saturation (S)"][0].setValue(c.saturation())
        self.sliders["Value / Brightness (V)"][0].setValue(c.value())
        for s, _ in self.sliders.values():
            s.blockSignals(False)
        self._update()

    def _update(self):
        h = self.sliders["Hue (H)"][0].value()
        s = self.sliders["Saturation (S)"][0].value()
        v = self.sliders["Value / Brightness (V)"][0].value()
        c = QColor.fromHsv(h, s, v)

        # Update previews - use QColor instead of Qt.white/Qt.black
        pal = self.preview.palette(); pal.setColor(QPalette.Window, c); self.preview.setPalette(pal)
        fg = QColor(255, 255, 255) if c.lightness() < 150 else QColor(0, 0, 0)
        self.preview.setStyleSheet(
            f"border-radius:8px;border:2px solid #555;color:{fg.name()}")
        self.preview.setText(c.name().upper())

        comp = QColor.fromHsv((h + 180) % 360, s, v)
        pal2 = self.comp_preview.palette(); pal2.setColor(QPalette.Window, comp); self.comp_preview.setPalette(pal2)
        fg2 = QColor(255, 255, 255) if comp.lightness() < 150 else QColor(0, 0, 0)
        self.comp_preview.setStyleSheet(
            f"border-radius:8px;border:2px solid #555;color:{fg2.name()}")
        self.comp_preview.setText(comp.name().upper())

        self.hex_lbl.setText(f"{c.name().upper()}  |  Complement: {comp.name().upper()}")
        self.rgb_lbl.setText(f"R: {c.red():3d}   G: {c.green():3d}   B: {c.blue():3d}")

        # Calculate HSL
        r, g, b = c.redF(), c.greenF(), c.blueF()
        mx, mn = max(r, g, b), min(r, g, b)
        l_val = (mx + mn) / 2
        if mx == mn:
            s_hsl = 0.0
        else:
            d = mx - mn
            s_hsl = d / (2 - mx - mn) if l_val > 0.5 else d / (mx + mn)
        self.hsl_lbl.setText(f"HSL:  H: {h}   S: {int(s_hsl * 100)}%  L: {int(l_val * 100)}%")
        self.hsv_lbl.setText(f"HSV:  H: {h}   S: {int(s / 255 * 100)}%  V: {int(v / 255 * 100)}%")

        self.sliders["Hue (H)"][1].setText(f"{h} deg")
        self.sliders["Saturation (S)"][1].setText(f"{int(s / 255 * 100)}%")
        self.sliders["Value / Brightness (V)"][1].setText(f"{int(v / 255 * 100)}%")

        self.colorChanged.emit(c)


# ═══════════════════════════════════════════════════════════════════════
#  THEORY GUIDE PAGE
# ═══════════════════════════════════════════════════════════════════════

class TheoryPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)

        header = QLabel("Understanding Colour Theory")
        header.setFont(QFont("Segoe UI", 18, QFont.Bold))
        header.setStyleSheet("color:#e0e0f0;padding:14px 14px 4px 14px")
        lay.addWidget(header)

        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea{border:none;background:transparent}")
        content = QWidget(); cl = QVBoxLayout(content); cl.setSpacing(14)

        sections = [
            ("The Colour Wheel",
             "The colour wheel arranges hues in a circle showing their relationships. "
             "Isaac Newton created the first circular diagram in 1666 by splitting sunlight "
             "through a prism. The wheel reveals harmonies - patterns of colours that look "
             "pleasing together - based on geometric relationships.\n\n"
             "The wheel has 12 main segments: 3 primaries, 3 secondaries, and 6 tertiaries. "
             "Understanding the wheel is the foundation of all colour theory."),

            ("Primary Colours",
             "Primary colours cannot be mixed from other colours - they are the building blocks.\n\n"
             "RGB (Additive / Light): Red, Green, Blue. Used in screens & lighting. "
             "All three combined make White.\n"
             "RYB (Subtractive / Paint): Red, Yellow, Blue. Used in traditional art. "
             "All three combined make a dark brown/black.\n"
             "CMYK (Print): Cyan, Magenta, Yellow, Key (Black). Used in printing."),

            ("Secondary Colours",
             "Made by mixing two primary colours in equal proportion:\n\n"
             "RGB model: Cyan (Green+Blue), Magenta (Red+Blue), Yellow (Red+Green)\n"
             "RYB model: Orange (Red+Yellow), Green (Yellow+Blue), Purple (Red+Blue)\n\n"
             "Secondaries sit between their parent primaries on the colour wheel."),

            ("Tertiary Colours",
             "Made by mixing a primary with an adjacent secondary (e.g. Red-Orange, Yellow-Green). "
             "There are 6 tertiary colours per model, filling the wheel to create 12 distinct segments.\n\n"
             "Tertiary colours are often named with the primary first: Red-Orange, not Orange-Red. "
             "This naming convention indicates which primary dominates."),

            ("Colour Temperature",
             "Warm colours (red to yellow) advance toward the viewer and evoke energy, passion, "
             "warmth, urgency. Cool colours (blue to green) recede and evoke calm, trust, serenity, "
             "professionalism.\n\n"
             "Temperature is relative - a blue can be 'warm' if it leans toward violet, "
             "and a green can be 'cool' if it leans toward blue-green. Designers use temperature "
             "to create depth, mood, and focal points."),

            ("Value, Saturation & Chroma",
             "Value (Lightness): How light or dark a colour is. Tints = hue + white. "
             "Shades = hue + black. High-value palettes feel airy; low-value palettes feel dramatic.\n"
             "Saturation (Chroma): Intensity or purity of a colour. Tones = hue + gray. "
             "Desaturated colours feel muted and sophisticated; saturated colours feel vivid and energetic.\n"
             "Hue: The colour family name (red, blue, green, etc.)."),

            ("Simultaneous Contrast",
             "A colour appears different depending on its neighbours. Grey on yellow looks "
             "purplish; grey on blue looks orange-ish. This optical illusion is one of the "
             "most important principles in colour theory, discovered by Michel Eugene Chevreul "
             "in 1839.\n\n"
             "Designers use this knowledge to make colours appear more vibrant by placing them "
             "next to their complements, or to create subtle variation without changing the actual colour."),

            ("The 60-30-10 Rule",
             "A classic interior design and branding guideline:\n"
             "60% - Dominant colour (background, large areas)\n"
             "30% - Secondary colour (furniture, sections)\n"
             "10% - Accent colour (highlights, calls to action)\n\n"
             "This creates visual hierarchy and prevents colour chaos. The accent is often "
             "a complementary or triadic colour for maximum impact."),

            ("Accessibility & Colour",
             "About 8% of men and 0.5% of women have colour-vision deficiency (CVD). "
             "The most common types are red-green blindness (protanopia & deuteranopia).\n\n"
             "Never rely on colour alone to convey meaning - add labels, patterns, or icons.\n"
             "Use contrast ratios >= 4.5:1 for body text (WCAG AA).\n"
             "Test your palettes with CVD simulators.\n"
             "Avoid red/green and blue/yellow combinations as sole differentiators."),

            ("Colour Psychology",
             "Colours evoke emotional and cultural associations:\n\n"
             "Red: Passion, urgency, danger, appetite (food brands)\n"
             "Blue: Trust, calm, professionalism (banks, tech)\n"
             "Yellow: Optimism, warmth, caution (warning signs)\n"
             "Green: Nature, growth, health, wealth\n"
             "Purple: Luxury, creativity, spirituality\n"
             "Orange: Energy, friendliness, affordability\n"
             "Black: Elegance, power, sophistication\n\n"
             "Note: These associations vary by culture. White means purity in Western cultures "
             "but mourning in some Eastern cultures."),
        ]

        for title, body in sections:
            f = QFrame()
            f.setStyleSheet("QFrame{background:#252540;border-radius:10px;padding:16px;"
                            "border:1px solid #333355}")
            fl = QVBoxLayout(f)
            h = QLabel(title); h.setFont(QFont("Segoe UI", 12, QFont.Bold))
            h.setStyleSheet("color:#c0c0e0;border:none"); fl.addWidget(h)
            b = QLabel(body); b.setWordWrap(True)
            b.setStyleSheet("color:#a0a0c0;font-size:11px;border:none"); fl.addWidget(b)
            cl.addWidget(f)

        cl.addStretch()
        scroll.setWidget(content)
        lay.addWidget(scroll)


# ═══════════════════════════════════════════════════════════════════════
#  MAIN WINDOW
# ═══════════════════════════════════════════════════════════════════════

class MainWindow(QMainWindow):
    PAGES = [
        ("Colour Wheel",     "wheel"),
        ("Harmonies",         "harmonies"),
        ("Colour Mixing",     "mixing"),
        ("Colour Properties", "properties"),
        ("HSL Explorer",      "hsl"),
        ("Accessibility",     "access"),
        ("Colour Blindness",  "blind"),
        ("Theory Guide",      "theory"),
    ]

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Color Theory Visualizer - Interactive Education")
        self.setMinimumSize(1020, 700)
        self.resize(1250, 830)
        self._color = QColor(0, 200, 200)
        self._apply_theme()
        self._build()

    def _apply_theme(self):
        self.setStyleSheet("""
            QMainWindow { background: #1a1a2e; }
            QWidget { background: #1a1a2e; color: #e0e0e0; }
            QPushButton {
                background: #2a2a4a; color: #e0e0e0;
                border: 1px solid #3a3a5a; border-radius: 8px;
                padding: 10px 14px; font-size: 12px; font-weight: bold; text-align: left;
            }
            QPushButton:hover { background: #3a3a5a; border-color: #5a5a8a; }
            QPushButton:checked { background: #4a4a7a; border-color: #7070b0; color: white; }
            QSlider::groove:horizontal {
                height: 8px; background: #333; border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #7070b0; border: none;
                width: 18px; height: 18px; margin: -5px 0; border-radius: 9px;
            }
            QSlider::handle:horizontal:hover { background: #9090d0; }
            QSlider::sub-page:horizontal { background: #5050a0; border-radius: 4px; }
            QScrollBar:vertical {
                background: #1a1a2e; width: 10px; border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #444; border-radius: 5px; min-height: 30px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
            QScrollBar:horizontal {
                background: #1a1a2e; height: 10px; border-radius: 5px;
            }
            QScrollBar::handle:horizontal {
                background: #444; border-radius: 5px; min-width: 30px;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
        """)

    def _build(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setSpacing(0)
        root.setContentsMargins(0, 0, 0, 0)

        # ── Sidebar ──
        sb = QFrame()
        sb.setFixedWidth(215)
        sb.setStyleSheet("QFrame{background:#12122a;border-right:1px solid #2a2a4a}")
        sl = QVBoxLayout(sb)
        sl.setContentsMargins(10, 16, 10, 14)
        sl.setSpacing(4)

        app_title = QLabel("Color Theory")
        app_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        app_title.setStyleSheet("color:#b0b0e0;padding:4px")
        sl.addWidget(app_title)

        app_sub = QLabel("Interactive Visualizer")
        app_sub.setStyleSheet("color:#6060a0;font-size:10px;padding:0 4px 14px 4px")
        sl.addWidget(app_sub)

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background:#2a2a4a")
        sl.addWidget(sep)

        self.nav_btns = []
        for text, pid in self.PAGES:
            b = QPushButton(text)
            b.setCheckable(True)
            b.setProperty("pid", pid)
            b.setMinimumHeight(38)
            b.clicked.connect(lambda _, p=pid: self._go(p))
            sl.addWidget(b)
            self.nav_btns.append(b)

        sl.addStretch(1)

        # Sidebar colour preview
        sep2 = QFrame()
        sep2.setFixedHeight(1)
        sep2.setStyleSheet("background:#2a2a4a")
        sl.addWidget(sep2)

        sel_label = QLabel("Selected Colour")
        sel_label.setStyleSheet("color:#7070a0;font-size:9px;padding:4px 2px 0 2px")
        sl.addWidget(sel_label)

        self.sb_prev = QLabel()
        self.sb_prev.setFixedHeight(40)
        self.sb_prev.setAutoFillBackground(True)
        self.sb_prev.setStyleSheet("border-radius:6px;border:1px solid #555")
        sl.addWidget(self.sb_prev)

        self.sb_hex = QLabel()
        self.sb_hex.setAlignment(Qt.AlignCenter)
        self.sb_hex.setStyleSheet("color:#777;font-size:10px;font-family:Consolas")
        sl.addWidget(self.sb_hex)

        root.addWidget(sb)

        # ── Stack ──
        self.stack = QStackedWidget()
        self._make_pages()
        root.addWidget(self.stack, 1)

        self._go("wheel")
        self._propagate()

    # ── Helpers ──
    def _page_frame(self):
        w = QWidget()
        w.setLayout(QVBoxLayout(w))
        w.layout().setContentsMargins(28, 18, 28, 18)
        w.layout().setSpacing(12)
        return w

    def _title_label(self, text, size=16):
        l = QLabel(text)
        l.setFont(QFont("Segoe UI", size, QFont.Bold))
        l.setStyleSheet("color:#e0e0f0")
        return l

    def _desc_label(self, text):
        l = QLabel(text)
        l.setWordWrap(True)
        l.setStyleSheet("color:#888;font-size:11px")
        return l

    def _wrap_scroll(self, widget):
        s = QScrollArea()
        s.setWidgetResizable(True)
        s.setWidget(widget)
        s.setStyleSheet("QScrollArea{border:none;background:transparent}")
        return s

    def _slider_row(self, label, lo, hi, val, callback):
        row = QHBoxLayout()
        lbl = QLabel(label)
        lbl.setFixedWidth(100)
        lbl.setStyleSheet("color:#ccc;font-weight:bold;font-size:11px")
        row.addWidget(lbl)
        sl = QSlider(Qt.Horizontal)
        sl.setRange(lo, hi)
        sl.setValue(val)
        sl.valueChanged.connect(callback)
        row.addWidget(sl)
        val_lbl = QLabel("")
        val_lbl.setFixedWidth(45)
        val_lbl.setStyleSheet("color:#aaa;font-family:Consolas;font-size:11px")
        row.addWidget(val_lbl)
        return row, sl, val_lbl

    # ── Build all pages ──
    def _make_pages(self):
        # ─── 0: Colour Wheel ───
        p = self._page_frame()
        body = QHBoxLayout()

        left = QWidget(); ll = QVBoxLayout(left); ll.setSpacing(8)
        ll.addWidget(self._title_label("Interactive Colour Wheel"))
        ll.addWidget(self._desc_label(
            "Click or drag the hue ring to pick a colour. Use the sliders below to adjust "
            "saturation and brightness. The selected colour carries to every other page in the app."))

        self.wheel = ColorWheelWidget()
        self.wheel.colorSelected.connect(self._on_wheel)
        ll.addWidget(self.wheel, alignment=Qt.AlignCenter)

        s_row, self.sat_sl, self.sat_val = self._slider_row("Saturation", 0, 255, 255, self._on_sat)
        ll.addLayout(s_row)
        v_row, self.val_sl, self.val_val = self._slider_row("Brightness", 0, 255, 255, self._on_val)
        ll.addLayout(v_row)
        ll.addStretch()
        body.addWidget(left, 3)

        right = QWidget(); rl = QVBoxLayout(right); rl.setSpacing(8)
        rl.addWidget(self._title_label("Colour Info", 13))

        self.wheel_info = QFrame()
        self.wheel_info.setStyleSheet("QFrame{background:#252540;border-radius:10px;padding:14px;border:1px solid #333355}")
        info_l = QVBoxLayout(self.wheel_info)
        self.wheel_swatch = QLabel()
        self.wheel_swatch.setFixedSize(200, 100)
        self.wheel_swatch.setAutoFillBackground(True)
        self.wheel_swatch.setStyleSheet("border-radius:8px")
        info_l.addWidget(self.wheel_swatch, alignment=Qt.AlignCenter)
        self.wheel_hex = QLabel()
        self.wheel_hex.setFont(QFont("Consolas", 16, QFont.Bold))
        self.wheel_hex.setAlignment(Qt.AlignCenter)
        self.wheel_hex.setStyleSheet("color:#ddd")
        info_l.addWidget(self.wheel_hex)
        self.wheel_rgb = QLabel()
        self.wheel_rgb.setAlignment(Qt.AlignCenter)
        self.wheel_rgb.setStyleSheet("color:#888;font-family:Consolas;font-size:11px")
        info_l.addWidget(self.wheel_rgb)
        self.wheel_hsl_info = QLabel()
        self.wheel_hsl_info.setAlignment(Qt.AlignCenter)
        self.wheel_hsl_info.setStyleSheet("color:#888;font-family:Consolas;font-size:11px")
        info_l.addWidget(self.wheel_hsl_info)
        rl.addWidget(self.wheel_info)

        # Complement display
        self.wheel_comp_frame = QFrame()
        self.wheel_comp_frame.setStyleSheet("QFrame{background:#252540;border-radius:10px;padding:14px;border:1px solid #333355}")
        comp_l = QVBoxLayout(self.wheel_comp_frame)
        comp_title = QLabel("Complementary Colour")
        comp_title.setFont(QFont("Segoe UI", 10, QFont.Bold))
        comp_title.setStyleSheet("color:#aaa")
        comp_l.addWidget(comp_title)
        self.wheel_comp_swatch = QLabel()
        self.wheel_comp_swatch.setFixedSize(200, 60)
        self.wheel_comp_swatch.setAutoFillBackground(True)
        self.wheel_comp_swatch.setStyleSheet("border-radius:8px")
        comp_l.addWidget(self.wheel_comp_swatch, alignment=Qt.AlignCenter)
        self.wheel_comp_hex = QLabel()
        self.wheel_comp_hex.setFont(QFont("Consolas", 12, QFont.Bold))
        self.wheel_comp_hex.setAlignment(Qt.AlignCenter)
        self.wheel_comp_hex.setStyleSheet("color:#aaa")
        comp_l.addWidget(self.wheel_comp_hex)
        rl.addWidget(self.wheel_comp_frame)
        rl.addStretch()
        body.addWidget(right, 2)

        p.layout().addLayout(body)
        self.stack.addWidget(self._wrap_scroll(p))

        # ─── 1: Harmonies ───
        p2 = self._page_frame()
        p2.layout().addWidget(self._title_label("Colour Harmonies"))
        p2.layout().addWidget(self._desc_label(
            "Colour harmonies are proven combinations based on geometric relationships on the colour wheel. "
            "Each harmony creates a different mood and level of contrast. The base colour is your current selection."))
        self.harmony_widget = HarmonyWidget()
        p2.layout().addWidget(self.harmony_widget)
        self.stack.addWidget(self._wrap_scroll(p2))

        # ─── 2: Colour Mixing ───
        p3 = self._page_frame()
        p3.layout().addWidget(self._title_label("Colour Mixing Models"))
        p3.layout().addWidget(self._desc_label(
            "Understanding additive and subtractive mixing is fundamental. "
            "Additive mixing (light) combines RGB to make white - used in screens. "
            "Subtractive mixing (pigment) combines RYB to make dark - used in paint and print."))
        self.mixing_widget = ColorMixingWidget()
        p3.layout().addWidget(self.mixing_widget)
        self.stack.addWidget(self._wrap_scroll(p3))

        # ─── 3: Colour Properties ───
        p4 = self._page_frame()
        p4.layout().addWidget(self._title_label("Colour Properties"))
        p4.layout().addWidget(self._desc_label(
            "Every hue can be modified in three ways: add white to create tints, "
            "add black to create shades, or add gray to create tones. "
            "Saturation controls intensity, and temperature shifts the warm/cool balance."))
        self.props_widget = ColorPropertiesWidget()
        p4.layout().addWidget(self.props_widget)
        self.stack.addWidget(self._wrap_scroll(p4))

        # ─── 4: HSL Explorer ───
        p5 = self._page_frame()
        self.hsl_explorer = HSLExplorerWidget()
        self.hsl_explorer.colorChanged.connect(self._on_hsl_change)
        p5.layout().addWidget(self.hsl_explorer)
        self.stack.addWidget(self._wrap_scroll(p5))

        # ─── 5: Accessibility ───
        p6 = self._page_frame()
        self.contrast_checker = ContrastCheckerWidget()
        p6.layout().addWidget(self.contrast_checker)
        self.stack.addWidget(p6)

        # ─── 6: Colour Blindness ───
        p7 = self._page_frame()
        p7.layout().addWidget(self._title_label("Colour Blindness Simulation"))
        p7.layout().addWidget(self._desc_label(
            "See how your selected colour appears to people with different types of colour vision deficiency. "
            "The palette below shows common UI colours through each type of colour blindness."))
        self.blindness_widget = ColorBlindnessWidget()
        p7.layout().addWidget(self.blindness_widget)

        p7.layout().addWidget(self._title_label("UI Palette Under Colour Blindness", 12))
        p7.layout().addWidget(self._desc_label(
            "Notice how Success (green) and Error (red) become nearly indistinguishable "
            "under protanopia and deuteranopia - this is why colour alone should never convey meaning."))
        self.palette_blindness = PaletteBlindnessWidget()
        p7.layout().addWidget(self.palette_blindness)
        self.stack.addWidget(self._wrap_scroll(p7))

        # ─── 7: Theory Guide ───
        p8 = TheoryPage()
        self.stack.addWidget(p8)

    # ── Navigation ──
    def _go(self, pid):
        idx = next(i for i, (_, p) in enumerate(self.PAGES) if p == pid)
        self.stack.setCurrentIndex(idx)
        for b in self.nav_btns:
            b.setChecked(b.property("pid") == pid)

    # ── Color propagation ──
    def _set_color(self, c):
        self._color = c
        self._propagate()

    def _propagate(self):
        c = self._color
        # Sidebar
        pal = self.sb_prev.palette()
        pal.setColor(QPalette.Window, c)
        self.sb_prev.setPalette(pal)
        self.sb_hex.setText(c.name().upper())

        # Wheel page info
        pal2 = self.wheel_swatch.palette()
        pal2.setColor(QPalette.Window, c)
        self.wheel_swatch.setPalette(pal2)
        self.wheel_hex.setText(c.name().upper())
        self.wheel_rgb.setText(f"R: {c.red()}  G: {c.green()}  B: {c.blue()}")
        h = c.hue() if c.hue() >= 0 else 0
        self.wheel_hsl_info.setText(f"H: {h}  S: {c.saturation()}  V: {c.value()}")

        # Complement
        comp = QColor.fromHsv((h + 180) % 360, c.saturation(), c.value())
        pal3 = self.wheel_comp_swatch.palette()
        pal3.setColor(QPalette.Window, comp)
        self.wheel_comp_swatch.setPalette(pal3)
        self.wheel_comp_hex.setText(comp.name().upper())

        # Other widgets
        self.harmony_widget.set_color(c)
        self.props_widget.set_color(c)
        self.blindness_widget.set_color(c)

    # ── Slot: wheel picked ──
    def _on_wheel(self, c):
        self._set_color(c)

    # ── Slot: saturation slider ──
    def _on_sat(self, v):
        self.sat_val.setText(f"{int(v / 255 * 100)}%")
        self.wheel.set_sat_val(v, self.val_sl.value())
        self._set_color(self.wheel.get_color())

    # ── Slot: value slider ──
    def _on_val(self, v):
        self.val_val.setText(f"{int(v / 255 * 100)}%")
        self.wheel.set_sat_val(self.sat_sl.value(), v)
        self._set_color(self.wheel.get_color())

    # ── Slot: HSL explorer changed ──
    def _on_hsl_change(self, c):
        self._set_color(c)
        # Sync wheel
        h = c.hue() if c.hue() >= 0 else 0
        self.wheel.set_hue(h)
        self.wheel.set_sat_val(c.saturation(), c.value())
        self.sat_sl.blockSignals(True)
        self.val_sl.blockSignals(True)
        self.sat_sl.setValue(c.saturation())
        self.val_sl.setValue(c.value())
        self.sat_sl.blockSignals(False)
        self.val_sl.blockSignals(False)
        self.sat_val.setText(f"{int(c.saturation() / 255 * 100)}%")
        self.val_val.setText(f"{int(c.value() / 255 * 100)}%")


# ═══════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Dark palette
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(26, 26, 46))
    palette.setColor(QPalette.WindowText, QColor(224, 224, 224))
    palette.setColor(QPalette.Base, QColor(18, 18, 42))
    palette.setColor(QPalette.AlternateBase, QColor(30, 30, 55))
    palette.setColor(QPalette.ToolTipBase, QColor(30, 30, 55))
    palette.setColor(QPalette.ToolTipText, QColor(224, 224, 224))
    palette.setColor(QPalette.Text, QColor(224, 224, 224))
    palette.setColor(QPalette.Button, QColor(42, 42, 74))
    palette.setColor(QPalette.ButtonText, QColor(224, 224, 224))
    palette.setColor(QPalette.BrightText, QColor(255, 255, 255))
    palette.setColor(QPalette.Highlight, QColor(90, 90, 170))
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()