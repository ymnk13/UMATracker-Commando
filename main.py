#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, six, math

if six.PY2:
    reload(sys)
    sys.setdefaultencoding('UTF8')

# determine if application is a script file or frozen exe
if getattr(sys, 'frozen', False):
    currentDirPath = sys._MEIPASS
    if os.name == 'nt':
        import win32api
        win32api.SetDllDirectory(sys._MEIPASS)
elif __file__:
    currentDirPath = os.getcwd()

# currentDirPath = os.path.abspath(os.path.dirname(__file__) )
sampleDataPath = os.path.join(currentDirPath,"data")
userDir        = os.path.expanduser('~')

from queue import Queue

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsItem, QGraphicsItemGroup, QGraphicsPixmapItem, QGraphicsEllipseItem, QFrame, QFileDialog, QPushButton
from PyQt5.QtGui import QPixmap, QImage, QPainter, QIcon, QCursor
from PyQt5.QtCore import QPoint, QPointF, QRectF, QEvent, Qt, QSizeF

import cv2
import numpy as np
import scipy.interpolate as interpolate
import pandas as pd
from functools import cmp_to_key
import icon

from lib.python import misc
from lib.python.ui.ui_main_window_base import Ui_MainWindowBase

# from lib.python.ui.tracking_path import TrackingPath
from lib.python.ui.tracking_path_group import TrackingPathGroup
from lib.python.ui.movable_poly_line import MovablePolyLine
from lib.python.ui.tracking_path import TrackingPath
from lib.python.ui.movable_arrow import MovableArrow
from lib.python.ui.resizable_object import ResizableRect, ResizableEllipse
from lib.python.ui.rotatable_ellipse import RotatableEllipse,RotatableEllipseData
from lib.python.ui.hand_input_system import HandInputSystem
# Log file setting.
# import logging
# logging.basicConfig(filename='MainWindow.log', level=logging.DEBUG)

# Log output setting.
# If handler = StreamHandler(), log will output into StandardOutput.
from logging import getLogger, NullHandler, StreamHandler, DEBUG
logger = getLogger(__name__)
handler = NullHandler() if True else StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)

class Ui_MainWindow(QtWidgets.QMainWindow, Ui_MainWindowBase):
    def __init__(self, path):
        super(Ui_MainWindow, self).__init__()
        self.setupUi(self)

        self.videoPlaybackInit()
        self.imgInit()
        self.menuInit()

        self.df = None
        self.handInputSystem = HandInputSystem()
        self.handInputSystem.setRect(self.inputScene.sceneRect())
        self.inputScene.addItem(self.handInputSystem)

        self.trackingPathGroup = None
        self.colors = []

        self.viewScaleRate = 1.0
        self.lastViewScaleRate = 1.0
        self.moveSceneRegionFlag = False
        self.moveSceneRegion = QtCore.QRect(0,0,960,540)        
        self.frameWidth = 30*5
        self.currentFrameNo = 0
        self.trackingPath = None

        self.df = pd.DataFrame({"x0":[],"y0":[]})

        self.circleCheckBox.stateChanged.connect(self.polyLineCheckBoxStateChanged)
        self.lineCheckBox.stateChanged.connect(self.polyLineCheckBoxStateChanged)
        self.overlayCheckBox.stateChanged.connect(self.overlayCheckBoxStateChanged)
        self.radiusSpinBox.valueChanged.connect(self.radiusSpinBoxValueChanged)

        self.frameNoSpinBox.valueChanged.connect(self.frameNoSpinBoxValueChanged)
        self.groupBox_2.hide()

        
        self.inputGraphicsView.mousePressEvent = self.inputGraphicsViewMousePressEvent
        self.inputGraphicsView.mouseMoveEvent = self.inputGraphicsViewMouseMoveEvent
        self.inputGraphicsView.mouseReleaseEvent = self.inputGraphicsViewMouseReleaseEvent
        
        self.inputGraphicsView.keyPressEvent = self.inputGraphicsViewKeyPressEvent
        self.inputGraphicsView.keyReleaseEvent = self.inputGraphicsViewKeyReleaseEvent
        self.drawing = False
        self.setCursor(QtCore.Qt.ArrowCursor)
        

        """
        self.RectA = RotatableEllipse(None)
        self.inputScene.addItem(self.RectA)
        self.RectA.setPoints([[100,100],[200,150]])
        self.RectA.setAngle(45*np.pi/180.0,True)
        self.RectA.hide()
        self.RectA.show()
        self.RectA.setPoints([[200,200],[300,250]])
        """

        self.processDropedFile("/Users/ymnk/temp/Dast/2016/01/hoge.avi")
        self.inputGraphicsView.setResizeAnchor(QGraphicsView.AnchorUnderMouse)#QGraphicsView.NoAnchor)
        self.inputGraphicsView.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.inputGraphicsView.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.inputGraphicsView.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        #self.inputGraphicsView.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.inputGraphicsView.setDragMode(QGraphicsView.ScrollHandDrag)
        #self.inputGraphicsView.translate(500,0);
    def inputGraphicsViewKeyReleaseEvent(self,event):
        key = event.key()
        if key == QtCore.Qt.Key_Control:
            self.moveSceneRegionFlag = False

    def inputGraphicsViewKeyPressEvent(self,event):
        mousePosition = QCursor().pos()
        mousePosition = self.inputGraphicsView.mapFromGlobal(mousePosition)
        mousePosition = self.inputGraphicsView.mapToScene(mousePosition)
        if event.type() == QtCore.QEvent.KeyPress:
            key = event.key()
            if key == QtCore.Qt.Key_Space:
                self.videoPlaybackWidget.playButtonClicked()
            elif key == QtCore.Qt.Key_Right:
                pass
            elif key == QtCore.Qt.Key_Left:
                pass
            elif key == QtCore.Qt.Key_Down:
                self.viewScaleRate -= 1
                if self.viewScaleRate <= 0:
                    self.viewScaleRate = 5
                    self.graphicsViewResized()
                    return
                self.setScale(self.viewScaleRate,mousePosition)
            elif key == QtCore.Qt.Key_Up:
                self.viewScaleRate += 1
                self.setScale(self.viewScaleRate,mousePosition)
                
            elif key == QtCore.Qt.Key_Backspace:
                # Delete Last Line
                self.handInputSystem.deleteLastInputLine()
            elif  0 <= key^0x30 <= 9:
                number = key^0x30
                print("深度:",number)
                self.handInputSystem.setDepth(self.currentFrameNo,number)
            elif key == QtCore.Qt.Key_B:
                self.videoPlaybackWidget.movePrevButtonClicked()
            elif key == QtCore.Qt.Key_N:
                self.videoPlaybackWidget.moveNextButtonClicked()
            elif key == QtCore.Qt.Key_M:
                # 座標もかえる
                self.handInputSystem.saveAngleDataToNextFrame(self.currentFrameNo)
                self.videoPlaybackWidget.moveNextButtonClicked()
            elif key == QtCore.Qt.Key_V:
                # 座標はかえない。
                self.handInputSystem.saveAngleDataToNextFrame(self.currentFrameNo,False)
                self.videoPlaybackWidget.moveNextButtonClicked()
            elif key == QtCore.Qt.Key_E:
                self.handInputSystem.saveInputedLine(self.currentFrameNo)
                frameNo = (int(self.currentFrameNo/self.frameWidth)+1)*self.frameWidth
                self.handInputSystem.setDataFrame(frameNo)
                self.videoPlaybackWidget.moveToFrame(frameNo)

            elif key == QtCore.Qt.Key_Q:
                self.handInputSystem.clearTrackingPath()
                self.handInputSystem.inputedPoints.clear()
                self.handInputSystem.setDataFrame(self.currentFrameNo)
                frameNo = ((int(self.currentFrameNo/(self.frameWidth))-1)*self.frameWidth)
                if frameNo < 0:
                    frameNo = 0
                self.handInputSystem.setDataFrame(frameNo)
                self.videoPlaybackWidget.moveToFrame(frameNo)
            elif key == QtCore.Qt.Key_C:
                widthAngleInput = 30
                frameNo = ((int(self.currentFrameNo/(widthAngleInput))+1)*widthAngleInput)
                self.handInputSystem.evaluateInputAngle(self.currentFrameNo)
                self.videoPlaybackWidget.moveToFrame(frameNo)
            elif key == QtCore.Qt.Key_Z:
                widthAngleInput = 30
                frameNo = ((int(self.currentFrameNo/(widthAngleInput))-1)*widthAngleInput)
                if frameNo < 0:
                    frameNo = 0
                self.videoPlaybackWidget.moveToFrame(frameNo)

            elif key == QtCore.Qt.Key_R:
                self.graphicsViewResized()
            elif key == QtCore.Qt.Key_Control:
                self.moveSceneRegionFlag = True
            elif key == QtCore.Qt.Key_A:
                #self.inputGraphicsView.translate(-10,0)
                if self.moveSceneRegion.topLeft().x()-10 < 0:
                    return
                """
                self.moveSceneRegion.moveTopLeft(QPoint(self.moveSceneRegion.topLeft().x()-10,
                                                    self.moveSceneRegion.topLeft().y()))
                self.moveSceneRegion.moveBottomRight(QPoint(self.moveSceneRegion.bottomRight().x()-10,
                                                            self.moveSceneRegion.bottomRight().y()))
                """
                self.moveSceneRegion.moveTo(QPoint(self.moveSceneRegion.topLeft().x()-10,
                                                   self.moveSceneRegion.topLeft().y()))
                self.inputGraphicsView.fitInView(QRectF(self.moveSceneRegion),
                                                 QtCore.Qt.KeepAspectRatio)
                #print("A",self.moveSceneRegion.bottomRight(),self.moveSceneRegion,self.moveSceneRegion.bottomRight().x()-10)
            elif key == QtCore.Qt.Key_D:
                self.moveSceneRegion.moveTopLeft(QPoint(self.moveSceneRegion.topLeft().x()+10,
                                                        self.moveSceneRegion.topLeft().y()))
                self.inputGraphicsView.fitInView(QRectF(self.moveSceneRegion),
                                                 QtCore.Qt.KeepAspectRatio)
                #print("D",self.moveSceneRegion)
            elif key == QtCore.Qt.Key_W:
                self.moveSceneRegion.moveTopLeft(QPoint(self.moveSceneRegion.topLeft().x(),
                                                        self.moveSceneRegion.topLeft().y()-10))
                self.inputGraphicsView.fitInView(QRectF(self.moveSceneRegion),
                                                 QtCore.Qt.KeepAspectRatio)
                #print("W",self.moveSceneRegion)
            elif key == QtCore.Qt.Key_S:
                self.moveSceneRegion.moveTopLeft(QPoint(self.moveSceneRegion.topLeft().x(),
                                                        self.moveSceneRegion.topLeft().y()+10))
                self.inputGraphicsView.fitInView(QRectF(self.moveSceneRegion),
                                                 QtCore.Qt.KeepAspectRatio)
                #print("S",self.moveSceneRegion)
            elif key == QtCore.Qt.Key_P:
                self.handInputSystem.save("a.csv")

    def setScale(self,viewScaleRate,mousePosition):
        viewScaleRate *= 0.1
        sceneRect = self.inputGraphicsView.sceneRect()
        scene = self.inputGraphicsView.scene()
        sceneRect = scene.sceneRect()
        posXY = sceneRect.bottomRight()
        x,y = posXY.x(),posXY.y()
        wX,wY = int(x/(1.0*viewScaleRate)),int(y/(1.0*viewScaleRate))
        
        wX_half,wY_half = int(wX*0.5),int(wY*0.5)
        mouseX,mouseY = mousePosition.x(),mousePosition.y()
        viewRect = QtCore.QRect(0,0,wX_half,wY_half)
        print(viewScaleRate,posXY,mouseX,mouseY)
        viewRect.moveCenter(QPoint(mouseX,mouseY))
        
        self.moveSceneRegion = viewRect
        self.inputGraphicsView.scale(1/self.lastViewScaleRate,1/self.lastViewScaleRate)
        self.inputGraphicsView.scale(viewScaleRate,viewScaleRate)
        self.lastViewScaleRate = viewScaleRate
        self.inputGraphicsView.translate(mouseX,mouseY)
   
        self.inputGraphicsView.fitInView(QRectF(viewRect),QtCore.Qt.KeepAspectRatioByExpanding)#KeepAspectRatio)
        #self.inputGraphicsView.viewport().update()
        ###self.updateInputGraphicsView()


    def overlayCheckBoxStateChanged(self, s):
        if self.overlayCheckBox.isChecked():
            self.frameBufferItemGroup.show()
        else:
            self.frameBufferItemGroup.hide()

        self.updateInputGraphicsView()

    def polyLineCheckBoxStateChanged(self, s):
        overlayFrameNo = self.frameNoSpinBox.value()

        min_value = max(self.currentFrameNo-overlayFrameNo,0)
        current_pos = self.currentFrameNo - min_value

        if self.trackingPathGroup is not None:
            self.trackingPathGroup.setDrawItem(current_pos, self.circleCheckBox.isChecked())
            self.trackingPathGroup.setDrawLine(self.lineCheckBox.isChecked())

            self.updateInputGraphicsView()

    def radiusSpinBoxValueChanged(self, value):
        if self.trackingPathGroup is not None:
            self.trackingPathGroup.setRadius(self.radiusSpinBox.value())
            self.updateInputGraphicsView()

    def frameNoSpinBoxValueChanged(self, value):
        if self.trackingPathGroup is not None:
            self.trackingPathGroup.setOverlayFrameNo(self.frameNoSpinBox.value())
            self.updateInputGraphicsView()

    def dragEnterEvent(self,event):
        event.acceptProposedAction()

    def dropEvent(self,event):
        # event.setDropAction(QtCore.Qt.MoveAction)
        mime = event.mimeData()
        if mime.hasUrls():
            urls = mime.urls()
            if len(urls) > 0:
                self.processDropedFile(urls[0].toLocalFile())

        event.acceptProposedAction()

    def processDropedFile(self,filePath):
        root,ext = os.path.splitext(filePath)
        if ext == ".filter":
            # Read Filter
            self.openFilterFile(filePath=filePath)
            return
        elif ext == ".csv":
            self.openCSVFile(filePath=filePath)
        elif self.openImageFile(filePath=filePath):
            return
        elif self.openVideoFile(filePath=filePath):
            return

    def videoPlaybackInit(self):
        self.videoPlaybackWidget.hide()
        self.videoPlaybackWidget.frameChanged.connect(self.setFrame, Qt.QueuedConnection)

    def setFrame(self, frame, frameNo):
        if frame is not None:
            if frameNo%(self.frameWidth) == self.frameWidth-1:
                frameNo = int(frameNo/(self.frameWidth))*self.frameWidth
                self.videoPlaybackWidget.moveToFrame(frameNo)

            self.cv_img = frame
            self.currentFrameNo = frameNo
            
            self.updateInputGraphicsView()
            self.evaluate()

    def imgInit(self):
        self.cv_img = cv2.imread(os.path.join(sampleDataPath,"color_filter_test.png"))


        self.frameBuffer = Queue()
        self.frameBufferItemGroup = QGraphicsItemGroup()
        self.frameBufferItemGroup.hide()
        self.inputPixmapRenderScene = QGraphicsScene()
        self.inputPixmapRenderScene.addItem(self.frameBufferItemGroup)

        self.inputScene = QGraphicsScene()
        self.inputGraphicsView.setScene(self.inputScene)
        self.inputGraphicsView.resizeEvent = self.graphicsViewResized
        # self.inputScene.addItem(self.frameBufferItemGroup)

        qimg = misc.cvMatToQImage(self.cv_img)
        self.inputPixmap = QPixmap.fromImage(qimg)
        self.inputPixmapItem = QGraphicsPixmapItem(self.inputPixmap)
        self.inputScene.addItem(self.inputPixmapItem)

        self.inputGraphicsView.viewport().installEventFilter(self)

        self.inputGraphicsView.setMouseTracking(False)
        self.overlayScene = QGraphicsScene()
        self.inputGraphicsView.setOverlayScene(self.overlayScene)

        self.zoomedGraphicsView.setScene(self.inputScene)
        self.zoomedGraphicsView.setOverlayScene(self.overlayScene)


    def inputGraphicsViewMousePressEvent(self, event):
        
        if event.modifiers() == QtCore.Qt.ShiftModifier:
            # Comment out to permit the view for sending the event to the child scene.
            QGraphicsView.mousePressEvent(self.inputGraphicsView, event)
        #elif event.button() & QtCore.Qt.RightButton:
        #QGraphicsView.mousePressEvent(self.inputGraphicsView, event)
        else:
            if event.button() & QtCore.Qt.RightButton:
                self.drawing = False
            else:
                self.drawing = True

        


    def inputGraphicsViewMouseMoveEvent(self, event):
        if event.modifiers() == QtCore.Qt.ShiftModifier:
            # Comment out to permit the view for sending the event to the child scene.
            QGraphicsView.mouseMoveEvent(self.inputGraphicsView, event)
            return
        
        if self.drawing == False:
            return
        if self.moveSceneRegionFlag == True:
            print("MoveRegion")
            mousePosition = self.inputGraphicsView.mapToScene(QPoint(event.pos()))
            self.inputGraphicsView.translate(1,0)

            return
        else:
            pass

        pos = self.inputGraphicsView.mapToScene(QPoint(event.pos()))
        A = np.array([pos.x(),pos.y()])
        mousePosition = A
        self.handInputSystem.inputMouseMoveEvent(mousePosition)
        

    def inputGraphicsViewMouseReleaseEvent(self, event):
        if event.modifiers() == QtCore.Qt.ShiftModifier:
            # Comment out to permit the view for sending the event to the child scene.
            QGraphicsView.mouseReleaseEvent(self.inputGraphicsView, event)
            return
        
        if self.drawing == True:
            self.drawing = False
        else:
            return
        if self.moveSceneRegionFlag == True:
            self.moveSceneRegionFlag = False

        self.setCursor(QtCore.Qt.ArrowCursor)
        self.handInputSystem.inputMouseReleaseEvent()
        self.inputGraphicsView.viewport().update()
        
    def menuInit(self):
        self.actionSaveCSVFile.triggered.connect(self.saveCSVFile)
        self.actionOpenCSVFile.triggered.connect(self.openCSVFile)

    def openVideoFile(self, activated=False, filePath = None):
        if filePath is None:
            filePath, _ = QFileDialog.getOpenFileName(None, 'Open Video File', userDir)

        if len(filePath) is not 0:
            self.filePath = filePath

            ret = self.videoPlaybackWidget.openVideo(filePath)
            if ret == False:
                return False

            self.videoPlaybackWidget.show()
            self.updateInputGraphicsView()

            self.evaluate()

            # self.evaluate()

            return True
        else:
            return False

    def openImageFile(self, activated=False, filePath = None):
        if filePath == None:
            filePath, _ = QFileDialog.getOpenFileName(None, 'Open Image File', userDir)

        if len(filePath) is not 0:
            self.filePath = filePath
            img = cv2.imread(filePath)
            if img is None:
                return False

            self.cv_img = img
            self.videoPlaybackWidget.hide()
            self.updateInputGraphicsView()

            self.evaluate()

            return True
        else:
            return False

    def openCSVFile(self, activated=False, filePath=None):
        if filePath is None:
            filePath, _ = QFileDialog.getOpenFileName(None, 'Open CSV File', userDir, 'CSV files (*.csv)')

        if len(filePath) is not 0:
            self.df = pd.read_csv(filePath, index_col=0)

            if self.trackingPathGroup is not None:
                self.inputScene.removeItem(self.trackingPathGroup)

            self.trackingPathGroup = TrackingPathGroup()
            self.trackingPathGroup.setRect(self.inputScene.sceneRect())
            #self.inputScene.addItem(self.trackingPathGroup)

            self.trackingPathGroup.setDataFrame(self.df)

            self.evaluate()

    def saveCSVFile(self, activated=False, filePath = None):
        if self.df is not None:
            filePath, _ = QFileDialog.getSaveFileName(None, 'Save CSV File', userDir, "CSV files (*.csv)")

            if len(filePath) is not 0:
                logger.debug("Saving CSV file: {0}".format(filePath))
                self.handInputSystem.save(filePath)
                #self.handInputSystem.save("./a.csv")

    def updateInputGraphicsView(self):
        ##print("update")
        # self.inputScene.clear()
        self.inputScene.removeItem(self.inputPixmapItem)
        qimg = misc.cvMatToQImage(self.cv_img)
        self.inputPixmap = QPixmap.fromImage(qimg)

        p = QPainter(self.inputPixmap)
        sourceRect = self.inputPixmapRenderScene.sceneRect()
        self.inputPixmapRenderScene.render(p, QRectF(sourceRect), QRectF(sourceRect), QtCore.Qt.IgnoreAspectRatio)

        self.inputPixmapItem = QGraphicsPixmapItem(self.inputPixmap)
        rect = QtCore.QRectF(self.inputPixmap.rect())
        self.inputScene.setSceneRect(rect)
        self.inputScene.addItem(self.inputPixmapItem)

        self.inputGraphicsView.viewport().update()
        self.graphicsViewResized()

        

    def eventFilter(self, obj, event):
        if obj is self.inputGraphicsView.viewport() and event.type()==QEvent.Wheel:
            return True
        else:
            return False

    def graphicsViewResized(self, event=None):
        #print("resize")
        #print(self.inputScene)
        self.viewScaleRate = 5
        self.inputGraphicsView.fitInView(QtCore.QRectF(self.inputPixmap.rect()), QtCore.Qt.KeepAspectRatio)
        self.moveSceneRegion = QtCore.QRectF(self.inputPixmap.rect())

    def evaluate(self):
        if not self.videoPlaybackWidget.isOpened():
            return

        qimg = misc.cvMatToQImage(self.cv_img)
        pixmapItem = QGraphicsPixmapItem(QPixmap.fromImage(qimg))
        pixmapItem.setOpacity(0.2)

        self.frameBuffer.put(pixmapItem)
        self.frameBufferItemGroup.addToGroup(pixmapItem)
        if self.frameBuffer.qsize() > 10:
            item = self.frameBuffer.get()
            self.frameBufferItemGroup.removeFromGroup(item)

        if self.trackingPathGroup is not None:
            self.trackingPathGroup.setPoints(self.currentFrameNo)
        if self.handInputSystem is not None:
            pass
            self.handInputSystem.setPoint(self.currentFrameNo)

        #if self.ellipseItem is not None:
        #scene = self.inputScene
        #self.ellipseItem.setRect(scene.sceneRect())

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = Ui_MainWindow(currentDirPath)
    MainWindow.setWindowIcon(QIcon(':/icon/icon.ico'))
    MainWindow.show()
    sys.exit(app.exec_())
