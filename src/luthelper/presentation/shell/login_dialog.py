from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from luthelper.presentation.theme import tokens
from luthelper.presentation.widgets.ui_kit import Pill, PrimaryButton, label


class LoginDialog(QDialog):
    """阶段二演示登录弹窗，不访问真实接口。"""

    demoLoginRequested = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("登录 · 抢课助手")
        self.setModal(True)
        self.setMinimumWidth(480)
        self.setMinimumHeight(530)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(26, 24, 26, 22)
        root.setSpacing(14)

        heading = QHBoxLayout()
        heading.addWidget(label("抢课助手", role="title"))
        heading.addStretch(1)
        heading.addWidget(Pill("演示模式", "live"))
        root.addLayout(heading)
        root.addWidget(label("使用兰州理工大学选课系统账号登录。", role="muted"))

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"color: {tokens.LINE};")
        root.addWidget(line)

        root.addWidget(label("学号", role="field"))
        account_row = QHBoxLayout()
        self.account_combo = QComboBox()
        self.account_combo.setEditable(False)
        self.account_combo.addItems(["2024******** · 最近使用", "2023********", "＋ 新增账号"])
        account_row.addWidget(self.account_combo, 1)
        add_button = QPushButton("+")
        add_button.setFixedWidth(36)
        account_row.addWidget(add_button)
        root.addLayout(account_row)

        root.addWidget(label("密码", role="field"))
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setPlaceholderText("输入密码")
        root.addWidget(self.password_edit)

        root.addWidget(label("验证码", role="field"))
        captcha_row = QHBoxLayout()
        self.captcha_edit = QLineEdit()
        self.captcha_edit.setPlaceholderText("输入验证码")
        self.captcha_edit.setMaxLength(8)
        self.captcha_box = QPushButton("7 A K 9")
        self.captcha_box.setFixedSize(126, 40)
        self.captcha_box.setStyleSheet(
            f"""
            QPushButton {{
                color: #2b5345;
                background: #f3f4e9;
                border: 1px dashed #aabbb3;
                border-radius: 8px;
                font-family: "Cascadia Mono", "Consolas";
                font-size: 16px;
                font-weight: 800;
                letter-spacing: 4px;
            }}
            QPushButton:hover {{
                border-color: {tokens.TEAL};
            }}
            """
        )
        captcha_row.addWidget(self.captcha_edit, 1)
        captcha_row.addWidget(self.captcha_box)
        root.addLayout(captcha_row)

        options = QHBoxLayout()
        self.remember = QCheckBox("记住密码")
        self.remember.setChecked(True)
        options.addWidget(self.remember)
        options.addStretch(1)
        options.addWidget(label("账号密码保存在 accounts.json", role="muted"))
        root.addLayout(options)

        self.error_label = label("", role="error")
        self.error_label.setStyleSheet(f"color: {tokens.RED}; font-size: 10px;")
        self.error_label.hide()
        root.addWidget(self.error_label)

        self.login_button = PrimaryButton("进入工作台")
        self.login_button.clicked.connect(self._on_login)
        root.addWidget(self.login_button)
        root.addStretch(1)

        footer = QHBoxLayout()
        footer.addWidget(label("阶段二 · 静态演示", role="muted"))
        footer.addStretch(1)
        footer.addWidget(label("LUTHelper", role="muted"))
        root.addLayout(footer)

    def _on_login(self) -> None:
        if not self.password_edit.text().strip():
            self.error_label.setText("请输入密码。")
            self.error_label.show()
            self.password_edit.setFocus()
            return
        if len(self.captcha_edit.text().strip()) < 4:
            self.error_label.setText("请输入 4 位验证码。")
            self.error_label.show()
            self.captcha_edit.setFocus()
            return
        self.error_label.hide()
        self.demoLoginRequested.emit(self.account_combo.currentText())
        self.accept()
