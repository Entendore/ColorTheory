from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont
from utils import (
    simulate_protanopia, simulate_deuteranopia,
    simulate_tritanopia, simulate_achromatopsia,
)


class ColorBlindnessWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.base = QColor(0, 200, 200)
        self.setMinimumHeight(350)

    def set_color(self, c):
        self.base = QColor(c)  # FIX: store a copy
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        sw, sh = 110, 70
        sims = [
            ("Normal Vision", self.base, "Trichromatic - 3 cone types (most common)"),
            ("Protanopia", simulate_protanopia(self.base),
             "Red-blind - ~1.3% of males - No L-cones"),
            ("Deuteranopia", simulate_deuteranopia(self.base),
             "Green-blind - ~1.2% of males - No M-cones"),
            ("Tritanopia", simulate_tritanopia(self.base),
             "Blue-blind - ~0.001% - No S-cones"),
            ("Achromatopsia", simulate_achromatopsia(self.base),
             "Total colour blindness - ~0.003% - No cones"),
        ]

        tf = QFont()
        tf.setPointSize(10)
        tf.setBold(True)
        df = QFont()
        df.setPointSize(8)

        for i, (name, col, desc) in enumerate(sims):
            row, column = i // 3, i % 3
            x = 10 + column * (max(320, self.width()) // 3)
            y = 8 + row * 150

            # Shadow
            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(QColor(0, 0, 0, 40)))
            p.drawRoundedRect(QRectF(x + 3, y + 3, sw, sh), 8, 8)

            # Swatch
            p.setBrush(QBrush(col))
            p.drawRoundedRect(QRectF(x, y, sw, sh), 8, 8)
            p.setPen(QPen(QColor(90, 90, 110), 1))
            p.setBrush(Qt.NoBrush)
            p.drawRoundedRect(QRectF(x, y, sw, sh), 8, 8)

            # Labels
            p.setFont(tf)
            p.setPen(QColor(210, 210, 230))
            p.drawText(x + sw + 12, y + 18, name)
            p.setFont(df)
            p.setPen(QColor(140, 140, 170))
            p.drawText(x + sw + 12, y + 36, desc)
            p.setPen(QColor(170, 170, 200))
            p.drawText(x + sw + 12, y + 54, f"Simulated: {col.name().upper()}")

            # FIX: show hex on the swatch itself for quick comparison
            p.setFont(df)
            fg = (
                QColor(255, 255, 255) if col.lightness() < 128
                else QColor(0, 0, 0)
            )
            p.setPen(fg)
            p.drawText(QRectF(x, y + sh - 16, sw, 14), Qt.AlignCenter, col.name().upper())

        p.end()


class PaletteBlindnessWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # BUG FIX: 5 rows × (28 swatch + 14 label + 24 gap) = 330 minimum
        self.setMinimumHeight(330)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        ui_colors = [
            ("Success", QColor(76, 175, 80)),
            ("Warning", QColor(255, 193, 7)),
            ("Error", QColor(244, 67, 54)),
            ("Info", QColor(33, 150, 243)),
            ("Link", QColor(103, 58, 183)),
        ]
        sims = [
            ("Normal", lambda c: c),
            ("Protanopia", simulate_protanopia),
            ("Deuteranopia", simulate_deuteranopia),
            ("Tritanopia", simulate_tritanopia),
            ("Achromat.", simulate_achromatopsia),
        ]
        sw, sh = 72, 28
        tf = QFont()
        tf.setPointSize(8)
        tf.setBold(True)
        hf = QFont()
        hf.setPointSize(7)

        row_h = sh + 24  # swatch height + label + gap
        for ri, (sname, sfn) in enumerate(sims):
            y = ri * row_h
            p.setFont(tf)
            p.setPen(QColor(160, 160, 180))
            p.drawText(0, y + 14, sname)
            x = 82
            for name, col in ui_colors:
                sc = sfn(col)
                p.setPen(Qt.NoPen)
                p.setBrush(QBrush(sc))
                p.drawRoundedRect(QRectF(x, y, sw, sh), 4, 4)
                p.setFont(hf)
                p.setPen(QColor(190, 190, 210))
                p.drawText(
                    QRectF(x, y + sh + 2, sw, 14), Qt.AlignCenter, name
                )
                x += sw + 10
        p.end()