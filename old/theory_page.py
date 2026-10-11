from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

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
            ("The Colour Wheel", "The colour wheel arranges hues in a circle showing their relationships. Isaac Newton created the first circular diagram in 1666 by splitting sunlight through a prism. The wheel reveals harmonies - patterns of colours that look pleasing together - based on geometric relationships.\n\nThe wheel has 12 main segments: 3 primaries, 3 secondaries, and 6 tertiaries. Understanding the wheel is the foundation of all colour theory."),
            ("Primary Colours", "Primary colours cannot be mixed from other colours - they are the building blocks.\n\nRGB (Additive / Light): Red, Green, Blue. Used in screens & lighting. All three combined make White.\nRYB (Subtractive / Paint): Red, Yellow, Blue. Used in traditional art. All three combined make a dark brown/black.\nCMYK (Print): Cyan, Magenta, Yellow, Key (Black). Used in printing."),
            ("Secondary Colours", "Made by mixing two primary colours in equal proportion:\n\nRGB model: Cyan (Green+Blue), Magenta (Red+Blue), Yellow (Red+Green)\nRYB model: Orange (Red+Yellow), Green (Yellow+Blue), Purple (Red+Blue)\n\nSecondaries sit between their parent primaries on the colour wheel."),
            ("Tertiary Colours", "Made by mixing a primary with an adjacent secondary (e.g. Red-Orange, Yellow-Green). There are 6 tertiary colours per model, filling the wheel to create 12 distinct segments.\n\nTertiary colours are often named with the primary first: Red-Orange, not Orange-Red. This naming convention indicates which primary dominates."),
            ("Colour Temperature", "Warm colours (red to yellow) advance toward the viewer and evoke energy, passion, warmth, urgency. Cool colours (blue to green) recede and evoke calm, trust, serenity, professionalism.\n\nTemperature is relative - a blue can be 'warm' if it leans toward violet, and a green can be 'cool' if it leans toward blue-green. Designers use temperature to create depth, mood, and focal points."),
            ("Value, Saturation & Chroma", "Value (Lightness): How light or dark a colour is. Tints = hue + white. Shades = hue + black. High-value palettes feel airy; low-value palettes feel dramatic.\nSaturation (Chroma): Intensity or purity of a colour. Tones = hue + gray. Desaturated colours feel muted and sophisticated; saturated colours feel vivid and energetic.\nHue: The colour family name (red, blue, green, etc.)."),
            ("Simultaneous Contrast", "A colour appears different depending on its neighbours. Grey on yellow looks purplish; grey on blue looks orange-ish. This optical illusion is one of the most important principles in colour theory, discovered by Michel Eugene Chevreul in 1839.\n\nDesigners use this knowledge to make colours appear more vibrant by placing them next to their complements, or to create subtle variation without changing the actual colour."),
            ("The 60-30-10 Rule", "A classic interior design and branding guideline:\n60% - Dominant colour (background, large areas)\n30% - Secondary colour (furniture, sections)\n10% - Accent colour (highlights, calls to action)\n\nThis creates visual hierarchy and prevents colour chaos. The accent is often a complementary or triadic colour for maximum impact."),
            ("Accessibility & Colour", "About 8% of men and 0.5% of women have colour-vision deficiency (CVD). The most common types are red-green blindness (protanopia & deuteranopia).\n\nNever rely on colour alone to convey meaning - add labels, patterns, or icons.\nUse contrast ratios >= 4.5:1 for body text (WCAG AA).\nTest your palettes with CVD simulators.\nAvoid red/green and blue/yellow combinations as sole differentiators."),
            ("Colour Psychology", "Colours evoke emotional and cultural associations:\n\nRed: Passion, urgency, danger, appetite (food brands)\nBlue: Trust, calm, professionalism (banks, tech)\nYellow: Optimism, warmth, caution (warning signs)\nGreen: Nature, growth, health, wealth\nPurple: Luxury, creativity, spirituality\nOrange: Energy, friendliness, affordability\nBlack: Elegance, power, sophistication\n\nNote: These associations vary by culture. White means purity in Western cultures but mourning in some Eastern cultures."),
        ]

        for title, body in sections:
            f = QFrame()
            f.setStyleSheet("QFrame{background:#252540;border-radius:10px;padding:16px;border:1px solid #333355}")
            fl = QVBoxLayout(f)
            h = QLabel(title); h.setFont(QFont("Segoe UI", 12, QFont.Bold))
            h.setStyleSheet("color:#c0c0e0;border:none"); fl.addWidget(h)
            b = QLabel(body); b.setWordWrap(True)
            b.setStyleSheet("color:#a0a0c0;font-size:11px;border:none"); fl.addWidget(b)
            cl.addWidget(f)

        cl.addStretch()
        scroll.setWidget(content)
        lay.addWidget(scroll)