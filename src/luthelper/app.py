from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from luthelper.presentation.theme.style import apply_theme
from luthelper.presentation.shell.login_dialog import LoginDialog
from luthelper.presentation.shell.main_window import create_main_window


def main() -> int:
    app = QApplication(sys.argv)
    apply_theme(app)

    login = LoginDialog()
    window = create_main_window()
    login.demoLoginRequested.connect(lambda _username: window.show())

    if login.exec() != LoginDialog.DialogCode.Accepted:
        return 0
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
