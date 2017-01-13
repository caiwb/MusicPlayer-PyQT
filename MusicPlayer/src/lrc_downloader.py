#-*- encoding: UTF-8 -*-
from PyQt4.QtCore import *
import urllib2, md5, json, os, json_parser

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


class LRCDownloader(QObject):
    def __init__(self, parent=None):
        QObject.__init__(self)
        self.shower = parent
        self.thread = None

    def findLRC(self, args=[]):
        if self.thread and self.thread.isRunning():
            self.thread.exit()
        self.thread = LRCDownloaderThread(args)
        self.connect(self.thread, SIGNAL("complete()"), self.downloadComplete)
        self.thread.start()

    def stop(self):
        if self.thread and self.thread.isRunning():
            self.thread.exit()

    def downloadComplete(self):
        print 'complete'
        self.shower.openLRC(self.thread.lrcPath)

class LRCDownloaderThread(QThread):
    def __init__(self, args):
        QThread.__init__(self)
        self.args = args #0-music 1-artist
        url = QString('http://geci.me/api/lyric')
        for arg in args:
            if isinstance(arg, QString):
                url = url.append(QString('/'))
                url = url.append(arg)
        self.url = unicode(url).encode('utf-8')
        self.lrcUrl = ''
        self.lrcPath = ''
        print self.url

    def run(self):
        self.getDownloadUrl()

    def getDownloadUrl(self):
            response = urllib2.urlopen(self.url)
            if response:
                jsonStr = response.read()
                jsonParser = json_parser.JsonParser()
                jsonParser.load(jsonStr)
                if jsonParser.data.has_key('result') and len(jsonParser.data['result']) \
                        and jsonParser.data['result'][0]['lrc']:
                    self.lrcUrl = jsonParser.data['result'][0]['lrc']
                    self.downloadLRCFile()
                else:
                    self.emit(SIGNAL("complete()"))
            else:
                self.emit(SIGNAL("complete()"))

    def downloadLRCFile(self):
        if self.lrcUrl:
            if isinstance(self.lrcUrl, unicode):
                self.lrcUrl = self.lrcUrl.encode('utf-8')
            f = urllib2.urlopen(self.lrcUrl)
            path = '../lrc/'
            if not os.path.exists(path):
                os.mkdir(path)
            path = path + unicode(self.args[0]) + '_' + unicode(self.args[1]) + '.lrc'
            data = f.read()
            with open(path, "wb+") as code:
                code.write(data)
            code.close()
            self.lrcPath = path
            self.emit(SIGNAL("complete()"))