from PySide2 import QtWidgets, QtGui, QtCore

class KKTMainWindow(QtWidgets.QMainWindow):
    '''
    KKT QMainWidow, there's some signals and rewrite closeEvent, keyPressEvent and keyReleaseEvent.
    '''
    close_Signal = QtCore.Signal(bool)
    start_Signal = QtCore.Signal(bool)
    pause_Signal = QtCore.Signal(bool)
    trigger_Signal = QtCore.Signal(bool)
    press_num_Signal = QtCore.Signal(object)
    press_Esc_Signal = QtCore.Signal(bool)
    delete_Signal = QtCore.Signal()
    setup_Signal = QtCore.Signal()

    def __init__(self, title='test mode', app=None, enable_menu_bar=True):
        super(KKTMainWindow, self).__init__()
        self.resize(1200, 800)
        self.app = app
        self.setWindowTitle(title)
        self.loop = True
        self.key_num_list = [QtCore.Qt.Key_0, QtCore.Qt.Key_1, QtCore.Qt.Key_2,
                             QtCore.Qt.Key_3, QtCore.Qt.Key_4, QtCore.Qt.Key_5,
                             QtCore.Qt.Key_6, QtCore.Qt.Key_7, QtCore.Qt.Key_8,
                             QtCore.Qt.Key_9]
        self.key_event = False
        self.lb_FPS = QtWidgets.QLabel('fps : ')
        self.lb_FPS.setFixedWidth(100)
        self.enable_menu_bar = enable_menu_bar
        # self.setup()
        # self._init_MenuBar()
        # self._init_StatusBar()
        pass

    def setup(self):
        self._init_MenuBar()
        self._init_StatusBar()
        pass

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        reply = QtWidgets.QMessageBox.question(None, 'Quit', 'Are you sure to quit??', QtWidgets.QMessageBox.Yes,
                                               QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            self.loop = False
            self.close_Signal.emit(True)
            self.delete_Signal.emit()
            event.accept()
            print('Quit Mode Window')
        else:
            event.ignore()

    def keyPressEvent(self, a0: QtGui.QKeyEvent) -> None:
        if not self.key_event:
            return
        # print('enter press')

        key = a0.key()
        keytext = a0.text()
        self.key = key

        if key in self.key_num_list:
            self.press_num_Signal.emit(key)
            # print(keytext)

        if key == QtCore.Qt.Key_Escape:
            self.press_Esc_Signal.emit(True)
            # print(keytext)

    def keyReleaseEvent(self, a0: QtGui.QKeyEvent) -> None:
        if not self.key_event:
            return
        # print('enter release')
        key = a0.key()
        if not hasattr(self, 'key'):
            print('no key')
            return

        if self.key != key:
            return

        if a0.isAutoRepeat():
            # print('release return')
            return

        keytext = a0.text()
        if key in self.key_num_list:
            self.press_num_Signal.emit(False)
            # print(keytext)

    def enableKeyPressEvent(self, enable=True):
        self.key_event = enable

    def pause(self):
        self.loop = False
        self.pause_Signal.emit(True)

    def start(self):
        self.start_Signal.emit(True)

    def _init_MenuBar(self):
        if not self.enable_menu_bar:
            return
        self.action_Connect = QtWidgets.QAction()
        self.action_Connect.setObjectName(u"action_Connect")
        self.actionDisconnect = QtWidgets.QAction()
        self.actionDisconnect.setObjectName(u"actionDisconnect")

        self.menuBar = QtWidgets.QMenuBar()
        self.menuBar.setObjectName(u"menuBar")
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 941, 21))
        self.menu_File = QtWidgets.QMenu(self.menuBar)
        self.menu_File.setObjectName(u"menu_File")
        self.setMenuBar(self.menuBar)
        self.menuBar.addAction(self.menu_File.menuAction())
        self.menu_File.addAction(self.action_Connect)
        self.menu_File.addAction(self.actionDisconnect)

        self.action_Connect.setText(QtCore.QCoreApplication.translate("MainWindow", u"&Connect", None))
        # if QT_CONFIG(tooltip)
        self.action_Connect.setToolTip(QtCore.QCoreApplication.translate("MainWindow", u"Connect to device", None))
        # endif // QT_CONFIG(tooltip)
        self.actionDisconnect.setText(QtCore.QCoreApplication.translate("MainWindow", u"Disconnect", None))
        self.menu_File.setTitle(QtCore.QCoreApplication.translate("MainWindow", u"&File", None))

    def _init_StatusBar(self):
        self.statusBar = QtWidgets.QStatusBar(self)
        self.statusBar.setObjectName(u"statusBar")
        self.setStatusBar(self.statusBar)

class ModeWindow(KKTMainWindow):
    '''
    Set QSplitter in the QMainWindow central and split to two area "canvas" and "scroll sublayout".
    '''
    def __init__(self, title='test mode', app=None, enable_menu_bar=False):
        super(ModeWindow, self).__init__(title, app, enable_menu_bar)
        # self.setup()
        pass

    def setup(self):
        super(ModeWindow, self).setup()
        self._init_splitter()
        self._init_sublayouts()
        self._init_panel_scroll_area()
        self.main_widget.addWidget(self.panel_scroll_area)
        self._init_canvas()
        self.main_widget.addWidget(self.canvas_widget)
        self.setCentralWidget(self.main_widget)
        self.statusBar.addPermanentWidget(QtWidgets.QLabel())
        self.statusBar.addPermanentWidget(self.lb_FPS)

        pass

    def _init_canvas(self):
        self.canvas_widget = QtWidgets.QFrame()
        self.canvas_widget.setContentsMargins(5,5,5,5)
        self.canvas_layout = QtWidgets.QVBoxLayout()
        self.canvas_layout.setAlignment(QtCore.Qt.AlignCenter)
        self.canvas_widget.setLayout(self.canvas_layout)

    def _init_splitter(self):
        self.main_widget = QtWidgets.QSplitter()
        self.main_widget.setStretchFactor(0, 4)
        self.main_widget.setStretchFactor(1, 1)
        self.main_widget.setStyleSheet("QSplitter::handle{background: lightgrey}")
        self.main_widget.setFrameStyle(QtWidgets.QFrame.Panel | QtWidgets.QFrame.Sunken)

    def _init_sublayouts(self):
        self.main_sublayout = QtWidgets.QGridLayout()
        self.main_sublayout.setContentsMargins(0, 3, 0, 3)
        self.main_sublayout.setSpacing(0)
        self.main_sublayout.setRowStretch(9, 1)


    def _init_panel_scroll_area(self):
        self.panel_scroll_area = QtWidgets.QScrollArea()
        self.panel_scroll_area.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.panel_scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.panel_scroll_area.setMaximumWidth(400)
        self.panel_scroll_area.setMinimumWidth(350)
        self.panel_scroll_area.setWidgetResizable(True)
        self.panel_scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.panel_scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.panel_scroll_area.horizontalScrollBar().setEnabled(False)

        self.panel_scroll_area_widget = QtWidgets.QStackedWidget(self.panel_scroll_area)
        self.panel_scroll_area.setWidget(self.panel_scroll_area_widget)
        self.main_sublayout_widget = QtWidgets.QWidget(self.panel_scroll_area_widget)
        self.main_sublayout_widget.setLayout(self.main_sublayout)
        self.panel_scroll_area_widget.addWidget(self.main_sublayout_widget)
        self.panel_scroll_area_widget.setCurrentWidget(self.main_sublayout_widget)

    def addWidgetToCanvas(self):
        pass

    def enableSublayoutWidget(self, enable):
        pass

    def addSublayoutWidget(self):
        pass






if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication([])
    TestMode = ModeWindow(title='KKT Test Window', app=app)
    TestMode.show()
    sys.exit(app.exec_())
