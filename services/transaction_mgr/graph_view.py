from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *

class BudgetNode(QGraphicsEllipseItem):
    def __init__(self, member, x, y):
        # Khởi tạo ellipse
        super().__init__(-30, -30, 60, 60)
        self.member = member
        self.setPos(x, y)
        self.setBrush(QBrush(member.color))
        self.setPen(QPen(Qt.GlobalColor.black, 2))
        
        # Bật kéo (không cần hover nữa)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)

        # Hiệu ứng glow
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setOffset(0, 0)
        self.setGraphicsEffect(self.shadow)

        # Tạo label text cố định — không dùng tooltip tạm thời
        self.label = QGraphicsTextItem("", self)  # parent = self → tự theo node
        self.label.setZValue(1000)
        self.label.setDefaultTextColor(Qt.GlobalColor.white)
        
        # Tùy chỉnh font và nền bằng HTML (vì QGraphicsTextItem hỗ trợ rich text)
        self.update_visuals()

    def update_visuals(self):
        total = self.member.total_income + self.member.total_expense
        base_size = 40
        max_size = 150
        size = base_size + min(total / 200_000, max_size - base_size)
        self.setRect(-size / 2, -size / 2, size, size)

        intensity = min(total / 1_000_000, 1.0)
        blur_radius = 20 + int(intensity * 80)
        opacity = 0.3 + intensity * 0.6
        glow_color = QColor(self.member.color)
        glow_color.setAlphaF(opacity)
        self.shadow.setBlurRadius(blur_radius)
        self.shadow.setColor(glow_color)

        # Cập nhật nội dung text
        text = (
            f"<div style='"
            f"background:rgba(30,30,40,220); "
            f"color:white; padding:6px; border-radius:5px; "
            f"font-family:Segoe UI; font-size:11px; text-align:center;'>"
            f"<b>{self.member.name}</b><br>"
            f"<span style='color:#27ae60'>💰 {self.member.total_income:,.0f}đ</span> | "
            f"<span style='color:#e74c3c'>{self.member.total_expense:,.0f}đ</span><br>"
            f"<span style='color:#3498db'>Δ {self.member.total_income - self.member.total_expense:,.0f}đ</span>"
            f"</div>"
        )
        self.label.setHtml(text)

        # Căn giữa label phía dưới node
        rect = self.rect()
        label_width = self.label.boundingRect().width()
        self.label.setPos(-label_width / 2, rect.height() / 2 + 5)

    def itemChange(self, change, value):
        # Tùy chọn: nếu bạn muốn label luôn "nổi" phía trên node khi kéo
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            # Không cần làm gì — vì label là con của node, nó tự động theo
            pass
        return super().itemChange(change, value)