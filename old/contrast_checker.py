from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QGroupBox, QColorDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPalette, QColor
from utils import contrast_ratio


class ContrastCheckerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.fg = QColor(255, 255, 255)
        self.bg = QColor(30, 30, 60)
        self._selected_color = QColor(0, 200, 200)  # IMPROVEMENT: track app color
        self._build()

    @staticmethod
    def _btn_style():
        return (
            "QPushButton{background:#2e2e50;color:#ddd;border:1px solid #4a4a6a;"
            "border-radius:5px;padding:6px 14px;font-weight:bold;font-size:11px}"
            "QPushButton:hover{background:#3e3e60}"
        )

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setSpacing(14)

        t = QLabel("WCAG Contrast Ratio Checker")
        t.setFont(QFont("Segoe UI", 15, QFont.Bold))
        t.setStyleSheet("color:#ddd")
        lay.addWidget(t)

        info = QLabel(
            "Contrast measures the luminance difference between text and background.\n"
            "WCAG 2.1 AA requires ≥ 4.5:1 for normal text, ≥ 3:1 for large text.\n"
            "WCAG 2.1 AAA requires ≥ 7:1 for normal text, ≥ 4.5:1 for large text."
        )
        info.setWordWrap(True)
        info.setStyleSheet("color:#888;font-size:11px")
        lay.addWidget(info)

        # IMPROVEMENT: "Use selected colour" row
        sel_row = QHBoxLayout()
        sel_row.addWidget(QLabel("App selected colour:"))
        self._sel_prev = QLabel()
        self._sel_prev.setFixedSize(28, 28)
        self._sel_prev.setAutoFillBackground(True)
        self._sel_prev.setStyleSheet("border-radius:4px;border:1px solid #555")
        sel_row.addWidget(self._sel_prev)
        self._sel_hex = QLabel("#00C8C8")
        self._sel_hex.setStyleSheet("color:#aaa;font-family:Consolas;font-size:11px")
        sel_row.addWidget(self._sel_hex)
        sel_row.addStretch()
        btn_fg = QPushButton("Use as Text →")
        btn_fg.setStyleSheet(self._btn_style())
        btn_fg.clicked.connect(self._use_selected_as_fg)
        sel_row.addWidget(btn_fg)
        btn_bg = QPushButton("Use as Background →")
        btn_bg.setStyleSheet(self._btn_style())
        btn_bg.clicked.connect(self._use_selected_as_bg)
        sel_row.addWidget(btn_bg)
        lay.addLayout(sel_row)

        row = QHBoxLayout()
        for attr, label, color in [
            ("fg", "Foreground (Text)", self.fg),
            ("bg", "Background", self.bg),
        ]:
            grp = QGroupBox(label)
            grp.setStyleSheet(
                "QGroupBox{color:#bbb;border:1px solid #444;border-radius:8px;"
                "margin-top:14px;padding-top:20px;font-weight:bold}"
                "QGroupBox::title{subcontrol-position:top left;padding:0 8px}"
            )
            gl = QVBoxLayout(grp)
            prev = QLabel()
            prev.setFixedSize(80, 80)
            prev.setAutoFillBackground(True)
            pal = prev.palette()
            pal.setColor(QPalette.Window, color)
            prev.setPalette(pal)
            gl.addWidget(prev, alignment=Qt.AlignCenter)
            hx = QLabel(color.name().upper())
            hx.setAlignment(Qt.AlignCenter)
            hx.setStyleSheet("color:#aaa;font-family:Consolas")
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

            preset_row = QHBoxLayout()
            if attr == "fg":
                for pc in [
                    QColor(255, 255, 255), QColor(0, 0, 0),
                    QColor(200, 200, 200), QColor(50, 50, 50),
                ]:
                    pb = QPushButton()
                    pb.setFixedSize(24, 24)
                    pb.setStyleSheet(
                        f"background:{pc.name()};border:1px solid #666;border-radius:3px"
                    )
                    pb.clicked.connect(lambda _, c=pc: self._set_fg(c))
                    preset_row.addWidget(pb)
            else:
                for pc in [
                    QColor(0, 0, 0), QColor(255, 255, 255),
                    QColor(30, 30, 60), QColor(240, 240, 240),
                ]:
                    pb = QPushButton()
                    pb.setFixedSize(24, 24)
                    pb.setStyleSheet(
                        f"background:{pc.name()};border:1px solid #666;border-radius:3px"
                    )
                    pb.clicked.connect(lambda _, c=pc: self._set_bg(c))
                    preset_row.addWidget(pb)
            gl.addLayout(preset_row)
            row.addWidget(grp)
        lay.addLayout(row)

        swap_btn = QPushButton("Swap Foreground / Background")
        swap_btn.setStyleSheet(self._btn_style())
        swap_btn.clicked.connect(self._swap)
        lay.addWidget(swap_btn)

        self.result = QFrame()
        self.result.setStyleSheet(
            "QFrame{background:#252540;border-radius:10px;padding:14px}"
        )
        rl = QVBoxLayout(self.result)

        self.ratio_lbl = QLabel("21.0 : 1")
        self.ratio_lbl.setFont(QFont("Segoe UI", 30, QFont.Bold))
        self.ratio_lbl.setAlignment(Qt.AlignCenter)
        self.ratio_lbl.setStyleSheet("color:#4CAF50")
        rl.addWidget(self.ratio_lbl)

        self.preview_lbl = QLabel(
            "The quick brown fox jumps over the lazy dog. 0123456789"
        )
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
            l.setStyleSheet(
                "color:#aaa;font-weight:bold;font-size:11px;padding:5px 8px;"
                "border-radius:4px;background:#1a1a30"
            )
            badges.addWidget(l)
            self.badges[key] = l
        rl.addLayout(badges)
        lay.addWidget(self.result)
        lay.addStretch()
        self._refresh()
        self._refresh_selected_preview()

    # IMPROVEMENT: receive the app's selected color
    def set_selected_color(self, c):
        self._selected_color = QColor(c)
        self._refresh_selected_preview()

    def _refresh_selected_preview(self):
        c = self._selected_color
        pal = self._sel_prev.palette()
        pal.setColor(QPalette.Window, c)
        self._sel_prev.setPalette(pal)
        self._sel_hex.setText(c.name().upper())

    def _use_selected_as_fg(self):
        self.fg = QColor(self._selected_color)
        self._refresh()

    def _use_selected_as_bg(self):
        self.bg = QColor(self._selected_color)
        self._refresh()

    def _pick_fg(self):
        c = QColorDialog.getColor(self.fg, self, "Foreground Colour")
        if c.isValid():
            self.fg = c
            self._refresh()

    def _pick_bg(self):
        c = QColorDialog.getColor(self.bg, self, "Background Colour")
        if c.isValid():
            self.bg = c
            self._refresh()

    def _set_fg(self, c):
        self.fg = QColor(c)
        self._refresh()

    def _set_bg(self, c):
        self.bg = QColor(c)
        self._refresh()

    def _swap(self):
        self.fg, self.bg = self.bg, self.fg
        self._refresh()

    def _refresh(self):
        for prev, hx, c in [
            (self._fg_prev, self._fg_hx, self.fg),
            (self._bg_prev, self._bg_hx, self.bg),
        ]:
            pal = prev.palette()
            pal.setColor(QPalette.Window, c)
            prev.setPalette(pal)
            hx.setText(c.name().upper())

        ratio = contrast_ratio(self.fg, self.bg)
        self.ratio_lbl.setText(f"{ratio:.2f} : 1")
        colour = (
            "#4CAF50" if ratio >= 7
            else "#8BC34A" if ratio >= 4.5
            else "#FF9800" if ratio >= 3
            else "#F44336"
        )
        self.ratio_lbl.setStyleSheet(
            f"color:{colour};font-size:30px;font-weight:bold"
        )

        self.preview_lbl.setStyleSheet(
            f"color:{self.fg.name()};background:{self.bg.name()};"
            f"padding:12px;border-radius:6px"
        )
        self.preview_large.setStyleSheet(
            f"color:{self.fg.name()};background:{self.bg.name()};"
            f"padding:10px;border-radius:6px"
        )

        checks = {
            "AA Normal": ratio >= 4.5,
            "AA Large": ratio >= 3,
            "AAA Normal": ratio >= 7,
            "AAA Large": ratio >= 4.5,
        }
        for k, v in checks.items():
            sym = "PASS" if v else "FAIL"
            c = "#4CAF50" if v else "#F44336"
            bg = "#1a3a1a" if v else "#3a1a1a"
            self.badges[k].setText(f"{k}: {sym}")
            self.badges[k].setStyleSheet(
                f"color:{c};font-weight:bold;font-size:11px;"
                f"padding:5px 8px;border-radius:4px;background:{bg}"
            )