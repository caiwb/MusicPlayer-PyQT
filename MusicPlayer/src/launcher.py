# -*- encoding:utf-8 -*-

from PyQt4 import QtGui
import music_player_main, music_system_tray


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    window = music_player_main.MainWindow()

    icon = QtGui.QIcon('../res/icon.png')

    window.setWindowIcon(icon)
    window.setWindowTitle('SxPlayer')
    window.show()

    taskIcon = music_system_tray.MusicSystemTray(window)
    window.mediaObject.stateChanged.connect(taskIcon.updateMenu)
    taskIcon.setIcon(icon)
    taskIcon.show()

    sys.exit(app.exec_())