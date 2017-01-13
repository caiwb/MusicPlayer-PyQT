#-*- encoding: UTF-8 -*-

import re, lrc_downloader
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

class LoadinLabel(QLabel):

    def __init__(self, parent=None):
        QLabel.__init__(self, parent)
        self.parent = parent

    def contextMenuEvent(self, event):
        self.parent.contextMenuEvent(event)


class LRCShower(QListView):

    def __init__(self, parent=None):
        QListView.__init__(self, parent)
        self.mainWidget = parent
        self.model = QStandardItemModel()
        self.setModel(self.model)

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

        self.lrcDownloader = lrc_downloader.LRCDownloader(self)

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

        self.loadingLabel = LoadinLabel(self)
        self.loadingLabel.setGeometry(150, 110, 200, 200)
        self.movie = QMovie("../res/loading.gif")
        self.movie.setScaledSize(QSize(200, 200))
        self.movie.start()
        self.movie.setSpeed(70)
        self.loadingLabel.setMovie(self.movie)
        self.loadingLabel.setContentsMargins(0, 0, 0, 0)
        self.loadingLabel.setHidden(True)

    def openLRC(self, path=None):
        self.loadingLabel.setHidden(True)
        print len(path)
        if path and len(path) == 0:
            print 'r'
            return
        if not path:
            path = QFileDialog.getOpenFileName(self, u'打开', self.lastOpenedPath, u'歌词文件 (*.lrc)')
            if path:
                self.lastOpenedPath = QFileInfo(path).absoluteDir().absolutePath()
        if path:
            if not isinstance(path, unicode):
                path = unicode(path)
            try:
                lrcFile = open(path)
                lrc = lrcFile.read()
                self.lrcDict = self.lrcToDict(lrc)
            except Exception as e:
                raise ValueError(e)
            finally:
                lrcFile.close()
            if self.lrcDict:
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
                        item.setFont(QFont(50))
                        self.model.appendRow(item)
                if self.mainWidget.playingMusic:
                    self.mainWidget.musicToLrcDict\
                    [_toUtf8(self.mainWidget.playingMusic.filePath).data()] = path

    def downloadLRC(self):

        self.loadingLabel.setHidden(False)
        args = [self.mainWidget.playingMusic.title, self.mainWidget.playingMusic.artist]
        self.lrcDownloader.findLRC(args)

    def deleteLRC(self):
        self.mainWidget.musicToLrcDict.pop(_toUtf8(self.mainWidget.playingMusic.filePath).data())
        self.model.clear()
        self.lrcDict = {}
        self.lrcTimeList = []
        self.lrcWordList = []
        self.currentRow = -1

    def updateLRC(self, ms):
        if not len(self.lrcDict.keys()) or not self.model.rowCount():
            return
        time = ms/1000
        for t in self.lrcTimeList:
            if time == t:
                if self.currentRow != -1:
                    self.model.item(self.currentRow, 0).setForeground(QBrush(QColor(0, 0, 0)))
                self.currentRow = self.lrcTimeList.index(t)
                self.model.item(self.currentRow, 0).setForeground(QBrush(QColor(255, 0, 0)))
                self.scrollTo(self.model.index(self.currentRow, 0), QAbstractItemView.PositionAtCenter)
            if time < t:
                if self.lrcTimeList.index(t) != 0:
                    if self.currentRow != -1:
                        self.model.item(self.currentRow, 0).setForeground(QBrush(QColor(0, 0, 0)))
                    self.currentRow = self.lrcTimeList.index(t) - 1
                    self.model.item(self.currentRow, 0).setForeground(QBrush(QColor(255, 0, 0)))
                    # self.scrollTo(self.model.index(self.currentRow, 0), QAbstractItemView.PositionAtCenter)
                break

    def updateMusic(self):
        self.loadingLabel.setHidden(True)
        self.lrcDownloader.stop()
        self.model.clear()
        self.lrcDict = {}
        self.lrcTimeList = []
        self.lrcWordList = []
        self.currentRow = -1
        if self.mainWidget.playingMusic and \
                self.mainWidget.musicToLrcDict.has_key(_toUtf8(self.mainWidget.playingMusic.filePath).data()):
            lrcPath = _fromUtf8(self.mainWidget.musicToLrcDict[_toUtf8(self.mainWidget.playingMusic.filePath).data()])
            self.openLRC(lrcPath)

    def contextMenuEvent(self, event):
        self.downloadAction.setEnabled(self.mainWidget.playingIndex != -1)
        # self.downloadAction.setEnabled(False)
        self.deleteAction.setEnabled(self.mainWidget.playingMusic is not None and
                                     self.mainWidget.musicToLrcDict.has_key(
                                         _toUtf8(self.mainWidget.playingMusic.filePath).data()))
        self.contextMenu.exec_(event.globalPos())

    def dragEnterEvent(self, event):
        if event.mimeData().urls()[0].path().toLower().contains('.lrc'):
            event.accept()
        else:
            super(QListView, self).dragMoveEvent(event)

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
                # 截取歌词
                lyric = line
                for tplus in time_stamps:
                    lyric = lyric.replace(tplus, '')
                # 解析时间
                for tplus in time_stamps:
                    t = remove(tplus)
                    tag_flag = t.split(':')[0]
                    # 跳过: [ar: 逃跑计划]
                    if not tag_flag.isdigit():
                        continue
                    # 时间累加
                    time_lrc = int(tag_flag) * 60
                    time_lrc += int(t.split(':')[1].split('.')[0])
                    lrc_dict[time_lrc] = lyric
        return lrc_dict