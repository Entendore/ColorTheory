import math
from PySide6.QtWidgets import QWidget, QSizePolicy
from PySide6.QtCore import Qt, Signal, QRectF, QPointF
from PySide6.QtGui import (
    QPainter, QColor, QPen, QBrush, QFont,
    QConicalGradient, QRadialGradient
)


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
        self.setCursor(Qt.PointingHandCursor)  # IMPROVEMENT: visual cursor hint

    def get_color(self):
        h = self._hue if self._hue >= 0 else 0
        return QColor.fromHsv(h, self._sat, self._val)

    def set_hue(self, h):
        self._hue = h % 360
        self.update()

    def set_sat_val(self, s, v):
        self._sat, self._val = s, v
        self.update()

    # IMPROVEMENT: combined setter avoids double repaint
    def set_hsv(self, h, s, v):
        self._hue = h % 360 if h >= 0 else 0
        self._sat, self._val = s, v
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        cx, cy = self.width() / 2, self.height() / 2
        outer_r = min(self.width(), self.height()) / 2 - 18
        inner_r = outer_r * 0.62

        # IMPROVEMENT: fewer gradient stops (60 is visually indistinguishable from 361)
        grad = QConicalGradient(QPointF(cx, cy), 0)
        for i in range(61):
            grad.setColorAt(i / 60.0, QColor.fromHsv(int(i * 6) % 360, 255, 255))
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(grad))
        p.drawEllipse(QPointF(cx, cy), outer_r, outer_r)

        inner_grad = QRadialGradient(QPointF(cx, cy), inner_r)
        inner_grad.setColorAt(0, QColor(35, 35, 55))
        inner_grad.setColorAt(1, QColor(22, 22, 38))
        p.setBrush(QBrush(inner_grad))
        p.drawEllipse(QPointF(cx, cy), inner_r, inner_r)

        col = self.get_color()
        disc_r = inner_r * 0.52
        p.setBrush(QBrush(col))
        p.setPen(QPen(QColor(255, 255, 255, 80), 2))
        p.drawEllipse(QPointF(cx, cy), disc_r, disc_r)

        p.setPen(
            QColor(255, 255, 255) if col.lightness() < 180
            else QColor(0, 0, 0)
        )
        f = p.font()
        f.setPointSize(12)
        f.setBold(True)
        p.setFont(f)
        p.drawText(
            QRectF(cx - 55, cy - 12, 110, 24), Qt.AlignCenter, col.name().upper()
        )

        hue = self._hue if self._hue >= 0 else 0
        a = math.radians(hue)
        mr = (outer_r + inner_r) / 2
        hx = cx + mr * math.cos(a)
        hy = cy + mr * math.sin(a)
        p.setPen(QPen(QColor(255, 255, 255), 3))
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(QPointF(hx, hy), 9, 9)
        p.setPen(QPen(QColor(0, 0, 0), 1.5))
        p.drawEllipse(QPointF(hx, hy), 9, 9)

        p.setPen(QColor(180, 180, 210, 180))
        f.setPointSize(7)
        f.setBold(False)
        p.setFont(f)
        labels = [
            (0, "0°"),  (30, "30°"),  (60, "60°"),  (90, "90°"),
            (120, "120°"), (150, "150°"), (180, "180°"), (210, "210°"),
            (240, "240°"), (270, "270°"), (300, "300°"), (330, "330°"),
        ]
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