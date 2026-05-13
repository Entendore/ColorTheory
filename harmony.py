from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont


class HarmonyWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.base = QColor(0, 200, 200)
        self.setMinimumHeight(500)

    def set_color(self, c):
        self.base = QColor(c)  # FIX: store a copy
        self.update()

    def _harmonies(self):
        h = self.base.hue() if self.base.hue() >= 0 else 0
        s, v = self.base.saturation(), self.base.value()
        return [
            (
                "Complementary",
                "Two colors opposite on the wheel — maximum contrast & vibrancy. "
                "Great for call-to-action buttons.",
                [self.base, QColor.fromHsv((h + 180) % 360, s, v)],
            ),
            (
                "Analogous",
                "3-5 adjacent hues — naturally harmonious, common in nature. "
                "Use one dominant, others as accents.",
                [
                    QColor.fromHsv((h - 30) % 360, s, v),
                    QColor.fromHsv((h - 15) % 360, s, v),
                    self.base,
                    QColor.fromHsv((h + 15) % 360, s, v),
                    QColor.fromHsv((h + 30) % 360, s, v),
                ],
            ),
            (
                "Triadic",
                "Three equally-spaced hues (120° apart) — vibrant yet balanced. "
                "Let one colour dominate.",
                [
                    self.base,
                    QColor.fromHsv((h + 120) % 360, s, v),
                    QColor.fromHsv((h + 240) % 360, s, v),
                ],
            ),
            (
                "Split-Complementary",
                "Base + two neighbours of its complement — contrast with less "
                "tension than pure complementary.",
                [
                    self.base,
                    QColor.fromHsv((h + 150) % 360, s, v),
                    QColor.fromHsv((h + 210) % 360, s, v),
                ],
            ),
            (
                "Tetradic (Rectangle)",
                "Four colours in two complementary pairs — rich and versatile. "
                "Balance warm & cool tones.",
                [
                    self.base,
                    QColor.fromHsv((h + 60) % 360, s, v),
                    QColor.fromHsv((h + 180) % 360, s, v),
                    QColor.fromHsv((h + 240) % 360, s, v),
                ],
            ),
            (
                "Square",
                "Four evenly-spaced hues (90° apart) — bold and dynamic. "
                "Best with one dominant colour.",
                [
                    self.base,
                    QColor.fromHsv((h + 90) % 360, s, v),
                    QColor.fromHsv((h + 180) % 360, s, v),
                    QColor.fromHsv((h + 270) % 360, s, v),
                ],
            ),
        ]

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        sw, sh, sp = 50, 50, 7
        y = 8
        tf = QFont()
        tf.setPointSize(11)
        tf.setBold(True)
        df = QFont()
        df.setPointSize(8)
        hf = QFont()
        hf.setPointSize(8)

        for name, desc, colors in self._harmonies():
            p.setFont(tf)
            p.setPen(QColor(210, 210, 230))
            p.drawText(10, y + 14, name)
            p.setFont(df)
            p.setPen(QColor(140, 140, 170))
            p.drawText(10, y + 30, desc)
            x = 10
            for c in colors:
                p.setPen(Qt.NoPen)
                p.setBrush(QBrush(c))
                p.drawRoundedRect(QRectF(x, y + 40, sw, sh), 5, 5)
                p.setPen(QPen(QColor(80, 80, 100), 1))
                p.setBrush(Qt.NoBrush)
                p.drawRoundedRect(QRectF(x, y + 40, sw, sh), 5, 5)
                p.setFont(hf)
                p.setPen(QColor(160, 160, 190))
                p.drawText(
                    QRectF(x - 2, y + 40 + sh + 2, sw + 4, 14),
                    Qt.AlignCenter,
                    c.name().upper(),
                )
                x += sw + sp
            y += sh + 65
        p.end()