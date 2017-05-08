# -*- encoding:utf-8 -*-

from PyQt4.phonon import Phonon
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


class BottomToolFrame(QFrame):

    def __init__(self, main, parent=None):
        QFrame.__init__(self, parent)
        self.main = main
        self._mediaObject = main.mediaObject
        self._audioOutput = main.audioOutput
        self._playingMusic = main.playingMusic
        self.playingOrder = 0

        self.setStyleSheet(
        '''
        BottomToolFrame{
        border-width: 1px 0 0 0;
        border-style: solid;
        border-color: gray;
        }
        ''')
        rect = parent.rect()
        self.setGeometry(0, rect.height() - 60, rect.width(), 60)
        self.lastButton = QPushButton()
        self.lastButton.setMinimumSize(40, 40)
        self.lastButton.setObjectName("btnSpecial")
        self.lastButton.setStyleSheet(
        '''
        QPushButton#btnSpecial {
        border-image: url(res/last.png);
        background-repeat: no-repeat;
        }
        QPushButton#btnSpecial:pressed {
        border-image: url(res/last_press.png);
        background-repeat: no-repeat;
        }
        ''')

        self.playButton = QPushButton()
        # self.playButton.setText(u"播放")
        self.playButton.setMinimumSize(40, 40)
        self.playButton.setObjectName("btnSpecial")
        self.playButton.setStyleSheet(
        '''
        QPushButton#btnSpecial {
        border-image: url(res/play.png);
        background-repeat: no-repeat;
        }
        QPushButton#btnSpecial:pressed {
        border-image: url(res/play_press.png);
        background-repeat: no-repeat;
        }
        ''')
        self.nextButton = QPushButton()
        self.nextButton.setMinimumSize(40, 40)
        self.nextButton.setObjectName("btnSpecial")
        self.nextButton.setStyleSheet(
        '''
        QPushButton#btnSpecial {
        border-image: url(res/next.png);
        background-repeat: no-repeat;
        }
        QPushButton#btnSpecial:pressed {
        border-image: url(res/next_press.png);
        background-repeat: no-repeat;
        }
        ''')

        self.orderButton = QPushButton()
        self.orderButton.setText(u"顺序播放")

        self.seekSlider = Phonon.SeekSlider()
        self.seekSlider.setMediaObject(self._mediaObject)

        self.curTimeInt = -1

        self.timeString = QString('00:00/00:00')
        self.timeLabel = QLabel(self.timeString)
        self.timeLabel.setAlignment(Qt.AlignCenter)
        self.timeLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.volumeSlider = Phonon.VolumeSlider()
        self.volumeSlider.setAudioOutput(self._audioOutput)

        hLayout = QHBoxLayout(self)
        hLayout.addWidget(self.lastButton)
        hLayout.addWidget(self.playButton)
        hLayout.addWidget(self.nextButton)
        hLayout.addWidget(self.orderButton)
        hLayout.addWidget(self.seekSlider)
        hLayout.addWidget(self.timeLabel)
        hLayout.addWidget(self.volumeSlider)
        hLayout.addStretch()
        hLayout.setStretchFactor(self.lastButton, 1)
        hLayout.setStretchFactor(self.playButton, 1)
        hLayout.setStretchFactor(self.nextButton, 1)
        hLayout.setStretchFactor(self.orderButton, 1)
        hLayout.setStretchFactor(self.seekSlider, 10)
        hLayout.setStretchFactor(self.timeLabel, 1)
        hLayout.setStretchFactor(self.volumeSlider, 5)

        self.lastButton.clicked.connect(self.lastMusic)
        self.playButton.clicked.connect(self.playControl)
        self.nextButton.clicked.connect(self.nextMusic)
        self.orderButton.clicked.connect(self.changeOrder)

    def lastMusic(self):
        self.emit(SIGNAL("lastMusic()"))

    def nextMusic(self):
        self.emit(SIGNAL("nextMusic()"))

    def playControl(self):
        self.emit(SIGNAL("playControl()"))

    def stop(self):
        self.emit(SIGNAL("stop()"))

    def changeOrder(self):
        self.playingOrder = 1 - self.playingOrder
        self.orderButton.setText(u"顺序播放" if not self.playingOrder else u"随机播放")
        self.emit(SIGNAL("changeOrder(int)"), self.playingOrder)

    def updateTimeLabel(self, ms):
        time = ms/1000
        if not self.main.playingMusic:
            self.timeLabel.setText('00:00/00:00')
        elif self.curTimeInt != time:
            self.curTimeInt = time
            h = self.curTimeInt / 3600
            m = self.curTimeInt % 3600 / 60
            s = self.curTimeInt % 3600 % 60
            curTime = QTime(h, m, s)
            totTime = self.main.playingMusic.time
            curTimeString = curTime.toString("mm:ss") if not totTime.hour() else curTime.toString("hh:mm:ss")
            strList = QStringList()
            strList.append(curTimeString)
            strList.append(self.main.playingMusic.timeString)
            self.timeString = strList.join('/')
            self.timeLabel.setText(self.timeString)

    def updateButtons(self):
        state = self.main.mediaObject.state()
        if state == Phonon.PlayingState:
            self.playButton.setStyleSheet(
                '''
                QPushButton#btnSpecial {
                border-image: url(res/pause.png);
                background-repeat: no-repeat;
                }
                QPushButton#btnSpecial:pressed {
                border-image: url(res/pause_press.png);
                background-repeat: no-repeat;
                }
                ''')
        elif state == Phonon.PausedState or state == Phonon.StoppedState:
            self.playButton.setStyleSheet(
                '''
                QPushButton#btnSpecial {
                border-image: url(res/play.png);
                background-repeat: no-repeat;
                }
                QPushButton#btnSpecial:pressed {
                border-image: url(res/play_press.png);
                background-repeat: no-repeat;
                }
                ''')
