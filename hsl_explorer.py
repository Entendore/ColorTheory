from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont, QPalette


class HSLExplorerWidget(QWidget):
    colorChanged = Signal(QColor)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setSpacing(12)

        t = QLabel("HSL / HSV Colour Explorer")
        t.setFont(QFont("Segoe UI", 15, QFont.Bold))
        t.setStyleSheet("color:#ddd")
        lay.addWidget(t)

        d = QLabel(
            "Drag the sliders to see how Hue, Saturation, and Value interact.\n"
            "H = which colour  |  S = intensity / purity  |  V = brightness / lightness"
        )
        d.setWordWrap(True)
        d.setStyleSheet("color:#888;font-size:11px")
        lay.addWidget(d)

        prev_row = QHBoxLayout()
        self.preview = QLabel("Selected")
        self.preview.setFixedSize(180, 80)
        self.preview.setAutoFillBackground(True)
        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setFont(QFont("Consolas", 10, QFont.Bold))
        self.preview.setStyleSheet("border-radius:8px;border:2px solid #555")
        prev_row.addWidget(self.preview, alignment=Qt.AlignCenter)

        arrow = QLabel("↔")
        arrow.setFont(QFont("Segoe UI", 18))
        arrow.setStyleSheet("color:#666")
        prev_row.addWidget(arrow, alignment=Qt.AlignCenter)

        self.comp_preview = QLabel("Complement")
        self.comp_preview.setFixedSize(180, 80)
        self.comp_preview.setAutoFillBackground(True)
        self.comp_preview.setAlignment(Qt.AlignCenter)
        self.comp_preview.setFont(QFont("Consolas", 10, QFont.Bold))
        self.comp_preview.setStyleSheet("border-radius:8px;border:2px solid #555")
        prev_row.addWidget(self.comp_preview, alignment=Qt.AlignCenter)
        lay.addLayout(prev_row)

        self.hex_lbl = QLabel("#00C8C8")
        self.hex_lbl.setFont(QFont("Consolas", 14, QFont.Bold))
        self.hex_lbl.setAlignment(Qt.AlignCenter)
        self.hex_lbl.setStyleSheet("color:#aaa")
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

        self.sliders = {}
        slider_defs = [
            ("Hue (H)", 0, 359, 180),
            ("Saturation (S)", 0, 255, 255),
            ("Value / Brightness (V)", 0, 255, 255),
        ]
        for name, lo, hi, default in slider_defs:
            r = QHBoxLayout()
            lbl = QLabel(name + ":")
            lbl.setFixedWidth(150)
            lbl.setStyleSheet("color:#ccc;font-weight:bold;font-size:11px")
            r.addWidget(lbl)
            sl = QSlider(Qt.Horizontal)
            sl.setRange(lo, hi)
            sl.setValue(default)
            sl.valueChanged.connect(self._update)
            r.addWidget(sl)
            val = QLabel("")
            val.setFixedWidth(50)
            val.setStyleSheet("color:#aaa;font-family:Consolas;font-size:11px")
            r.addWidget(val)
            lay.addLayout(r)
            self.sliders[name] = (sl, val)

        concept = QLabel(
            "HSV vs HSL: In HSV, V=100% means the brightest version of that hue. "
            "In HSL, L=50% is the purest hue; L=100% is always white. "
            "HSV is used in color pickers; HSL is common in CSS."
        )
        concept.setWordWrap(True)
        concept.setStyleSheet(
            "color:#999;font-size:10px;background:#252540;"
            "padding:10px;border-radius:6px"
        )
        lay.addWidget(concept)

        lay.addStretch()
        self._update()

    # ── FIX: block colorChanged signal to prevent infinite recursion ──
    def set_color(self, c):
        h = c.hue() if c.hue() >= 0 else 0
        # Block ALL signals on self so colorChanged is NOT emitted
        # during programmatic update (prevents _propagate → set_color → loop)
        self.blockSignals(True)
        for s, _ in self.sliders.values():
            s.blockSignals(True)
        self.sliders["Hue (H)"][0].setValue(h)
        self.sliders["Saturation (S)"][0].setValue(c.saturation())
        self.sliders["Value / Brightness (V)"][0].setValue(c.value())
        self._update()
        for s, _ in self.sliders.values():
            s.blockSignals(False)
        self.blockSignals(False)

    def _update(self):
        h = self.sliders["Hue (H)"][0].value()
        s = self.sliders["Saturation (S)"][0].value()
        v = self.sliders["Value / Brightness (V)"][0].value()
        c = QColor.fromHsv(h, s, v)

        pal = self.preview.palette()
        pal.setColor(QPalette.Window, c)
        self.preview.setPalette(pal)
        fg = QColor(255, 255, 255) if c.lightness() < 150 else QColor(0, 0, 0)
        self.preview.setStyleSheet(
            f"border-radius:8px;border:2px solid #555;color:{fg.name()}"
        )
        self.preview.setText(c.name().upper())

        comp = QColor.fromHsv((h + 180) % 360, s, v)
        pal2 = self.comp_preview.palette()
        pal2.setColor(QPalette.Window, comp)
        self.comp_preview.setPalette(pal2)
        fg2 = QColor(255, 255, 255) if comp.lightness() < 150 else QColor(0, 0, 0)
        self.comp_preview.setStyleSheet(
            f"border-radius:8px;border:2px solid #555;color:{fg2.name()}"
        )
        self.comp_preview.setText(comp.name().upper())

        self.hex_lbl.setText(f"{c.name().upper()}  |  Complement: {comp.name().upper()}")
        self.rgb_lbl.setText(f"R: {c.red():3d}   G: {c.green():3d}   B: {c.blue():3d}")

        r, g, b = c.redF(), c.greenF(), c.blueF()
        mx, mn = max(r, g, b), min(r, g, b)
        l_val = (mx + mn) / 2
        if mx == mn:
            s_hsl = 0.0
        else:
            d = mx - mn
            s_hsl = d / (2 - mx - mn) if l_val > 0.5 else d / (mx + mn)
        self.hsl_lbl.setText(
            f"HSL:  H: {h}   S: {int(s_hsl * 100)}%  L: {int(l_val * 100)}%"
        )
        self.hsv_lbl.setText(
            f"HSV:  H: {h}   S: {int(s / 255 * 100)}%  V: {int(v / 255 * 100)}%"
        )

        self.sliders["Hue (H)"][1].setText(f"{h}°")
        self.sliders["Saturation (S)"][1].setText(f"{int(s / 255 * 100)}%")
        self.sliders["Value / Brightness (V)"][1].setText(f"{int(v / 255 * 100)}%")

        self.colorChanged.emit(c)