#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QGraphicsObject

from PyQt5.QtWidgets import QGraphicsItem
from PyQt5.QtCore import QRectF, QPointF
from PyQt5.QtCore import Qt
import copy
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QColor
import math
from .movable_arrow import MovableArrow
import numpy as np

def ang(v1, v2):
    ## numpy is Dangerous
    A = -1*(math.atan2(v2[1],v2[0])-math.atan2(v1[1],v1[0]))
    if A < 0:
        A = A+np.pi*2
    return A


class RotatableArrowObject(QGraphicsObject):
    #geometryChange = pyqtSignal(object)

    def __init__(self, parent=None):
        super(RotatableArrowObject, self).__init__(parent)
        self.setZValue(2)

        self.mouseIsPressed = None

        self.setFlags(QGraphicsItem.ItemIsSelectable |
                      QGraphicsItem.ItemIsFocusable |
                      QGraphicsItem.ItemIsMovable |
                      QGraphicsItem.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)

        self.setFocus(Qt.ActiveWindowFocusReason)

        self.rotationAngle = 0#np.pi/4

        self.majorAxis = None
        self.minorAxis = None


    def setPoints(self, points):
        scene = self.scene()
        if self.majorAxis is not None and self.minorAxis is not None:
            if scene is not None:
                scene.removeItem(self.majorAxis)
                scene.removeItem(self.minorAxis)
                self.minorAxis = None
                self.majorAxis = None

        self.points = points
        rect = QRectF(QPointF(*points[0]), QPointF(*points[1]))
        self.setRect(rect)

        self.majorAxis = MovableArrow()
        T = self._rect.center()
        self.majorAxis.begin = np.array([T.x(),T.y()])
        self.majorAxis.end = np.array([T.x()+self._rect.width()*0.5,T.y()])
        self.minorAxis = MovableArrow()
        T = self._rect.center()
        self.minorAxis.begin = np.array([T.x(),T.y()])
        self.minorAxis.end = np.array([T.x(),T.y()-self._rect.height()*0.5])
        self.minorAxis.angleFixedFlag = True


        self.majorAxis.mousePressEvent = self.generateItemMousePressEvent(self.majorAxis)
        self.majorAxis.mouseMoveEvent = self.generateItemMouseMoveEvent(self.majorAxis)
        self.minorAxis.mousePressEvent = self.generateItemMousePressEvent(self.minorAxis)
        self.minorAxis.mouseMoveEvent = self.generateItemMouseMoveEvent(self.minorAxis)

        self.majorAxis.setObjectName("major")
        self.minorAxis.setObjectName("minor")

        self.majorAxis.setColor((255,0,0))
        self.minorAxis.setColor((0,0,255))

        scene = self.scene()

        scene.addItem(self.majorAxis)
        scene.addItem(self.minorAxis)

    def hide(self):
        self.majorAxis.hide()
        self.minorAxis.hide()
        super(RotatableArrowObject, self).hide()
    
    def show(self):
        self.majorAxis.show()
        self.minorAxis.show()
        self.update()
        self.prepareGeometryChange()
        super(RotatableArrowObject, self).show()
    
    def generateItemMouseMoveEvent(self,item):
        def itemMouseMoveEvent(event):
            MovableArrow.mouseMoveEvent(item,event)
            objName = item.objectName
            if objName == "major":
                # set the width of the _rect
                majorWidth = 2*np.linalg.norm(self.majorAxis.end-self.majorAxis.begin)
                self._rect.setWidth(majorWidth)
                self._rect.moveCenter(QPointF(*self.majorAxis.begin))
                self.setRect(self._rect)
                # set the minor Axis
                D = np.linalg.norm(self.minorAxis.end-self.minorAxis.begin)
                T = (self.majorAxis.end-self.majorAxis.begin)
                rad90 = 90.0*np.pi/180.0
                endMajorPoint = np.array([np.cos(rad90)*T[0]-np.sin(rad90)*T[1],
                                          np.sin(rad90)*T[0]+np.cos(rad90)*T[1]])
                endMajorPoint = endMajorPoint/np.linalg.norm(endMajorPoint)
                endMajorPoint = np.array([D*endMajorPoint[0],
                                          D*endMajorPoint[1]])
                
                self.minorAxis.end = -1*endMajorPoint+self.minorAxis.begin
                # get Angle
                rad = ang(T,np.array([1,0]))
                self.setAngle(rad)

            elif objName == "minor":
                norm = 2*np.linalg.norm(self.minorAxis.end-self.minorAxis.begin)
                self._rect.setHeight(norm)
                self._rect.moveCenter(QPointF(*self.majorAxis.begin))
                self.setRect(self._rect)
            self.prepareGeometryChange()
            self.update()
        return itemMouseMoveEvent

    def generateItemMousePressEvent(self,item):
        def itemMousePressEvent(event):
            MovableArrow.mousePressEvent(item,event)
        return itemMousePressEvent

    def setAngle(self,angle,flag = False):
        self.rotationAngle = angle
        if self.minorAxis is not None and \
           self.majorAxis is not None and flag == True:
            #print(self.majorAxis.begin)
            rad = self.rotationAngle
            majorVect = self.majorAxis.getVector()
            norm = np.linalg.norm(majorVect)
            T = np.array([np.cos(rad)*majorVect[0]-np.sin(rad)*majorVect[1],
                          np.sin(rad)*majorVect[0]+np.cos(rad)*majorVect[1]])
            self.majorAxis.end = T+self.majorAxis.begin

            # set the minor Axis
            D = np.linalg.norm(self.minorAxis.end-self.minorAxis.begin)
            T = (self.majorAxis.end-self.majorAxis.begin)
            rad90 = 90.0*np.pi/180.0
            endMajorPoint = np.array([np.cos(rad90)*T[0]-np.sin(rad90)*T[1],
                                      np.sin(rad90)*T[0]+np.cos(rad90)*T[1]])
            endMajorPoint = endMajorPoint/np.linalg.norm(endMajorPoint)
            endMajorPoint = np.array([D*endMajorPoint[0],
                                      D*endMajorPoint[1]])
            
            self.minorAxis.end = -1*endMajorPoint+self.minorAxis.begin
            self.update()
    def setRect(self, rect):
        self._rect = rect
        self._boundingRect = rect

    def prepareGeometryChange(self):
        #top = self._rect.topLeft()
        #bottom = self._rect.bottomRight()
        #self.geometryChange.emit([[top.x(), top.y()], [bottom.x(), bottom.y()]])
        super(RotatableArrowObject, self).prepareGeometryChange()

    def hoverMoveEvent(self, event):
        hoverMovePos = event.scenePos()
        mouseHoverArea = None
        self.setCursor(QtCore.Qt.SizeAllCursor)
        super(RotatableArrowObject, self).hoverMoveEvent(event)

    def hoverEnterEvent(self, event):
        self.setCursor(QtCore.Qt.SizeAllCursor)
        super(RotatableArrowObject, self).hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.setCursor(QtCore.Qt.ArrowCursor)
        super(RotatableArrowObject, self).hoverLeaveEvent(event)

    def mousePressEvent(self, event):
        self.mouseIsPressed = True
        self.mousePressPos = event.scenePos()
        self.rectPress = copy.deepcopy(self._rect)
        self.mousePressArea = None
        super(RotatableArrowObject, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.mouseIsPressed = False
        self.updateResizeHandles()
        self.prepareGeometryChange()
        super(RotatableArrowObject, self).mouseReleaseEvent(event)

    def paint(self, painter, option, widget):
        self.updateResizeHandles()
        self.draw(painter, option, widget, self._rect)
        self.majorAxis.paint(painter,option,widget)
        self.minorAxis.paint(painter,option,widget)
    def draw(self, painter, option, widget, rect):
        return

    def boundingRect(self):
        return self._boundingRect

    def shape(self):
        path = QtGui.QPainterPath()
        path.addRect(self.boundingRect())
        return path

    def mouseMoveEvent(self, event):
        mouseMovePos = event.scenePos()
        if self.mouseIsPressed:
            self._rect.moveCenter(
                self.rectPress.center() - (self.mousePressPos - mouseMovePos)
            )
        self.updatePosition()
        self.updateResizeHandles()
        self.prepareGeometryChange()
    def updatePosition(self):
        T = self._rect.center()
        majorVect = self.majorAxis.end-self.majorAxis.begin
        self.majorAxis.begin = np.array([T.x(),T.y()])
        self.majorAxis.end = self.majorAxis.begin+majorVect

        minorVect = self.minorAxis.end-self.minorAxis.begin
        self.minorAxis.begin = np.array([T.x(),T.y()])
        self.minorAxis.end = self.minorAxis.begin+minorVect


    def updateResizeHandles(self):
        self.resizeHandleSize = 4.0
        self._rect = self._rect.normalized()

        # FIXME:結構アドホック，複数のビューでシーンを表示してるときには問題が出る．
        views = self.scene().views()
        self.offset = self.resizeHandleSize * (views[0].mapToScene(1, 0).x() - views[0].mapToScene(0, 1).x())

        self._boundingRect = self._rect.adjusted(
            -self.offset*2,
            -self.offset*2,
            self.offset*2,
            self.offset*2
        )
        majorVec = self.majorAxis.end - self.majorAxis.begin
        minorVec = self.minorAxis.end - self.majorAxis.end
        xMax = np.max([np.abs(majorVec[0]),np.abs(minorVec[0])])
        yMax = np.max([np.abs(majorVec[1]),np.abs(minorVec[1])])
        D = 2
        x = self._rect.center().x()-xMax*D
        y = self._rect.center().y()-yMax*D
        w = xMax*D*2
        h = yMax*D*2
        #self._boundingRect = self._boundingRect.adjusted(0,0,w,h)
        self._boundingRect.setTopLeft(QPointF(x,y))
        self._boundingRect.setWidth(w)
        self._boundingRect.setHeight(h)
        
        

class RotatableEllipse(RotatableArrowObject):
    def __init__(self, parent=None):
        super(RotatableEllipse, self).__init__(parent)

    def draw(self, painter, option, widget, rect):
        painter.setPen(QtGui.QPen(QtCore.Qt.red, 0, QtCore.Qt.DashLine))
        painter.save()
        T = self._rect.center()
        painter.translate(T.x(),T.y())
        painter.rotate(self.rotationAngle*180.0/np.pi)
        painter.translate(-T.x(),-T.y())

        painter.drawEllipse(rect)
        painter.restore()
        painter.setPen(QtGui.QPen(QtCore.Qt.black, 0, QtCore.Qt.SolidLine))
        painter.drawRect(self.boundingRect())
        painter.setBrush(QtGui.QBrush(QtGui.QColor(255, 255, 255)))
        super(RotatableEllipse, self).draw(painter,option,widget,rect)
    def prepareGeometryChange(self):
        super(RotatableEllipse, self).prepareGeometryChange()

class RotatableEllipseData(RotatableArrowObject):
    def __init__(self,parent = None):
        super(RotatableEllipseData,self).__init__(parent)

    def setDataFrame(self,data,mapper):
        self.data = data
        self.indexMapper = mapper
        x = self.data[mapper['x']]
        y = self.data[mapper['y']]
        if np.isnan(self.data[self.indexMapper['VX0']]) and \
           np.isnan(self.data[self.indexMapper['VY0']]) and \
           np.isnan(self.data[self.indexMapper['VX1']]) and \
           np.isnan(self.data[self.indexMapper['VY1']]):
            self.data[mapper['VX0']] = 50
            self.data[mapper['VY0']] = 0
            self.data[mapper['VX1']] = 50
            self.data[mapper['VY1']] = 0
            self.data[mapper['depth']] = 0
            w = 100
            h = 100
            angle = 0
            self.setPoints([[x-w/2.0,y-h/2.0],[x+w/2.0,y+h/2.0]])
        else:
            # calc Angle  width height

            majorVect = np.array([self.data[mapper['VX0']],
                                  self.data[mapper['VY0']]])
            minorVect = np.array([self.data[mapper['VX1']],
                                  self.data[mapper['VY1']]])
            w = np.linalg.norm(majorVect)*2
            h = np.linalg.norm(minorVect)*2
            self.setPoints([[x-w/2.0,y-h/2.0],[x+w/2.0,y+h/2.0]])
            angle = ang(majorVect,np.array([1,0]))
            self.setAngle(angle,True)
        self.update()
    
    def draw(self, painter, option, widget, rect):
        painter.setPen(QtGui.QPen(QtCore.Qt.red, 0, QtCore.Qt.DashLine))
        painter.save()
        T = self._rect.center()
        painter.translate(T.x(),T.y())
        painter.rotate(self.rotationAngle*180.0/np.pi)
        painter.translate(-T.x(),-T.y())

        painter.drawEllipse(rect)
        painter.restore()
        painter.setPen(QtGui.QPen(QtCore.Qt.black, 0, QtCore.Qt.SolidLine))
        painter.drawRect(self.boundingRect())
        painter.setBrush(QtGui.QBrush(QtGui.QColor(255, 255, 255)))
        super(RotatableEllipseData,self).draw(painter,option,widget,rect)
    def prepareGeometryChange(self):
        mapper = self.indexMapper
        majorVect = self.majorAxis.getVector()
        self.data[mapper['VX0']] = majorVect[0]
        self.data[mapper['VY0']] = majorVect[1]
        minorVect = self.minorAxis.getVector()
        self.data[mapper['VX1']] = minorVect[0]
        self.data[mapper['VY1']] = minorVect[1]

        self.data[mapper['x']] = self.majorAxis.begin[0]
        self.data[mapper['y']] = self.majorAxis.begin[1]
        super(RotatableEllipseData,self).prepareGeometryChange()
        
def main():
    pass

if __name__ == "__main__":
    main()
    
