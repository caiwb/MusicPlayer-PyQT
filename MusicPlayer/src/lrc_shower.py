#-*- encoding: UTF-8 -*-

import re
from music_file_object import *
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

class StateLabel(QLabel):

    def __init__(self, parent=None):
        QLabel.__init__(self, parent)
        self.parent = parent
        self.setAcceptDrops(True)

    def contextMenuEvent(self, event):
        self.parent.contextMenuEvent(event)

    def dragEnterEvent(self, event):
        self.parent.dragEnterEvent(event)

    def dragMoveEvent(self, event):
        self.parent.dragMoveEvent(event)

    def dropEvent(self, event):
        self.parent.dropEvent(self, event)


class LRCShower(QListView):

    def __init__(self, parent=None):
        QListView.__init__(self, parent)
        self.mainWidget = parent
        self.model = QStandardItemModel()
        self.setModel(self.model)
        self.setStyleSheet(
            '''
            LRCShower{background-color: rgba(230, 230, 240, 0)}
            '''
        )

        self.setWordWrap(True)
        self.setUniformItemSizes(True)
        self.setGridSize(QSize(self.rect().width(), 30))
        self.setFont(QFont("Microsoft YaHei", 10))
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setFocusPolicy(Qt.NoFocus)
        self.setSelectionMode(QAbstractItemView.NoSelection)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setAcceptDrops(True)

        self.lrcTimeList = []
        self.lrcWordList = []
        self.currentRow = -1
        self.lrcDict = {}

        self.lastOpenedPath = self.mainWidget.lastLRCOpenedPath
        self.contextMenu = QMenu(self)
        self.openAction = QAction(u'打开歌词', self)
        self.downloadAction = QAction(u'下载歌词', self)
        self.deleteAction = QAction(u'删除歌词', self)
        self.connect(self.openAction, SIGNAL('triggered()'), self.openLRC)
        self.connect(self.downloadAction, SIGNAL('triggered()'), self.downloadLRC)
        self.connect(self.deleteAction, SIGNAL('triggered()'), self.deleteLRC)
        self.contextMenu.addAction(self.openAction)
        self.contextMenu.addSeparator()
        self.contextMenu.addAction(self.downloadAction)
        self.contextMenu.addSeparator()
        self.contextMenu.addAction(self.deleteAction)

        self.downloadingLabel = StateLabel(self)
        self.downloadingLabel.setGeometry(150, 110, 200, 200)
        self.movie = QMovie("res/loading.gif")
        self.movie.setScaledSize(QSize(200, 200))
        self.movie.start()
        self.movie.setSpeed(70)
        self.downloadingLabel.setMovie(self.movie)
        self.downloadingLabel.setContentsMargins(0, 0, 0, 0)
        self.downloadingLabel.setHidden(True)

        self.waitForLrcLabel = StateLabel(self)
        self.waitForLrcLabel.setText(u"将歌词文件拖入打开，\n   或右键点击下载")
        self.waitForLrcLabel.setGeometry(190, 110, 200, 200)
        self.waitForLrcLabel.setHidden(False)

        self.downloadFailedLabel = StateLabel(self)
        self.downloadFailedLabel.setText(u"   歌词下载失败了，\n请打开本地歌词文件")
        self.downloadFailedLabel.setGeometry(180, 110, 200, 200)
        self.downloadFailedLabel.setHidden(True)

    def openLRC(self, path=None):
        if not path:
            path = QFileDialog.getOpenFileName(self, u'打开', self.lastOpenedPath, u'歌词文件 (*.lrc)')
            if path:
                self.lastOpenedPath = QFileInfo(path).absoluteDir().absolutePath()
        if path:
            self.clear()
            if not isinstance(path, unicode):
                path = unicode(path)
            try:
                lrcFile = open(path)
                lrc = lrcFile.read()
                self.lrcDict = self.lrcToDict(lrc)
            except Exception as e:
                logging.warning(e.message)
            finally:
                lrcFile.close()
                if self.lrcDict:
                    if self.mainWidget.playingMusic:
                        self.mainWidget.playingMusic.lrcState = LRCState.lrcShowing
                    self.lrcTimeList = self.lrcDict.keys()
                    self.lrcTimeList.sort()
                    self.lrcWordList = [self.lrcDict[key] for key in self.lrcTimeList]
                    for word in self.lrcWordList:
                        try:
                            word = word.decode("utf-8")
                        except:
                            word = word.decode("gbk")
                        finally:
                            item = QStandardItem(word)
                            item.setTextAlignment(Qt.AlignCenter)
                            self.model.appendRow(item)
                    if self.mainWidget.playingMusic:
                        self.mainWidget.musicToLrcDict\
                        [_toUtf8(self.mainWidget.playingMusic.filePath).data()] = path

    def downloadLRC(self):
        self.connect(self.mainWidget.playingMusic,
                     SIGNAL('downloadLRCComplete(QString, QString)'), self.downloadComplete)
        self.mainWidget.playingMusic.downloadLRC()
        self.mainWidget.playingMusic.lrcState = LRCState.downloading
        self.updateMusic()

    def downloadComplete(self, musicPath, lrcPath):
        if not len(lrcPath):
            if self.mainWidget.playingMusic.filePath == musicPath:
                self.updateMusic()
        elif self.mainWidget.playingMusic.filePath == musicPath:
            self.openLRC(lrcPath)
        else:
            self.mainWidget.musicToLrcDict[_toUtf8(musicPath).data()] = unicode(lrcPath)

    def deleteLRC(self):
        self.mainWidget.musicToLrcDict.pop(_toUtf8(self.mainWidget.playingMusic.filePath).data())
        self.mainWidget.playingMusic.lrcState = LRCState.waitForLrc
        self.updateMusic()

    def updateLRC(self, ms):
        if not len(self.lrcDict.keys()) or not self.model.rowCount():
            return
        time = ms/1000
        for t in self.lrcTimeList:
            if time == t:
                if self.currentRow != -1:
                    self.model.item(self.currentRow, 0).setForeground(QBrush(QColor(0, 0, 0)))
                self.currentRow = self.lrcTimeList.index(t)
                self.model.item(self.currentRow, 0).setForeground(QBrush(QColor(255, 100, 100)))
                self.scrollTo(self.model.index(self.currentRow, 0), QAbstractItemView.PositionAtCenter)
            if time < t:
                if self.lrcTimeList.index(t) != 0:
                    if self.currentRow != -1:
                        self.model.item(self.currentRow, 0).setForeground(QBrush(QColor(0, 0, 0)))
                    self.currentRow = self.lrcTimeList.index(t) - 1
                    self.model.item(self.currentRow, 0).setForeground(QBrush(QColor(255, 100, 100)))
                    self.scrollTo(self.model.index(self.currentRow, 0), QAbstractItemView.PositionAtCenter)
                break

    def clear(self):
        self.downloadingLabel.setHidden(True)
        self.waitForLrcLabel.setHidden(True)
        self.downloadFailedLabel.setHidden(True)
        self.model.clear()
        self.lrcDict = {}
        self.lrcTimeList = []
        self.lrcWordList = []
        self.currentRow = -1

    def updateMusic(self):
        self.clear()

        if not self.mainWidget.playingMusic:
            self.waitForLrcLabel.setHidden(False)
            return

        if self.mainWidget.playingMusic and \
                self.mainWidget.musicToLrcDict.has_key(_toUtf8(self.mainWidget.playingMusic.filePath).data()):
            self.mainWidget.playingMusic.lrcState = LRCState.lrcShowing

        state = self.mainWidget.playingMusic.lrcState

        if state == LRCState.waitForLrc:
            self.waitForLrcLabel.setHidden(False)
        elif state == LRCState.downloading:
            self.downloadingLabel.setHidden(False)
        elif state == LRCState.downloadFailed:
            self.downloadFailedLabel.setHidden(False)
        elif state == LRCState.lrcShowing:
            lrcPath = _fromUtf8(
                self.mainWidget.musicToLrcDict[_toUtf8(self.mainWidget.playingMusic.filePath).data()])
            self.openLRC(lrcPath)

    def contextMenuEvent(self, event):
        self.downloadAction.setEnabled(self.mainWidget.playingIndex != -1)
        self.deleteAction.setEnabled(self.mainWidget.playingMusic is not None and
                                     self.mainWidget.musicToLrcDict.has_key(
                                         _toUtf8(self.mainWidget.playingMusic.filePath).data()))
        self.contextMenu.exec_(event.globalPos())

    def dragEnterEvent(self, event):
        if event.mimeData().urls()[0].path().toLower().contains('.lrc'):
            event.accept()
        else:
            super(QListView, self).dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.mimeData().urls()[0].path().toLower().contains('.lrc'):
            event.accept()
        else:
            super(QListView, self).dragMoveEvent(event)

    def dropEvent(self, event):
        path = event.mimeData().urls()[0].path().remove(0, 1)
        self.openLRC(path)

    def lrcToDict(self, lrc):
        lrc_dict = {}
        remove = lambda x: x.strip('[|]')
        for line in lrc.split('\n'):
            time_stamps = re.findall(r'\[[^\]]+\]', line)
            if time_stamps:
                lyric = line
                for tplus in time_stamps:
                    lyric = lyric.replace(tplus, '')
                for tplus in time_stamps:
                    t = remove(tplus)
                    tag_flag = t.split(':')[0]
                    if not tag_flag.isdigit():
                        continue
                    time_lrc = int(tag_flag) * 60
                    time_lrc += int(t.split(':')[1].split('.')[0])
                    lrc_dict[time_lrc] = lyric
        return lrc_dict