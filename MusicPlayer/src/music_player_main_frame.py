# -*- encoding:utf-8 -*-

from PyQt4.QtGui import *

class MusicPlayerMainFrame(QFrame):
    def __init__(self, parent=None):
        QFrame.__init__(self, parent)
        self.parent = parent
        self.setStyleSheet(
        '''
        MusicPlayerMainFrame{
        border-image: url(res/background.jpg);
        background-repeat: no-repeat;
        }
        ''')
        self.setGeometry(0, 67, 800, 533)
