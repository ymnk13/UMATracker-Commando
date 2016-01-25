#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Last-Updated : <2016/01/24 02:24:48 by ymnk>
import sys

from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QGridLayout, QLabel, QLineEdit
from PyQt5.QtWidgets import QTextEdit, QWidget, QDialog, QApplication
from PyQt5.QtWidgets import QStyle

import numpy as np
from PyQt5.QtCore import pyqtSignal, pyqtSlot

from .colorlabelchange_widget import Ui_ColorLabelChange_Widget

class ColorLabelChange_Widget(QtWidgets.QWidget,Ui_ColorLabelChange_Widget):
    dataFrameChanged = pyqtSignal(bool,int,np.ndarray)
    def __init__(self,parent):
        super(ColorLabelChange_Widget, self).__init__(parent)
        self.setupUi(self)
        qApp = QtWidgets.qApp
        self.moveNextDataButton.setIcon(qApp.style().standardIcon(QStyle.SP_ArrowRight))#SP_MediaSeekForward))
        self.movePrevDataButton.setIcon(qApp.style().standardIcon(QStyle.SP_ArrowLeft))#SP_MediaSeekBackward))

        self.movePrevDataButton.clicked.connect(self.movePrevDataButtonClicked)
        self.moveNextDataButton.clicked.connect(self.moveNextDataButtonClicked)
        self.ColorIconLabel.mousePressEvent = self.colorIconLabelmousePressEvent

        self.dataFrameNo = -1
        self.editingNo = 0
        self.colorList = []
        
        
        rgb = np.array(self.addDataFrame())
        self.setColorLabel(rgb)
        self.setUniqueIDLabel()
        
    def clear(self):
        self.colorList = []
        self.dataFrameNo = -1
        self.editingNo = 0

    def getColor(self):
        #print(self.colorList)
        return self.colorList[self.editingNo]
    def colorIconLabelmousePressEvent(self,event):
        rgb = np.random.randint(0, 255, (1, 3))[0]
        self.colorList[self.editingNo] = rgb
        self.setColorLabel(rgb)
        self.dataFrameChanged.emit(False, self.editingNo,rgb)

    def setColorLabel(self,rgb):
        colorItem = QColor(*rgb)
        icon = QPixmap(32,32)
        icon.fill(colorItem)
        colorIcon = QIcon(icon);
        self.ColorIconLabel.setPixmap(icon)
        
    def addDataFrame(self):
        self.dataFrameNo+=1
        rgb = np.random.randint(0, 255, (1, 3)).tolist()[0]
        self.colorList.append(rgb)
        return self.colorList[-1]
        
    def movePrevDataButtonClicked(self):
        if self.editingNo > 0:
            self.editingNo -=1
        rgb = np.array(self.colorList[self.editingNo])
        self.setColorLabel(rgb)
        self.dataFrameChanged.emit(False, self.editingNo,rgb)
        self.setUniqueIDLabel()        

    def moveNextDataButtonClicked(self):
        if self.editingNo < self.dataFrameNo:
            self.editingNo+=1
            rgb = np.array(self.colorList[self.editingNo])
            self.setColorLabel(rgb)
            self.dataFrameChanged.emit(False, self.editingNo,rgb)
        else:
            rgb = np.array(self.addDataFrame())
            self.editingNo+=1
            self.setColorLabel(rgb)
            self.dataFrameChanged.emit(True, self.editingNo,rgb)
        self.setUniqueIDLabel()
    def setUniqueIDLabel(self):
        self.inidividualUniqueID.setText("{0}/{1}".format(self.editingNo+1,self.dataFrameNo+1))
    
        
def main():
    
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()

    #widget = VideoPlaybackWidget(MainWindow)
    widget = ColorLabelChange_Widget(MainWindow)
    MainWindow.setCentralWidget(widget)
    MainWindow.show()
    sys.exit(app.exec_())
    
    

    


if __name__  == "__main__":
    main()
