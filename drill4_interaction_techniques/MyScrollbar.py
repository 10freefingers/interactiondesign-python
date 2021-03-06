# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore
from MyMarker import MyMarker


class MyScrollbar(QtGui.QScrollBar):
    def __init__(self, ui):
        QtGui.QScrollBar.__init__(self)
        self.pixmap = QtGui.QLabel()
        self.overlay = None
        self.setMouseTracking(True)
        self.current_position = 0
        self.current_marker = 0
        self.cursor_pos = 0
        self.rect_visualization_w = 35
        self.rect_visualization_h = 35
        self.markers = []
        self.visualizations = {}
        self.ui = ui
        self.counter = 0

    def mousePressEvent(self, event):
        QtGui.QScrollBar.mousePressEvent(self, event)
        self.cursor_pos = event.pos()

    def updatePosition(self, value):
        self.current_position = value

        ratio = self.ui.height() / self.ui.scene.sceneRect().height()
        for k, v in self.visualizations.iteritems():
            y_relative = self.value() + v.y_absolute * ratio
            value = y_relative - v.rect().y()
            v.setPos(0, value)
            v.update()

    def setMarker(self):
        index = None
        try:
            index = self.markers.index(self.current_position)
            self.removeMarkers(index)
        except ValueError:
            index = None
        if index is None:
            self.markers.append(self.current_position)
            self.visualizeMarker(self.current_position)

    def sortMarkers(self):
        return sorted(self.markers, key=int, reverse=True)

    def removeMarkers(self, index):
        marker = self.markers.pop(index)
        self.ui.scene.removeItem(self.visualizations[marker])
        del self.visualizations[marker]
        self.ui.update()

    def visualizeMarker(self, marker):
        if (self.ui is not None) and (self.ui.scene is not None):
            y_absolute = marker + self.cursor_pos.y()
            ratio = self.ui.height() / self.ui.scene.sceneRect().height()
            y_relative = self.value() + y_absolute * ratio

            rect_marker = QtCore.QRectF(
                self.ui.window_width - self.rect_visualization_w,
                y_relative, self.rect_visualization_w,
                self.rect_visualization_h)

            tmp_rect = MyMarker(rect_marker, y_absolute)
            tmp_rect.saveScreenshot(
                self.makeScreenshot(), self.ui.scene.sceneRect())
            tmp_rect.setCursor(QtCore.Qt.PointingHandCursor)
            tmp_rect.setAcceptHoverEvents(True)
            tmp_rect.setZValue(1)
            self.visualizations[marker] = tmp_rect

            qobject = self.visualizations[marker].getQObject()
            self.connect(qobject, QtCore.SIGNAL(
                "markerEntered"), self.markerEntered)
            self.connect(qobject, QtCore.SIGNAL(
                "markerLeft"), self.markerLeft)

            self.ui.scene.addItem(self.visualizations[marker])
            self.ui.update()

    def makeScreenshot(self):
        return QtGui.QPixmap.grabWindow(self.ui.winId())

    def getNextMaker(self, index=None):
        next_marker = None
        if index is None:
            markers_asc = self.sortMarkers()
            if len(markers_asc) > 0:
                for i in range(0, len(markers_asc)):
                    if markers_asc[i] < self.current_position:
                        next_marker = markers_asc[i]
                        return next_marker
                next_marker = markers_asc[0]
        else:
            index -= 1
            if index < len(self.markers):
                next_marker = self.markers[index]
        return next_marker

    def isMarkerClicked(self, pos):
        value = None
        for k, v in self.visualizations.iteritems():
            tmp_pos = QtCore.QPoint(0, 0)
            tmp_pos.setX(pos.x())
            tmp_pos.setY(pos.y() + (v.y() * -1))
            if v.rect().contains(tmp_pos) is True:
                self.markerLeft()
                value = k
                break
        return value

    def markerEntered(self, marker):
        screenshot = marker.getScreenshot()
        self.overlay = self.ui.scene.addRect(QtCore.QRectF(
            0, self.current_position, self.ui.width(), self.ui.height()),
            pen=QtGui.QPen(QtCore.Qt.NoPen),
            brush=QtGui.QBrush(QtGui.QColor(200, 200, 200, alpha=194)))
        self.pixmap = self.ui.scene.addPixmap(screenshot)
        self.pixmap.setOffset(self.ui.width() / 2, self.value())
        self.ui.update()

    def markerLeft(self):
        self.ui.scene.removeItem(self.overlay)
        self.ui.scene.removeItem(self.pixmap)
        self.ui.update()
