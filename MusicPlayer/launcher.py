# -*- encoding:utf-8 -*-

from PyQt4 import QtGui

from src import music_player_widget
import music_system_tray_icon
import sys, os

if __name__ == "__main__":

    path = os.path.join(os.getcwd(), "src")
    path = os.path.join(os.getcwd(), "lib")
    sys.path.append(path)

    app = QtGui.QApplication(sys.argv)
    window = music_player_widget.MainWindow()

    icon = QtGui.QIcon('res/icon.png')

    window.setWindowIcon(icon)
    window.setWindowTitle('CCPlayer')
    window.show()

    taskIcon = music_system_tray_icon.MusicSystemTray(window)
    window.mediaObject.stateChanged.connect(taskIcon.updateMenu)
    taskIcon.activated.connect(window.trayIconActived)
    taskIcon.setIcon(icon)
    taskIcon.show()

    sys.exit(app.exec_())