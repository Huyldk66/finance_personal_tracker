
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

from ..setting import SoundManager
from . import *
from core._const import THEMES_DEBT_PAGE



class BudgetMgr(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Master Budget Pro - Âm Thanh Sống Động")
        self.resize(1100, 750)
        self.setup_ui()
        self.apply_theme("spring")
        
        # --- Khởi động nhạc nền ---
        SoundManager.instance() 

    def setup_ui(self):
        toolbar = QToolBar("Main Toolbar"); toolbar.setIconSize(QSize(24, 24)); self.addToolBar(toolbar)
        lbl_theme = QLabel("  🎨 Giao diện: "); self.combo_theme = QComboBox(); self.combo_theme.addItems(THEMES.keys())
        self.combo_theme.currentTextChanged.connect(self.apply_theme) # signal 
        toolbar.addWidget(lbl_theme); toolbar.addWidget(self.combo_theme)
        
        # --- Volume Control ---
        toolbar.addSeparator()
        lbl_vol = QLabel("  🔊 Nhạc nền: ")
        self.sld_vol = QSlider(Qt.Orientation.Horizontal)
        self.sld_vol.setRange(0, 100); self.sld_vol.setValue(80); self.sld_vol.setFixedWidth(100)
        self.sld_vol.valueChanged.connect(lambda v: SoundManager.instance().set_bgm_volume(v/100))
        toolbar.addWidget(lbl_vol); toolbar.addWidget(self.sld_vol)

        self.tabs = QTabWidget(); 
        self.tabs.setTabPosition(QTabWidget.TabPosition.North); 
        self.setCentralWidget(self.tabs)
        
        self.tab_personal = BudgetApp(); 
        self.tabs.addTab(self.tab_personal, "🔐 Két Sắt Cá Nhân")

        self.tab_group = GroupFundMgr(); 
        self.tabs.addTab(self.tab_group, "👥 Quỹ Nhóm & Dự Án")
        self.tabs.setStyleSheet(""" QTabBar::tab { height: 40px; width: 200px; font-weight: bold; font-size: 14px; } QTabWidget::pane { border-top: 2px solid #bdc3c7; } """)

    def apply_theme(self, key):
        # 1. Lấy dictionary màu từ key (spring, summer, autumn, winter)
        theme = THEMES_DEBT_PAGE.get(key)
        
        if not theme:
            print(f"Theme '{key}' không tồn tại!")
            return

        # 2. Xây dựng chuỗi QSS (Qt Style Sheet)
        # Chúng ta map các biến màu vào các thành phần UI tương ứng
        stylesheet = f"""
            /* --- CẤU HÌNH CHUNG --- */
            QMainWindow, QWidget {{
                background-color: {theme['bg_primary']};
                color: {theme['text_main']};
                font-family: 'Segoe UI', Arial, sans-serif;
            }}

            /* --- BUTTONS (Dùng màu bg_secondary làm chủ đạo) --- */
            QPushButton {{
                background-color: {theme['bg_secondary']};
                color: {theme['text_light']};
                border: 1px solid {theme['bg_secondary']};
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {theme['btn_hover']};
                border-color: {theme['btn_hover']};
            }}
            QPushButton:pressed {{
                background-color: {theme['accent']}; /* Nhấn vào sẽ ra màu Accent */
            }}

            /* --- TABS (QTabWidget & QTabBar) --- */
            QTabWidget::pane {{
                border: 2px solid {theme['bg_secondary']}; /* Viền bao quanh nội dung tab */
                background-color: {theme['bg_primary']};
                border-radius: 4px;
            }}
            
            QTabBar::tab {{
                background: {theme['bg_primary']};     /* Tab chưa chọn trùng màu nền */
                color: {theme['text_main']};           /* Chữ màu chính */
                border: 1px solid {theme['accent']};   /* Viền mỏng màu Accent */
                border-bottom: none;
                padding: 8px 20px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                min-width: 120px;
            }}

            QTabBar::tab:selected {{
                background: {theme['bg_secondary']};   /* Tab đang chọn nổi bật */
                color: {theme['text_light']};          /* Chữ trắng */
                font-weight: bold;
            }}
            
            QTabBar::tab:hover:!selected {{
                background: {theme['accent']};         /* Hover vào tab chưa chọn */
                color: {theme['text_light']};
            }}

            /* --- INPUTS (QLineEdit, QTextEdit...) --- */
            QLineEdit, QTextEdit, QSpinBox {{
                background-color: #FFFFFF;             /* Nền input luôn trắng cho dễ đọc */
                color: {theme['text_main']};
                border: 1px solid {theme['accent']};   /* Viền input dùng màu Accent */
                border-radius: 4px;
                padding: 4px;
            }}
            QLineEdit:focus {{
                border: 2px solid {theme['bg_secondary']}; /* Focus vào input thì viền đậm hơn */
            }}
            
            /* --- LABELS --- */
            QLabel {{
                color: {theme['text_main']};
            }}
            
            /* Label tiêu đề (nếu bạn có set objectName='title') */
            QLabel#title {{
                color: {theme['bg_secondary']};
                font-size: 18px;
                font-weight: bold;
            }}
        """

        # 3. Áp dụng Style Sheet lên toàn bộ Main Window
        self.setStyleSheet(stylesheet)

        # 4. Cập nhật cho các Widget con đặc biệt (nếu chúng cần xử lý logic vẽ riêng)
        # Nếu tab_personal và tab_group chỉ là Widget chứa Button/Label thông thường
        # thì dòng self.setStyleSheet ở trên đã lo hết, không cần gọi update_theme bên dưới.
        # Tuy nhiên, nếu chúng có biểu đồ (Chart) cần redraw lại màu, hãy giữ lại dòng này:
        if hasattr(self, 'tab_personal') and hasattr(self.tab_personal, 'update_theme'):
            self.tab_personal.update_theme(theme)
            
        if hasattr(self, 'tab_group') and hasattr(self.tab_group, 'update_theme'):
            self.tab_group.update_theme(theme)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    window = BudgetMgr()
    window.show()
    sys.exit(app.exec())