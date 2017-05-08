#-*- encoding: UTF-8 -*-

import logging
from PyQt4.QtCore import *
import urllib2, json, os

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

class LRCDownloaderThread(QThread):
    def __init__(self, args):
        QThread.__init__(self)
        self.args = args # 0-music 1-artist
        url = QString('http://geci.me/api/lyric')
        for arg in args:
            if isinstance(arg, QString):
                url = url.append(QString('/'))
                url = url.append(arg)
        self.url = unicode(url).encode('utf-8')
        self.lrcUrl = ''
        self.lrcPath = QString()

    def run(self):
        self.getDownloadUrl()

    def getDownloadUrl(self):
        try:
            response = urllib2.urlopen(self.url)
            if response:
                jsonStr = response.read()
                data = json.loads(jsonStr)
                if data.has_key('result') and len(data['result']) \
                        and data['result'][0]['lrc']:
                    self.lrcUrl = data['result'][0]['lrc']
                    self.downloadLRCFile()
                else:
                    self.emit(SIGNAL("complete(bool)"), False)
            else:
                self.emit(SIGNAL("complete(bool)"), False)
        except:
            self.emit(SIGNAL("complete(bool)"), False)

    def downloadLRCFile(self):
        try:
            if self.lrcUrl:
                if isinstance(self.lrcUrl, unicode):
                    self.lrcUrl = self.lrcUrl.encode('utf-8')
                f = urllib2.urlopen(self.lrcUrl)
                path = 'lrc/'
                if not os.path.exists(path):
                    os.mkdir(path)
                path = path + unicode(self.args[0]) + '_' + unicode(self.args[1]) + '.lrc'
                data = f.read()
                if data:
                    with open(path, "wb+") as code:
                        code.write(data)
                    code.close()
                    self.lrcPath = QString(path)
                    self.emit(SIGNAL("complete(bool)"), True)
                else:
                    self.emit(SIGNAL("complete(bool)"), False)
        except:
            self.emit(SIGNAL("complete(bool)"), False)
