from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from datetime import datetime
import sys

   

class ButtonInfo(object):
    def __init__(self, time,query,type,x=0, y=0, w=0, h=0, is_toggled=False):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.type = type
        self.is_toggled = is_toggled
        self.time = time
        self.query = query
    
    def setXY(self,x,y):
        self.x=x
        self.y=y

    def setWH(self,w,h):
        self.w=w
        self.h=h

    def isToggled(self,b):
        self.is_toggled = b
    
    def setTime(self,time):
        self.time=time
    

class Bar(QtWidgets.QWidget):

    clickedButton = QtCore.Signal(ButtonInfo)

    def __init__(self,  *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding,
            QtWidgets.QSizePolicy.MinimumExpanding
        )

        self.unselected = 'images\icons8-100--60.png'
        self.selected = 'images\icons8-filled-circle-90.png'
        self.list_of_timestamps = []


    def paintEvent(self, e):
        painter = QtGui.QPainter(self)

        margin = 50
        begin_x = margin
        begin_y = 0
        
        begin_circle = QPixmap('images\icons8-circle-50.png')
        painter.drawPixmap(begin_x/2, begin_y,begin_circle.width()/2,begin_circle.height()/2,begin_circle)


        end_circle = begin_circle
        end_x = painter.device().width()-margin
        end_y = begin_y
        end_w = end_circle.width()/2
        end_h = end_circle.height()/2
        painter.drawPixmap(end_x, end_y,end_w,end_h,end_circle)

        brush = QtGui.QBrush()
        brush.setColor(QtGui.QColor('black'))
        brush.setStyle(Qt.SolidPattern)
        self.begin_rect = (begin_circle.width()/2.2)+begin_x/2
        self.width_rect = ((painter.device().width()-margin)-end_circle.width()+5)
        rect = QtCore.QRect(self.begin_rect ,begin_circle.height()/4.7,self.width_rect  , 8)
        painter.fillRect(rect, brush)

        painter.drawText(begin_x/2, begin_y+45, "00:00")
        painter.drawText(end_x, begin_y+45, "23:59")


        for time in self.list_of_timestamps:
            icon = self.unselected
            if time.is_toggled: 
                icon = self.selected
            time_circle = QPixmap(icon)
            time_x = self._get_time_line_translated(time.time)
            time_y = begin_y
            time.setXY(time_x,time_y)
            time.setWH(end_w,end_h)
            painter.drawPixmap(time_x, time_y,time.w,time.h,time_circle)



        painter.end()

    def sizeHint(self):
        return QtCore.QSize(750, 50)

    def _add_timestamp(self, time,ty,query=None):
        new = ButtonInfo(time=time,type=ty, query = query)
        print(new)
        self.list_of_timestamps.append(new)
        self.update()
    
    def reset_time_stamps(self):
        self.list_of_timestamps.clear()

    def _get_time_line_translated(self, time):
        percentage_time = self._get_time_percentage(time)
        zero_percent = self.begin_rect
        hundred_percent = self.begin_rect+self.width_rect
        x = ((percentage_time * (hundred_percent-zero_percent)) / 100)+zero_percent
        """ print("percentage_time ",percentage_time)
        print("zero_percent ",zero_percent)
        print("hundred_percent ",hundred_percent)
        print("x ",x) """
        return x

    def _get_time_percentage(self,input_datetime):
        return (input_datetime.msecsSinceStartOfDay() / 86_400_0)


    def _calculate_clicked_value(self, e):
        activated =""
        for i in self.list_of_timestamps:
            if i.x < e.x() and (i.x+i.w) > e.x():
                activated = i
                i.isToggled(True)
        for i in self.list_of_timestamps:
            if(i != activated):
                i.isToggled(False)

        self.update()
        self.clickedButton.emit(activated)


    def mousePressEvent(self, e):
        self._calculate_clicked_value(e)


class Timeline(QtWidgets.QWidget):

    colorChanged = QtCore.Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        layout = QtWidgets.QVBoxLayout()

        self.timeedit = QTimeEdit()
        self.timeedit.setTime(QTime.currentTime())
        self.label = QLabel("")

        self._bar = Bar(self.timeedit, self.label)

        layout.addWidget(self._bar)


        
        self.add_button = QPushButton("Add Time")
        self.add_button.clicked.connect(self._bar._add_timestamp)


        


        
        layout.addWidget(self.timeedit)
        layout.addWidget(self.add_button)
        layout.addWidget(self.label)

        self.setLayout(layout)

    def __getattr__(self, name):
        if name in self.__dict__:
            return self[name]

        #return getattr(self._dial, name)


    def setColor(self, color):
        self._bar.steps = [color] * self._bar.n_steps
        self._bar.update()

    def setColors(self, colors):
        self._bar.n_steps = len(colors)
        self._bar.steps = colors
        self._bar.update()

    def setBarPadding(self, i):
        self._bar._padding = int(i)
        self._bar.update()

    def setBarSolidPercent(self, f):
        self._bar._bar_solid_percent = float(f)
        self._bar.update()

    def setBackgroundColor(self, color):
        self._bar._background_color = QtGui.QColor(color)
        self._bar.update()
