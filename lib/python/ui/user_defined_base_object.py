#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QGraphicsObject

from PyQt5.QtWidgets import QGraphicsItem
from PyQt5.QtCore import QRectF, QPointF
from PyQt5.QtCore import Qt
import copy
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QTransform
import numpy as np

class ResizableGraphicsObject(QGraphicsObject):
    geometryChange = pyqtSignal(object)

    def __init__(self, parent=None):
        super(ResizableGraphicsObject, self).__init__(parent)
        self.setZValue(1000)

        self.mouseIsPressed = None

        self.setFlags(QGraphicsItem.ItemIsSelectable |
                      QGraphicsItem.ItemIsFocusable |
                      QGraphicsItem.ItemIsMovable |
                      QGraphicsItem.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)

        self._buttonList = {}
        self.setFocus(Qt.ActiveWindowFocusReason)

        self.rotationAngle = 0
    def setAngle(self,angle):
        self.rotationAngle = angle
        rad = self.rotationAngle
        rotationMatrix = QTransform(np.cos(rad),np.sin(rad),-np.sin(rad),np.cos(rad)
                                    ,0.0,0.0)
        
        self.setTransform(rotationMatrix)

    def setMove(self,pos):
        rad = -1*self.rotationAngle
        A = self._rect.center()
        B = [np.cos(-rad)*A.x()-np.sin(-rad)*A.y(),
             np.sin(-rad)*A.x()+np.cos(-rad)*A.y()]
        C = [B[0]+pos[0],B[1]+pos[1]]
        D = [np.cos(rad)*C[0]-np.sin(rad)*C[1],
             np.sin(rad)*C[0]+np.cos(rad)*C[1]]
        self._rect.moveCenter(QPointF(D[0],D[1]))
        """
        rotationMatrix = QTransform(np.cos(rad),np.sin(rad),-np.sin(rad),np.cos(rad)
                                    ,pos[0],pos[1])
        
        self.setTransform(rotationMatrix)
        """

    def setPoints(self, points):
        self.points = points
        rect = QRectF(QPointF(*points[0]), QPointF(*points[1]))
        self.setRect(rect)

    def setRect(self, rect):
        self._rect = rect
        self._boundingRect = rect

    def prepareGeometryChange(self):
        top = self._rect.topLeft()
        bottom = self._rect.bottomRight()
        self.geometryChange.emit([[top.x(), top.y()], [bottom.x(), bottom.y()]])
        super(ResizableGraphicsObject, self).prepareGeometryChange()

    def hoverMoveEvent(self, event):
        hoverMovePos = event.scenePos()
        mouseHoverArea = None
        for item in self._buttonList:
            if self._buttonList[item].contains(hoverMovePos):
                mouseHoverArea = item
                break
        if mouseHoverArea:
            self.setCursor(QtCore.Qt.PointingHandCursor)
            return
        self.setCursor(QtCore.Qt.SizeAllCursor)
        super(ResizableGraphicsObject, self).hoverMoveEvent(event)

    def hoverEnterEvent(self, event):
        self.setCursor(QtCore.Qt.SizeAllCursor)
        super(ResizableGraphicsObject, self).hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.setCursor(QtCore.Qt.ArrowCursor)
        super(ResizableGraphicsObject, self).hoverLeaveEvent(event)

    def mousePressEvent(self, event):
        self.mouseIsPressed = True
        self.mousePressPos = event.scenePos()
        self.rectPress = copy.deepcopy(self._rect)
        self.mousePressArea = None
        for item in self._buttonList:
            if self._buttonList[item].contains(self.mousePressPos):
                print("Hit")
                self.mousePressArea = item
                break
        
        #super(ResizableGraphicsObject, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        #self.setAngle(-1*self.rotationAngle)
        """
        self.setX(self._rect.center().x())
        self.setY(self._rect.center().y())
        
        self.setAngle(self.rotationAngle)
        """
        self.mouseIsPressed = False
        self.updateResizeHandles()
        self.prepareGeometryChange()
        super(ResizableGraphicsObject, self).mouseReleaseEvent(event)

    def paint(self, painter, option, widget):
        self.updateResizeHandles()

        self.draw(painter, option, widget, self._rect)
        for item in self._buttonList:
            painter.drawRect(self._buttonList[item])

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
            if self.mousePressArea == 'topRect':
                self._rect.setTop(
                        self.rectPress.y() - (self.mousePressPos.y() - mouseMovePos.y())
                        )
            elif self.mousePressArea == 'bottomRect':
                self._rect.setBottom(
                        self.rectPress.bottom() - (self.mousePressPos.y() - mouseMovePos.y())
                        )
            elif self.mousePressArea == 'leftRect':
                self._rect.setLeft(
                        self.rectPress.left() - (self.mousePressPos.x() - mouseMovePos.x())
                        )
            elif self.mousePressArea == 'rightRect':
                self._rect.setRight(
                        self.rectPress.right() - (self.mousePressPos.x() - mouseMovePos.x())
                        )
            elif self.mousePressArea == 'topleftRect':
                self._rect.setTopLeft(
                        self.rectPress.topLeft() - (self.mousePressPos - mouseMovePos)
                        )
            elif self.mousePressArea == 'toprightRect':
                self._rect.setTopRight(
                        self.rectPress.topRight() - (self.mousePressPos - mouseMovePos)
                        )
            elif self.mousePressArea == 'bottomleftRect':
                self._rect.setBottomLeft(
                        self.rectPress.bottomLeft() - (self.mousePressPos - mouseMovePos)
                        )
            elif self.mousePressArea == 'bottomrightRect':
                self._rect.setBottomRight(
                        self.rectPress.bottomRight() - (self.mousePressPos - mouseMovePos)
                        )
            elif self.mousePressArea == 'topRotation':
                rectCenter = self._rect.center()
                pressedPos = self.mousePressPos
                #mouseMovePos
                A = (pressedPos-rectCenter)
                B = (mouseMovePos-rectCenter)
                pro = A.x()*B.x()+A.y()*B.y()
                theta = np.arctan2(A.x()*B.y()-A.y()*B.x(),pro)
                #theta = self.rotationAngle+theta
                self._rect.moveCenter(QPointF(0,0))
                #
                self.setAngle(theta)
                pos = self.rectPress.center()
                rad = self.rotationAngle
                self._rect.moveCenter(QPointF(pos.x()*np.cos(rad)-np.sin(rad)*pos.y(),
                                      pos.x()*np.sin(rad)+np.cos(rad)*pos.y()))
                #print("RotationBegginn")
            else:
                #pos = self.mousePressPos - mouseMovePos
                pos = self.rectPress.center() - (self.mousePressPos- mouseMovePos)
                rad = -1*self.rotationAngle
                deltaPos = (self.mousePressPos- mouseMovePos)
                self._rect.moveCenter(QPointF(
                    self.rectPress.center().x()-(np.cos(rad)*deltaPos.x()-np.sin(rad)*deltaPos.y()),
                    self.rectPress.center().y()-(np.sin(rad)*deltaPos.x()+np.cos(rad)*deltaPos.y())
                ))

        self.updateResizeHandles()
        self.prepareGeometryChange()

    def updateResizeHandles(self):
        self.resizeHandleSize = 4.0
        self._rect = self._rect.normalized()

        # FIXME:結構アドホック，複数のビューでシーンを表示してるときには問題が出る．
        views = self.scene().views()
        self.offset = self.resizeHandleSize * (views[0].mapToScene(1, 0).x() - views[0].mapToScene(0, 1).x())
        D = 2
        self._boundingRect = self._rect.adjusted(
                -self.offset*D,
                -self.offset*D,
                self.offset*D,
                self.offset*D
            )
        
        self._buttonList["topRect"] = QRectF(
                self._rect.center().x(),
                self._boundingRect.topLeft().y()+self.offset,
                D*self.offset,
                D*self.offset
            )
        self._buttonList["bottomRect"] = QRectF(
                self._rect.center().x(),
                self._rect.bottom()-self.offset,
                D*self.offset,
                D*self.offset
            )
        self._buttonList["leftRect"] = QRectF(
                self._rect.x()-self.offset,
                self._rect.center().y()-self.offset,
                D*self.offset,
                D*self.offset
            )
        self._buttonList["rightRect"] = QRectF(
                self._rect.right()-self.offset,
                self._rect.center().y()-self.offset,
                D*self.offset,
                D*self.offset
            )
        self._buttonList["topleftRect"] = QRectF(
                self._boundingRect.topLeft().x()+self.offset,
                self._boundingRect.topLeft().y()+self.offset,
                D*self.offset,
                D*self.offset
            )
        self._buttonList["toprightRect"] = QRectF(
                self._boundingRect.topRight().x()-3*self.offset,
                self._boundingRect.topRight().y()+self.offset,
                D*self.offset,
                D*self.offset
            )
        self._buttonList["bottomleftRect"] = QRectF(
                self._boundingRect.bottomLeft().x()+self.offset,
                self._boundingRect.bottomLeft().y()-3*self.offset,
                D*self.offset,
                D*self.offset
            )
        self._buttonList["bottomrightRect"] = QRectF(
                self._boundingRect.bottomRight().x()-self.offset*3,
                self._boundingRect.bottomRight().y()-self.offset*3,
                D*self.offset,
                D*self.offset
            )
        self._buttonList["topRotation"] = QRectF(
            self._boundingRect.center().x(),
            self._boundingRect.top()-self.offset,
            D*self.offset,
            D*self.offset
        )

def main():
    pass

if __name__ == "__main__":
    main()
    
