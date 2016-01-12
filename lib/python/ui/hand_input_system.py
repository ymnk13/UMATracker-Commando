#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsItem, QGraphicsItemGroup, QGraphicsPixmapItem, QGraphicsEllipseItem, QFrame, QFileDialog, QPushButton, QGraphicsObject, QMenu, QAction
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPolygonF, QColor
from PyQt5.QtCore import QPoint, QPointF, QRectF, pyqtSlot, QObject

import numpy as np
import pandas as pd

import scipy.interpolate as interpolate
from functools import cmp_to_key
from .tracking_path import TrackingPath
#from .rotatable_ellipse import RotatableArrowObject
from .rotatable_ellipse import RotatableEllipseData,RotatableEllipse
class HandInputSystem(QGraphicsObject):
    def __init__(self,parent = None):
        super(HandInputSystem,self).__init__(parent)

        self.setZValue(1000)
        self.rect = QRectF()
        self.df = pd.DataFrame({"x0":[],"y0":[],
                                "VX0_0":[],"VY0_0":[],
                                "VX1_0":[],"VY1_0":[],
                                "depth_0":[]})

        self.currentFrameNo = 0
        self.frameWidth = 30*5

        self.inputedPoints = interpolateLine([[]])
        self.trackingPath = None
        self.inputedTrackingPath = None

        self.ellipseItem = None
        self.editingOriginData = None
        self.frameWidthAngle = 30

    def setPoint(self,currentFrameNo):
        #currentFrameNo = 1
        if self.ellipseItem == None:
            self.ellipseItem = RotatableEllipseData(None)
            
            scene = self.scene()
            scene.addItem(self.ellipseItem)
            self.ellipseItem.setPoints([[100,100],[200,150]])
            self.ellipseItem.setAngle(0*np.pi/180.0,True)
            self.ellipseItem.hide()
        currentFrameData = self.df.loc[currentFrameNo:currentFrameNo]
        dataIndex = 0
        indexMapper = self.generateIndexMapper(dataIndex)
        if len(currentFrameData) is 0:
            return False
        currentFrameData = self.df.iloc[currentFrameNo]
        self.editingOriginData = currentFrameData.copy()
        if np.isnan(currentFrameData[indexMapper['x']]) and\
           np.isnan(currentFrameData[indexMapper['y']]):
            self.ellipseItem.hide()
            return False
        else:
            # View Initial Ellipse
            # position is known
            self.ellipseItem.setDataFrame(currentFrameData,indexMapper)
            self.ellipseItem.show()
            return True
    def generateIndexMapper(self,dataNumber):
        dataIndex = dataNumber
        indexMapper = {'x':'x{0}'.format(dataIndex),
                       'y':'y{0}'.format(dataIndex),
                       'VX0':'VX0_{0}'.format(dataIndex), #major
                       'VY0':'VY0_{0}'.format(dataIndex),
                       'VX1':'VX1_{0}'.format(dataIndex), #minor
                       'VY1':'VY1_{0}'.format(dataIndex),
                       'depth':'depth_{0}'.format(dataIndex)}
        return indexMapper
    def setDepth(self,currentFrameNo,depth):
        currentFrameData = self.df.loc[currentFrameNo:currentFrameNo]
        dataIndex = 0
        indexMapper = self.generateIndexMapper(dataIndex)
        if len(currentFrameData) is 0:
            return False
        index = range(currentFrameNo+1,currentFrameNo+self.frameWidthAngle+2)
        currentFrameData = self.df.iloc[currentFrameNo]
        #[currentFrameData[indexMapper['depth']]
        d = {
            indexMapper['depth']:np.array([depth]*30)
        }
        # index制限を行うべき
        index = range(currentFrameNo,currentFrameNo+30)
        
        df1 = pd.DataFrame(d,index = index)
        print(df1)
        self.df = df1.combine_first(self.df)

    def saveAngleDataToNextFrame(self,currentFrameNo,flag = True):
        currentFrameData = self.df.loc[currentFrameNo:currentFrameNo]
        dataIndex = 0
        indexMapper = self.generateIndexMapper(dataIndex)
        if len(currentFrameData) is 0:
            return False
        currentFrameData = self.df.iloc[currentFrameNo]
        nextFrameData = self.df.iloc[currentFrameNo+1]
        if flag == True:
            nextFrameData[indexMapper['x']] = currentFrameData[indexMapper['x']]
            nextFrameData[indexMapper['y']] = currentFrameData[indexMapper['y']]
        nextFrameData[indexMapper['VX0']] = currentFrameData[indexMapper['VX0']]
        nextFrameData[indexMapper['VX1']] = currentFrameData[indexMapper['VX1']]
        nextFrameData[indexMapper['VY0']] = currentFrameData[indexMapper['VY0']]
        nextFrameData[indexMapper['VY1']] = currentFrameData[indexMapper['VY1']]
        nextFrameData[indexMapper['depth']] = currentFrameData[indexMapper['depth']]

    def evaluateInputAngle(self,currentFrameNo):
        firstFrame = int(currentFrameNo/(self.frameWidth))*self.frameWidth
        endFrame = (int(currentFrameNo/(self.frameWidth))+1)*self.frameWidth
        print("EvaluateInputAngle",firstFrame,endFrame)
        # SemiAuto input angle data
        index = range(currentFrameNo+1,currentFrameNo+self.frameWidthAngle+2)
        dataNumber = 0
        dataMap = self.generateIndexMapper(dataNumber)
        currentFrameData = self.df.iloc[currentFrameNo]
        diffVector = np.array([currentFrameData[dataMap['x']],
                               currentFrameData[dataMap['y']]])-\
                     np.array([self.editingOriginData[dataMap['x']],
                               self.editingOriginData[dataMap['y']]])
        
        X = self.df.loc[currentFrameNo+1:currentFrameNo+self.frameWidthAngle+1,dataMap['x']].as_matrix()
        Y = self.df.loc[currentFrameNo+1:currentFrameNo+self.frameWidthAngle+1,dataMap['y']].as_matrix()
        X+=diffVector[0]
        Y+=diffVector[1]
        N = currentFrameNo+self.frameWidthAngle+1-(currentFrameNo+1)+1
        # TODO: 移動角度で補完をおこなう
        d = {
            dataMap['VX0']:np.array([currentFrameData[dataMap['VX0']]]*N),
            dataMap['VX1']:np.array([currentFrameData[dataMap['VX1']]]*N),
            dataMap['VY0']:np.array([currentFrameData[dataMap['VY0']]]*N),
            dataMap['VY1']:np.array([currentFrameData[dataMap['VY1']]]*N),
            dataMap['depth']:np.array([currentFrameData[dataMap['depth']]]*N),
        }
        df1 = pd.DataFrame(d,index = index)
        self.df = df1.combine_first(self.df)

    def clearTrackingPath(self):
        scene = self.scene()
        if not self.trackingPath == None:
            scene.removeItem(self.trackingPath)
            self.trackingPath = None


    def inputMouseMoveEvent(self, mousePosition):
        if mousePosition[0] <0:
            return
        if mousePosition[1] < 0:
            return
        if not len(self.inputedPoints[-1]) == 0:
            lastInputedPosition = self.inputedPoints[-1][-1]
            distance = np.linalg.norm(mousePosition-lastInputedPosition)
            if  distance > 10:
                self.inputedPoints[-1].append(mousePosition)
        else:
            self.inputedPoints[-1].append(mousePosition)

    def inputMouseReleaseEvent(self):
        if len(self.inputedPoints[-1]) < 2:
            del self.inputedPoints[-1]
            return 
        self.viewInterpolatedPath()
        if not self.inputedPoints[-1] == []:
            self.inputedPoints.append([])

    def viewInterpolatedPath(self):
        scene = self.scene()
        if not self.trackingPath == None:
            scene.removeItem(self.trackingPath)
        tmp_new = self.inputedPoints.calcInterpolateLine()

        self.trackingPath = TrackingPath(None)
        self.trackingPath.setColor([255,0,0])
        self.trackingPath.setLineWidth(1)
        flags = np.full(len(tmp_new), False, dtype=np.bool)
        self.trackingPath.setPoints(tmp_new,flags)
        
        self.trackingPath.setRect(scene.sceneRect())
        scene.addItem(self.trackingPath)        

    def deleteLastInputLine(self):
        if self.inputedPoints.len() > 1:
            del self.inputedPoints[-2]
            self.viewInterpolatedPath()
            self.inputedPoints.append([])
            self.inputMouseReleaseEvent()

    def saveInputedLine(self,currentFrameNo):
        firstFrame = int(currentFrameNo/(self.frameWidth))*self.frameWidth
        endFrame = (int(currentFrameNo/(self.frameWidth))+1)*self.frameWidth
        print("saveInputedLine",firstFrame,endFrame)
        tmp_new = self.inputedPoints.calcInterpolateLine()
        a = np.array([tmp_new])
        if len(tmp_new) is not 0:
            axis = ['x{0}', 'y{0}'] # Save Line
            d = dict((axe.format(i), a[i,:,j]) for i in range(a.shape[0]) for axe,j in zip(axis, range(2)))
            # d = {x0:[],y0:}
            index = range(firstFrame,endFrame)
            df1 = pd.DataFrame(d,index = index)
            self.df = df1.combine_first(self.df)
        if not self.trackingPath == None:
            scene = self.scene()
            scene.removeItem(self.trackingPath)
            self.trackingPath = None
            self.inputedPoints.clear()

    

    def setDataFrame(self,currentFrameNo):
        frameNo = currentFrameNo
        min_value = frameNo
        max_value = frameNo+self.frameWidth-1
        scene = self.scene()
        if not self.inputedTrackingPath == None:
            
            scene.removeItem(self.inputedTrackingPath)
            self.inputedTrackingPath = None
        min_value = frameNo
        max_value = frameNo+self.frameWidth
        array = self.df.loc[min_value:max_value,('x0','y0')].as_matrix()
        flags = np.full(len(array), False, dtype=np.bool)

        if not self.inputedTrackingPath == None:
            scene.removeItem(self.inputedTrackingPath)
            self.inputedTrackingPath = None

        if len(array) <= 0:
            return

        self.inputedTrackingPath = TrackingPath(None)
        self.inputedTrackingPath.setColor([0,0,255])
        self.inputedTrackingPath.setLineWidth(1)
        self.inputedTrackingPath.setPoints(array,flags)
        self.inputedTrackingPath.setRect(scene.sceneRect())
        scene.addItem(self.inputedTrackingPath)
        self.inputedPoints.clear()

        self.inputedPoints.clear()

    def save(self,filePath):
        df = self.df.copy()
        inputElementN = 6
        col_n = int(df.as_matrix().shape[1]/inputElementN)

        """
        col_names = np.array([('x{0}'.format(i),
                               'y{0}'.format(i),
                               'VX0_{0}'.format(i),
                               'VY0_{0}'.format(i),
                               'VX1_{0}'.format(i),
                               'VY1_{0}'.format(i),
                               'depth_{0}'.format(i)) for i in range(int(round(col_n)))]).flatten()
        """
        #df.columns = pd.Index(col_names)
        print(df)
        df.to_csv(filePath)


    def setPoints(self,frameNo = None):
        pass
    def setRect(self,rect):
        self.rect = rect
    def paint(self, painter, option, widget):
        pass




class interpolateLine:
    # http://stackoverflow.com/questions/27698604/what-do-the-different-values-of-the-kind-argument-mean-in-scipy-interpolate-inte
    def __init__(self,A = [],inputWidth = 150):
        super(interpolateLine,self).__init__()
        self.pointLists = A
        self.interpolateLine = []
        self.inputWidth = inputWidth
    def calcInterpolateLine(self):
        print(self.pointLists)
        self.sortedRawPoints()
        time_new = np.linspace(0,150,150)
        tmp = np.array([i for item in self.pointLists for i in item])
        time_old = np.linspace(0,150,len(tmp))
        if len(tmp) <= 0:
            return []
        X = tmp[:,0]
        Y = tmp[:,1]
        mode = 'slinear'
        X_new = interpolate.interp1d(time_old,X,kind = mode)(time_new)
        Y_new = interpolate.interp1d(time_old,Y,kind = mode)(time_new)
        tmp_new = np.dstack([X_new,Y_new])[0]
        self.interpolateResult = tmp_new
        return tmp_new

    def sortedRawPoints(self):
        def sortComp(X,Y):
            if len(X) < 2 or len(Y) < 2:
                return False
            topBottom = np.sum(list(map(lambda XX:np.linalg.norm(XX),(np.array(X[:2])-np.array(Y[-2:])))))
            bottomTop = np.sum(list(map(lambda XX:np.linalg.norm(XX),(np.array(X[-2:])-np.array(Y[:2])))))
            if topBottom < bottomTop:
                return True
            return False
        self.pointLists = sorted(self.pointLists, key=cmp_to_key(sortComp))
        return True

    def getInterpolateLine(self):
        return self.interpolateLine
    def getRawPoints(self):
        return self.pointLists
    def clear(self):
        self.pointLists = [[]]
        self.interpolateLine = []
    def append(self,item):
        self.pointLists.append(item)
    def len(self):
        return len(self.pointLists)
    def __delitem__(self, key):
        #self.pointLists.__delattr__(key)
        del self.pointLists[key]
    def __getitem__(self, key):
        if len(self.pointLists) == 0:
            self.pointLists.append([])
        return self.pointLists[key]
    def __setitem__(self, key, value):
        self.pointLists[key] =  value
    def __str__(self):
        return str(self.pointLists)


def main():
    A = interpolateLine([
        [[220,100],[220,110],[230,110]],
        [[200,100],[200,110],[210,110]],
        [[210,110],[215,110],[220,110]],
    ])
    A.sortedRawPoints()
    A.calcInterpolateLine()
    


if __name__  == "__main__":
    main()
