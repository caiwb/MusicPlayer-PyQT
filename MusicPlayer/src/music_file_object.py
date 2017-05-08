# -*- encoding: UTF-8 -*-

import enum, chardet
from lib.mutagen.mp3 import MP3
from lib.mutagen.asf import ASF
from lrc_downloader import *
from PyQt4.phonon import Phonon

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


class LRCState(enum.Enum):
    waitForLrc = 0
    downloading = 1
    downloadFailed = 2
    lrcShowing = 3


class MusicFile(QObject):
    def __init__(self, filePath):
        QObject.__init__(self)
        self.filePath = filePath  # QString
        self.file = QFileInfo(filePath)
        self.title = QString()
        self.artist = QString()
        self.time = QTime()
        self.timeString = QString()
        self.bitrate = QString()
        self.src = None
        self.musicInfo(self.file)
        self.lrcPath = QString()
        self.lrcState = LRCState.waitForLrc
        self.lrcDownloadThread = LRCDownloaderThread([self.title, self.artist])
        self.connect(self.lrcDownloadThread, SIGNAL('complete(bool)'), self.downloadLRCComplete)

    def downloadLRC(self):
        if self.lrcDownloadThread.isRunning():
            self.lrcDownloadThread.terminate()
            self.lrcDownloadThread.start()
        else:
            self.lrcDownloadThread.start()

    def stopDownloadLRC(self):
        if self.lrcDownloadThread.isRunning():
            self.lrcDownloadThread.terminate()

    def downloadLRCComplete(self, suc):
        self.lrcState = LRCState.lrcShowing if suc else LRCState.downloadFailed
        self.emit(SIGNAL('downloadLRCComplete(QString, QString)'), self.filePath, self.lrcDownloadThread.lrcPath)

    def absoluteDirPath(self):
        return self.file.absoluteDir().absolutePath()

    def absolutePath(self):
        return self.file.absoluteFilePath()

    def suffix(self):
        return self.file.suffix().toLower()

    def getFileName(self):
        return self.file.fileName()

    def getBaseName(self):
        return self.file.baseName()

    def getType(self):
        return self.getMediaSource().type()

    def getMediaSource(self):
        if self.src:
            return self.src
        else:
            self.src = Phonon.MediaSource(self.file.filePath())
            return self.src

    def getStringCode(self, s):
        global defaultcode
        try:
            dic = chardet.detect(s)
            code = chardet.detect(s)['encoding']
            if QString(s).toLower().contains('\\u'):
                s = s.decode('raw_unicode_escape')
            elif not code:
                s = s.decode(defaultcode)
            elif QString(code).toLower().contains('ascii'):
                s = s.decode(code)
            else:
                s = _toUtf8(QString.fromLocal8Bit(QString(s)))
            return s
        except:
            s = s.decode('raw_unicode_escape')
            return s

    def musicInfo(self, file):
        if self.getType() == 1:
            self.title = file.fileName()
            return
        suffix = self.suffix()
        if suffix == 'mp3':
            audio = MP3(unicode(file.filePath().toUtf8().data(), 'utf-8'))
            if audio.has_key('TIT2'):
                s = audio.tags.get('TIT2').text[0].encode('raw_unicode_escape')
                self.title = QString().fromUtf8(self.getStringCode(s))
            if audio.has_key('TPE1'):
                s = audio.tags.get('TPE1').text[0].encode('raw_unicode_escape')
                self.artist = QString().fromUtf8(self.getStringCode(s))
            if audio.info.length:
                self.time = QTime().addSecs(audio.info.length)
                self.timeString = self.time.toString("mm:ss") \
                    if not self.time.hour() else self.time.toString("hh:mm:ss")
            if audio.info.bitrate:
                self.bitrate = QString(str(audio.info.bitrate / 1000) + 'kbps')

        elif suffix == 'wma':
            audio = ASF(unicode(file.filePath().toUtf8().data(), 'utf-8'))
            if audio.has_key('Title'):
                s = audio.tags.get('Title')[0].value.encode('raw_unicode_escape')
                self.title = QString().fromUtf8(self.getStringCode(s))
            if audio.has_key('Author'):
                s = audio.tags.get('Author')[0].value.encode('raw_unicode_escape')
                self.artist = QString().fromUtf8(self.getStringCode(s))
            if audio.info.length:
                self.time = QTime().addSecs(audio.info.length)
                self.timeString = self.time.toString("mm:ss") \
                    if not self.time.hour() else self.time.toString("hh:mm:ss")
            if audio.info.bitrate:
                self.bitrate = QString(str(audio.info.bitrate / 1000) + 'kbps')