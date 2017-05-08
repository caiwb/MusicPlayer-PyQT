# -*- encoding:utf-8 -*-

from PyQt4 import QtGui
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import lrc_shower

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

class MusicInfoFrame(QFrame):

    def __init__(self, main, parent=None):
        QFrame.__init__(self, parent)
        self.main = main
        self._playingIndex = -1
        self._mediaObject = main.mediaObject
        rect = parent.rect()

        self.setGeometry(0, 60, rect.width() - 300, rect.height() - 120)

        self.titleLabel = QLabel()
        self.titleLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.titleLabel.setMaximumWidth(rect.width() - 300)
        self.titleLabel.setWordWrap(True)
        titleFont = QFont("Microsoft YaHei", 15, 75)
        self.titleLabel.setFont(titleFont)
        self.titleLabel.setAlignment(Qt.AlignCenter)

        self.artistLabel = QLabel()
        self.artistLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.artistLabel.setMaximumWidth(rect.width() - 300)
        self.artistLabel.setAlignment(Qt.AlignCenter)

        self.lrcShower = lrc_shower.LRCShower(self.main)

        vLayout = QtGui.QVBoxLayout(self)
        vLayout.addWidget(self.titleLabel)
        vLayout.addWidget(self.artistLabel)
        vLayout.addWidget(self.lrcShower)
        vLayout.addStretch()
        vLayout.setStretchFactor(self.titleLabel, 1)
        vLayout.setStretchFactor(self.artistLabel, 1)
        vLayout.setStretchFactor(self.lrcShower, 10)

    def updateInfo(self):
        if self._playingIndex != self.main.playingIndex:
            self.lrcShower.updateMusic()
            if self.main.playingIndex != -1:
                self._playingIndex = self.main.playingIndex
                self.titleLabel.setText(self.main.playingMusic.title)
                self.artistLabel.setText(self.main.playingMusic.artist)
            else:
                self.titleLabel.setText(QString())
                self.artistLabel.setText(QString())

