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

    def __init__(self, main, parent=None):
        QFrame.__init__(self, parent)
        self.main = main
        self.setStyleSheet(
        '''
        border-image: url(res/bgColor.png);
        background-repeat: no-repeat;
        ''')
        self.isDraging = False
        self.setGeometry(0, 0, 800, 60)
        self.addRobotLogo(main)
        self.addButtons(self)
        titleLabel = QLabel(self)
        titleLabel.setText(u'CC音乐')
        titleLabel.setGeometry(110, 10, 100, 40)
        titleFont = QFont("Microsoft YaHei", 15, 70)
        titleLabel.setFont(titleFont)
        titleLabel.setStyleSheet("color: rgb(255, 255, 255)")

    def addRobotLogo(self, main):
        btn = QPushButton(main)
        btn.setObjectName("btnSpecial")
        btn.setStyleSheet(
            '''
            QPushButton#btnSpecial {
            border-image: url(res/robot_1.png);
            background-repeat: no-repeat;
            }
            QPushButton#btnSpecial:hover {
            border-image: url(res/robot_2.png);
            background-repeat: no-repeat;
            }
            QPushButton#btnSpecial:pressed {
            border-image: url(res/robot_3.png);
            background-repeat: no-repeat;
            }
            ''')
        btn.setGeometry(20, 60, 67, 60)

    def addButtons(self, main):
        closeButton = PushButton(main)
        closeButton.loadPixmap('res/close.png')
        closeButton.setGeometry(770, 10, 16, 16)
        closeButton.clicked.connect(self.main.close)

        miniButton = PushButton(main)
        miniButton.loadPixmap('res/mini.png')
        miniButton.setGeometry(740, 10, 16, 16)
        miniButton.clicked.connect(self.main.showMinimized)

    def mousePressEvent(self, event):
        self.isDraging = True
        self.main.dragPostion = event.globalPos() - self.main.pos()

    def mouseReleaseEvent(self, event):
        self.isDraging = False

    def mouseMoveEvent(self, event):
        if self.isDraging:
            self.main.move(event.globalPos() - self.main.dragPostion)


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