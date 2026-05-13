from PySide6.QtGui import QColor

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