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


class MusicTableView(QTableView):
    def __init__(self, type, parent=None):
        QTableView.__init__(self, None)

        self.setStyleSheet(
            '''
            MusicTableView
            {background-color: rgba(230, 230, 240, 0);
            selection-background-color: rgba(100, 100, 255, 55)}
            '''
        )

        self._playingIndex = -1
        self._parent = parent
        self.type = type
        self.model = QStandardItemModel()
        self._musicList = parent.musicList
        self._favList = parent.favList
        self.tipRow = -1
        self.list = self._musicList if self.type == 'all' else self._favList

        self.model.setColumnCount(3)

        self.setFixedWidth(300)
        self.setShowGrid(False)
        self.setWordWrap(False)
        self.setMouseTracking(True)

        self.verticalHeader().setResizeMode(QHeaderView.ResizeToContents)
        self.verticalHeader().setClickable(False)

        self.horizontalHeader().setResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setClickable(False)
        self.horizontalHeader().hide()

        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.setFocusPolicy(Qt.NoFocus)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.setModel(self.model)

        self.contextMenu = QMenu(self)
        self.playAction = QAction(u'播放', self)
        self.deleteAction = QAction(u'移除', self)
        self.favAction = QAction(u'收藏', self)
        self.openFolderAction = QAction(u'打开文件', self)

        # signals
        self.connect(self.playAction, SIGNAL('triggered()'), self.playSelections)
        self.connect(self.deleteAction, SIGNAL('triggered()'), self.deleteSelections)
        self.connect(self.favAction, SIGNAL('triggered()'), self.collectSelections)
        self.connect(self.openFolderAction, SIGNAL('triggered()'), self.addMusics)

        if self.type == 'all':
            self.setAcceptDrops(True)
            # menu
            self.contextMenu.addAction(self.playAction)
            self.contextMenu.addSeparator()
            self.contextMenu.addAction(self.deleteAction)
            self.contextMenu.addSeparator()
            self.contextMenu.addAction(self.favAction)
            self.contextMenu.addSeparator()
            self.contextMenu.addAction(self.openFolderAction)

        elif self.type == 'fav':
            # menu
            self.contextMenu.addAction(self.playAction)
            self.contextMenu.addSeparator()
            self.contextMenu.addAction(self.deleteAction)

    def playSelections(self):
        selectedRows = self.selectionModel().selectedRows()
        if len(selectedRows):
            index = selectedRows[0]
            i = self.model.itemFromIndex(index).row()
            self.playMusic(i)

    def deleteSelections(self):
        selectedRows = self.selectionModel().selectedRows()
        musicDelList = []
        if self.type == 'all':
            for index in selectedRows:
                i = self.model.itemFromIndex(index).row()
                if self._parent.playingIndex == i:
                    self._parent.stop()
                musicDelList.append(self._musicList[i])
            for music in musicDelList:
                self._musicList.remove(music)
        elif self.type == 'fav':
            for index in selectedRows:
                i = self.model.itemFromIndex(index).row()
                if self._parent.playingIndex == i:
                    self._parent.stop()
                musicDelList.append(self._favList[i])
            for music in musicDelList:
                self._favList.remove(music)
        self.update()

    def collectSelections(self):
        selectedRows = self.selectionModel().selectedRows()
        for index in selectedRows:
            i = self.model.itemFromIndex(index).row()
            if all(music.absolutePath() != self._musicList[i].absolutePath() for music in self._favList):
                self._favList.append(self._musicList[i])
        self.update()

    def addMusics(self):
        self.emit(SIGNAL("addMusics()"))

    def update(self):
        self.emit(SIGNAL("update()"))

    def playMusic(self, row):
        self.emit(SIGNAL("playMusic(int)"), row)

    def contextMenuEvent(self, event):
        pos = event.pos()
        index = self.indexAt(pos)

        self.playAction.setEnabled(self.model.itemFromIndex(index) is not None)
        self.deleteAction.setEnabled(self.model.itemFromIndex(index) is not None)
        self.favAction.setEnabled(self.model.itemFromIndex(index) is not None)

        if self.type == 'all' and self.model.itemFromIndex(index):
            if self._parent.musicList[self.model.itemFromIndex(index).row()] in self._parent.favList:
                self.favAction.setText(u"取消收藏")
            else:
                self.favAction.setText(u"收藏")

        self.contextMenu.exec_(event.globalPos())

    def mouseDoubleClickEvent(self, event):
        QTableView.mouseDoubleClickEvent(self, event)
        if event.button() == Qt.LeftButton:
            pos = event.pos()
            index = self.indexAt(pos)
            if self.model.itemFromIndex(index):
                i = self.model.itemFromIndex(index).row()
                self.playMusic(i)

    def dragEnterEvent(self, event):
        for url in event.mimeData().urls():
            if url.path().toLower().contains('.mp3') or url.path().toLower().contains('.wma'):
                event.accept()
                break
            else:
                super(QTableView, self).dragMoveEvent(event)

    def dragMoveEvent(self, event):
        for url in event.mimeData().urls():
            if url.path().toLower().contains('.mp3') or url.path().toLower().contains('.wma'):
                event.accept()
                break
            else:
                super(QTableView, self).dragMoveEvent(event)

    def dropEvent(self, event):
        paths = []
        for url in event.mimeData().urls():
            if url.path().toLower().contains('.mp3') or url.path().toLower().contains('.wma'):
                s = url.path().remove(0, 1)
                paths.append(s)
        self._parent.addMusics(paths)

    def updatePlayingItem(self):
        if self._playingIndex != self._parent.playingIndex:
            if self._playingIndex != -1 and self.model.rowCount() > self._playingIndex:
                self.model.item(self._playingIndex, 0).setForeground(QBrush(QColor(0, 0, 0)))
                self.model.item(self._playingIndex, 1).setForeground(QBrush(QColor(0, 0, 0)))
                self.model.item(self._playingIndex, 2).setForeground(QBrush(QColor(0, 0, 0)))
            self._playingIndex = self._parent.playingIndex
            if self._playingIndex != -1 and self.model.rowCount() > self._playingIndex:
                self.model.item(self._playingIndex, 0).setForeground(QBrush(QColor(255, 100, 100)))
                self.model.item(self._playingIndex, 1).setForeground(QBrush(QColor(255, 100, 100)))
                self.model.item(self._playingIndex, 2).setForeground(QBrush(QColor(255, 100, 100)))
