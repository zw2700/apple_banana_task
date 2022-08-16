# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import QApplication
from widget import Widget, CDialog


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dlg = CDialog()
    res = dlg.exec()
    if res == CDialog.Accepted:
        w = Widget()
        w.showMaximized()
        sys.exit(app.exec_())
    else:
        sys.exit(0)