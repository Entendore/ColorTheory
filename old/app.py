import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QSlider, QFrame, QStackedWidget, QScrollArea
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPalette, QColor

from color_wheel import ColorWheelWidget
from harmony import HarmonyWidget
from color_mixing import ColorMixingWidget
from color_properties import ColorPropertiesWidget
from color_blindness import ColorBlindnessWidget, PaletteBlindnessWidget
from contrast_checker import ContrastCheckerWidget
from hsl_explorer import HSLExplorerWidget
from theory_page import TheoryPage


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

        left = QWidget()
        ll = QVBoxLayout(left)
        ll.setSpacing(8)
        ll.addWidget(self._title_label("Interactive Colour Wheel"))
        ll.addWidget(self._desc_label(
            "Click or drag the hue ring to pick a colour. Use the sliders below to adjust "
            "saturation and brightness. The selected colour carries to every other page in the app."
        ))

        self.wheel = ColorWheelWidget()
        self.wheel.colorSelected.connect(self._on_wheel)
        ll.addWidget(self.wheel, alignment=Qt.AlignCenter)

        s_row, self.sat_sl, self.sat_val = self._slider_row(
            "Saturation", 0, 255, 255, self._on_sat
        )
        ll.addLayout(s_row)
        v_row, self.val_sl, self.val_val = self._slider_row(
            "Brightness", 0, 255, 255, self._on_val
        )
        ll.addLayout(v_row)
        ll.addStretch()
        body.addWidget(left, 3)

        right = QWidget()
        rl = QVBoxLayout(right)
        rl.setSpacing(8)
        rl.addWidget(self._title_label("Colour Info", 13))

        self.wheel_info = QFrame()
        self.wheel_info.setStyleSheet(
            "QFrame{background:#252540;border-radius:10px;padding:14px;border:1px solid #333355}"
        )
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

        self.wheel_comp_frame = QFrame()
        self.wheel_comp_frame.setStyleSheet(
            "QFrame{background:#252540;border-radius:10px;padding:14px;border:1px solid #333355}"
        )
        comp_l = QVBoxLayout(self.wheel_comp_frame)
        comp_title = QLabel("Complementary Colour")
        comp_title.setFont(QFont("Segoe UI", 11, QFont.Bold))
        comp_title.setStyleSheet("color:#ccc;border:none")
        comp_l.addWidget(comp_title)
        self.wheel_comp_swatch = QLabel()
        self.wheel_comp_swatch.setFixedSize(200, 60)
        self.wheel_comp_swatch.setAutoFillBackground(True)
        self.wheel_comp_swatch.setAlignment(Qt.AlignCenter)
        self.wheel_comp_swatch.setFont(QFont("Consolas", 10, QFont.Bold))
        self.wheel_comp_swatch.setStyleSheet("border-radius:8px")
        comp_l.addWidget(self.wheel_comp_swatch, alignment=Qt.AlignCenter)
        rl.addWidget(self.wheel_comp_frame)

        rl.addStretch()
        body.addWidget(right, 2)
        p.layout().addLayout(body)
        self.stack.addWidget(self._wrap_scroll(p))

        # ─── 1: Harmonies ───
        p = self._page_frame()
        p.layout().addWidget(self._title_label("Colour Harmonies"))
        p.layout().addWidget(self._desc_label(
            "Harmonies are pleasing colour combinations based on geometric "
            "relationships on the colour wheel."
        ))
        self.harmony = HarmonyWidget()
        p.layout().addWidget(self.harmony)
        self.stack.addWidget(self._wrap_scroll(p))

        # ─── 2: Colour Mixing ───
        p = self._page_frame()
        p.layout().addWidget(self._title_label("Colour Mixing Models"))
        p.layout().addWidget(self._desc_label(
            "How primary colours combine to create new colours depends on the medium."
        ))
        self.mixing = ColorMixingWidget()
        p.layout().addWidget(self.mixing)
        self.stack.addWidget(self._wrap_scroll(p))

        # ─── 3: Colour Properties ───
        p = self._page_frame()
        p.layout().addWidget(self._title_label("Tints, Shades & Tones"))
        p.layout().addWidget(self._desc_label(
            "Modifying a base colour by adding white, black, or gray creates "
            "variations in value and intensity."
        ))
        self.properties = ColorPropertiesWidget()
        p.layout().addWidget(self.properties)
        self.stack.addWidget(self._wrap_scroll(p))

        # ─── 4: HSL Explorer ───
        p = self._page_frame()
        self.hsl_explorer = HSLExplorerWidget()
        self.hsl_explorer.colorChanged.connect(self._on_hsl_change)
        p.layout().addWidget(self.hsl_explorer)
        self.stack.addWidget(self._wrap_scroll(p))

        # ─── 5: Accessibility ───
        p = self._page_frame()
        p.layout().addWidget(self._title_label("Accessibility & Contrast"))
        p.layout().addWidget(self._desc_label(
            "Ensure your colour choices are readable and accessible to all users."
        ))
        self.contrast = ContrastCheckerWidget()
        p.layout().addWidget(self.contrast)
        self.stack.addWidget(self._wrap_scroll(p))

        # ─── 6: Colour Blindness ───
        p = self._page_frame()
        p.layout().addWidget(self._title_label("Colour Blindness Simulation"))
        p.layout().addWidget(self._desc_label(
            "See how your selected colour looks to people with different types "
            "of colour vision deficiency."
        ))
        self.blindness = ColorBlindnessWidget()
        p.layout().addWidget(self.blindness)
        p.layout().addWidget(self._title_label("UI Palette Simulation", 13))
        p.layout().addWidget(self._desc_label(
            "Common UI colours (Success, Warning, Error, Info, Link) as seen "
            "under different CVD types."
        ))
        self.palette_blindness = PaletteBlindnessWidget()
        p.layout().addWidget(self.palette_blindness)
        self.stack.addWidget(self._wrap_scroll(p))

        # ─── 7: Theory Guide ───
        p = self._page_frame()
        p.layout().setContentsMargins(0, 0, 0, 0)
        self.theory = TheoryPage()
        p.layout().addWidget(self.theory)
        self.stack.addWidget(p)

    # ── Navigation & State ──
    def _go(self, pid):
        idx = [p[1] for p in self.PAGES].index(pid)
        self.stack.setCurrentIndex(idx)
        for btn in self.nav_btns:
            btn.setChecked(btn.property("pid") == pid)

    def _on_wheel(self, color):
        self._color = QColor(color)  # FIX: store a copy, not a reference
        # FIX: block signals so setValue doesn't trigger _on_sat/_on_val → _propagate
        self.sat_sl.blockSignals(True)
        self.val_sl.blockSignals(True)
        self.sat_sl.setValue(color.saturation())
        self.val_sl.setValue(color.value())
        self.sat_sl.blockSignals(False)
        self.val_sl.blockSignals(False)
        self._propagate()

    def _on_sat(self, val):
        # FIX: handle achromatic (hue=-1) by defaulting to 0 (red)
        # FIX: create new QColor instead of mutating in place
        h = self._color.hue() if self._color.hue() >= 0 else 0
        self._color = QColor.fromHsv(h, val, self._color.value())
        self.wheel.set_sat_val(val, self._color.value())
        self._propagate()

    def _on_val(self, val):
        h = self._color.hue() if self._color.hue() >= 0 else 0
        self._color = QColor.fromHsv(h, self._color.saturation(), val)
        self.wheel.set_sat_val(self._color.saturation(), val)
        self._propagate()

    def _on_hsl_change(self, color):
        self._color = QColor(color)  # FIX: store a copy
        self.wheel.set_hsv(color.hue(), color.saturation(), color.value())  # FIX: single call
        # FIX: block signals so setValue doesn't trigger _on_sat/_on_val → _propagate
        self.sat_sl.blockSignals(True)
        self.val_sl.blockSignals(True)
        self.sat_sl.setValue(color.saturation())
        self.val_sl.setValue(color.value())
        self.sat_sl.blockSignals(False)
        self.val_sl.blockSignals(False)
        self._propagate()

    def _propagate(self):
        c = self._color
        h = c.hue() if c.hue() >= 0 else 0

        # Sidebar
        pal = self.sb_prev.palette()
        pal.setColor(QPalette.Window, c)
        self.sb_prev.setPalette(pal)
        self.sb_hex.setText(c.name().upper())

        # Wheel page
        pal = self.wheel_swatch.palette()
        pal.setColor(QPalette.Window, c)
        self.wheel_swatch.setPalette(pal)
        self.wheel_hex.setText(c.name().upper())
        self.wheel_rgb.setText(
            f"R: {c.red():3d}   G: {c.green():3d}   B: {c.blue():3d}"
        )

        r, g, b = c.redF(), c.greenF(), c.blueF()
        mx, mn = max(r, g, b), min(r, g, b)
        l_val = (mx + mn) / 2
        if mx == mn:
            s_hsl = 0.0
        else:
            d = mx - mn
            s_hsl = d / (2 - mx - mn) if l_val > 0.5 else d / (mx + mn)
        self.wheel_hsl_info.setText(
            f"H: {h}   S: {int(s_hsl * 100)}%   L: {int(l_val * 100)}%"
        )

        comp = QColor.fromHsv((h + 180) % 360, c.saturation(), c.value())
        pal = self.wheel_comp_swatch.palette()
        pal.setColor(QPalette.Window, comp)
        self.wheel_comp_swatch.setPalette(pal)
        fg = (
            QColor(255, 255, 255) if comp.lightness() < 150
            else QColor(0, 0, 0)
        )
        self.wheel_comp_swatch.setStyleSheet(
            f"border-radius:8px; color:{fg.name()}"
        )
        self.wheel_comp_swatch.setText(comp.name().upper())

        self.sat_val.setText(f"{int(c.saturation() / 255 * 100)}%")
        self.val_val.setText(f"{int(c.value() / 255 * 100)}%")

        # Other pages
        self.harmony.set_color(c)
        self.properties.set_color(c)
        self.blindness.set_color(c)
        self.hsl_explorer.set_color(c)   # now safe: signals blocked inside set_color
        self.contrast.set_selected_color(c)  # IMPROVEMENT: pass color to contrast checker


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())