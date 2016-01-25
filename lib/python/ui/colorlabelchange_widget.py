# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'colorlabelchange_widget.ui'
#
# Created by: PyQt5 UI code generator 5.4.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ColorLabelChange_Widget(object):
    def setupUi(self, ColorLabelChange_Widget):
        ColorLabelChange_Widget.setObjectName("ColorLabelChange_Widget")
        ColorLabelChange_Widget.resize(184, 44)
        self.horizontalLayout = QtWidgets.QHBoxLayout(ColorLabelChange_Widget)
        self.horizontalLayout.setContentsMargins(1, 0, 1, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.movePrevDataButton = QtWidgets.QPushButton(ColorLabelChange_Widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(32)
        sizePolicy.setVerticalStretch(32)
        sizePolicy.setHeightForWidth(self.movePrevDataButton.sizePolicy().hasHeightForWidth())
        self.movePrevDataButton.setSizePolicy(sizePolicy)
        self.movePrevDataButton.setMaximumSize(QtCore.QSize(32, 32))
        self.movePrevDataButton.setText("")
        self.movePrevDataButton.setObjectName("movePrevDataButton")
        self.horizontalLayout.addWidget(self.movePrevDataButton)
        self.ColorIconLabel = QtWidgets.QLabel(ColorLabelChange_Widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ColorIconLabel.sizePolicy().hasHeightForWidth())
        self.ColorIconLabel.setSizePolicy(sizePolicy)
        self.ColorIconLabel.setMinimumSize(QtCore.QSize(32, 32))
        self.ColorIconLabel.setMaximumSize(QtCore.QSize(32, 32))
        self.ColorIconLabel.setText("")
        self.ColorIconLabel.setObjectName("ColorIconLabel")
        self.horizontalLayout.addWidget(self.ColorIconLabel)
        self.inidividualUniqueID = QtWidgets.QLabel(ColorLabelChange_Widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.inidividualUniqueID.sizePolicy().hasHeightForWidth())
        self.inidividualUniqueID.setSizePolicy(sizePolicy)
        self.inidividualUniqueID.setMinimumSize(QtCore.QSize(64, 0))
        self.inidividualUniqueID.setMaximumSize(QtCore.QSize(32, 32))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.inidividualUniqueID.setFont(font)
        self.inidividualUniqueID.setAlignment(QtCore.Qt.AlignCenter)
        self.inidividualUniqueID.setObjectName("inidividualUniqueID")
        self.horizontalLayout.addWidget(self.inidividualUniqueID)
        self.moveNextDataButton = QtWidgets.QPushButton(ColorLabelChange_Widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.moveNextDataButton.sizePolicy().hasHeightForWidth())
        self.moveNextDataButton.setSizePolicy(sizePolicy)
        self.moveNextDataButton.setMaximumSize(QtCore.QSize(32, 32))
        self.moveNextDataButton.setText("")
        self.moveNextDataButton.setObjectName("moveNextDataButton")
        self.horizontalLayout.addWidget(self.moveNextDataButton)

        self.retranslateUi(ColorLabelChange_Widget)
        QtCore.QMetaObject.connectSlotsByName(ColorLabelChange_Widget)

    def retranslateUi(self, ColorLabelChange_Widget):
        _translate = QtCore.QCoreApplication.translate
        ColorLabelChange_Widget.setWindowTitle(_translate("ColorLabelChange_Widget", "Form"))
        self.inidividualUniqueID.setText(_translate("ColorLabelChange_Widget", "1"))

