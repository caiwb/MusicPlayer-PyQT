# -*- encoding:utf-8 -*-

import ConfigParser
import logging
import os
import random

from PyQt4.phonon import Phonon

import bottom_tool_frame
import music_info_frame
import music_player_main_frame
import top_tool_frame
from music_file_object import *
from music_tableview import *

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


class MainWindow(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        # player
        self.mediaObject = Phonon.MediaObject(self)
        self.audioOutput = Phonon.AudioOutput(Phonon.VideoCategory, self)
        Phonon.createPath(self.mediaObject, self.audioOutput)
        self.playingIndex = -1
        self.playingList = None
        self.playingMusic = None
        self.playingOrder = 0
        self.tabIndex = 0

        self.musicList = []
        self.favList = []
        self.lastOpenedPath = QString('E:/')
        self.lastLRCOpenedPath = QString('E:/')
        self.musicToLrcDict = {}
        self.isImporting = False

        self.resize(800, 600)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowMinMaxButtonsHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.tableView = MusicTableView('all', self)
        self.tableViewFav = MusicTableView('fav', self)

        # 需tableView已初始化，musicInfoFrame未初始化
        self.importConfig()

        self.mainFrame = music_player_main_frame.MusicPlayerMainFrame(self)
        self.topToolFrame = top_tool_frame.TopToolFrame(self, self.mainFrame)
        self.bottomToolFrame = bottom_tool_frame.BottomToolFrame(self, self.mainFrame)
        self.musicInfoFrame = music_info_frame.MusicInfoFrame(self, self.mainFrame)
        rect = self.mainFrame.rect()
        self.tabWidget = QTabWidget(self.mainFrame)
        self.tabWidget.setGeometry(rect.right() - 300, 60, 301, rect.bottom() - 118)
        self.tabWidget.setStyleSheet(
            '''QTabWidget:pane {border-top:0px solid #e8f3f9; background:transparent;}
               QTabBar:tab {width:150px; height:25px}''')
        self.tabWidget.addTab(self.tableView, u'播放列表')
        self.tabWidget.addTab(self.tableViewFav, u'我的收藏')
        self.tabWidget.setCurrentIndex(0)

        self.connect(self.tableView, SIGNAL("addMusics()"), self.addMusics)
        self.connect(self.tableViewFav, SIGNAL("addMusics()"), self.addMusics)
        self.connect(self.tableView, SIGNAL("update()"), self.updateTableView)
        self.connect(self.tableViewFav, SIGNAL("update()"), self.updateTableView)
        self.connect(self.tableView, SIGNAL("playMusic(int)"), self.playMusicAtIndex)
        self.connect(self.tableViewFav, SIGNAL("playMusic(int)"), self.playMusicAtIndex)
        self.connect(self.bottomToolFrame, SIGNAL("lastMusic()"), self.lastMusic)
        self.connect(self.bottomToolFrame, SIGNAL("nextMusic()"), self.nextMusic)
        self.connect(self.bottomToolFrame, SIGNAL("playControl()"), self.playControl)
        self.connect(self.bottomToolFrame, SIGNAL("stop()"), self.stop)
        self.connect(self.bottomToolFrame, SIGNAL("changeOrder(int)"), self.changeOrder)

        self.mediaObject.stateChanged.connect(self.bottomToolFrame.updateButtons)
        self.mediaObject.stateChanged.connect(self.tableView.updatePlayingItem)
        self.mediaObject.stateChanged.connect(self.tableView.updatePlayingItem)
        self.mediaObject.stateChanged.connect(self.musicInfoFrame.updateInfo)
        self.mediaObject.finished.connect(self.finished)
        self.mediaObject.tick.connect(self.bottomToolFrame.updateTimeLabel)
        self.mediaObject.tick.connect(self.musicInfoFrame.lrcShower.updateLRC)

        self.tabWidget.currentChanged.connect(self.tabChanged)

    def closeEvent(self, event):
        self.exportConfig()
        event.accept()

    def addMusics(self, filePaths=[], favFilePaths=[]):
        if not len(filePaths) and not self.isImporting:
            filePaths = QFileDialog.getOpenFileNames(self, u'打开', self.lastOpenedPath, u'音频文件 (*.mp3 *.wma)')
        elif self.isImporting:
            self.isImporting = False
        if len(filePaths):
            filePaths.sort()
            for filePath in filePaths:
                if all(filePath != music.filePath for music in self.musicList) and os.path.exists(unicode(filePath)):
                    musicFile = MusicFile(filePath)
                    self.lastOpenedPath = musicFile.absoluteDirPath()
                    self.musicList.append(musicFile)
                    itemList = [QStandardItem(musicFile.title),
                                QStandardItem(musicFile.artist),
                                QStandardItem(musicFile.timeString)]
                    itemList[2].setTextAlignment(Qt.AlignCenter)
                    self.tableView.model.appendRow(itemList)

                    if filePath in favFilePaths:
                        self.favList.append(musicFile)
                        itemListFav = [QStandardItem(musicFile.title),
                                       QStandardItem(musicFile.artist),
                                       QStandardItem(musicFile.timeString)]
                        itemList[2].setTextAlignment(Qt.AlignCenter)
                        self.tableViewFav.model.appendRow(itemListFav)

    def updateTableView(self):
        self.tableView.model.clear()
        self.tableViewFav.model.clear()

        for musicFile in self.musicList:
            itemList = [QStandardItem(musicFile.title),
                        QStandardItem(musicFile.artist),
                        QStandardItem(musicFile.timeString)]
            itemList[2].setTextAlignment(Qt.AlignCenter)
            self.tableView.model.appendRow(itemList)
        for musicFile in self.favList:
            itemList = [QStandardItem(musicFile.title),
                        QStandardItem(musicFile.artist),
                        QStandardItem(musicFile.timeString)]
            itemList[2].setTextAlignment(Qt.AlignCenter)
            self.tableViewFav.model.appendRow(itemList)

    def exportConfig(self):
        config = ConfigParser.ConfigParser()
        config.add_section('Player')
        config.set('Player', 'lastOpenedPath', _toUtf8(self.lastOpenedPath).data())
        musicPathList = []
        favPathList = []
        for music in self.musicList:
            musicPathList.append(_toUtf8(music.filePath).data())
        for music in self.favList:
            favPathList.append(_toUtf8(music.filePath).data())
        config.set('Player', 'musicList', musicPathList)
        config.set('Player', 'favList', favPathList)
        config.set('Player', 'lastLRCOpenedPath', _toUtf8(self.musicInfoFrame.lrcShower.lastOpenedPath).data())
        config.set('Player', 'musicToLRCDict', self.musicToLrcDict)
        try:
            configFile = open('src/setting.ini', 'w+')
            config.write(configFile)
        except Exception as e:
            raise ValueError(e)
        finally:
            configFile.close()

    def importConfig(self):
        self.isImporting = True
        config = ConfigParser.ConfigParser()
        try:
            config.read('src/setting.ini')
            if config:
                self.lastOpenedPath = _fromUtf8(config.get('Player', 'lastOpenedPath'))
                musicList = eval(config.get('Player', 'musicList'))
                qMusicList = [QString.fromUtf8(music) for music in musicList]
                favList = eval(config.get('Player', 'favList'))
                qFavList = [QString.fromUtf8(music) for music in favList]
                self.lastLRCOpenedPath = _fromUtf8(config.get('Player', 'lastLRCOpenedPath'))
                self.addMusics(qMusicList, qFavList)
                self.musicToLrcDict = eval(config.get('Player', 'musicToLRCDict'))
        except Exception as e:
            logging.debug(e.message)
            config.add_section('Player')
            config.set('Player', 'lastOpenedPath',
                       _toUtf8(self.lastOpenedPath).data())
            musicPathList = []
            favPathList = []
            for music in self.musicList:
                musicPathList.append(_toUtf8(music.filePath).data())
            for music in self.favList:
                favPathList.append(_toUtf8(music.filePath).data())
            config.set('Player', 'musicList', [])
            config.set('Player', 'favList', [])
            config.set('Player', 'lastLRCOpenedPath', '')
            config.set('Player', 'musicToLRCDict', {})
            self.isImporting = False
            try:
                configFile = open('src/setting.ini', 'w+')
                config.write(configFile)
            except Exception as e:
                logging.debug(e.message)
            finally:
                self.isImporting = False
                configFile.close()

    def playMusicAtIndex(self, i):
        self.playingList = self.musicList if self.tabWidget.currentIndex() == 0 else self.favList
        self.playingMusic = self.playingList[i]
        self.playingIndex = i

        self.playMusic(self.playingMusic)

    def playMusic(self, musicFile):
        if not isinstance(musicFile, MusicFile):
            return
        self.mediaObject.setCurrentSource(musicFile.getMediaSource())
        self.mediaObject.play()

    def playControl(self):
        if self.playingMusic:
            if self.mediaObject.state() == 2:
                self.mediaObject.pause()
            else:
                self.mediaObject.play()
        else:
            self.playingList = self.musicList if self.tabIndex == 0 else self.favList
            tableView = self.tableView if self.tabIndex == 0 else self.tableViewFav
            selectedRows = tableView.selectionModel().selectedRows()
            if len(selectedRows):
                self.playingIndex = tableView.model.itemFromIndex(selectedRows[0]).row()
            else:
                self.playingIndex = 0
            if len(self.playingList) > self.playingIndex:
                self.playingMusic = self.playingList[self.playingIndex]
                self.playMusic(self.playingMusic)

    def stop(self):
        if self.playingMusic:
            self.mediaObject.stop()
            self.playingList = self.musicList if self.tabIndex == 0 else self.favList
            self.playingIndex = -1
            self.playingMusic = None

    def lastMusic(self):
        if self.playingIndex - 1 >= 0:
            self.playingIndex -= 1
            self.playingMusic = self.playingList[self.playingIndex]
            self.playMusic(self.playingMusic)

    def nextMusic(self):
        if not self.playingList or not len(self.playingList) or self.playingIndex == -1:
            return
        if len(self.playingList) > self.playingIndex + 1:
            self.playingIndex += 1
            self.playingMusic = self.playingList[self.playingIndex]
            self.playMusic(self.playingMusic)
        else:
            self.stop()

    def changeOrder(self, order):
        self.playingOrder = order

    def finished(self):
        if not self.playingOrder:
            self.nextMusic()
        else:
            self.playingIndex = int(random.randint(0, len(self.playingList) - 1))
            self.playingMusic = self.playingList[self.playingIndex]
            self.playMusic(self.playingMusic)

    def tabChanged(self, i):
        self.tabIndex = i

    def trayIconActived(self, reason):
        self.activateWindow()
