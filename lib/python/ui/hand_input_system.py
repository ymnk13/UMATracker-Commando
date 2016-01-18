#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsItem, QGraphicsItemGroup, QGraphicsPixmapItem, QGraphicsEllipseItem, QFrame, QFileDialog, QPushButton, QGraphicsObject, QMenu, QAction
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPolygonF, QColor, QCursor
from PyQt5.QtCore import QPoint, QPointF, QRectF, pyqtSlot, QObject

import numpy as np
import pandas as pd

import scipy.interpolate as interpolate
from functools import cmp_to_key
from .tracking_path import TrackingPath
from .rotatable_ellipse import RotatableEllipseData,RotatableEllipse
from scipy import interpolate

class HandInputSystem(QGraphicsObject):
    def __init__(self,parent = None):
        super(HandInputSystem,self).__init__(parent)
        self.setZValue(1000)
        self.rect = QRectF()
        """
        self.df = pd.DataFrame({"x0":[],"y0":[],
                                "VX0_0":[],"VY0_0":[],
                                "VX1_0":[],"VY1_0":[],
                                "depth_0":[]})
        """
        self.df = pd.DataFrame()
        self.dataFrameNo = -1
        self.editingNo = 0
        self.lastInputedFrameIndex = {}
        self.currentFrameNo = 0
        self.itemList = []
        self.drawItemFlag = True
        
        """
        df = pd.DataFrame([[100,200]],columns = ["x0","y0"],index = [10])
        self.df = df.combine_first(self.df)
        df = pd.DataFrame([[100,200]],columns = ["x0","y0"],index = [10])

        self.df = df.combine_first(self.df)
        self.df.loc[100] = [200,100]
        #print(self.df.loc[100]['x0'])
        """
        """
        print(self.df.loc[100:100,('x0','y0')])
        self.df.loc[100:100,('x0','y0')] = [500,200]
        print(self.df.loc[100:100,('x0','y0')])
        """

        """
        self.workingNo += 1
        self.addNewDataFrame(self.workingNo)
        """

        #print(self.df.iloc[0])
        #self.df.concat([[100,100],["x0","y0"]])
        #data = data.append(pd.dataFrame([1,2,3,4,5],columns=["A","B","C","D","E"],index=data[-1:].index+1))
        self.positionStack = {}
    

    def inputMouseMoveEvent(self,mousePosition,currentFrameNo):
        mapper = self.generateIndexMapper(self.editingNo)
        #self.positionStack[currentFrameNo] = mousePosition
        #print(currentFrameNo)
        #self.positionStack.append(mousePosition)
        """
        df = pd.DataFrame([mousePosition],columns = [mapper['x'],mapper['y']],index = [currentFrameNo])
        self.df = df.combine_first(self.df)
        print(currentFrameNo)
        """

    def inputMouseReleaseEvent(self):
        mapper = self.generateIndexMapper(self.editingNo)
        mouses = np.array(list(self.positionStack.values()))
        if len(mouses) is 0:
            return
        data = {
            mapper['x']:mouses[:,0],
            mapper['y']:mouses[:,1]
        }
        dataIndex = list(self.positionStack.keys())
        df = pd.DataFrame(data,index = dataIndex)
        self.df = df.combine_first(self.df)
        #self.df.insert(df)
        print(self.df)
        lastInputedFrameNum = self.lastInputedFrameIndex[self.editingNo]
        print("BB",self.lastInputedFrameIndex[self.editingNo],min(dataIndex))
        if self.lastInputedFrameIndex[self.editingNo] == min(dataIndex)-1:
            print("AA",self.lastInputedFrameIndex[self.editingNo])
            self.lastInputedFrameIndex[self.editingNo] = max(dataIndex)
            self.positionStack = {}            
            return False
        else:
            newDataIndex = range(lastInputedFrameNum,min(dataIndex))
            A = self.df.ix[lastInputedFrameNum+1:min(dataIndex)-1]
            X_new,Y_new = [],[]
            time_new = []
            if A.empty:
                ## 補完
                
                if lastInputedFrameNum == 0:
                    time_old = range(min(dataIndex),min(dataIndex)+6)
                    time_new = list(range(lastInputedFrameNum,min(dataIndex)))
                    data = self.df.ix[min(dataIndex):min(dataIndex)+5].as_matrix()
                    X,Y = data[:,0],data[:,1]
                    A = np.array([time_old,np.ones(len(time_old))])
                    A = A.T
                    # X
                    a,b = np.linalg.lstsq(A,X)[0]
                    time_new = np.array(time_new)
                    X_new = a*time_new+b
                    # Y
                    a,b = np.linalg.lstsq(A,Y)[0]
                    time_new = np.array(time_new)
                    Y_new = a*time_new+b
                    tmp_new = np.dstack([X_new,Y_new])[0]
                    
                else:
                    time_old = list(range(min(dataIndex),min(dataIndex)+6))+\
                               list(range(lastInputedFrameNum-6,lastInputedFrameNum))
                    time_new = list(range(lastInputedFrameNum+1,min(dataIndex)))
                    data0 = self.df.ix[min(dataIndex):min(dataIndex)+5].as_matrix()
                    data1 = self.df.ix[lastInputedFrameNum-5:lastInputedFrameNum].as_matrix()
                    
                    data = np.r_[data0,data1]
                    X,Y = data[:,0],data[:,1]
                    mode = 'slinear'
                    X_new = interpolate.interp1d(time_old,X,kind = mode)(time_new)
                    Y_new = interpolate.interp1d(time_old,Y,kind = mode)(time_new)
            self.lastInputedFrameIndex[self.editingNo] = max(dataIndex)
            data = {
                mapper['x']:X_new,
                mapper['y']:Y_new
            }
            df = pd.DataFrame(data,index = time_new)
            self.df = df.combine_first(self.df)
            print(self.df)
        
        self.positionStack = {}
        #self.addNewDataFrame()
        return True
    def setPoints(self,frameNo = None):
        if frameNo is not None:
            self.currentFrameNo = frameNo
        self.overlayFrameNo = 30
        min_value = max(self.currentFrameNo - self.overlayFrameNo, 0)
        max_value = self.currentFrameNo + self.overlayFrameNo
        pos = self.currentFrameNo - min_value
        
        for i, item in enumerate(self.itemList):
            mapper = self.generateIndexMapper(i)
            array = self.df.loc[min_value:max_value, (mapper['x'],mapper['y'])].as_matrix()
            if len(array) is 0:
                continue
            
            flags = np.full(len(array), False, dtype=np.bool)
            if self.drawItemFlag and pos < len(array):
                flags[pos] = True

            item.setPoints(array, flags)

    def nextDataFrame(self):
        print("NextDataFrame")
        if self.editingNo <= self.dataFrameNo-1:
            self.editingNo+=1
        else:
            self.addNewDataFrame()
            self.editingNo+=1
        self.setEditingLastValidFrameNo()
        
    def setEditingLastValidFrameNo(self):
        #
        mapper = self.generateIndexMapper(self.editingNo)
        firstValidIndex = self.df[mapper['x']].last_valid_index()
        if firstValidIndex is None:
            firstValidIndex = 0
        self.lastInputedFrameIndex[self.editingNo] = firstValidIndex
        
    def getLastInputedFrameIndex(self):
        return self.lastInputedFrameIndex[self.editingNo]

    def previousDataFrame(self):
        if self.editingNo > 0:
            self.editingNo-=1
        #print(self.df,self.editingNo)
        self.setEditingLastValidFrameNo()

    def addNewDataFrame(self):
        workingNo = self.dataFrameNo+1
        mapper = self.generateIndexMapper(workingNo)
        df = pd.DataFrame(dict(zip(mapper.values(),[[] for i in range(len(mapper.values()))])))
        self.df = self.df.append(df)
        self.dataFrameNo+=1
        self.lastInputedFrameIndex[self.dataFrameNo] = 0

        #
        scene = self.scene()
        """
        if scene is not None:
            for item in self.itemList:
                scene.removeItem(item)
                del item
        self.itemList.clear()
        """
        rgb = (255,0,0)
        rgb = np.random.randint(0, 255, (1, 3)).tolist()[0]
        trackingPath = TrackingPath(self)
        trackingPath.setRect(scene.sceneRect())
        trackingPath.setColor(rgb)
        trackingPath.setLineWidth(14)
        #trackingPath.setRadius(10)
        #trackingPath.itemSelected.connect(self.itemSelected)
        
        self.itemList.append(trackingPath)



    def appendPosition(self,mousePosition,frameNo = None):
        if frameNo is not None:
            self.currentFrameNo = frameNo
        self.positionStack[self.currentFrameNo] = mousePosition

    def generateIndexMapper(self,dataNumber):
        dataIndex = dataNumber
        indexMapper = {'x':'x{0}'.format(dataIndex),'y':'y{0}'.format(dataIndex),
        }
        """
                       'VX0':'VX0_{0}'.format(dataIndex), #major
                       'VY0':'VY0_{0}'.format(dataIndex),
                       'VX1':'VX1_{0}'.format(dataIndex), #minor
                       'VY1':'VY1_{0}'.format(dataIndex),
                       'depth':'depth_{0}'.format(dataIndex)}
        """
        return indexMapper

    def saveCSV(self,filePath):
        df = self.df.copy()
        N = len(self.generateIndexMapper(0).keys())
        col_n = df.as_matrix().shape[1]/N
        col_names = np.array([('x{0}'.format(i),
                               'y{0}'.format(i)) for i in range(int(round(col_n)))]).flatten()
        df.columns = pd.Index(col_names)
        df.to_csv(filePath)
    def setDataFrame(self,df):
        mapper = self.generateIndexMapper(0)
        columnNum = len(mapper.values())
        shape = df.shape
        self.dataFrameNo = int(shape[1]/columnNum)-1
        self.editingNo = 0
        self.df = df
        self.setEditingLastValidFrameNo()

        scene = self.scene()
        
        if scene is not None:
            for item in self.itemList:
                scene.removeItem(item)
                del item
        self.itemList.clear()

        for i in range(self.dataFrameNo+1):
            print(i)
            rgb = np.random.randint(0, 255, (1, 3)).tolist()[0]
            trackingPath = TrackingPath(self)
            trackingPath.setRect(scene.sceneRect())
            trackingPath.setColor(rgb)
            trackingPath.setLineWidth(14)
            #trackingPath.setRadius(10)
            #trackingPath.itemSelected.connect(self.itemSelected)
            self.itemList.append(trackingPath)

        
    def setRect(self, rect):
        self.rect = rect
    def boundingRect(self):
        return self.rect
    def paint(self, painter, option, widget):
        pass
        
    


def main():
    pass

if __name__  == "__main__":
    main()
