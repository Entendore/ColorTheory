from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPainter, QColor, QBrush, QFont, QRadialGradient


class ColorMixingWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(420, 520)

    def _draw_mixing(self, p, cx, cy, radius, colors, labels, overlap_labels, title):
        tf = QFont()
        tf.setPointSize(12)
        tf.setBold(True)
        p.setFont(tf)
        p.setPen(QColor(240, 240, 255))
        p.drawText(
            QRectF(cx - 180, cy - radius - 40, 360, 28),
            Qt.AlignCenter, title,
        )

        offsets = [(-0.5, -0.3), (0.5, -0.3), (0.0, 0.35)]
        positions = [(cx + radius * ox, cy + radius * oy) for ox, oy in offsets]

        for i, (px, py) in enumerate(positions):
            g = QRadialGradient(px, py, radius * 0.9)
            c = colors[i]
            g.setColorAt(0, QColor(c.red(), c.green(), c.blue(), 180))
            g.setColorAt(1, QColor(c.red(), c.green(), c.blue(), 0))
            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(g))
            p.drawEllipse(QPointF(px, py), radius * 0.65, radius * 0.65)

        lf = QFont()
        lf.setPointSize(9)
        lf.setBold(True)
        p.setFont(lf)
        for i, (px, py) in enumerate(positions):
            p.setPen(QColor(240, 240, 255))
            p.drawText(
                QRectF(px - 28, py - 8, 56, 16),
                Qt.AlignCenter, labels[i],
            )

        sf = QFont()
        sf.setPointSize(7)
        p.setFont(sf)
        p.setPen(QColor(200, 200, 220, 200))
        mid01 = (
            (positions[0][0] + positions[1][0]) / 2,
            (positions[0][1] + positions[1][1]) / 2 - radius * 0.2,
        )
        mid02 = (
            (positions[0][0] + positions[2][0]) / 2 - radius * 0.14,
            (positions[0][1] + positions[2][1]) / 2 + 4,
        )
        mid12 = (
            (positions[1][0] + positions[2][0]) / 2 + radius * 0.14,
            (positions[1][1] + positions[2][1]) / 2 + 4,
        )
        center = (cx, cy + radius * 0.03)
        for (lx, ly), txt in zip(
            [mid01, mid02, mid12, center], overlap_labels
        ):
            p.drawText(QRectF(lx - 24, ly - 6, 48, 12), Qt.AlignCenter, txt)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        r = min(w / 3, h / 5) * 0.68

        self._draw_mixing(
            p, w / 2, h * 0.24, r,
            [QColor(255, 0, 0), QColor(0, 255, 0), QColor(0, 0, 255)],
            ["Red", "Green", "Blue"],
            ["Yellow", "Magenta", "Cyan", "White"],
            "Additive Mixing (Light - RGB Model)",
        )

        self._draw_mixing(
            p, w / 2, h * 0.68, r,
            [QColor(220, 40, 40), QColor(230, 210, 0), QColor(30, 60, 210)],
            ["Red", "Yellow", "Blue"],
            ["Orange", "Purple", "Green", "Dark"],
            "Subtractive Mixing (Paint - RYB Model)",
        )

        p.setFont(QFont("Segoe UI", 9))
        p.setPen(QColor(120, 120, 150))
        p.drawText(
            QRectF(10, h - 36, w - 20, 30), Qt.AlignCenter,
            "Additive = more light = brighter  |  "
            "Subtractive = more pigment = darker",
        )
        p.end()