#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Last-Updated : <2016/01/16 15:53:59 by ymnk>
import sys,os
import cv2
import copy
from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsPixmapItem, QFrame, QFileDialog, QGraphicsEllipseItem, QWidget
from PyQt5.QtGui import QPixmap, QImage, QTransform, QColor
from PyQt5.QtWidgets import QRubberBand

from PyQt5.QtWidgets import QGraphicsRectItem,QGraphicsItem
from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QColor,QPen
from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Main(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(400, 300)
        self.centralWidget = QtWidgets.QWidget(MainWindow)
        self.centralWidget.setObjectName("centralWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralWidget)
        self.horizontalLayout.setContentsMargins(11, 11, 11, 11)
        self.horizontalLayout.setSpacing(6)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.inputGraphicsView = QtWidgets.QGraphicsView(self.centralWidget)
        self.inputGraphicsView.setObjectName("graphicsView")
        #self.centralWidget.addWidget(self.inputGraphicsView)
        MainWindow.setCentralWidget(self.centralWidget)
        #super(Ui_Main, self).setupUi(MainWindow)


def main():

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_Main()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())


if __name__  == "__main__":
    main()
