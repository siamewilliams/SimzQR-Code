"""
SimzQR code — Professional QR Code Generator
PySide6 + qrcode + Pillow

Created by William Siame
Software Developer · Machine Learning Engineer
siamewilliam10@gmail.com

Run:  python simzqr_code.py
"""

import io
import math
import os
import sys

from PySide6.QtCore import (
    Qt, QTimer, QSize, QRectF, QPointF, QSettings, Signal,
)
from PySide6.QtGui import (
    QPixmap, QColor, QAction, QIcon,
    QPainter, QPen, QBrush, QLinearGradient, QPainterPath,
)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPlainTextEdit, QPushButton, QComboBox, QSpinBox, QFrame,
    QColorDialog, QFileDialog, QMessageBox, QSizePolicy, QScrollArea, QDialog,
)

import qrcode
from qrcode.constants import (
    ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q, ERROR_CORRECT_H,
)
from PIL import Image


# ============================================================
#  App metadata
# ============================================================
APP_NAME = "SimzQR code"
APP_VERSION = "1.1.0"
ORG_NAME = "SimzQR"
AUTHOR_NAME = "William Siame"
AUTHOR_ROLES = "Software Developer · Machine Learning Engineer"
AUTHOR_EMAIL = "siamewilliam10@gmail.com"


# ============================================================
#  Theme palettes
# ============================================================
THEME_LIGHT = {
    "bg":             "#eef1f6",
    "card":           "#ffffff",
    "border":         "#dfe4ec",
    "border_soft":    "#e9edf3",
    "text":           "#2b2f3a",
    "text_strong":    "#1a1f2b",
    "text_muted":     "#7a8395",
    "text_dim":       "#6b7385",
    "accent":         "#4361ee",
    "accent_hover":   "#3451d8",
    "accent_pressed": "#2a44c2",
    "input_bg":       "#f7f8fb",
    "preview_bg":     "#f7f8fb",
    "preview_border": "#e3e7ee",
    "warning":        "#b45309",
    "scrollbar":      "#c8cfdb",
    "scrollbar_hover":"#a8b2c4",
}

THEME_DARK = {
    "bg":             "#0f1117",
    "card":           "#1a1e26",
    "border":         "#2d3543",
    "border_soft":    "#252b36",
    "text":           "#d6dbe6",
    "text_strong":    "#f1f4fa",
    "text_muted":     "#8892a6",
    "text_dim":       "#6b7385",
    "accent":         "#5b7cfa",
    "accent_hover":   "#738ffb",
    "accent_pressed": "#4a6bea",
    "input_bg":       "#232833",
    "preview_bg":     "#13161d",
    "preview_border": "#2a3140",
    "warning":        "#f59e0b",
    "scrollbar":      "#39404f",
    "scrollbar_hover":"#4a5262",
}


# ============================================================
#  App logo — rendered programmatically
# ============================================================
def _draw_icon_pixmap(size: int) -> QPixmap:
    pix = QPixmap(size, size)
    pix.fill(Qt.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing, True)
    p.setRenderHint(QPainter.SmoothPixmapTransform, True)

    margin = size * 0.05
    rect = QRectF(margin, margin, size - 2 * margin, size - 2 * margin)
    grad = QLinearGradient(rect.topLeft(), rect.bottomRight())
    grad.setColorAt(0.0, QColor("#5b7cfa"))
    grad.setColorAt(1.0, QColor("#2a44c2"))
    p.setPen(Qt.NoPen)
    p.setBrush(QBrush(grad))
    p.drawRoundedRect(rect, size * 0.22, size * 0.22)

    inner = size * 0.20
    grid = size - 2 * inner
    unit = grid / 7.0
    ox, oy = inner, inner
    white = QColor("#ffffff")

    pen = QPen(white)
    pen.setWidthF(max(1.0, unit))
    pen.setJoinStyle(Qt.RoundJoin)
    p.setPen(pen)
    p.setBrush(Qt.NoBrush)
    inset = unit / 2.0
    p.drawRoundedRect(
        QRectF(ox + inset, oy + inset, 6 * unit, 6 * unit),
        unit * 0.55, unit * 0.55,
    )

    p.setPen(Qt.NoPen)
    p.setBrush(white)
    p.drawRoundedRect(
        QRectF(ox + 2 * unit, oy + 2 * unit, 3 * unit, 3 * unit),
        unit * 0.35, unit * 0.35,
    )

    p.end()
    return pix


def _draw_sun_icon_pixmap(size: int) -> QPixmap:
    pix = QPixmap(size, size)
    pix.fill(Qt.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing, True)

    color = QColor("#f59e0b")
    cx = cy = size / 2.0
    r = size * 0.18

    p.setPen(Qt.NoPen)
    p.setBrush(color)
    p.drawEllipse(QPointF(cx, cy), r, r)

    pen = QPen(color)
    pen.setWidthF(max(1.4, size * 0.09))
    pen.setCapStyle(Qt.RoundCap)
    p.setPen(pen)

    r1 = r * 1.6
    r2 = size * 0.38
    for i in range(8):
        ang = math.pi * i / 4.0
        x1 = cx + r1 * math.cos(ang)
        y1 = cy + r1 * math.sin(ang)
        x2 = cx + r2 * math.cos(ang)
        y2 = cy + r2 * math.sin(ang)
        p.drawLine(QPointF(x1, y1), QPointF(x2, y2))

    p.end()
    return pix


def _draw_moon_icon_pixmap(size: int) -> QPixmap:
    pix = QPixmap(size, size)
    pix.fill(Qt.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing, True)

    color = QColor("#475569")
    cx = cy = size / 2.0
    r = size * 0.36

    path = QPainterPath()
    path.addEllipse(QPointF(cx, cy), r, r)
    cut = QPainterPath()
    cut.addEllipse(QPointF(cx + r * 0.55, cy - r * 0.45), r * 0.92, r * 0.92)
    path = path.subtracted(cut)

    p.setPen(Qt.NoPen)
    p.setBrush(color)
    p.drawPath(path)
    p.end()
    return pix


def make_app_icon() -> QIcon:
    icon = QIcon()
    for s in (16, 24, 32, 48, 64, 128, 256, 512):
        icon.addPixmap(_draw_icon_pixmap(s))
    return icon


def _icon_label(size: int) -> QLabel:
    lbl = QLabel()
    lbl.setAlignment(Qt.AlignCenter)
    lbl.setFixedSize(size, size)
    lbl.setPixmap(
        _draw_icon_pixmap(size * 2).scaled(
            size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
    )
    return lbl


# ============================================================
#  Stylesheet builder
# ============================================================
def build_qss(c: dict) -> str:
    return f"""
        QWidget {{
            font-family: "Segoe UI", "Inter", "Helvetica Neue", Arial, sans-serif;
            font-size: 13px;
            color: {c['text']};
        }}
        QMainWindow {{ background: {c['bg']}; }}
        QDialog     {{ background: {c['card']}; }}

        #Header {{
            background: {c['card']};
            border-bottom: 1px solid {c['border']};
        }}
        #HeaderTitle    {{ font-size: 19px; font-weight: 700; color: {c['text_strong']}; }}
        #HeaderSubtitle {{ font-size: 12px; color: {c['text_muted']}; }}

        QPushButton#HeaderButton, QPushButton#IconButton {{
            background: {c['input_bg']};
            border: 1px solid {c['border']};
            border-radius: 6px;
            padding: 6px 16px;
            font-weight: 600;
            color: {c['text']};
        }}
        QPushButton#IconButton {{ padding: 0; }}
        QPushButton#HeaderButton:hover, QPushButton#IconButton:hover {{
            border-color: {c['accent']};
            color: {c['accent']};
        }}

        #Card {{
            background: {c['card']};
            border: 1px solid {c['border']};
            border-radius: 12px;
        }}
        #Section {{
            color: {c['accent']};
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.6px;
        }}
        #Hint    {{ color: {c['text_muted']}; font-size: 12px; }}
        #Warning {{ color: {c['warning']};    font-size: 12px; }}
        #Status  {{ color: {c['text_dim']};   font-size: 12px; }}

        #Preview {{
            background: {c['preview_bg']};
            border: 1px solid {c['preview_border']};
            border-radius: 10px;
            color: {c['text_muted']};
            font-size: 14px;
        }}

        QPlainTextEdit, QLineEdit {{
            background: {c['input_bg']};
            border: 1px solid {c['border']};
            border-radius: 8px;
            padding: 8px;
            color: {c['text']};
            selection-background-color: {c['accent']};
            selection-color: #ffffff;
        }}
        QPlainTextEdit:focus, QLineEdit:focus {{
            border: 1px solid {c['accent']};
            background: {c['card']};
        }}

        QComboBox {{
            background: {c['input_bg']};
            border: 1px solid {c['border']};
            border-radius: 8px;
            padding: 7px 10px;
            color: {c['text']};
            min-height: 22px;
        }}
        QComboBox:hover {{ border: 1px solid {c['accent']}; }}
        QComboBox::drop-down {{ border: none; width: 24px; }}
        QComboBox QAbstractItemView {{
            background: {c['card']};
            border: 1px solid {c['border']};
            color: {c['text']};
            selection-background-color: {c['accent']};
            selection-color: #ffffff;
            outline: none;
        }}

        QSpinBox {{
            background: {c['input_bg']};
            border: 1px solid {c['border']};
            border-radius: 8px;
            padding: 7px 8px;
            color: {c['text']};
            min-height: 22px;
        }}
        QSpinBox:focus {{ border: 1px solid {c['accent']}; }}

        QPushButton {{
            background: {c['card']};
            border: 1px solid {c['border']};
            border-radius: 8px;
            padding: 9px 14px;
            font-weight: 600;
            color: {c['text']};
        }}
        QPushButton:hover   {{ background: {c['input_bg']}; border-color: {c['accent']}; }}
        QPushButton:pressed {{ background: {c['border_soft']}; }}
        QPushButton:disabled {{
            color: {c['text_muted']};
            background: {c['input_bg']};
            border-color: {c['border']};
        }}
        QPushButton#Primary {{
            background: {c['accent']};
            color: #ffffff;
            border: none;
        }}
        QPushButton#Primary:hover   {{ background: {c['accent_hover']}; }}
        QPushButton#Primary:pressed {{ background: {c['accent_pressed']}; }}
        QPushButton#Primary:disabled{{ background: {c['border']}; color: {c['text_muted']}; }}

        QMenuBar {{
            background: {c['card']};
            border-bottom: 1px solid {c['border']};
            padding: 2px 8px;
            color: {c['text']};
        }}
        QMenuBar::item {{
            background: transparent;
            padding: 6px 12px;
            border-radius: 4px;
            color: {c['text']};
        }}
        QMenuBar::item:selected {{ background: {c['input_bg']}; }}
        QMenu {{
            background: {c['card']};
            border: 1px solid {c['border']};
            padding: 6px;
            color: {c['text']};
        }}
        QMenu::item {{
            padding: 6px 22px 6px 16px;
            border-radius: 4px;
        }}
        QMenu::item:selected {{
            background: {c['accent']};
            color: #ffffff;
        }}

        QScrollArea {{ background: transparent; border: none; }}
        QScrollBar:vertical {{
            background: transparent; width: 10px; margin: 0;
        }}
        QScrollBar::handle:vertical {{
            background: {c['scrollbar']}; border-radius: 5px; min-height: 30px;
        }}
        QScrollBar::handle:vertical:hover {{ background: {c['scrollbar_hover']}; }}
        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {{ height: 0; }}
        QScrollBar::add-page:vertical,
        QScrollBar::sub-page:vertical {{ background: transparent; }}

        /* ------- About dialog ------- */
        #AboutTitle      {{ font-size: 22px; font-weight: 800; color: {c['text_strong']}; }}
        #AboutVersion    {{ font-size: 12px; color: {c['text_muted']}; }}
        #AboutDesc       {{ font-size: 13px; color: {c['text']}; }}
        #AboutCreatedBy  {{
            font-size: 10px;
            font-weight: 700;
            letter-spacing: 1px;
            color: {c['text_muted']};
        }}
        #AboutAuthor     {{ font-size: 17px; font-weight: 700; color: {c['text_strong']}; }}
        #AboutRoles      {{ font-size: 12px; font-weight: 600; color: {c['accent']}; }}
        #AboutEmail      {{ font-size: 13px; }}
        #AboutSeparator  {{ background: {c['border_soft']}; border: none; }}
    """


# ============================================================
#  Custom widgets
# ============================================================
class ColorButton(QPushButton):
    colorChanged = Signal(QColor)

    def __init__(self, color="#000000", parent=None):
        super().__init__(parent)
        self._color = QColor(color)
        self.setFixedHeight(34)
        self.setCursor(Qt.PointingHandCursor)
        self.clicked.connect(self._choose)
        self._refresh()

    def _choose(self):
        c = QColorDialog.getColor(self._color, self, "Choose colour")
        if c.isValid():
            self._color = c
            self._refresh()
            self.colorChanged.emit(c)

    def _refresh(self):
        c = self._color
        text_color = "#111111" if c.lightness() > 150 else "#ffffff"
        self.setStyleSheet(
            f"QPushButton {{ background-color: {c.name()}; "
            f"border: 1px solid #c9cfd9; border-radius: 6px; "
            f"color: {text_color}; font-weight: 700; font-size: 11px; }}"
            f"QPushButton:hover {{ border: 1px solid #4361ee; }}"
        )
        self.setText(c.name().upper())

    def color(self) -> QColor:
        return self._color


class PreviewLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._pix = None
        self.setObjectName("Preview")
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(420, 420)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setText("Enter text or a URL to get started")

    def set_qr(self, pixmap: QPixmap | None):
        self._pix = pixmap
        if pixmap is None or pixmap.isNull():
            self.setPixmap(QPixmap())
            self.setText("Enter text or a URL to get started")
        else:
            self.setText("")
            self._rescale()

    def _rescale(self):
        if self._pix is None or self._pix.isNull():
            return
        target = self.contentsRect().size() - QSize(48, 48)
        if target.width() < 10 or target.height() < 10:
            return
        self.setPixmap(
            self._pix.scaled(target, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._rescale()


# ============================================================
#  About dialog
# ============================================================
class AboutDialog(QDialog):
    def __init__(self, colors: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"About {APP_NAME}")
        self.setWindowIcon(make_app_icon())
        self.setFixedWidth(460)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 28, 30, 22)
        layout.setSpacing(10)

        # Logo badge
        badge_row = QHBoxLayout()
        badge_row.addStretch()
        badge_row.addWidget(_icon_label(84))
        badge_row.addStretch()
        layout.addLayout(badge_row)

        # Title
        title = QLabel(APP_NAME)
        title.setObjectName("AboutTitle")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        version = QLabel(f"Version {APP_VERSION}")
        version.setObjectName("AboutVersion")
        version.setAlignment(Qt.AlignCenter)
        layout.addWidget(version)

        desc = QLabel(
            "A professional QR code generator\n"
            "built with PySide6."
        )
        desc.setObjectName("AboutDesc")
        desc.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc)

        # Divider
        sep = QFrame()
        sep.setObjectName("AboutSeparator")
        sep.setFixedHeight(1)
        layout.addWidget(sep)

        created_by = QLabel("CREATED BY")
        created_by.setObjectName("AboutCreatedBy")
        created_by.setAlignment(Qt.AlignCenter)
        layout.addWidget(created_by)

        author = QLabel(AUTHOR_NAME)
        author.setObjectName("AboutAuthor")
        author.setAlignment(Qt.AlignCenter)
        layout.addWidget(author)

        roles = QLabel(AUTHOR_ROLES)
        roles.setObjectName("AboutRoles")
        roles.setAlignment(Qt.AlignCenter)
        layout.addWidget(roles)

        accent = colors["accent"]
        email = QLabel(
            f'<a href="mailto:{AUTHOR_EMAIL}" '
            f'style="color:{accent}; text-decoration:none;">'
            f'{AUTHOR_EMAIL}</a>'
        )
        email.setObjectName("AboutEmail")
        email.setAlignment(Qt.AlignCenter)
        email.setOpenExternalLinks(True)
        layout.addWidget(email)

        layout.addSpacing(12)

        close = QPushButton("Close")
        close.setObjectName("Primary")
        close.setFixedHeight(38)
        close.setCursor(Qt.PointingHandCursor)
        close.clicked.connect(self.accept)
        layout.addWidget(close)


# ============================================================
#  Main window
# ============================================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} — Professional QR Code Generator")
        self.setWindowIcon(make_app_icon())
        self.resize(1180, 800)
        self.setMinimumSize(1000, 700)

        self._logo_path: str | None = None
        self._current_img: Image.Image | None = None

        # Theme state (loaded from settings below, after menu is built)
        self._settings = QSettings(ORG_NAME, APP_NAME)
        self._dark_mode = self._settings.value("theme/dark", False, type=bool)
        self._colors = THEME_DARK if self._dark_mode else THEME_LIGHT

        self._debounce = QTimer(self)
        self._debounce.setSingleShot(True)
        self._debounce.setInterval(220)
        self._debounce.timeout.connect(self.update_preview)

        self._build_ui()
        self._build_menu()
        self._connect_signals()

        self.dark_mode_action.setChecked(self._dark_mode)
        self._apply_theme()
        self.update_preview()

    # --------------------------------------------------------
    #  UI construction
    # --------------------------------------------------------
    def _section(self, text: str) -> QLabel:
        lbl = QLabel(text.upper())
        lbl.setObjectName("Section")
        return lbl

    def _separator(self) -> QFrame:
        line = QFrame()
        line.setFixedHeight(1)
        line.setStyleSheet("background: #e9edf3; border: none;")
        line.setProperty("class", "HLine")
        return line

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ---------- Header ----------
        header = QFrame()
        header.setObjectName("Header")
        header.setFixedHeight(78)
        h = QHBoxLayout(header)
        h.setContentsMargins(22, 0, 26, 0)
        h.setSpacing(12)

        h.addWidget(_icon_label(46))
        h.addSpacing(2)

        title = QLabel(APP_NAME)
        title.setObjectName("HeaderTitle")
        subtitle = QLabel("Professional QR Code Generator")
        subtitle.setObjectName("HeaderSubtitle")

        v = QVBoxLayout()
        v.setSpacing(0)
        v.addWidget(title)
        v.addWidget(subtitle)
        h.addLayout(v)
        h.addStretch()

        # Theme toggle
        self.theme_btn = QPushButton()
        self.theme_btn.setObjectName("IconButton")
        self.theme_btn.setFixedSize(36, 36)
        self.theme_btn.setIconSize(QSize(20, 20))
        self.theme_btn.setCursor(Qt.PointingHandCursor)
        h.addWidget(self.theme_btn)

        # About
        self.about_btn = QPushButton("About")
        self.about_btn.setObjectName("HeaderButton")
        self.about_btn.setFixedHeight(32)
        self.about_btn.setCursor(Qt.PointingHandCursor)
        h.addWidget(self.about_btn)

        root.addWidget(header)

        # ---------- Body ----------
        body = QHBoxLayout()
        body.setContentsMargins(20, 20, 20, 20)
        body.setSpacing(20)
        root.addLayout(body, 1)

        # ===== Left control panel =====
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setFixedWidth(420)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.viewport().setAutoFillBackground(False)
        scroll.setStyleSheet("background: transparent; border: none;")

        card = QFrame()
        card.setObjectName("Card")
        ll = QVBoxLayout(card)
        ll.setContentsMargins(20, 20, 20, 20)
        ll.setSpacing(12)

        ll.addWidget(self._section("Content"))
        self.text_edit = QPlainTextEdit()
        self.text_edit.setPlaceholderText("https://example.com  or  any text…")
        self.text_edit.setFixedHeight(96)
        ll.addWidget(self.text_edit)

        ll.addWidget(self._separator())
        ll.addWidget(self._section("Appearance"))

        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(10)
        grid.setColumnStretch(1, 1)

        grid.addWidget(QLabel("Foreground"), 0, 0)
        self.fg_btn = ColorButton("#1a1a1a")
        grid.addWidget(self.fg_btn, 0, 1)

        grid.addWidget(QLabel("Background"), 1, 0)
        self.bg_btn = ColorButton("#ffffff")
        grid.addWidget(self.bg_btn, 1, 1)

        grid.addWidget(QLabel("Box size"), 2, 0)
        self.box_size_spin = QSpinBox()
        self.box_size_spin.setRange(1, 40)
        self.box_size_spin.setValue(10)
        grid.addWidget(self.box_size_spin, 2, 1)

        grid.addWidget(QLabel("Border"), 3, 0)
        self.border_spin = QSpinBox()
        self.border_spin.setRange(0, 20)
        self.border_spin.setValue(4)
        grid.addWidget(self.border_spin, 3, 1)

        ll.addLayout(grid)

        ll.addWidget(self._separator())
        ll.addWidget(self._section("Quality"))

        self.ec_combo = QComboBox()
        self.ec_combo.addItem("Low — 7% recovery", ERROR_CORRECT_L)
        self.ec_combo.addItem("Medium — 15% recovery", ERROR_CORRECT_M)
        self.ec_combo.addItem("Quartile — 25% recovery", ERROR_CORRECT_Q)
        self.ec_combo.addItem("High — 30% recovery", ERROR_CORRECT_H)
        self.ec_combo.setCurrentIndex(1)
        ll.addWidget(self.ec_combo)

        ll.addWidget(self._separator())
        ll.addWidget(self._section("Center logo (optional)"))

        row = QHBoxLayout()
        self.logo_btn = QPushButton("Choose image…")
        self.logo_clear_btn = QPushButton("Clear")
        self.logo_clear_btn.setEnabled(False)
        row.addWidget(self.logo_btn, 1)
        row.addWidget(self.logo_clear_btn)
        ll.addLayout(row)

        self.logo_label = QLabel("No logo selected")
        self.logo_label.setObjectName("Hint")
        ll.addWidget(self.logo_label)

        self.logo_warning = QLabel("Tip: use High error correction when adding a logo.")
        self.logo_warning.setObjectName("Warning")
        self.logo_warning.setWordWrap(True)
        ll.addWidget(self.logo_warning)

        ll.addStretch(1)

        ll.addWidget(self._separator())
        self.reset_btn = QPushButton("Reset to defaults")
        ll.addWidget(self.reset_btn)

        scroll.setWidget(card)
        body.addWidget(scroll)

        # ===== Right preview panel =====
        right = QFrame()
        right.setObjectName("Card")
        rl = QVBoxLayout(right)
        rl.setContentsMargins(20, 20, 20, 20)
        rl.setSpacing(14)

        self.preview = PreviewLabel()
        rl.addWidget(self.preview, 1)

        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("Status")
        rl.addWidget(self.status_label)

        btns = QHBoxLayout()
        btns.setSpacing(10)
        self.save_png_btn = QPushButton("Save PNG")
        self.save_png_btn.setObjectName("Primary")
        self.save_svg_btn = QPushButton("Save SVG")
        self.copy_btn = QPushButton("Copy image")
        btns.addWidget(self.save_png_btn)
        btns.addWidget(self.save_svg_btn)
        btns.addWidget(self.copy_btn)
        rl.addLayout(btns)

        body.addWidget(right, 1)

    # --------------------------------------------------------
    #  Menu bar
    # --------------------------------------------------------
    def _build_menu(self):
        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)

        view_menu = menubar.addMenu("&View")
        self.dark_mode_action = QAction("Dark Mode", self)
        self.dark_mode_action.setCheckable(True)
        self.dark_mode_action.setShortcut("Ctrl+D")
        self.dark_mode_action.triggered.connect(self._set_dark_mode)
        view_menu.addAction(self.dark_mode_action)

        help_menu = menubar.addMenu("&Help")
        about_action = QAction(f"&About {APP_NAME}", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _show_about(self):
        AboutDialog(self._colors, self).exec()

    # --------------------------------------------------------
    #  Theme handling
    # --------------------------------------------------------
    def _set_dark_mode(self, dark: bool):
        if self._dark_mode == dark:
            return
        self._dark_mode = dark
        if self.dark_mode_action.isChecked() != dark:
            self.dark_mode_action.blockSignals(True)
            self.dark_mode_action.setChecked(dark)
            self.dark_mode_action.blockSignals(False)
        self._apply_theme()

    def _toggle_theme(self):
        self._set_dark_mode(not self._dark_mode)

    def _apply_theme(self):
        self._colors = THEME_DARK if self._dark_mode else THEME_LIGHT
        self.setStyleSheet(build_qss(self._colors))

        if self._dark_mode:
            self.theme_btn.setIcon(QIcon(_draw_sun_icon_pixmap(20)))
            self.theme_btn.setToolTip("Switch to light mode")
        else:
            self.theme_btn.setIcon(QIcon(_draw_moon_icon_pixmap(20)))
            self.theme_btn.setToolTip("Switch to dark mode")

        self._settings.setValue("theme/dark", self._dark_mode)

    # --------------------------------------------------------
    #  Signals
    # --------------------------------------------------------
    def _connect_signals(self):
        self.theme_btn.clicked.connect(self._toggle_theme)
        self.about_btn.clicked.connect(self._show_about)
        self.text_edit.textChanged.connect(self._schedule)
        self.ec_combo.currentIndexChanged.connect(self._schedule)
        self.box_size_spin.valueChanged.connect(self._schedule)
        self.border_spin.valueChanged.connect(self._schedule)
        self.fg_btn.colorChanged.connect(lambda _: self._schedule())
        self.bg_btn.colorChanged.connect(lambda _: self._schedule())
        self.logo_btn.clicked.connect(self._pick_logo)
        self.logo_clear_btn.clicked.connect(self._clear_logo)
        self.save_png_btn.clicked.connect(self._save_png)
        self.save_svg_btn.clicked.connect(self._save_svg)
        self.copy_btn.clicked.connect(self._copy_image)
        self.reset_btn.clicked.connect(self._reset_defaults)

    def _schedule(self):
        self._debounce.start()

    # --------------------------------------------------------
    #  QR generation
    # --------------------------------------------------------
    def _render_qr(self) -> Image.Image:
        text = self.text_edit.toPlainText().strip()
        if not text:
            raise ValueError("No content")

        qr = qrcode.QRCode(
            version=None,
            error_correction=self.ec_combo.currentData(),
            box_size=max(1, self.box_size_spin.value()),
            border=max(0, self.border_spin.value()),
        )
        qr.add_data(text)
        qr.make(fit=True)

        fg = self.fg_btn.color().getRgb()[:3]
        bg = self.bg_btn.color().getRgb()[:3]
        img = qr.make_image(fill_color=fg, back_color=bg).convert("RGB")

        if self._logo_path and os.path.exists(self._logo_path):
            img = self._apply_logo(img)
        return img

    def _apply_logo(self, img: Image.Image) -> Image.Image:
        logo = Image.open(self._logo_path).convert("RGBA")
        qr_w, qr_h = img.size
        max_logo = int(min(qr_w, qr_h) * 0.22)
        if max_logo < 8:
            return img

        logo.thumbnail((max_logo, max_logo), Image.LANCZOS)
        pad = max(2, int(max_logo * 0.10))
        bg = self.bg_btn.color().getRgb()[:3] + (255,)
        canvas = Image.new(
            "RGBA", (logo.width + pad * 2, logo.height + pad * 2), bg
        )
        canvas.paste(logo, (pad, pad), logo)

        img = img.convert("RGBA")
        x = (qr_w - canvas.width) // 2
        y = (qr_h - canvas.height) // 2
        img.paste(canvas, (x, y), canvas)
        return img.convert("RGB")

    def update_preview(self):
        text = self.text_edit.toPlainText().strip()
        if not text:
            self._current_img = None
            self.preview.set_qr(None)
            self._set_actions_enabled(False)
            self.status_label.setText("Waiting for input…")
            return

        try:
            img = self._render_qr()
        except Exception as exc:  # noqa: BLE001
            self._current_img = None
            self.preview.set_qr(None)
            self._set_actions_enabled(False)
            self.status_label.setText(f"⚠ {exc}")
            return

        self._current_img = img

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        pix = QPixmap()
        pix.loadFromData(buf.getvalue(), "PNG")
        self.preview.set_qr(pix)

        self._set_actions_enabled(True)
        size_kb = len(buf.getvalue()) / 1024
        self.status_label.setText(
            f"{img.width} × {img.height} px   ·   {size_kb:.1f} KB"
        )

    def _set_actions_enabled(self, enabled: bool):
        self.save_png_btn.setEnabled(enabled)
        self.save_svg_btn.setEnabled(enabled)
        self.copy_btn.setEnabled(enabled)

    # --------------------------------------------------------
    #  Logo
    # --------------------------------------------------------
    def _pick_logo(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select logo", "",
            "Images (*.png *.jpg *.jpeg *.bmp *.webp *.gif)",
        )
        if not path:
            return
        self._logo_path = path
        self.logo_label.setText(os.path.basename(path))
        self.logo_clear_btn.setEnabled(True)

        if self.ec_combo.currentData() != ERROR_CORRECT_H:
            self.logo_warning.setText(
                "High error correction is strongly recommended with a logo."
            )
        else:
            self.logo_warning.setText("")
        self.update_preview()

    def _clear_logo(self):
        self._logo_path = None
        self.logo_label.setText("No logo selected")
        self.logo_clear_btn.setEnabled(False)
        self.logo_warning.setText("Tip: use High error correction when adding a logo.")
        self.update_preview()

    # --------------------------------------------------------
    #  Save / Copy
    # --------------------------------------------------------
    def _save_png(self):
        if self._current_img is None:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Save PNG", "qrcode.png", "PNG Image (*.png)"
        )
        if not path:
            return
        if not path.lower().endswith(".png"):
            path += ".png"
        try:
            self._current_img.save(path, "PNG")
            self.status_label.setText(f"Saved: {os.path.basename(path)}")
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(self, "Save failed", str(exc))

    def _save_svg(self):
        text = self.text_edit.toPlainText().strip()
        if not text:
            return

        if self._logo_path:
            QMessageBox.information(
                self, "Note",
                "SVG export does not include the centre logo.\n"
                "Use PNG export to include the logo.",
            )

        path, _ = QFileDialog.getSaveFileName(
            self, "Save SVG", "qrcode.svg", "SVG Image (*.svg)"
        )
        if not path:
            return
        if not path.lower().endswith(".svg"):
            path += ".svg"

        try:
            qr = qrcode.QRCode(
                version=None,
                error_correction=self.ec_combo.currentData(),
                box_size=10,
                border=max(0, self.border_spin.value()),
            )
            qr.add_data(text)
            qr.make(fit=True)
            matrix = qr.get_matrix()

            n = len(matrix)
            box = 10
            dim = n * box
            fg = self.fg_btn.color().name()
            bg = self.bg_btn.color().name()

            parts = [
                '<?xml version="1.0" encoding="UTF-8"?>',
                f'<svg xmlns="http://www.w3.org/2000/svg" '
                f'width="{dim}" height="{dim}" viewBox="0 0 {dim} {dim}" '
                f'shape-rendering="crispEdges">',
                f'<rect width="{dim}" height="{dim}" fill="{bg}"/>',
                f'<path fill="{fg}" d="',
            ]
            for y, row in enumerate(matrix):
                for x, val in enumerate(row):
                    if val:
                        parts.append(
                            f"M{x * box} {y * box}h{box}v{box}h-{box}z"
                        )
            parts.append('"/>')
            parts.append("</svg>")

            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(parts))
            self.status_label.setText(f"Saved: {os.path.basename(path)}")
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(self, "Save failed", str(exc))

    def _copy_image(self):
        if self._current_img is None:
            return
        buf = io.BytesIO()
        self._current_img.save(buf, format="PNG")
        pix = QPixmap()
        pix.loadFromData(buf.getvalue(), "PNG")
        QApplication.clipboard().setPixmap(pix)
        self.status_label.setText("Image copied to clipboard")

    # --------------------------------------------------------
    #  Reset
    # --------------------------------------------------------
    def _reset_defaults(self):
        self.fg_btn._color = QColor("#1a1a1a")
        self.fg_btn._refresh()
        self.bg_btn._color = QColor("#ffffff")
        self.bg_btn._refresh()
        self.box_size_spin.setValue(10)
        self.border_spin.setValue(4)
        self.ec_combo.setCurrentIndex(1)
        self._clear_logo()
        self.update_preview()


# ============================================================
#  Entry point
# ============================================================
def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationDisplayName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName(ORG_NAME)
    app.setWindowIcon(make_app_icon())
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()