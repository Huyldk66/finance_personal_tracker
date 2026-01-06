import sys, math, random

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *

from agent import BotChatAgent

TET_RED_BG = "#b30000"       # Đỏ nền
TET_GOLD = "#FFD700"         # Vàng kim loại
TET_CREAM = "#FFF8E1"        # Màu kem (giấy)
TET_TEXT_DARK = "#5D4037"    # Nâu đất


# --- 1. CẤU HÌNH THEME (GIỮ NGUYÊN) ---
THEMES = {
    "spring": {
        "name": "Xuân (Tết)",
        "sidebar_bg": "#b30000",
        "sidebar_border": "#FFD700",
        "content_bg": "#FFF8E1",
        "text_color": "#5D4037",
        "accent_color": "#FFD700",
        "btn_hover": "rgba(255, 215, 0, 0.2)",
        "icon": "🌸"
    },
    "summer": {
        "name": "Hạ (Biển Xanh)",
        "sidebar_bg": "#0277BD",
        "sidebar_border": "#4FC3F7",
        "content_bg": "#E1F5FE",
        "text_color": "#01579B",
        "accent_color": "#E0F7FA",
        "btn_hover": "rgba(79, 195, 247, 0.3)",
        "icon": "🏖️"
    },
    "autumn": {
        "name": "Thu (Lá Vàng)",
        "sidebar_bg": "#E65100",
        "sidebar_border": "#FFB74D",
        "content_bg": "#FFF3E0",
        "text_color": "#3E2723",
        "accent_color": "#FFCC80",
        "btn_hover": "rgba(255, 183, 77, 0.3)",
        "icon": "🍁"
    },
    "winter": {
        "name": "Đông (Băng Giá)",
        "sidebar_bg": "#263238",
        "sidebar_border": "#B0BEC5",
        "content_bg": "#ECEFF1",
        "text_color": "#37474F",
        "accent_color": "#FFFFFF",
        "btn_hover": "rgba(176, 190, 197, 0.3)",
        "icon": "❄️"
    }
}

# --- 2. HỆ THỐNG EFFECT (GIỮ NGUYÊN CỦA BẠN) ---
class Particle:
    def __init__(self, w, h, mode="spring"):
        self.mode = mode
        self.reset(w, h, first_time=True)

    def reset(self, w, h, first_time=False):
        self.x = random.uniform(0, w)
        self.size = random.uniform(5, 15)
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-2, 2)
        
        if self.mode == "spring": 
            self.y = random.uniform(-h, 0) if not first_time else random.uniform(0, h)
            self.speed_y = random.uniform(1, 3)
            self.drift = random.uniform(-0.5, 0.5)
            self.color = QColor("#FFD700") if random.choice([True, False]) else QColor("#FFB7C5")
            self.shape = "flower"
            self.size = random.uniform(10, 20)
        elif self.mode == "summer":
            self.y = h + random.uniform(0, 100) if not first_time else random.uniform(0, h)
            self.speed_y = random.uniform(-1, -3)
            self.drift = random.uniform(-0.2, 0.2)
            self.color = QColor(255, 255, 255, 100)
            self.shape = "bubble"
            self.size = random.uniform(5, 15)
        elif self.mode == "autumn":
            self.y = random.uniform(-h, 0) if not first_time else random.uniform(0, h)
            self.speed_y = random.uniform(1, 2)
            self.drift = random.uniform(-1, 1)
            self.color = random.choice([QColor("#D84315"), QColor("#F9A825"), QColor("#6D4C41")])
            self.shape = "leaf"
            self.size = random.uniform(12, 22)
        elif self.mode == "winter":
            self.y = random.uniform(-h, 0) if not first_time else random.uniform(0, h)
            self.speed_y = random.uniform(2, 5)
            self.drift = 0
            self.color = QColor("#FFFFFF")
            self.shape = "snow"
            self.size = random.uniform(3, 6)

        self.path = QPainterPath()
        if self.shape == "flower": self.create_flower_path()
        elif self.shape == "leaf": self.create_leaf_path()

    def create_flower_path(self):
        center = QPointF(0, 0)
        petal_radius = self.size / 2
        for i in range(5):
            angle = math.radians(i * 72)
            tip = QPointF(center.x() + petal_radius * math.cos(angle), center.y() + petal_radius * math.sin(angle))
            ctrl1 = QPointF(center.x() + petal_radius*0.6 * math.cos(angle-0.3), center.y() + petal_radius*0.6 * math.sin(angle-0.3))
            ctrl2 = QPointF(center.x() + petal_radius*0.6 * math.cos(angle+0.3), center.y() + petal_radius*0.6 * math.sin(angle+0.3))
            if i == 0: self.path.moveTo(center)
            self.path.cubicTo(ctrl1, tip, ctrl2)
        self.path.closeSubpath()

    def create_leaf_path(self):
        self.path.moveTo(0, -self.size/2)
        self.path.lineTo(self.size/3, 0)
        self.path.lineTo(0, self.size/2)
        self.path.lineTo(-self.size/3, 0)
        self.path.closeSubpath()

    def update(self, w, h):
        self.y += self.speed_y
        self.x += self.drift
        if self.shape == "leaf" or self.shape == "flower":
            self.x += math.sin(self.y / 50) * 0.5
        self.rotation += self.rotation_speed
        if (self.speed_y > 0 and self.y > h + 20) or (self.speed_y < 0 and self.y < -20):
            self.reset(w, h)
        if self.x < -20 or self.x > w + 20:
            self.reset(w, h)

# --- OVERLAY EFFECT ---
class SeasonalOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.particles = []
        self.current_season = "spring"
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.initialized = False

    def set_season(self, season):
        self.current_season = season
        self.particles = []
        self.init_particles()

    def init_particles(self):
        if self.width() > 0:
            count = 60 if self.current_season != "winter" else 150
            self.particles = [Particle(self.width(), self.height(), self.current_season) for _ in range(count)]
            if not self.timer.isActive(): self.timer.start(16)
            self.initialized = True

    def update_animation(self):
        w, h = self.width(), self.height()
        for p in self.particles: p.update(w, h)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        for p in self.particles:
            painter.save()
            painter.translate(p.x, p.y)
            painter.rotate(p.rotation)
            if p.shape == "bubble":
                painter.setPen(QPen(p.color, 1))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawEllipse(QPointF(0,0), p.size/2, p.size/2)
            elif p.shape == "snow":
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(p.color))
                painter.drawEllipse(QPointF(0,0), p.size/2, p.size/2)
            else:
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(p.color))
                painter.drawPath(p.path)
            painter.restore()

# --- 3. CLASS NÚT BOT NỔI (MỚI THÊM) ---
class FloatingBotButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(60, 60)
        self.setText("🤖") # Icon Robot
        
        # Style cho nút
        self.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-size: 30px;
                border-radius: 30px;
                border: 2px solid white;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        # Hiệu ứng bóng đổ
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(shadow)
        
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Timer rung lắc
        self.shake_timer = QTimer(self)
        self.shake_timer.timeout.connect(self.shake)
        self.shake_timer.start(5000) # Rung mỗi 5 giây

    def shake(self):
        self.anim = QPropertyAnimation(self, b"pos")
        self.anim.setDuration(500)
        self.anim.setLoopCount(1)
        
        # Lấy vị trí hiện tại
        current_pos = self.pos()
        x, y = current_pos.x(), current_pos.y()
        
        # KeyFrames rung lắc
        self.anim.setKeyValueAt(0, QPoint(x, y))
        self.anim.setKeyValueAt(0.1, QPoint(x - 5, y))
        self.anim.setKeyValueAt(0.2, QPoint(x + 5, y))
        self.anim.setKeyValueAt(0.3, QPoint(x - 5, y))
        self.anim.setKeyValueAt(0.4, QPoint(x + 5, y))
        self.anim.setEndValue(QPoint(x, y))
        self.anim.start()





# --- MÀU SẮC (Dùng lại của bạn) ---
TET_RED_BG = "#b30000"
TET_GOLD = "#FFD700"
TET_CREAM = "#FFF8E1"

class UserProfileWidget(QFrame):
    def __init__(self, parent=None, callback=None):
        super().__init__(parent)
        self.callback = callback
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(160) # Cố định chiều cao cho đẹp

        # --- 1. SETUP UI STYLE ---
        # Dùng Gradient cho nền và viền bo tròn
        self.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(179, 0, 0, 0.6); /* Đỏ trong suốt */
                border: 1px solid {TET_GOLD};
                border-radius: 20px;
                margin: 5px;
            }}
        """)

        # Tạo bóng đổ (Drop Shadow)
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(15)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(5)
        self.shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(self.shadow)

        # --- 2. LAYOUT ---
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 20, 10, 20)
        layout.setSpacing(5)

        # Avatar "Rồng"
        self.avatar = QLabel("🐉")
        self.avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.avatar.setFixedSize(70, 70)
        # Style Avatar: Tròn, Viền vàng, Nền kem
        self.avatar.setStyleSheet(f"""
            QLabel {{
                background-color: {TET_CREAM};
                color: {TET_RED_BG};
                font-size: 35px;
                border: 2px solid {TET_GOLD};
                border-radius: 35px; /* 70/2 = 35 để tròn vo */
            }}
        """)
        
        # Tên User
        self.lbl_name = QLabel("Login Tet Account")
        self.lbl_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_name.setStyleSheet(f"""
                    QLabel {{
                        color: {TET_GOLD}; 
                        font-weight: bold; 
                        font-size: 15px; 
                        border: none; 
                        background: transparent;
                        margin-top: 10px; 
                    }}
                """)
        # Trạng thái
        self.lbl_status = QLabel("Guest Mode")
        self.lbl_status.setStyleSheet("color: #FFECB3; font-size: 11px; font-style: italic; border: none; background: transparent;")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.avatar, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_name)
        layout.addWidget(self.lbl_status)
        self.setLayout(layout)

        # --- 3. VARIABLES CHO ANIMATION ---
        self._ripple_radius = 0
        self._ripple_opacity = 0
        self._center_click = QPoint()
        
        # Animation hover (Nổi lên)
        self.hover_anim = QPropertyAnimation(self, b"geometry") # Placeholder, thực tế ta animate margin hoặc shadow

    # --- RIPPLE EFFECT LOGIC (VẼ SÓNG KHI CLICK) ---
    @pyqtProperty(float)
    def ripple_radius(self):
        return self._ripple_radius

    @ripple_radius.setter
    def ripple_radius(self, radius):
        self._ripple_radius = radius
        self.update() # Vẽ lại widget

    @pyqtProperty(float)
    def ripple_opacity(self):
        return self._ripple_opacity

    @ripple_opacity.setter
    def ripple_opacity(self, opacity):
        self._ripple_opacity = opacity
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # 1. Lưu vị trí click
            self._center_click = event.position().toPoint()
            
            # 2. Setup Animation Radius (Lan tỏa)
            self.anim_radius = QPropertyAnimation(self, b"ripple_radius")
            self.anim_radius.setDuration(400)
            self.anim_radius.setStartValue(0)
            self.anim_radius.setEndValue(self.width())
            self.anim_radius.setEasingCurve(QEasingCurve.Type.OutQuad)

            # 3. Setup Animation Opacity (Mờ dần)
            self.anim_opacity = QPropertyAnimation(self, b"ripple_opacity")
            self.anim_opacity.setDuration(400)
            self.anim_opacity.setStartValue(0.5)
            self.anim_opacity.setEndValue(0)

            # 4. Chạy
            self.anim_radius.start()
            self.anim_opacity.start()

            # Gọi callback gốc
            if self.callback:
                QTimer.singleShot(150, self.callback) # Delay nhẹ để thấy hiệu ứng

        super().mousePressEvent(event)

    def paintEvent(self, event):
        # Vẽ giao diện gốc (Background, border...)
        super().paintEvent(event)
        
        # Vẽ hiệu ứng Ripple đè lên trên
        if self._ripple_opacity > 0:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setPen(Qt.PenStyle.NoPen)
            
            # Màu sóng (Trắng pha vàng)
            color = QColor(255, 215, 0)
            color.setAlphaF(self._ripple_opacity)
            painter.setBrush(QBrush(color))
            
            # --- SỬA DÒNG NÀY ---
            # Chuyển QPoint thành QPointF để vẽ được với bán kính float
            painter.drawEllipse(QPointF(self._center_click), self._ripple_radius, self._ripple_radius)


    # --- HOVER ANIMATION (DI CHUỘT VÀO) ---
    def enterEvent(self, event):
        # 1. Hiệu ứng Avatar to lên
        self.anim_avatar = QPropertyAnimation(self.avatar, b"geometry")
        # Lưu ý: Cần tính toán rect mới để nó vẫn ở giữa (Logic hơi phức tạp nên dùng StyleSheet anim đơn giản hơn)
        self.avatar.setStyleSheet(f"""
            QLabel {{
                background-color: {TET_CREAM};
                color: {TET_RED_BG};
                font-size: 38px; /* Chữ to lên */
                border: 4px solid {TET_GOLD}; /* Viền dày hơn */
                border-radius: 35px;
            }}
        """)
        
        # 2. Shadow đậm hơn
        self.shadow.setBlurRadius(25)
        self.shadow.setYOffset(8)
        
        # 3. Đổi nền sáng hơn xíu
        self.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(179, 0, 0, 0.8); /* Đậm hơn */
                border: 2px solid {TET_GOLD}; /* Viền dày */
                border-radius: 20px;
                margin: 5px;
            }}
        """)
        super().enterEvent(event)

    def leaveEvent(self, event):
        # Reset về cũ
        self.avatar.setStyleSheet(f"""
            QLabel {{
                background-color: {TET_CREAM};
                color: {TET_RED_BG};
                font-size: 35px;
                border: 2px solid {TET_GOLD};
                border-radius: 35px;
            }}
        """)
        self.shadow.setBlurRadius(15)
        self.shadow.setYOffset(5)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(179, 0, 0, 0.6);
                border: 1px solid {TET_GOLD};
                border-radius: 20px;
                margin: 5px;
            }}
        """)
        super().leaveEvent(event)
    
    def update_info(self, name, email):
        self.lbl_name.setText(name)
        self.lbl_status.setText(email)
        self.avatar.setText(name[0].upper())


# --- SETTINGS PAGE ---
class SettingsPage(QWidget):
    def __init__(self, apply_callback):
        super().__init__()
        self.apply_callback = apply_callback
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        lbl_title = QLabel("Cài Đặt Hệ Thống")
        lbl_title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(lbl_title)
        
        form_layout = QFormLayout()
        self.combo_season = QComboBox()
        self.combo_season.addItems(["spring", "summer", "autumn", "winter"])
        self.combo_season.setItemText(0, "Mùa Xuân (Tết)")
        self.combo_season.setItemText(1, "Mùa Hạ (Biển)")
        self.combo_season.setItemText(2, "Mùa Thu (Lá rụng)")
        self.combo_season.setItemText(3, "Mùa Đông (Tuyết)")
        self.combo_season.setStyleSheet("padding: 5px; font-size: 14px;")
        self.combo_season.currentTextChanged.connect(self.on_change)
        
        form_layout.addRow("Chọn Giao Diện:", self.combo_season)
        layout.addLayout(form_layout)
        layout.addStretch()
        lbl_note = QLabel("Note: Thay đổi sẽ áp dụng ngay lập tức.")
        lbl_note.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(lbl_note)
        self.setLayout(layout)

    def on_change(self):
        keys = ["spring", "summer", "autumn", "winter"]
        idx = self.combo_season.currentIndex()
        self.apply_callback(keys[idx])

# --- MAIN APP ---
class FinanceApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Finance Tracker App")
        # self.resize(800,650)
        self.current_season = "spring" # Lưu mùa hiện tại
        self.user_data = None  # data user
        
        # --- UI Setup ---
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(0)
        self.main_widget.setLayout(self.main_layout)
        
        # Sidebar
        self.sidebar = QFrame()
        # self.sidebar.setFixedWidth(240)
        self.sidebar.setMinimumWidth(240)
        self.sidebar.setMaximumWidth(240)
        self.sidebar_layout = QVBoxLayout()
        self.sidebar_layout.setContentsMargins(0,20,0,0)
        
        self.lbl_sidebar_title = QLabel("FINANCE APP")
        self.lbl_sidebar_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_sidebar_title.setStyleSheet("font-weight: bold; font-size: 18px; margin-top: 20px;")
        self.sidebar_layout.addWidget(self.lbl_sidebar_title)

        from core.app_context import AppContext
        self.app_ctx = AppContext.instance()
        self.app_ctx.user_state_changed.connect(self.on_user_state_changed)
        self.profile_widget = UserProfileWidget(callback=self.handle_google_login)
        self.sidebar_layout.addWidget(self.profile_widget)

        self.nav_btns = []
        self.nav_layout = QVBoxLayout()
        self.nav_layout.setSpacing(10)
        self.sidebar_layout.addLayout(self.nav_layout)
        self.sidebar_layout.addStretch()
        self.sidebar.setLayout(self.sidebar_layout)
        
        # Content
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0,0,0,0)
        
        self.header = QFrame()
        self.header.setFixedHeight(60)
        self.header_layout = QHBoxLayout()
        self.btn_toggle = QPushButton("☰")
        self.btn_toggle.setFixedSize(40,40)
        self.btn_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_toggle.clicked.connect(self.toggle_sidebar)
        
        self.lbl_header_title = QLabel("🥰🥰😉✌️")
        self.lbl_header_title.setStyleSheet("font-size: 18px; font-weight: bold;")

        self.lbl_header_decor = QLabel("🌺 Vạn Sự Như Ý 🌺")
        self.lbl_header_decor.setStyleSheet(f"color: {TET_TEXT_DARK}; font-style: italic; border:none;")

        self.header_layout.addWidget(self.btn_toggle)
        self.header_layout.addWidget(self.lbl_header_title)
        self.header_layout.addStretch()
        self.header_layout.addWidget(self.lbl_header_decor)
        self.header.setLayout(self.header_layout)
        
        self.pages = QStackedLayout()
        self.init_pages()
        
        self.content_layout.addWidget(self.header)
        self.content_layout.addLayout(self.pages)
        self.content_area.setLayout(self.content_layout)
        
        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.content_area)
        
        # --- CÁC THÀNH PHẦN NỔI (OVERLAY + BOT BUTTON) ---
        
        # 1. Overlay Effect
        self.overlay = SeasonalOverlay(self.centralWidget())
        self.overlay.show()
        self.overlay.raise_()
        
        # 2. BOT BUTTON (Mới thêm)
        self.bot_btn = FloatingBotButton(self)
        self.bot_btn.clicked.connect(self.open_chatbot)
        self.bot_btn.show()
        self.bot_btn.raise_() # Đảm bảo nút nằm trên cùng
        self.chat_window = None # Biến giữ cửa sổ chat
        
        self.create_navs()
        self.apply_theme("spring")

    def create_navs(self):
        items = [("Thống Kê", 0), ("Thu Chi", 1), ("Sổ Nợ", 2), ("Ngân sách", 3), ("Lịch", 4), ("Cài Đặt", 5)]
        for text, idx in items:
            btn = QPushButton(text)
            btn.setFixedHeight(50)
            btn.setCheckable(True)
            btn.setAutoExclusive(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, i=idx: self.pages.setCurrentIndex(i))
            self.nav_layout.addWidget(btn)
            self.nav_btns.append(btn)
        self.nav_btns[0].setChecked(True)

    def init_pages(self):
        # __all__ = ["CalendarMgr", "DebtManager", "TransactionMgr", "MainDashboard", "FinanceApp"]
        from services import MainDashboard, CalendarMgr, DebtManager, TransactionMgr, BudgetMgr

        self.pages.addWidget(MainDashboard())
        self.pages.addWidget(TransactionMgr())
        self.pages.addWidget(DebtManager())
        self.pages.addWidget(BudgetMgr())
        self.pages.addWidget(CalendarMgr())

        # 3 trang đầu demo
        # for name in ["Thống Kê", "Sổ Nợ", "Lịch"]:
        #     lbl = QLabel(name)
        #     lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        #     lbl.setStyleSheet("font-size: 40px; color: gray;")
        #     self.pages.addWidget(lbl)
        
        # Trang 4: Settings
        self.settings_page = SettingsPage(apply_callback=self.apply_theme)
        self.pages.addWidget(self.settings_page)

    def open_chatbot(self):

        self.bot_btn.shake() 
        if self.chat_window is None:
            self.chat_window = BotChatAgent(self.current_season)
        else:
            self.chat_window.update_theme(self.current_season)
        
        self.chat_window.show()
        self.chat_window.raise_()
        self.chat_window.activateWindow()

    def apply_theme(self, season_name):
        self.current_season = season_name
        theme = THEMES[season_name]
        
        self.overlay.set_season(season_name)
        
        self.sidebar.setStyleSheet(f"""
            QFrame {{ background-color: {theme['sidebar_bg']}; border-right: 1px solid {theme['sidebar_border']}; }}
            QLabel {{ color: {theme['accent_color']}; }}
        """)
        
        self.content_area.setStyleSheet(f"background-color: {theme['content_bg']};")
        
        self.header.setStyleSheet(f"background-color: white; border-bottom: 2px solid {theme['sidebar_bg']};")
        self.btn_toggle.setStyleSheet(f"QPushButton {{ border: none; font-size: 24px; color: {theme['sidebar_bg']}; }} QPushButton:hover {{ color: {theme['sidebar_border']}; }}")
        self.lbl_header_title.setStyleSheet(f"color: {theme['sidebar_bg']}; font-weight: bold; font-size: 18px;")
        
        # Update Bot Button Style theo mùa
        self.bot_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme['sidebar_bg']};
                color: {theme['accent_color']};
                font-size: 30px;
                border-radius: 30px;
                border: 2px solid white;
            }}
            QPushButton:hover {{ background-color: {theme['sidebar_border']}; }}
        """)

        for btn in self.nav_btns:
            btn.setStyleSheet(f"""
                QPushButton {{ border: none; text-align: left; padding-left: 30px; color: {theme['accent_color']}; font-size: 15px; background-color: transparent; }}
                QPushButton:hover {{ background-color: {theme['btn_hover']}; color: white; border-left: 4px solid {theme['sidebar_border']}; }}
                QPushButton:checked {{ background-color: {theme['content_bg']}; color: {theme['sidebar_bg']}; font-weight: bold; border-left: 6px solid {theme['sidebar_border']}; border-top-right-radius: 25px; border-bottom-right-radius: 25px; }}
            """)
        
        for i in range(5):
            widget = self.pages.widget(i)
            if isinstance(widget, QLabel):
                widget.setStyleSheet(f"font-size: 40px; color: {theme['text_color']}; font-weight: bold;")
        
        # Nếu đang mở chat thì update luôn theme cho chat
        if self.chat_window:
            self.chat_window.update_theme(season_name)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'overlay'):
            self.overlay.setGeometry(self.centralWidget().rect())
            if not self.overlay.initialized: 
                self.overlay.init_particles()
        
        # --- LOGIC GIỮ NÚT Ở GÓC DƯỚI PHẢI ---
        if hasattr(self, 'bot_btn'):
            # Cách lề phải 80px, cách lề dưới 80px
            new_x = self.width() - 80
            new_y = self.height() - 80
            self.bot_btn.move(new_x, new_y)

    def toggle_sidebar(self):
            # 1. Lấy chiều rộng hiện tại
            width = self.sidebar.width()
            
            # 2. Tính chiều rộng đích (Nếu đang to > 0 thì thu về 0, ngược lại thì ra 240)
            # Lưu ý: check width > 0 thay vì 100 để chính xác hơn
            new_width = 0 if width > 0 else 240

            # 3. Tạo Animation Group để chạy song song 2 thuộc tính
            self.anim_group = QParallelAnimationGroup()

            # Animation cho Minimum Width (Quan trọng: cái này giúp sidebar co lại)
            self.anim_min = QPropertyAnimation(self.sidebar, b"minimumWidth")
            self.anim_min.setDuration(400)
            self.anim_min.setStartValue(width)
            self.anim_min.setEndValue(new_width)
            self.anim_min.setEasingCurve(QEasingCurve.Type.InOutQuart)

            # Animation cho Maximum Width
            self.anim_max = QPropertyAnimation(self.sidebar, b"maximumWidth")
            self.anim_max.setDuration(400)
            self.anim_max.setStartValue(width)
            self.anim_max.setEndValue(new_width)
            self.anim_max.setEasingCurve(QEasingCurve.Type.InOutQuart)

            # Thêm cả 2 vào group và chạy
            self.anim_group.addAnimation(self.anim_min)
            self.anim_group.addAnimation(self.anim_max)
            self.anim_group.start()

    def handle_google_login(self):
        if self.app_ctx.user_data and self.app_ctx.user_data.get("source") == "google":
            # Đã đăng nhập → chỉ show thông báo
            name = self.app_ctx.user_data["name"]
            QMessageBox.information(self, "Tài Khoản", f"Xin chào: {name}\nChúc mừng năm mới! 🧧")
        else:
            # Chưa đăng nhập → gọi login qua AppContext
            self.app_ctx.google_login()

    def on_user_state_changed(self, user_data):
        """Cập nhật profile widget khi user login/logout toàn cục."""
        if user_data and user_data.get("source") == "google":
            self.user_data = user_data
            self.profile_widget.update_info(user_data["name"], user_data["email"])
        else:
            # Guest mode
            self.user_data = None
            self.profile_widget.lbl_name.setText("Login Tet Account")
            self.profile_widget.lbl_status.setText("Guest Mode")
            self.profile_widget.avatar.setText("🐉")
