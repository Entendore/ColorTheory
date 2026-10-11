from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont


class ColorPropertiesWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.base = QColor(0, 200, 200)
        self.setMinimumHeight(500)

    def set_color(self, c):
        self.base = QColor(c)  # FIX: store a copy
        self.update()

    def _draw_scale(self, p, y, title, desc, colors):
        sw, sh, sp = 50, 50, 7
        tf = QFont()
        tf.setPointSize(11)
        tf.setBold(True)
        df = QFont()
        df.setPointSize(8)
        hf = QFont()
        hf.setPointSize(8)
        p.setFont(tf)
        p.setPen(QColor(210, 210, 230))
        p.drawText(10, y + 14, title)
        p.setFont(df)
        p.setPen(QColor(140, 140, 170))
        p.drawText(10, y + 30, desc)
        x = 10
        for c in colors:
            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(c))
            p.drawRoundedRect(QRectF(x, y + 40, sw, sh), 4, 4)
            p.setPen(QPen(QColor(70, 70, 90), 1))
            p.setBrush(Qt.NoBrush)
            p.drawRoundedRect(QRectF(x, y + 40, sw, sh), 4, 4)
            p.setFont(hf)
            p.setPen(QColor(155, 155, 180))
            p.drawText(
                QRectF(x - 2, y + 40 + sh + 2, sw + 4, 13),
                Qt.AlignCenter,
                c.name().upper(),
            )
            x += sw + sp

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        r, g, b = self.base.red(), self.base.green(), self.base.blue()
        y = 8

        tints = [
            QColor(
                int(r + (255 - r) * i / 8),
                int(g + (255 - g) * i / 8),
                int(b + (255 - b) * i / 8),
            )
            for i in range(9)
        ]
        self._draw_scale(
            p, y, "Tints  (adding white)",
            "Lighter, softer versions - increase value, reduce contrast",
            tints,
        )
        y += 115

        shades = [
            QColor(
                int(r * (1 - i / 8)),
                int(g * (1 - i / 8)),
                int(b * (1 - i / 8)),
            )
            for i in range(9)
        ]
        self._draw_scale(
            p, y, "Shades  (adding black)",
            "Darker, richer versions - deepen and add drama",
            shades,
        )
        y += 115

        gr = 128
        tones = [
            QColor(
                int(r + (gr - r) * i / 8),
                int(g + (gr - g) * i / 8),
                int(b + (gr - b) * i / 8),
            )
            for i in range(9)
        ]
        self._draw_scale(
            p, y, "Tones  (adding gray)",
            "Muted, subtle versions - reduced intensity, sophisticated feel",
            tones,
        )
        y += 115

        tf = QFont()
        tf.setPointSize(11)
        tf.setBold(True)
        p.setFont(tf)
        p.setPen(QColor(210, 210, 230))
        p.drawText(10, y + 14, "Color Temperature Spectrum")
        df = QFont()
        df.setPointSize(8)
        p.setFont(df)
        p.setPen(QColor(140, 140, 170))
        p.drawText(
            10, y + 30,
            "Warm (red-yellow) advance & energize - "
            "Cool (blue-green) recede & calm - Temperature is relative",
        )
        tw = max(1, (min(800, self.width()) - 20) / 12)
        for i in range(12):
            c = QColor.fromHsv(i * 30, 200, 220)
            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(c))
            p.drawRoundedRect(QRectF(10 + i * tw, y + 44, tw - 2, 30), 3, 3)
        p.setFont(QFont("Segoe UI", 8))
        p.setPen(QColor(255, 160, 110))
        p.drawText(10, y + 92, "<- Warm")
        p.setPen(QColor(110, 160, 255))
        p.drawText(int(10 + 11 * tw), y + 92, "Cool ->")

        y += 110
        h = self.base.hue() if self.base.hue() >= 0 else 0  # FIX: achromatic guard
        sat_colors = [
            QColor.fromHsv(h, int(255 * i / 8), self.base.value())
            for i in range(9)
        ]
        self._draw_scale(
            p, y, "Saturation Scale",
            "From fully desaturated (gray) to fully saturated (vivid)",
            sat_colors,
        )
        p.end()