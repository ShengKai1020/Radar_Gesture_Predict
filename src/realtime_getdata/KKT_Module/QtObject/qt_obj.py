# -*- coding: utf-8 -*-
"""
Created on July 17 2020

@author: hm
"""
import os.path
import pprint
import time

from KKT_Module.ksoc_global import kgl
from PySide2 import QtGui, QtCore, QtWidgets



class QCustomWidgetMsg1(QtWidgets.QMessageBox):
    def __init__ (self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.signal = None
    def setSignal(self, sig):
        self.signal = sig
    def keyPressEvent (self, eventQKeyEvent):
        key = eventQKeyEvent.key()
        if key == QtCore.Qt.Key_Y:
            if self.signal != None:
                self.signal('y')
            self.close()
        elif key == QtCore.Qt.Key_N:
            if self.signal != None:
                self.signal('n')
            self.close()

class QCustomWidgetMsg(QtWidgets.QMessageBox):
    def __init__ (self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.signal = None
        self.keyRes = None
        self.boxRes = QtWidgets.QMessageBox.No
    def setSignal(self, sig):
        self.signal = sig
    def run_exec(self):
        self.boxRes = self.exec_()
        if self.keyRes != None:
            return self.keyRes
        else:
            return self.boxRes
    def keyPressEvent (self, eventQKeyEvent):
        key = eventQKeyEvent.key()
        if key == QtCore.Qt.Key_Y:
            self.keyRes = QtWidgets.QMessageBox.Yes
            if self.signal != None:
                self.signal('y')
            self.close()
        elif key == QtCore.Qt.Key_N:
            self.keyRes = QtWidgets.QMessageBox.No
            if self.signal != None:
                self.signal('n')
            self.close()

class TCustomWidgetMsg(QtWidgets.QMessageBox):
    def __init__(self, text1='1',text2='auto save' , timeout=3, *args, **kwargs):
        super(TCustomWidgetMsg, self).__init__(*args, **kwargs)
        # self.setWindowTitle("message")

        self.signal = None
        self.keyRes = None
        self.boxRes = QtWidgets.QMessageBox.No
        self.time_to_wait = timeout
        self.text1 = text1
        self.text2 = text2
        self.setText(self.text1 + "\n({} in {} secondes.)".format(self.text2, timeout))

        self.timer = QtCore.QTimer(self)
        # self.timer.setInterval(1000)
        self.timer.timeout.connect(self.changeContent)
        self.timer.start(1000)

    def setSignal(self, sig):
        self.signal = sig

    def run_exec(self):
        self.boxRes = self.exec_()
        if self.keyRes != None:
            return self.keyRes
        else:
            return self.boxRes

    def keyPressEvent(self, eventQKeyEvent):
        key = eventQKeyEvent.key()
        if key == QtCore.Qt.Key_Y:
            self.keyRes = QtWidgets.QMessageBox.Yes
            if self.signal != None:
                self.signal('y')
            self.close()
        elif key == QtCore.Qt.Key_N:
            self.keyRes = QtWidgets.QMessageBox.No
            if self.signal != None:
                self.signal('n')
            self.close()

    def changeContent(self, ):
        self.setText(self.text1 + "\n({} in {} secondes.)".format(self.text2, self.time_to_wait - 1))
        self.time_to_wait -= 1
        if self.time_to_wait <= 0:
            self.button(QtWidgets.QMessageBox.Yes).click()

    def closeEvent(self, event):
        self.timer.stop()
        event.accept()

def CMessageBox(msg, str):
    QMsgBox = QCustomWidgetMsg(msg, 'Question', str, QtWidgets.QMessageBox.Yes)
    QMsgBox.addButton(QtWidgets.QMessageBox.No)
    QMsgBox.setDefaultButton(QtWidgets.QMessageBox.No)
    if msg == QtWidgets.QMessageBox.Warning:
        QMsgBox.setStyleSheet("QLabel{ color: red}")
    ret = QMsgBox.run_exec()
    if ret == QtWidgets.QMessageBox.Yes:
        return 'y'
    else:
        return 'n'

def OKMessageBox(msg, str):

    if msg == QtWidgets.QMessageBox.Warning:
        QMsgBox = QCustomWidgetMsg(msg, 'Waring', str, QtWidgets.QMessageBox.Yes)
        QMsgBox.setStyleSheet("QLabel{ color: red}")
    else:
        QMsgBox = QCustomWidgetMsg(msg, 'Question', str, QtWidgets.QMessageBox.Yes)
    QMsgBox.run_exec()

def TimeMessageBox(msg_box:QtWidgets.QMessageBox, question:str, to_do:str, timeout:int):
    QMsgBox = TCustomWidgetMsg(question, to_do, timeout, msg_box, 'Question', question, QtWidgets.QMessageBox.Yes)
    QMsgBox.addButton(QtWidgets.QMessageBox.No)
    if msg_box == QtWidgets.QMessageBox.Warning:
        QMsgBox.setStyleSheet("QLabel{ color: red}")
    ret = QMsgBox.run_exec()
    # if ret == QtWidgets.QMessageBox.Yes:
    #     return str.lower('y')
    # else:
    #     return str.lower('n')
    return ret



class SubWidgetQFrame(QtWidgets.QFrame):
    def __init__(self, border=True):
        super(SubWidgetQFrame, self).__init__()
        self.setObjectName("frame")
        if border:
            self.default_css = "#frame {border: 1px solid lightgrey; border-radius: 3px;}"
            self.setStyleSheet(self.default_css)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 6, 0, 6)

        self.grid_widget = QtWidgets.QWidget()
        self.layout.addWidget(self.grid_widget)

        self.grid = QtWidgets.QGridLayout(self.grid_widget)
        self.grid.setContentsMargins(6, 0, 6, 0)
        self.grid.setColumnStretch(0, 1)
        self.grid.setColumnStretch(1, 1)
        self.setup()

    def setup(self):
        pass

class SubWidgetQGroupBox(QtWidgets.QGroupBox):
    def __init__(self,title=''):
        super(SubWidgetQGroupBox, self).__init__()
        self.setObjectName("frame")
        self.setTitle(title)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 6, 0, 6)

        self.grid_widget = QtWidgets.QWidget()
        self.layout.addWidget(self.grid_widget)

        self.grid = QtWidgets.QGridLayout(self.grid_widget)
        self.grid.setContentsMargins(6, 0, 6, 0)
        self.grid.setColumnStretch(0, 1)
        self.grid.setColumnStretch(1, 1)
        self.setup()

    def setup(self):
        pass

class CollapsibleSection(QtWidgets.QFrame):
    def __init__(self, header_text, init_collapsed=False, is_top=False):
        super().__init__()
        self.setObjectName("CollapsibleSection")
        self.setStyleSheet("#CollapsibleSection{border: 1px solid lightgrey;}")

        self._layout = QtWidgets.QVBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        self.setLayout(self._layout)
        self._header_widget = QtWidgets.QWidget()
        self.body_widget = QtWidgets.QWidget()
        self._layout.addWidget(self._header_widget)
        self._layout.addWidget(self.body_widget)

        self.grid = QtWidgets.QGridLayout()
        self.body_widget.setLayout(self.grid)
        self.grid.setContentsMargins(9, 0, 9, 9)
        self.grid.setColumnStretch(0, 1)
        self.grid.setColumnStretch(1, 1)

        self._header_widget_layout = QtWidgets.QHBoxLayout()
        self._header_widget_layout.setContentsMargins(7, 7, 7, 7)
        self._header_widget.setLayout(self._header_widget_layout)

        self._button = QtWidgets.QToolButton()
        self._button.setText(header_text)
        self._button.setCheckable(True)
        self._button.setStyleSheet("QToolButton { border: none; }")
        self._button.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self._button.pressed.connect(self.button_event)
        self.button_event(override=init_collapsed)
        self._header_widget_layout.addWidget(self._button)
        self._header_widget_layout.addStretch()

    def button_event(self, override=None):
        if override is None:
            checked = not self._button.isChecked()
        else:
            checked = override
            self._button.setChecked(checked)

        if checked:  # collapsed
            self._button.setArrowType(QtCore.Qt.ArrowType.RightArrow)
            self.body_widget.hide()
        else:
            self._button.setArrowType(QtCore.Qt.ArrowType.DownArrow)
            self.body_widget.show()

class HTextLineWidget(SubWidgetQFrame):
    def __init__(self, label='label', default_text=None, border=True):
        self._label_text = label
        self._default_text= default_text
        super(HTextLineWidget, self).__init__(border)
    def setup(self):
        self._Label = QtWidgets.QLabel(self._label_text)
        self._LineEdit = QtWidgets.QLineEdit()
        if self._default_text is not None:
            self._LineEdit.setText(str(self._default_text))
        self.grid.addWidget(self._Label, 0 ,0 ,1, 1)
        self.grid.addWidget(self._LineEdit, 0, 1, 1, 2)

        # self._LineEdit.textEdited.connect(lambda :self._editLine())
    def _editLine(self):
        print('edit')

    def getLineText(self):
        return self._LineEdit.text()

class VTextLineWidget(SubWidgetQFrame):
    def __init__(self, label='label', default_text=None, border=True):
        self._label_text = label
        self._default_text= default_text
        super(VTextLineWidget, self).__init__(border)
    def setup(self):
        self._Label = QtWidgets.QLabel(self._label_text)
        self._LineEdit = QtWidgets.QLineEdit()
        if self._default_text is not None:
            self._LineEdit.setText(str(self._default_text))
        self.grid.addWidget(self._Label, 0 ,0 ,1, 1)
        self.grid.addWidget(self._LineEdit, 1, 0, 1, 2)

        # self._LineEdit.textEdited.connect(lambda :self._editLine())
    def _editLine(self):
        print('edit')

    def getLineText(self):
        return self._LineEdit.text()

class HComboBoxWidget(SubWidgetQFrame):
    changeIndex = QtCore.Signal()
    def __init__(self, label='label', box_list=[], border=True):
        self._label_text = label
        self._box_list = box_list
        super(HComboBoxWidget, self).__init__(border)

    def setup(self):
        self._Label = QtWidgets.QLabel(self._label_text)
        self._ComboBox = QtWidgets.QComboBox()
        self._ComboBox.addItems(self._box_list)
        self.grid.addWidget(self._Label, 0 ,0 ,1, 1)
        self.grid.addWidget(self._ComboBox, 0, 1, 1, 2)
        self._ComboBox.currentIndexChanged.connect(lambda : self._selectComboBox())
        self._selectComboBox()
    def _selectComboBox(self):
        # print(self._ComboBox.currentIndex())
        self.changeIndex.emit()

    def getCurrentComboBox(self):
        return self._box_list[self._ComboBox.currentIndex()]

    def setComboBox(self, text):
        assert text in self._box_list, 'Text not in combobox!'
        self._ComboBox.setCurrentIndex(self._box_list.index(text))

class VComboBoxWidget(SubWidgetQFrame):
    changeIndex = QtCore.Signal()
    def __init__(self, label='label', box_list=[], border=True):
        self._label_text = label
        self._box_list = box_list
        super(VComboBoxWidget, self).__init__(border)

    def setup(self):
        self._Label = QtWidgets.QLabel(self._label_text)
        self._ComboBox = QtWidgets.QComboBox()
        self._ComboBox.addItems(self._box_list)
        self.grid.addWidget(self._Label, 0 ,0 ,1, 1)
        self.grid.addWidget(self._ComboBox, 1, 0, 1, 1)
        self._ComboBox.currentIndexChanged.connect(lambda : self._selectComboBox())
        self._selectComboBox()

    def setComboBoxItems(self, box_list:list):
        self._box_list = box_list
        self._ComboBox.clear()
        self._ComboBox.addItems(box_list)

    def _selectComboBox(self):
        # print(self._ComboBox.currentIndex())
        self.changeIndex.emit()

    def getCurrentComboBox(self):
        return self._box_list[self._ComboBox.currentIndex()]

    def setComboBox(self, text):
        assert text in self._box_list, 'Text not in combobox!'
        self._ComboBox.setCurrentIndex(self._box_list.index(text))

class HSpinBoxWidget(SubWidgetQFrame):
    def __init__(self, label='label', range=[0,10], default_val=0, border=True):
        self._label_text = label
        self._default_val = default_val
        self._range = range
        super(HSpinBoxWidget, self).__init__(border)

    def setup(self):
        self._Label = QtWidgets.QLabel(self._label_text)
        self._SpinBox = QtWidgets.QSpinBox()
        self._SpinBox.setRange(self._range[0], self._range[1])
        self._SpinBox.setValue(self._default_val)
        self.grid.addWidget(self._Label, 0 ,0 ,1, 1)
        self.grid.addWidget(self._SpinBox, 0, 1, 1, 2)

    def getSpinBoxValue(self):
        return self._SpinBox.value()

class SelectFileWidget(SubWidgetQFrame):
    def __init__(self, label='label', button='Select file', border=True, default_dir = None):
        self._label_text = label
        self._button_text = button
        self._default_dir = default_dir
        super(SelectFileWidget, self).__init__(border)
    def setup(self):
        self._Label = QtWidgets.QLabel(self._label_text)
        self._pb = QtWidgets.QPushButton(self._button_text)
        self._pb.clicked.connect(lambda : self._pushButton())
        self._LineEdit = QtWidgets.QLineEdit()
        self._LineEdit.setReadOnly(True)
        self.grid.addWidget(self._Label, 0, 0, 1, 1)
        self.grid.addWidget(self._pb, 0, 1, 1, 1)
        self.grid.addWidget(self._LineEdit, 1, 0, 1, 2)
    def _pushButton(self):
        if self._default_dir is not None:
            file, type = QtWidgets.QFileDialog.getOpenFileName(None, dir = self._default_dir)
            self._LineEdit.setText(file)
            return
        file, type = QtWidgets.QFileDialog.getOpenFileName(None)
        self._LineEdit.setText(file)

    def getFilePath(self):
        return self._LineEdit.text()

    def setTextLine(self, string:str):
        self._LineEdit.setText(string)

class SelectFolderWidget(SubWidgetQFrame):
    def __init__(self, label='label', button='Select folder', border=True, default_dir=None):
        self._label_text = label
        self._button_text = button
        self._default_dir = default_dir
        super(SelectFolderWidget, self).__init__(border)
    def setup(self):
        self._Label = QtWidgets.QLabel(self._label_text)
        self._pb = QtWidgets.QPushButton(self._button_text)
        self._pb.clicked.connect(lambda : self._pushButton())
        self._LineEdit = QtWidgets.QLineEdit()
        self._LineEdit.setReadOnly(True)
        self.grid.addWidget(self._Label, 0, 0, 1, 1)
        self.grid.addWidget(self._pb, 0, 1, 1, 1)
        self.grid.addWidget(self._LineEdit, 1, 0, 1, 2)

    def _pushButton(self):
        if self._default_dir is not None:
            assert os.path.isdir(self._default_dir), "Directory not exist !"
            file= QtWidgets.QFileDialog.getExistingDirectory(None, dir=str(self._default_dir))
            self._LineEdit.setText(file)
            return
        file = QtWidgets.QFileDialog.getExistingDirectory(None)
        self._LineEdit.setText(file)

    def getFilePath(self):
        return self._LineEdit.text()

class InputThreshold(SubWidgetQFrame):
    ThresholdChanged = QtCore.Signal()
    def __init__(self, threshold=[0.2, 0.4], border=True):
        self._threshold = threshold
        self.current_threshold = threshold
        super(InputThreshold, self).__init__(border)

    def setup(self):
        self._lb_lower = QtWidgets.QLabel('Lower Threshold:')
        self._lb_upper = QtWidgets.QLabel('Upper Threshold:')
        self._sb_lower = QtWidgets.QDoubleSpinBox(singleStep=0.1, maximum=1, minimum=0)
        self._sb_upper = QtWidgets.QDoubleSpinBox(singleStep=0.1, maximum=1, minimum=0)
        self.initPlots()
        self._sb_upper.valueChanged.connect(lambda: self._changeSpinValue())
        self._sb_lower.valueChanged.connect(lambda: self._changeSpinValue())

        self.grid.addWidget(self._lb_lower,0,0,1,1)
        self.grid.addWidget(self._sb_lower,1,0,1,1)
        self.grid.addWidget(self._lb_upper,0,1,1,1)
        self.grid.addWidget(self._sb_upper,1,1,1,1)

    def initPlots(self):
        self._sb_lower.setValue(self._threshold[0])
        self._sb_upper.setValue(self._threshold[1])

    def _changeSpinValue(self):
        if self._sb_lower.value() <= self._sb_upper.value():
            self.current_threshold[0] = self._sb_lower.value()
            self.current_threshold[1] = self._sb_upper.value()
            self.ThresholdChanged.emit()
        else:
            self._sb_lower.setValue(self.current_threshold[0])
            self._sb_upper.setValue(self.current_threshold[1])
            OKMessageBox(QtWidgets.QMessageBox.Warning,'lower threshold must be less than upper threshold !')


    def getThreshold(self):
        return self._threshold

    def setThreshold(self, threshold):
        self._threshold = threshold
        self.initPlots()

class MapLevelBar(SubWidgetQFrame):
    LevelChanged = QtCore.Signal()
    def __init__(self, slider_param=[100,1500,800,100], border=True ):
        self.slider_param =slider_param
        super(MapLevelBar, self).__init__(border)

    def setup(self):
        self.label = QtWidgets.QLabel()
        self._level_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self._level_slider.setMaximum(self.slider_param[1])
        self._level_slider.setMinimum(self.slider_param[0])
        self._level_slider.setValue(self.slider_param[2])
        self._level_slider.setTickInterval(self.slider_param[3])
        self._level_slider.setTickPosition(QtWidgets.QSlider.TicksAbove)
        self._setLevel()
        self._level_slider.valueChanged.connect(lambda: self._setLevel())
        self.grid.addWidget(self.label,0,0,1,1)
        self.grid.addWidget(self._level_slider,1,0,1,2)

    def _setLevel(self):
        self.label.setText('Max Map Level = ' + str(self._level_slider.value()))
        self.LevelChanged.emit()

    def getLevel(self):
        return self._level_slider.value()

class LevelBar(SubWidgetQFrame):
    LevelChanged = QtCore.Signal()
    def __init__(self, bar_label='Value', slider_param=[100,1500,800,100], border=True ):
        self.slider_param =slider_param
        self.slider_factor = 1
        self.bar_level = bar_label
        super(LevelBar, self).__init__(border)

    def setup(self):
        self.label = QtWidgets.QLabel()
        self._level_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.setSlider()
        self._level_slider.setTickPosition(QtWidgets.QSlider.TicksAbove)
        self._setLevel()
        self._level_slider.valueChanged.connect(lambda: self._setLevel())
        self.grid.addWidget(self.label,0,0,1,1)
        self.grid.addWidget(self._level_slider,1,0,1,2)

    def setSlider(self, factor=1):
        self.slider_factor = factor
        self._level_slider.setMaximum(self.slider_param[1] * self.slider_factor)
        self._level_slider.setMinimum(self.slider_param[0] * self.slider_factor)
        self._level_slider.setValue(self.slider_param[2] * self.slider_factor)
        self._level_slider.setTickInterval(self.slider_param[3] * self.slider_factor)


    def _setLevel(self):
        self.label.setText('{} = '.format(self.bar_level) + str(self._level_slider.value()))
        self.LevelChanged.emit()

    def getLevel(self):
        return self._level_slider.value()

class GesRecordModeWidget(SubWidgetQFrame):
    def __init__(self, label='label', box_list=[], border=True):
        self._label_text = label
        self._box_list = box_list
        self._duration = None
        self._min_gap = None
        super(GesRecordModeWidget, self).__init__(border)


    def setup(self):
        self._Label = QtWidgets.QLabel(self._label_text)
        self.ComboBox = QtWidgets.QComboBox()
        self.ComboBox.addItems(self._box_list)
        self.grid.addWidget(self._Label, 0 ,0 ,1, 1)
        self.grid.addWidget(self.ComboBox, 0, 1, 1, 2)
        self.ComboBox.currentIndexChanged.connect(lambda : self._selectComboBox())
        self._selectComboBox()

    def _selectComboBox(self):
        # print(self._ComboBox.currentIndex())
        if self._duration != None:
            self.grid.removeWidget(self._duration)
            self.grid.removeWidget(self._min_gap)
            self._duration = None
            self._min_gap = None

        if self._box_list[self.ComboBox.currentIndex()] == 'Pre-define':
            self._duration = HTextLineWidget('Duration :', '20', border=False)
            self._min_gap = HTextLineWidget('Minimum Gap :', '10', border=False)
            self.grid.addWidget(self._duration, 1, 0, 1, 2)
            self.grid.addWidget(self._min_gap, 2, 0, 1, 2)

    def getCurrentComboBox(self):
        return self._box_list[self.ComboBox.currentIndex()]

    def getPreDefineConfig(self):
        if self._duration == None:
            return [],[]
        return int(self._duration.getLineText()), int(self._min_gap.getLineText())

class NumberOfGestureWidget(SubWidgetQFrame):
    def __init__(self, label='label', range=[0,10], default_val=0, ges_dict={}, border=True):
        self._label_text = label
        self._default_val = default_val
        self._range = range
        self._ges_dict = ges_dict
        self._ges_list = []
        super(NumberOfGestureWidget, self).__init__(border)

    def setup(self):
        self._Label = QtWidgets.QLabel(self._label_text)
        self._SpinBox = QtWidgets.QSpinBox()
        self._SpinBox.valueChanged.connect(lambda: self._genGestureList())
        self._SpinBox.setRange(self._range[0], self._range[1])
        self._SpinBox.setValue(self._default_val)
        self.grid.addWidget(self._Label, 0 ,0 ,1, 1)
        self.grid.addWidget(self._SpinBox, 0, 1, 1, 2)

    def getSpinBoxValue(self):
        return self._SpinBox.value()

    def _genGestureList(self):
        for ges in self._ges_list:
            # self.grid.removeWidget(ges)
            ges.deleteLater()

        l = list(self._ges_dict.values())
        l.pop(0)
        num = self._SpinBox.value()
        self._ges_list =[]
        if num == 0:
            ges = HComboBoxWidget('Gesture 1 :', ['Background'], border=False)
            self.grid.addWidget(ges,1,0,1,2)
            self._ges_list.append(ges)
            return

        for i in range(num):
            ges = HComboBoxWidget('Gesture {} :'.format(i+1), l, border=False)
            ges.getCurrentComboBox()
            self.grid.addWidget(ges,i+1,0,1,2)
            self._ges_list.append(ges)

    def getGestureList(self):
        ges_list = []
        for ges in self._ges_list:
            ges_list.append(ges.getCurrentComboBox())
        return ges_list

class CheckBoxListWidget(SubWidgetQFrame):
    check_Signal = QtCore.Signal()
    def __init__(self, items:dict, label=None, cols=1, border=True):
        self._items = items
        self._label_text = label
        self._cols = cols
        self.status_changed = True
        super(CheckBoxListWidget, self).__init__(border)

    def setup(self):

        if self._label_text is not None:
            self._label = QtWidgets.QLabel(self._label_text)
            self.grid.addWidget(self._label,0,0,1,2)

        for k, v in self._items.items():
            v['item'] = QtWidgets.QCheckBox(k)
            if v.get('check') is not None:
                v['item'].setChecked(v.get('check'))
            if v.get('enable') is not None:
                v['item'].setEnabled(v.get('enable'))
            v['item'].toggled.connect(self._checkBox)

        row = 1
        col = 0
        for k, v in self._items.items():
            if v.get('item') is None:
                continue
            self.grid.addWidget(v['item'], row, col, 1, 1)
            col = col + 1
            if col == self._cols:
                row = row +1
                col = 0

    def setItemsConfigs(self, item_dict=None):
        if item_dict is None:
            item_dict = self._items
        for k, v in item_dict.items():
            if v.get('check') is not None:
                v['item'].setChecked(v.get('check'))


    def _checkBox(self):
        for k, v in self._items.items():
            if v['item'] is self.sender():
                v['check'] = v['item'].isChecked()
                print(k, v['check'])
                self.status_changed = True
                break
        self.check_Signal.emit()
        # print(self._items)

    def setEnable(self, item, enable):
        if self._items.get(item) is None:
            return
        self._items[item]['enable'] = enable
        self._items[item].setEnabled(True)

    def getItemsStatus(self):
        return self._items

    def getItemCheck(self, item):
        return self._items[item]['check']

    def setDefault(self):
        for k, v in self._items.items():
            if v.get('Default') is not None:
                v['check'] = v.get('Default')
            if v.get('check') is not None:
                v['item'].setChecked(v.get('check'))

class SetScriptWidget(SubWidgetQFrame):
    SetScript_Signal =QtCore.Signal()
    def __init__(self, setting_list ,label=None, progress_bar=True,  border=True):
        self._setting_list = setting_list
        self._progress_bar = progress_bar
        self._lable_text = label
        self._script_set = False
        super(SetScriptWidget, self).__init__(border)


    def _getConfigList(self):
        from operator import itemgetter
        new_Vparams = []
        Vparams = []
        params=[]
        dirs = os.listdir(kgl.KKTTempParam)
        for dir in dirs:
            if not os.path.isdir(os.path.join(kgl.KKTTempParam, dir)):
                # dirs.remove(dir)
                continue
            if dir.split('-')[0] == 'K60168':
                dir = dir.split('-')
                new_Vparams.append(dir)
            else:
                if len(dir.split('.')) == 3 and dir[0] == 'v':
                    dir = dir.split('v')[1]
                    dir = dir.split('.')
                    dir = [int(dir[i]) for i in range(3)]
                    Vparams.append(dir)
                else:
                    params.append(dir)
        new_Vparams.sort(key=itemgetter(2, -1), reverse=True)
        for p in range(len(new_Vparams)):
            new_Vparams[p] = '-'.join(new_Vparams[p])
        Vparams.sort(key=itemgetter(0, 1, 2), reverse=True)
        for i in range(len(Vparams)):
            Vparams[i] = 'v' + str(Vparams[i][0]) + '.' + str(Vparams[i][1]) + '.' + str(Vparams[i][2])

        dirs = new_Vparams + Vparams + params
        return dirs

    def mousePressComboBox(self, event:QtGui.QMouseEvent) -> None:
        self._setting_list = self._getConfigList()
        self._setting_comboBox.clear()
        self._setting_comboBox.addItems(self._setting_list)
        self._setting_comboBox.showPopup()


    def setup(self):
        self.grid.setColumnStretch(2, 1)
        self._setting_comboBox = QtWidgets.QComboBox()
        self._setting_comboBox.addItems(self._setting_list)
        self._setting_comboBox.mousePressEvent = self.mousePressComboBox
        self._lb = QtWidgets.QLabel(' [ Progress ]')
        self._pgb = QtWidgets.QProgressBar()
        self._pgb.setRange(0, 100)
        # pgb.setFormat('%p%')
        self._pgb.setValue(0)
        self._pgb.setFormat('%v%')
        self._pgb.setTextVisible(True)
        self._pb_start = QtWidgets.QPushButton('Set Script')
        self._pb_start.clicked.connect(lambda :self._setScript())

        self.openRX = HComboBoxWidget('Open RX :',['RX23'])
        self._RXCheckBox = CheckBoxListWidget({'RX1':{'enable':True, 'check':False},
                                               'RX2':{'enable':True, 'check':True},
                                               'RX3':{'enable':False, 'check':True}},label='Open RX :',cols=3)

        if self._lable_text is not None:
            self._title = QtWidgets.QLabel(self._lable_text)
            self.grid.addWidget(self._title, 0, 0, 1, 1)
        self.grid.addWidget(self._setting_comboBox,0, 1, 1, 1)
        self.grid.addWidget(self._pb_start,0, 2, 1, 1)
        self.grid.addWidget(self._RXCheckBox, 3, 0, 1, 3)
        if self._progress_bar:
            self.grid.addWidget(self._pgb, 2, 0, 1, 3)
            self.grid.addWidget(self._lb, 2, 0, 1, 3)
        pass

    def _setScript(self):
        self.initStatus()
        self.enableWidget(False)
        self.SetScript_Signal.emit()

    def getItemCheck(self, item):
        return self._RXCheckBox.getItemCheck(item)

    def getItemStatus(self):
        return self._RXCheckBox.getItemsStatus()

    def getSetting(self):
        return self._setting_comboBox.currentText()

    def initStatus(self):
        self._script_set = False
        self._pgb.setValue(0)
        self._lb.setText(' [ Progress ]')

    def updateProcess(self, process):
        if not self._progress_bar:
            return
        # process = self._setting_proc.getProgress()
        if process is None:
            return
        self._lb.setText(' [ {} ] ({}/{})'.format(process[0], process[1][0], process[1][1]))
        v = process[2]
        self._pgb.setValue(v)
        QtWidgets.QApplication.processEvents()
        if v == 100:
            self.enableWidget(True)
            self._script_set = True
        pass

    def enableWidget(self, enable:bool):
        self._pb_start.setEnabled(enable)
        self._RXCheckBox.setEnabled(enable)
        self._setting_comboBox.setEnabled(enable)
        pass

class SetScriptWidget2(SubWidgetQFrame):
    SetScript_Signal =QtCore.Signal()
    def __init__(self, setting_list ,label=None, progress_bar=True,  border=True):
        self._setting_list = setting_list
        self._progress_bar = progress_bar
        self._lable_text = label
        self._script_set = False
        super(SetScriptWidget2, self).__init__(border)

    def setup(self):
        # self.grid.setColumnStretch(2, 1)
        self._setting_comboBox = QtWidgets.QComboBox()
        self._setting_comboBox.addItems(self._setting_list)
        self._lb = QtWidgets.QLabel(' [ Progress ]')
        self._pgb = QtWidgets.QProgressBar()
        self._pgb.setRange(0, 100)
        # pgb.setFormat('%p%')
        self._pgb.setValue(0)
        self._pgb.setFormat('%v%')
        self._pgb.setTextVisible(True)
        DEFAULT_STYLE = """ 
        QProgressBar{ 
            border: 1px solid lightgrey; 
            text-align: center 
        } 

        QProgressBar::chunk { 
            background-color: lightgreen; 

        } 
        """
        self._pgb.setStyleSheet(DEFAULT_STYLE)



        self._pb_start = QtWidgets.QPushButton('Set Script')
        self._pb_start.clicked.connect(lambda :self._setScript())

        self.openRX = HComboBoxWidget('Open RX :',['RX23'])
        self._RXCheckBox = CheckBoxListWidget({'RX1':{'enable':True, 'check':False},
                                               'RX2':{'enable':True, 'check':True},
                                               'RX3':{'enable':False, 'check':True}},label='Open RX :',cols=3)


        if self._lable_text is not None:
            self._title = QtWidgets.QLabel(self._lable_text)
            self.grid.addWidget(self._title, 0, 0, 1, 1)
        self.grid.addWidget(self._setting_comboBox,1, 0, 1, 2)
        self.grid.addWidget(self._pb_start,0, 1, 1, 1)
        self.grid.addWidget(self._RXCheckBox, 3, 0, 1, 2)
        if self._progress_bar:
            self.grid.addWidget(self._pgb, 2, 0, 1, 2)
            self.grid.addWidget(self._lb, 2, 0, 1, 2)
        pass

    def setProgressBarColor(self, color):

        self._pgb.setStyleSheet("QProgressBar:chunk{background-color: b;}"
                                )
    def setRXSection(self, visible, RX1, RX2, RX3):
        self._RXCheckBox.setVisible(visible)
        item_dict = self.getItemStatus()
        item_dict.get('RX1')['check'] = RX1
        item_dict.get('RX2')['check'] = RX2
        item_dict.get('RX3')['check'] = RX3
        self._RXCheckBox.setItemsConfigs(item_dict)

    def _setScript(self):
        self.initStatus()
        self.enableWidget(False)
        self.SetScript_Signal.emit()

    def getItemCheck(self, item):
        return self._RXCheckBox.getItemCheck(item)

    def getItemStatus(self):
        return self._RXCheckBox.getItemsStatus()

    def getSetting(self):
        return self._setting_comboBox.currentText()

    def initStatus(self):
        self._script_set = False
        self._pgb.setValue(0)
        self._lb.setText(' [ Progress ]')

    def updateProcess(self, process):
        if not self._progress_bar:
            return
        # process = self._setting_proc.getProgress()
        if process is None:
            return
        self._lb.setText(' [ {} ] ({}/{})'.format(process[0], process[1][0], process[1][1]))
        v = process[2]
        self._pgb.setValue(v)
        QtWidgets.QApplication.processEvents()
        if v == 0:
            COMPLETED_STYLE = """ 
            QProgressBar{ 
                border: 1px solid lightgrey; 
                text-align: center 
            } 

            QProgressBar::chunk { 
                background-color: lightgreen; 
            } 
            """
            self._pgb.setStyleSheet(COMPLETED_STYLE)
        if v == 100:
            COMPLETED_STYLE = """ 
            QProgressBar{ 
                border: 1px solid lightgrey; 
                text-align: center 
            } 

            QProgressBar::chunk { 
                background-color: limegreen; 
            } 
            """
            self._pgb.setStyleSheet(COMPLETED_STYLE)
            self._lb.setText(' [ Done ]')
            self.enableWidget(True)
            self._script_set = True
        pass

    def enableWidget(self, enable:bool):
        self._pb_start.setEnabled(enable)
        self._RXCheckBox.setEnabled(enable)
        self._setting_comboBox.setEnabled(enable)
        pass

class ModeSelectWidget(SubWidgetQFrame):
    changeIndex = QtCore.Signal()
    PressStart_signal = QtCore.Signal()
    def  __init__(self, label='label', box_list=[], border=True):
        self._label_text = label
        self._box_list = box_list
        super(ModeSelectWidget, self).__init__(border)

    def setup(self):
        # self.grid.setColumnStretch(2, 1)
        self._Label = QtWidgets.QLabel(self._label_text)
        self._ComboBox = QtWidgets.QComboBox()
        self._ComboBox.addItems(self._box_list)
        self._pb_start = QtWidgets.QPushButton('Start')
        self.grid.addWidget(self._Label, 0 ,0 ,1, 1)
        self.grid.addWidget(self._ComboBox, 0, 1, 1, 1)
        self.grid.addWidget(self._pb_start, 1, 0, 1, 2)
        self._ComboBox.currentIndexChanged.connect(lambda : self._selectComboBox())
        self._pb_start.clicked.connect(lambda :self._pressStart())
        self._selectComboBox()

    def _selectComboBox(self):
        # print(self._ComboBox.currentIndex())
        self.changeIndex.emit()

    def getCurrentComboBox(self):
        return self._box_list[self._ComboBox.currentIndex()]

    def setComboBox(self, text):
        assert text in self._box_list, 'Text not in combobox!'
        self._ComboBox.setCurrentIndex(self._box_list.index(text))

    def _pressStart(self):
        self.PressStart_signal.emit()

    def initComboBox(self):
        self._ComboBox.addItems(self._box_list)

    def updateModeList(self, mode_list):
        self._box_list = mode_list

class SpinCheckBoxListWidget(SubWidgetQFrame):
    def __init__(self, items:dict, label=None, cols=1, border=True):
        self._items = items
        self._label_text = label
        self._cols = cols
        super(SpinCheckBoxListWidget, self).__init__(border)

    def setup(self):

        if self._label_text is not None:
            self._label = QtWidgets.QLabel(self._label_text)
            self.grid.addWidget(self._label,0,0,1,2)

        for k, v in self._items.items():
            v['CheckBox'] = QtWidgets.QCheckBox(k)
            v['CheckBox'].clicked.connect(lambda :self._checkBox())
            v['Combobox'] = QtWidgets.QSpinBox()
            v['Combobox'].setValue(v['Value'])
            v['Combobox'].setAxisRange(v['Range'][0], [1])
            v['Combobox'].setAxisRange(v['Range'][0], [1])
            if v.get('check') is not None:
                v['CheckBox'].setChecked(v.get('check'))
            if v.get('enable') is not None:
                v['CheckBox'].setEnabled(v.get('enable'))

        row = 1
        col = 0
        for k, v in self._items.items():
            if v.get('item') is None:
                continue
            self.grid.addWidget(v['item'], row, col, 1, 1)
            col = col + 1
            if col == self._cols:
                row = row +1
                col = 0

    def _checkBox(self):
        for k, v in self._items.items():
            v['check'] = v['item'].isChecked()
        # print(self._items)

    def setEnable(self, item, enable):
        if self._items.get(item) is None:
            return
        self._items[item]['enable'] = enable
        self._items[item].setEnabled(True)

    def getItemsStatus(self):
        return self._items

    def getItemCheck(self, item):
        return self._items[item]['check']

class SpinBoxListWidget(SubWidgetQFrame):
    change_Signal = QtCore.Signal()
    def __init__(self, items:dict, label=None, cols=1, border=True):
        self._items = items
        self._label_text = label
        self._cols = cols
        super(SpinBoxListWidget, self).__init__(border)

    def setup(self):

        if self._label_text is not None:
            self._label = QtWidgets.QLabel(self._label_text)
            self.grid.addWidget(self._label,0,0,1,2)

        for k, v in self._items.items():
            v['Item'] = QtWidgets.QLabel('{} :'.format(k))
            if v.get('Label') is not None:
                v['Item'] = QtWidgets.QLabel('{} :'.format(v['Label']))
            v['Spin'] = QtWidgets.QSpinBox()
            v['Spin'].setRange(v['Range'][0], v['Range'][1])
            v['Spin'].setValue(v['Value'])
            v['Default'] = v['Value']
            v['Spin'].valueChanged.connect(lambda : self._changeSpinBox())

            if v.get('enable') is not None:
                v['Item'].setEnabled(v.get('enable'))
                v['Spin'].setEnabled(v.get('enable'))

        row = 1
        col = 0
        for k, v in self._items.items():
            if v.get('Item') is None:
                continue
            self.grid.addWidget(v['Item'], row, col, 1, 1)
            self.grid.addWidget(v['Spin'], row, col+1, 1, 1)
            self.grid.setColumnStretch(col, 1)
            self.grid.setColumnStretch(col+1, 1)
            col = col + 2
            if col == self._cols*2:
                row = row +1
                col = 0

    def setEnable(self, item, enable):
        if self._items.get(item) is None:
            return
        self._items[item]['enable'] = enable
        self._items[item]['Item'].setEnabled(True)
        self._items[item]['Spin'].setEnabled(True)

    def getItemsStatus(self):
        for k, v in self._items.items():
            v['Value'] = v['Spin'].value()
        return self._items

    def setDefault(self):
        for k, v in self._items.items():
            if v.get('Default') is not None:
                v['Value'] = v.get('Default')
                v['Spin'].setValue(v['Value'])

    def _changeSpinBox(self):
        self.change_Signal.emit()
        for k, v in self._items.items():
            v['Value'] = v['Spin'].value()
        pass
    def setValue(self, item, value):
        self._items.get(item)['Spin'].setValue(value)
        self._items.get(item)['Value'] = value


class DoubleSpinBoxListWidget(SubWidgetQFrame):
    change_Signal = QtCore.Signal()
    def __init__(self, items:dict, label=None, cols=1, border=True):
        self._items = items
        self._label_text = label
        self._cols = cols
        super(DoubleSpinBoxListWidget, self).__init__(border)

    def setup(self):

        if self._label_text is not None:
            self._label = QtWidgets.QLabel(self._label_text)
            self.grid.addWidget(self._label,0,0,1,2)

        for k, v in self._items.items():
            v['Item'] = QtWidgets.QLabel('{} :'.format(k))
            if v.get('Label') is not None:
                v['Item'] = QtWidgets.QLabel('{} :'.format(v['Label']))
            v['Spin'] = QtWidgets.QDoubleSpinBox()
            v['Spin'].setRange(v['Range'][0], v['Range'][1])
            v['Spin'].setSingleStep(v['Range'][2])
            v['Spin'].setValue(v['Value'])
            v['Default'] = v['Value']
            v['Spin'].valueChanged.connect(lambda : self._changeSpinBox())

            if v.get('enable') is not None:
                v['Item'].setEnabled(v.get('enable'))
                v['Spin'].setEnabled(v.get('enable'))

        row = 1
        col = 0
        for k, v in self._items.items():
            if v.get('Item') is None:
                continue
            self.grid.addWidget(v['Item'], row, col, 1, 1)
            self.grid.addWidget(v['Spin'], row, col+1, 1, 1)
            self.grid.setColumnStretch(col, 1)
            self.grid.setColumnStretch(col+1, 1)
            col = col + 2
            if col == self._cols*2:
                row = row +1
                col = 0

    def setEnable(self, item, enable):
        if self._items.get(item) is None:
            return
        self._items[item]['enable'] = enable
        self._items[item]['Item'].setEnabled(True)
        self._items[item]['Spin'].setEnabled(True)

    def setRange(self,item , range):
        item = self._items.get(item)
        item['Spin'].setRange(range[0], range[1])
        item['Spin'].setSingleStep(range[2])

    def getItemsStatus(self):
        for k, v in self._items.items():
            v['Value'] = v['Spin'].value()
        return self._items

    def setDefault(self):
        for k, v in self._items.items():
            if v.get('Default') is not None:
                v['Value'] = v.get('Default')
                v['Spin'].setValue(v['Value'])

    def _changeSpinBox(self):
        self.change_Signal.emit()
        for k, v in self._items.items():
            v['Value'] = v['Spin'].value()
        pass

class GainWidget(SubWidgetQFrame):
    change_Signal = QtCore.Signal()
    check_Signal = QtCore.Signal()
    class RXSpinBox(QtWidgets.QSpinBox):
        TX_level = 3

        def textFromValue(self, val: int) -> str:
            d = {1: ['-8.80', '-5.50', '-1.80', '0.80'], 2: ['-5.80', '-2.50', '1.20', '3.80'],
                 3: ['-3.30', "0.00", '3.70', '6.30'], 4: ['-1.30', '2.00', '5.70', '8.30']}
            return d.get(self.TX_level)[val - 1]
    class TXSpinBox(QtWidgets.QSpinBox):
        TX_level = 3

        def textFromValue(self, val: int) -> str:
            d = {1: '-4.5', 2: '-1.57', 3: '1', 4: '2.9'}
            return d.get(val)
    def __init__(self, items: dict, label=None, border=True):
        self._items = items
        self._label_text = label
        self.status_changed = True
        self.check_changed = True
        super(GainWidget, self).__init__(border)



    def setup(self):

        if self._label_text is not None:
            self._label = QtWidgets.QLabel(self._label_text)
            self.grid.addWidget(self._label, 0, 0, 1, 2)
        self._items.get('TX')['Spin'] = self.TXSpinBox()
        self._items.get('TX')['Spin'].wheelEvent = lambda event: None
        self._items.get('TX')['Spin'].setRange(self._items.get('TX')['Range'][0], self._items.get('TX')['Range'][1])
        self._items.get('TX')['Spin'].valueChanged.connect(self._changeSpinBox)
        RX_spin = self.RXSpinBox()
        RX_spin.wheelEvent = lambda event: None
        RX_spin.setRange(self._items.get('TX')['Range'][0], self._items.get('TX')['Range'][1])
        RX_spin.valueChanged.connect(self._changeSpinBox)
        self._items.get('RX1')['Spin'] = RX_spin
        self._items.get('RX2')['Spin'] = RX_spin
        self._items.get('RX3')['Spin'] = RX_spin

        lb_TX = QtWidgets.QLabel('Power Level (dBm) :')
        lb_RX = QtWidgets.QLabel('Gain Level (dB):')
        frame = QtWidgets.QFrame()
        frame.setFrameStyle(QtWidgets.QFrame.HLine | QtWidgets.QFrame.Sunken)
        frame.frameRect()


        for k, v in self._items.items():
            v['Item'] = QtWidgets.QCheckBox('{}'.format(v['Label']))
            v['Item'].setChecked(v['Check'])
            v['Item'].toggled.connect(self._clickCheckBox)
            v['Default'] = v['Value']
            v['Spin'].setValue(v['Value'])
            v['Item'].setEnabled(v['enable'])

        # self.enableCheckbox(True)
        # self.enableCheckbox(False, 'TX')
        # self.enableCheckbox(False, 'RX3')

        self.grid.addWidget(self._items.get('TX')['Item'], 1, 0, 1, 1)
        self.grid.addWidget(lb_TX, 2, 0, 1, 2)
        self.grid.addWidget(self._items.get('TX')['Spin'], 2, 1, 1, 2)
        self.grid.addWidget(frame, 3, 0, 1, 3)
        self.grid.addWidget(self._items.get('RX1')['Item'], 4, 0, 1, 1)
        self.grid.addWidget(lb_RX, 5, 0, 1, 2)
        self.grid.addWidget(self._items.get('RX1')['Spin'], 5, 1, 1, 2)
        self.grid.addWidget(self._items.get('RX2')['Item'], 4, 1, 1, 1)
        self.grid.addWidget(self._items.get('RX3')['Item'], 4, 2, 1, 1)

    def setItemsConfigs(self, item_dict=None):
        if item_dict is None:
            item_dict = self._items
        for k, v in item_dict.items():
            v['Item'].setChecked(v['Check'])
            v['Spin'].setValue(v['Value'])
        pass



    def setEnable(self, item, enable):
        if self._items.get(item) is None:
            return
        self._items[item]['enable'] = enable
        self._items[item]['Item'].setEnabled(enable)
        self._items[item]['Spin'].setEnabled(True)

    def setGain(self, item, level):
        self._items.get(item)['Spin'].setValue(int(level))

    def setRXCheck(self, item, check):
        if self._items.get(item) is None:
            return
        self._items[item]['Item'].setChecked(bool(check))


    def getItemsStatus(self):
        for k, v in self._items.items():
            v['Value'] = v['Spin'].value()
        return self._items

    def setDefault(self):
        for k, v in self._items.items():
            if v.get('Default') is not None:
                v['Value'] = v.get('Default')
                v['Spin'].setValue(v['Value'])

    def _changeSpinBox(self):
        sender = self.sender()
        for k, v in self._items.items():
            if v['Spin'] == sender:
                v['Value'] = v['Spin'].value()
            v['Spin'].TX_level = self._items.get('TX')['Spin'].value()
            v['Spin'].setValue(v['Spin'].value())
        self.status_changed = True


        # pprint.pprint(self._items)
        self.change_Signal.emit()
        pass

    def _clickCheckBox(self):
        sender = self.sender()
        for k, v in self._items.items():
            if v['Item'] == sender:
                v['Check'] = v['Item'].isChecked()
                self.check_changed = True
                break
        print(k, v['Check'])
        self.check_Signal.emit()
        pass

    def enableCheckbox(self, enable, item=''):
        item = self._items.get(item)
        if item is not None:
            item['enable'] = enable
            item['Item'].setEnabled(enable)
            return
        for k, v in self._items.items():
            v['enable'] = enable
            v['Item'].setEnabled(enable)

    def checkCheckBox(self, check, item=''):
        item = self._items.get(item)
        if item is not None:
            item['Enable'] = check
            item.setEnabled(check)
            return
        for k, v in self._items.items():
            v['Enable'] = check
            v['Item'].setEnabled(check)


class SaveCurrentDataWidget(SubWidgetQGroupBox):
    save_Signal = QtCore.Signal()
    replay_Signal = QtCore.Signal(bool)
    def __init__(self, title=''):
        super(SaveCurrentDataWidget, self).__init__(title)
        self.replaying = False
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(lambda :self._countFrame())

    def setup(self):
        self._pb_save = QtWidgets.QPushButton('Save')
        self._pb_save.clicked.connect(lambda: self._pressSave())
        self._pb_load = QtWidgets.QPushButton('Load')
        self._pb_load.clicked.connect(lambda: self._pressLoad())
        self._el_load = QtWidgets.QLineEdit()
        self._el_load.setReadOnly(True)
        self._lb_load = QtWidgets.QLabel('Load Buffered Data :')
        self._pb_replay = QtWidgets.QPushButton('Replay')
        self._pb_replay.clicked.connect(lambda: self._replayBuffedData())
        self._lb_max_buf_frame = QtWidgets.QLabel('Max Buffer Length (Frames) :')
        self._lb_current_frame = QtWidgets.QLabel('Buffered Frames :')
        self._el_max_buf_frame = QtWidgets.QLineEdit()
        self._el_max_buf_frame.setText('100')
        self._el_current_frame = QtWidgets.QLineEdit()
        self._el_current_frame.setText('0')
        self._el_current_frame.setReadOnly(True)

        self.grid.addWidget(self._pb_save, 0 ,0 ,1, 1)
        self.grid.addWidget(self._pb_load, 0, 1, 1, 1)
        self.grid.addWidget(self._lb_load, 1, 0, 1, 1)
        self.grid.addWidget(self._el_load, 1, 1, 1, 1)
        self.grid.addWidget(self._pb_replay, 2, 0, 1, 2)
        self.grid.addWidget(self._lb_max_buf_frame, 3, 0, 1, 1)
        self.grid.addWidget(self._lb_current_frame, 4, 0, 1, 1)
        self.grid.addWidget(self._el_max_buf_frame, 3, 1, 1, 1)
        self.grid.addWidget(self._el_current_frame, 4, 1, 1, 1)

    def _pressSave(self):
        self.save_Signal.emit()
        print('press save')

    def _pressLoad(self):
        buf_dir = os.path.join(kgl.KKTRecord, 'Buffed Data')
        self._load_file_name, type = QtWidgets.QFileDialog.getOpenFileName(None, 'Save Buffered Data', buf_dir,
                                              "Text files(*.txt);;CSV Files (*.csv)")

        print(self._load_file_name)
        self._el_load.setText(os.path.basename(self._load_file_name))

    def getLoadDataPath(self):
        return self._load_file_name

    def setMaxBufferFrames(self, frames):
        self._el_max_buf_frame.setText(str(frames))

    def setCurrentBufferFrames(self, frames):
        self._el_current_frame.setText(str(frames))

    def getFrames(self):
        return self._el_max_buf_frame.text(), self._el_current_frame.text()

    def _replayBuffedData(self):
        assert self._el_load.text() != '', 'Load Buffered Data is empty !'
        if self.replaying:
            self.timer.stop()
            self._pb_replay.setText('Replay')
            self.replaying = False
            self.replay_Signal.emit(False)
            return
        self._pb_replay.setText('Stop')
        self.replay_Signal.emit(True)
        self._lb_current_frame.setText('Current Frame :')
        self.replaying = True
        self.timer.start(50)
        pass

    def _countFrame(self):
        if self._el_max_buf_frame.text() == self._el_current_frame.text():
            self.timer.stop()
            self._pb_replay.setText('Replay')
            self.replaying = False
            self.replay_Signal.emit(False)

    def setCurrentFrame(self):
        self._lb_current_frame.setText('Buffered Frame :')
        pass


    def enablewidgets(self, enable, enable_replay =True):
        self._pb_save.setEnabled(enable)
        self._pb_load.setEnabled(enable)
        self._el_load.setEnabled(enable)
        self._lb_load.setEnabled(enable)
        self._el_max_buf_frame.setReadOnly(not enable)
        if enable_replay:
            self._pb_replay.setEnabled(enable)

class VComboBoxListWidget(SubWidgetQFrame):
    changeIndex = QtCore.Signal()
    def __init__(self, items={}, label=None, cols=1, border=True):
        self._label_text = label
        self._items = items
        self._cols = cols
        self.status_changed = True
        super(VComboBoxListWidget, self).__init__(border)

    def setup(self):
        if self._label_text is not None:
            self._label = QtWidgets.QLabel(self._label_text)
            self.grid.addWidget(self._label,0,0,1,2)

        for k, v in self._items.items():
            v['Item'] = QtWidgets.QLabel('{} :'.format(v['Label']))
            v['Box'] = QtWidgets.QComboBox()
            v['Box'].wheelEvent = lambda event: None
            v['Box'].addItems(v['List'])
            v['Default'] = v['Index']
            v['Box'].setCurrentIndex(v['Default'])
            v['Box'].currentIndexChanged.connect(self._changeComboBox)


            if v.get('Enable') is not None:
                v['Item'].setEnabled(v.get('Enable'))
                v['Box'].setEnabled(v.get('Enable'))

        row = 1
        col = 0
        for k, v in self._items.items():
            if v.get('Item') is None:
                continue
            self.grid.addWidget(v['Item'], row, col, 1, 1)
            self.grid.addWidget(v['Box'], row, col + 1, 1, 1)
            self.grid.setColumnStretch(col, 1)
            self.grid.setColumnStretch(col + 1, 1)
            col = col + 2
            if col == self._cols * 2:
                row = row + 1
                col = 0

    def visibleItems(self, item_name, item_dict=None):
        if item_dict is None:
            self._items[item_name]['Box'].clear()
            self._items[item_name]['Box'].addItems(self._items[item_name]['List'])
            return

        temp_items = list(self._items[item_name]['List'])
        for k,v in item_dict.items():
            if not v:
                temp_items.remove(k)
            else:
                temp_items.append(k)
        self._items[item_name]['Box'].clear()
        self._items[item_name]['Box'].addItems(temp_items)

    def setItemsConfigs(self, item_dict):
        if item_dict is None:
            item_dict = self._items
        for k, v in item_dict.items():
            v['Box'].setCurrentIndex(v['Index'])

    def _changeComboBox(self):
        for k, v in self._items.items():
            if v['Box'] == self.sender():
                v['Index'] = v['Box'].currentIndex()
                self.status_changed = True
                break
        print(k ,v['Index'])
        self.changeIndex.emit()

    def setDefault(self):
        for k, v in self._items.items():
            v['Index'] = v['Default']
            v['Box'].setCurrentIndex(v['Default'])

    def getCurrentComboBox(self, item=''):
        item = self._items.get(item)
        if item is not None:
            return item
        return self._items

class LongClickButton(QtWidgets.QPushButton):
    sig_Click = QtCore.Signal()
    sig_longClick = QtCore.Signal()
    def __init__(self, text: str):
        super().__init__(text)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.longClick)

    def mousePressEvent(self, e):
        self.sig_Click.emit()
        self.timer.start(800)

    def mouseReleaseEvent(self, e):
        self.timer.stop()

    # 长按后要执行的操作
    def longClick(self):
        self.timer.stop()
        self.timer.start(50)
        self.sig_longClick.emit()




def main():
    coll = CollapsibleSection('132')
    lt1 = HTextLineWidget('test')
    lt2 = HComboBoxWidget('test132154', box_list=['1', '2', '3'], )
    lt3 = HSpinBoxWidget('test132154', )
    lt4 = SelectFileWidget('test132154')
    lt5 = HSpinBoxWidget('test132154', )
    lt6 = InputThreshold()
    lt7 = MapLevelBar()
    lt7.setEnabled(False)
    lt8 = SelectFolderWidget('test132154')
    lt9 = GesRecordModeWidget('Mode:', ['Manual', 'Pre-define'])
    lt10 = NumberOfGestureWidget('Number of gesture : ', default_val=1,
                                 ges_dict={'0': 'Background', '1': 'NearDoublePinch', '2': 'PatPat', '3': 'FrontFront', '4': 'BackBack', '5': 'LeftLeft', '6': 'RightRight'})
    lt11 = CheckBoxListWidget({'1332':{'check':True, 'enable':True},
                               '1322':{'check':False, 'enable':False},
                               '1321': {'check': True, 'enable': False},
                               '1222': {'check': False, 'enable': True},
                               }, 'Test :', cols=3)
    lt12 = SetScriptWidget(['1','2'], 'Hardware setting :')
    lt13 = ModeSelectWidget('test132154', box_list=['1', '2', '3'],)
    lt14 = SaveCurrentDataWidget()
    lt15 = SpinBoxListWidget(items={'test1':{'Value':1,
                                            'Range':[0,10]},
                                   'test2': {'Value': 1,
                                             'Range': [0, 10]},
                                   },label='test' ,cols=2)
    coll.grid.addWidget(lt1, 0, 0, 1, 2)
    coll.grid.addWidget(lt2, 1, 0, 1, 2)
    coll.grid.addWidget(lt3, 2, 0, 1, 1)
    coll.grid.addWidget(lt5, 2, 1, 1, 1)
    coll.grid.addWidget(lt4, 3, 0, 1, 2)
    coll.grid.addWidget(lt6, 4, 0, 1, 2)
    coll.grid.addWidget(lt7, 5, 0, 1, 2)
    coll.grid.addWidget(lt8, 6, 0, 1, 2)
    coll.grid.addWidget(lt9, 7, 0, 1, 2)
    coll.grid.addWidget(lt10, 8, 0, 1, 2)
    coll.grid.addWidget(lt11, 9, 0, 1, 2)
    coll.grid.addWidget(lt12, 10, 0, 1, 2)
    coll.grid.addWidget(lt13, 11, 0, 1, 2)
    coll.grid.addWidget(lt14, 12, 0, 1, 2)
    coll.grid.addWidget(lt15, 13, 0, 1, 2)

    return coll

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    win = QtWidgets.QMainWindow()
    win.resize(350,100)
    win.setCentralWidget(main())
    win.setWindowTitle('Unit test')
    win.show()
    app.exec_()