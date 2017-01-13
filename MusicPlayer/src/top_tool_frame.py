# -*- encoding:utf-8 -*-

from PyQt4.QtGui import *
from PyQt4.QtCore import *

try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _toUtf8 = QString.toUtf8
except AttributeError:
    def _toUtf8(s):
        return s


class TopToolFrame(QFrame):

    def __init__(self, parent=None):
        QFrame.__init__(self, parent)
        self.parent = parent
        self.setStyleSheet(
        '''
        border-image: url(../res/box.png);
        background-repeat: no-repeat;
        ''')
        self.isDraging = False
        self.setGeometry(0, 0, 800, 60)
        self.addRobotLogo(parent)
        self.addButtons(self)

    def addRobotLogo(self, parent):
        btn = QPushButton(parent)
        btn.setObjectName("btnSpecial")
        btn.setStyleSheet(
            '''
            QPushButton#btnSpecial {
            border-image: url(../res/robot_1.png);
            background-repeat: no-repeat;
            }
            QPushButton#btnSpecial:hover {
            border-image: url(../res/robot_2.png);
            background-repeat: no-repeat;
            }
            QPushButton#btnSpecial:pressed {
            border-image: url(../res/robot_3.png);
            background-repeat: no-repeat;
            }
            ''')
        btn.setGeometry(20, 0, 67, 60)

    def addButtons(self, parent):
        closeButton = PushButton(parent)
        closeButton.loadPixmap('../res/close.png')
        closeButton.setGeometry(770, 10, 16, 16)
        closeButton.clicked.connect(self.parent.close)

        miniButton = PushButton(parent)
        miniButton.loadPixmap('../res/mini.png')
        miniButton.setGeometry(740, 10, 16, 16)
        miniButton.clicked.connect(self.parent.showMinimized)

    def mousePressEvent(self, event):
        self.isDraging = True
        self.parent.dragPostion = event.globalPos() - self.parent.pos()

    def mouseReleaseEvent(self, event):
        self.isDraging = False

    def mouseMoveEvent(self, event):
        if self.isDraging:
            self.parent.move(event.globalPos() - self.parent.dragPostion)


class PushButton(QPushButton):
    def __init__(self, parent=None):
        super(PushButton, self).__init__(parent)

        self.status = 1

    def loadPixmap(self, pic_name):
        self.pixmap = QPixmap(pic_name)
        self.btn_width = self.pixmap.width() / 4
        self.btn_height = self.pixmap.height()

    def enterEvent(self, event):
        if not self.isChecked() and self.isEnabled():
            self.status = 0
            self.update()

    def setDisabled(self, bool):
        super(PushButton, self).setDisabled(bool)
        if not self.isEnabled():
            self.status = 2
            self.update()
        else:
            self.status = 1
            self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.status = 2
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(True)
        if not self.isChecked():
            self.status = 3
        if self.menu():
            self.menu().exec_(event.globalPos())
        self.update()

    def leaveEvent(self, event):
        if not self.isChecked() and self.isEnabled():
            self.status = 1
            self.update()

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.drawPixmap(self.rect(),
                           self.pixmap.copy(self.btn_width * self.status, 0, self.btn_width, self.btn_height))
        painter.end()