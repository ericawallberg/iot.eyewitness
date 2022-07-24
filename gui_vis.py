################################################################################
##                            IoT.EYEWITNESS                                  ##
##                             gui_vis.py                                     ##   
##  SCRIPT TO VISUALIZE THE DATA                                              ##
## "Usage: python gui_vis.py"                                                 ##
################################################################################
import sys
import folium
from PySide2 import QtWidgets
from PySide2 import QtCore
from PySide2 import QtGui
from PySide2.QtGui import QPainter
from PySide2.QtWidgets import (QMainWindow, QApplication) 
from PySide2.QtCharts import QtCharts as QtCharts
from PySide2.QtMultimedia import QMediaPlayer, QAudioOutput, QMediaPlaylist
import mysql.connector
from mysql.connector import Error
from functools import partial
from collapsiblebox import CollapsibleBox
from collections import defaultdict
import io
from PySide2.QtWebEngineWidgets import QWebEngineView
from timeline import Bar, ButtonInfo
import enum
from datetime import timedelta
from ui_interface import *
from utils import *

shadow_elements = { 
    "left_menu_frame",
    "frame_3",
    "header_frame",
    "frame_8"
}


class ArtifactType(enum.Enum):
    sleepStart = 0
    sleepFinish = 1
    heart_rate = 2 
    weight = 3 
    exercise = 4
    gps = 5
    activities = 6
    body =7


class MainWindow(QMainWindow):


    def __init__(self, parent=None):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()

        self.ui.setupUi(self)
 
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint) 

        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
      
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(20)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        
        self.ui.centralwidget.setGraphicsEffect(self.shadow)   

        self.setWindowIcon(QtGui.QIcon(":/icons/icons/pie-chart.svg"))
        self.setWindowTitle("Eye.Witness")

        QSizeGrip(self.ui.size_grip)

        self.ui.minimize_window_button.clicked.connect(lambda: self.showMinimized())
        self.ui.close_window_button.clicked.connect(lambda: self.close())
        self.ui.restore_window_button.clicked.connect(lambda: self.restore_or_maximize_window())
        
        self.ui.open_close_side_bar_btn.clicked.connect(lambda: self.slideLeftMenu())


        def moveWindow(e):
            if self.isMaximized() == False: #Not maximized
                if e.buttons() == Qt.LeftButton:  
                    #Move window 
                    self.move(self.pos() + e.globalPos() - self.clickPosition)
                    self.clickPosition = e.globalPos()
                    e.accept()


        self.ui.header_frame.mouseMoveEvent = moveWindow
        
        self.show()


        self.font = QFont()
        self.font.setFamily(u"NovaFlat")

        self.font1 = QFont()
        self.font1.setFamily(u"NovaFlat")
        self.font1.setBold(True)
        self.font1.setPointSize(50)

        for x in shadow_elements:
                effect = QtWidgets.QGraphicsDropShadowEffect(self)
                effect.setBlurRadius(18)
                effect.setXOffset(0)
                effect.setYOffset(0)
                effect.setColor(QColor(0, 0, 0, 255))  
                getattr(self.ui, x).setGraphicsEffect(effect) 


        #create the DB connection
        try:
            self.connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="pass",
                database="iot.eyewitness"
            )
            if self.connection.is_connected():
                db_Info = self.connection.get_server_info()
                print("Connected to MySQL Server version ", db_Info)
                self.cursor = self.connection.cursor()
                self.cursor.execute("select database();")
                record = self.cursor.fetchone()
                print("You're connected to database: ", record)
        except Error as e:
            print("Error while connecting to MySQL", e)


        self.create_left_menu()


    def restore_or_maximize_window(self):
        # If window is maxmized
        if self.isMaximized():
            self.showNormal()
            # Change Icon
            self.ui.restore_window_button.setIcon(QtGui.QIcon(u":/icons/icons/maximize-2.svg"))
        else:
            self.showMaximized()
            # Change Icon
            self.ui.restore_window_button.setIcon(QtGui.QIcon(u":/icons/icons/minimize-2.svg"))


    def slideLeftMenu(self):
        # Get current left menu width
        width = self.ui.left_menu_frame.width()

        # If minimized
        if width == 0:
            # Expand menu
            newWidth = 200
            self.ui.open_close_side_bar_btn.setIcon(QtGui.QIcon(u":/icons/icons/chevron-left.svg"))
        # If maximized
        else:
            # Restore menu
            newWidth = 0
            self.ui.open_close_side_bar_btn.setIcon(QtGui.QIcon(u":/icons/icons/align-center.svg"))

        # Animate the transition
        self.animation = QPropertyAnimation(self.ui.left_menu_frame, b"maximumWidth")#Animate minimumWidht
        self.animation.setDuration(550)
        self.animation.setStartValue(width)#Start value is the current menu width
        self.animation.setEndValue(newWidth)#end value is the new menu width
        self.animation.setEasingCurve(QtCore.QEasingCurve.OutBounce)
        self.animation.start()



    def mousePressEvent(self, event):
        # Get the current position of the mouse
        self.clickPosition = event.globalPos()
        # We will use this value to move the window


    def create_left_menu(self):

        query = "SELECT * FROM cases"
        self.cursor.execute(query)
        result = self.cursor.fetchall()

        rows=[]
        for row in result:
            rows.append(row[1])
            print(row)
        
        self.ui.scrollArea = QScrollArea(self.ui.frame_4)
        self.ui.scrollArea.setObjectName(u"scrollArea")
        self.ui.scrollArea.setWidgetResizable(True)
        self.ui.scrollArea.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.ui.scrollAreaWidgetContents = QWidget()
        self.ui.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.ui.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 0, 0)) 
       # self.ui.scrollAreaWidgetContents.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.ui.widget = QWidget(self.ui.scrollAreaWidgetContents)
        self.ui.widget.setObjectName(u"widget")
        self.ui.widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.ui.scrollArea.setWidget(self.ui.widget)
        self.ui.scrollArea.setWidgetResizable(True)
        self.ui.verticalLayout_17 = QVBoxLayout()
        self.ui.verticalLayout_17.setObjectName(u"verticalLayout_17")
        for i in result:
            box = CollapsibleBox(i[1])
            self.ui.verticalLayout_17.addWidget(box)
            lay = QVBoxLayout()
            
            format = "'{}_%'".format(i[0])
            artifacts = """SHOW TABLES LIKE %s""" % format
            self.cursor.execute(artifacts)
            result2 = self.cursor.fetchall()
            result2.append("Overview")


            for j in result2:
                if not j[0].endswith('exercise_profile') and not j[0].endswith('heart_rate_profile') and  not j[0].endswith('weight_profile') and not j[0].endswith('sleep') and not j[0].endswith('photos') and not j[0].endswith('sounds'):
                    if j != "Overview": 
                        label = QPushButton(j[0][2:])
                        label.clicked.connect(partial(self.assign_handle, j[0][j[0].rfind('_')+1:],j[0], result2))
                    else: 
                        label = QPushButton(j)
                        label.setStyleSheet("background-color : darkred")
                        label.clicked.connect(partial(self.assign_handle, j,j,result2))
                    
                    
                    lay.addWidget(label)
                
            
            box.setContentLayout(lay)
            lay.addStretch()

        self.ui.verticalLayout_17.addStretch()
        

        self.ui.verticalLayout_18.addLayout(self.ui.verticalLayout_17)
        self.ui.verticalLayout_16.addWidget(self.ui.widget)

        self.ui.scrollArea.setWidget(self.ui.scrollAreaWidgetContents)
        self.ui.verticalLayout_3.addWidget(self.ui.scrollArea)

    @QtCore.Slot(str)
    def assign_handle(self, text,table_name,all_tables_case):
        print(text)
        if text == "activities":
            self.activities(table_name)
        if text == "body":
            self.body(table_name)
        if text == "sleep":
            self.sleep(table_name)
        if text == "foods":
            self.foods(table_name)
        if text == "gps":
            self.GPS(table_name)
        if text == "profile":
            self.profile(table_name)
        """ if text == "sounds":
            self.sounds(table_name) """
        if text == "Overview":
            self.overview(all_tables_case)


    def activities(self,table_name):
        self.ui.label_11.setText("ACTIVITIES")
        self.deleteLayout(self.ui.frame_8.layout())

        #set the tabs
        self.tabWidget = QTabWidget(self.ui.frame_8)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setEnabled(True)
        self.tabWidget.setStyleSheet(u"color: rgb(0, 0, 0);")
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.tab.setStyleSheet(u"")
        self.gridLayout_7 = QGridLayout(self.tab)
        self.gridLayout_7.setSpacing(0)
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.gridLayout_7.setContentsMargins(0, 0, 0, 0)
        self.frame = QFrame(self.tab)
        self.frame.setObjectName(u"frame")
        sizePolicy2 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy2)
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.gridLayout_5 = QGridLayout(self.frame)
        self.gridLayout_5.setSpacing(0)

        self.widget_2 = QWidget(self.frame)
        self.widget_2.setObjectName(u"widget_2")
        self.label_3 = QLabel("label",self.widget_2)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(100, 60, 47, 13))
        self.label_3.setStyleSheet(u"background-color: rgb(0, 0, 0);\n"
"color: rgb(255, 255, 255);")

        self.gridLayout_5.addWidget(self.create_line_chart(  "Calories_Burned", table_name), 0, 0, 1, 1)

        self.gridLayout_5.addWidget(self.create_line_chart(  "Steps", table_name), 0, 1, 1, 1)

        self.gridLayout_5.addWidget(self.create_line_chart(  "Distance", table_name), 1, 0, 1, 1)

        self.gridLayout_5.addWidget(self.create_line_chart(  "Floors", table_name), 1, 1, 1, 1)

        self.gridLayout_7.addWidget(self.frame, 0, 0, 1, 1)

        self.tabWidget.addTab(self.tab, "")

        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")

        self.gridLayout_8 = QGridLayout(self.tab_2)
        self.gridLayout_8.setSpacing(0)
        self.gridLayout_8.setObjectName(u"gridLayout_8")
        self.gridLayout_8.setContentsMargins(0, 0, 0, 0)
        self.frame1 = QFrame(self.tab_2)
        self.frame1.setObjectName(u"frame1")
        sizePolicy3 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.frame1.sizePolicy().hasHeightForWidth())
        self.frame1.setSizePolicy(sizePolicy3)
        self.frame1.setFrameShape(QFrame.StyledPanel)
        self.frame1.setFrameShadow(QFrame.Raised)
        self.gridLayout_6 = QGridLayout(self.frame1)
        self.gridLayout_6.setSpacing(0)

        self.widget_2 = QWidget(self.frame1)
        self.widget_2.setObjectName(u"widget_2")
        self.label_3 = QLabel("label",self.widget_2)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(100, 60, 47, 13))
        self.label_3.setStyleSheet(u"background-color: rgb(0, 0, 0);\n"
"color: rgb(255, 255, 255);")

        #add the graphs
        self.gridLayout_6.addWidget(self.create_line_chart(  "Minutes_Sedentary",table_name), 0, 0, 1, 1)

        self.gridLayout_6.addWidget(self.create_line_chart(  "Minutes_Lightly_Active",table_name), 0, 1, 1, 1)

        self.gridLayout_6.addWidget(self.create_line_chart(  "Minutes_Fairly_Active",table_name), 1, 0, 1, 1)

        self.gridLayout_6.addWidget(self.create_line_chart(  "Minutes_Very_Active",table_name), 1, 1, 1, 1)

        self.gridLayout_8.addWidget(self.frame1, 0, 0, 1, 1)


        self.tabWidget.addTab(self.tab_2, "")

        self.ui.verticalLayout_4.addWidget(self.tabWidget)

        self.tabWidget.setCurrentIndex(0)

        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("MainWindow", u"Overview", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("MainWindow", u"Minutes", None))
     
    def populateFrame(self):
        self.deleteLayout(self.frame.layout())
        layout = QtGui.QVBoxLayout(self.frame)

    def deleteLayout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.deleteLayout(item.layout())
            #sip.delete(layout)

    def body(self,table_name):
        self.ui.label_11.setText("BODY")
        self.deleteLayout(self.ui.frame_8.layout())

        self.tabWidgetBody = QTabWidget(self.ui.frame_8)
        self.tabWidgetBody.setEnabled(True)
        self.tabWidgetBody.setStyleSheet(u"color: rgb(0, 0, 0);")
        self.tabBody = QWidget()
        self.gridLayout_7Body = QGridLayout(self.tabBody)
        self.gridLayout_7Body.setSpacing(0)
        self.gridLayout_7Body.setContentsMargins(0, 0, 0, 0)
        self.frameBody = QFrame(self.tabBody)
        self.frameBody.setObjectName(u"frame")
        sizePolicy2Body = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy2Body.setHorizontalStretch(0)
        sizePolicy2Body.setVerticalStretch(0)
        sizePolicy2Body.setHeightForWidth(self.frameBody.sizePolicy().hasHeightForWidth())
        self.frameBody.setSizePolicy(sizePolicy2Body)
        self.frameBody.setFrameShape(QFrame.StyledPanel)
        self.frameBody.setFrameShadow(QFrame.Raised)
        self.gridLayout_5Body = QGridLayout(self.frameBody)
        self.gridLayout_5Body.setSpacing(0)

        self.widget_2Body = QWidget(self.frameBody)
        self.label_3Body = QLabel("label",self.widget_2Body)
        self.label_3Body.setObjectName(u"label_3")
        self.label_3Body.setGeometry(QRect(100, 60, 47, 13))
        self.label_3Body.setStyleSheet(u"background-color: rgb(0, 0, 0);\n"
"color: rgb(255, 255, 255);")

        self.gridLayout_5Body.addWidget(self.create_line_chart(  "Weight",table_name), 0, 0, 1, 1)

        self.gridLayout_5Body.addWidget(self.create_line_chart(  "BMI",table_name), 0, 1, 1, 1)

        self.gridLayout_5Body.addWidget(self.create_line_chart(  "Fat",table_name), 1, 0, 1, 1)

        self.gridLayout_7Body.addWidget(self.frameBody, 0, 0, 1, 1)

        self.tabWidgetBody.addTab(self.tabBody, "")

        

        self.ui.verticalLayout_4.addWidget(self.tabWidgetBody)

        self.tabWidgetBody.setCurrentIndex(0)

        self.tabWidgetBody.setTabText(self.tabWidgetBody.indexOf(self.tabBody), QCoreApplication.translate("MainWindow", u"Overview", None))
        
    def sleep(self,table_name):
        self.ui.label_11.setText("SLEEP")
        self.deleteLayout(self.ui.frame_8.layout())

        self.tabWidgetSleep = QTabWidget(self.ui.frame_8)
        self.tabWidgetSleep.setObjectName(u"tabWidget")
        self.tabWidgetSleep.setEnabled(True)
        self.tabWidgetSleep.setStyleSheet(u"color: rgb(0, 0, 0);")
        self.tabSleep = QWidget()
        self.tabSleep.setObjectName(u"tab")
        self.tabSleep.setStyleSheet(u"")
        self.gridLayout_7Sleep = QGridLayout(self.tabSleep)
        self.gridLayout_7Sleep.setSpacing(0)
        self.gridLayout_7Sleep.setObjectName(u"gridLayout_7")
        self.gridLayout_7Sleep.setContentsMargins(0, 0, 0, 0)
        self.frameSleep = QFrame(self.tabSleep)
        self.frameSleep.setObjectName(u"frame")
        sizePolicy2Sleep = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy2Sleep.setHorizontalStretch(0)
        sizePolicy2Sleep.setVerticalStretch(0)
        sizePolicy2Sleep.setHeightForWidth(self.frameSleep.sizePolicy().hasHeightForWidth())
        self.frameSleep.setSizePolicy(sizePolicy2Sleep)
        self.frameSleep.setFrameShape(QFrame.StyledPanel)
        self.frameSleep.setFrameShadow(QFrame.Raised)
        self.gridLayout_5Sleep = QGridLayout(self.frameSleep)
        self.gridLayout_5Sleep.setSpacing(0)

        self.widget_2Sleep= QWidget(self.frameSleep)
        self.widget_2Sleep.setObjectName(u"widget_2")
        self.label_3Sleep = QLabel("label",self.widget_2Sleep)
        self.label_3Sleep.setObjectName(u"label_3")
        self.label_3Sleep.setGeometry(QRect(100, 60, 47, 13))
        self.label_3Sleep.setStyleSheet(u"background-color: rgb(0, 0, 0);\n"
"color: rgb(255, 255, 255);")

        self.start_end_sleep_records()

        """ self.gridLayout_5Sleep.addWidget(self.create_line_chart("Start_Time",table_name), 0, 0, 1, 1)

        self.gridLayout_5Sleep.addWidget(self.create_line_chart("End_Time",table_name), 0, 1, 1, 1)

        self.gridLayout_5Sleep.addWidget(self.create_line_chart("Number_of_Awakenings",table_name), 1, 0, 1, 1)

        self.gridLayout_5Sleep.addWidget(self.create_line_chart("Time_in_Bed",table_name), 1, 1, 1, 1)
        """
        self.gridLayout_7Sleep.addWidget(self.frame, 0, 0, 1, 1)

        self.tabWidgetSleep.addTab(self.tabSleep, "")

        self.tab_2Sleep = QWidget()
        self.tab_2Sleep.setObjectName(u"tab_2")

        self.gridLayout_8Sleep = QGridLayout(self.tab_2Sleep)
        self.gridLayout_8Sleep.setSpacing(0)
        self.gridLayout_8Sleep.setObjectName(u"gridLayout_8")
        self.gridLayout_8Sleep.setContentsMargins(0, 0, 0, 0)
        self.frame1Sleep = QFrame(self.tab_2Sleep)
        self.frame1Sleep.setObjectName(u"frame1")
        sizePolicy3Sleep = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy3Sleep.setHorizontalStretch(0)
        sizePolicy3Sleep.setVerticalStretch(0)
        sizePolicy3Sleep.setHeightForWidth(self.frame1.sizePolicy().hasHeightForWidth())
        self.frame1Sleep.setSizePolicy(sizePolicy3Sleep)
        self.frame1Sleep.setFrameShape(QFrame.StyledPanel)
        self.frame1Sleep.setFrameShadow(QFrame.Raised)
        self.gridLayout_6 = QGridLayout(self.frame1)
        self.gridLayout_6.setSpacing(0)

        self.widget_2Sleep = QWidget(self.frame1Sleep)
        self.widget_2Sleep.setObjectName(u"widget_2")
        self.label_3Sleep = QLabel("label",self.widget_2Sleep)
        self.label_3Sleep.setObjectName(u"label_3")
        self.label_3Sleep.setGeometry(QRect(100, 60, 47, 13))
        self.label_3Sleep.setStyleSheet(u"background-color: rgb(0, 0, 0);\n"
"color: rgb(255, 255, 255);")

        #add the graphs
        """ self.gridLayout_6Sleep.addWidget(self.create_line_chart("Minutes_Asleep", "sleep"), 0, 0, 1, 1)

        self.gridLayout_6Sleep.addWidget(self.create_line_chart("Minutes_Awake", "sleep"), 0, 1, 1, 1)

        self.gridLayout_6Sleep.addWidget(self.create_line_chart("Minutes_REM_Sleep", "sleep"), 1, 0, 1, 1)

        self.gridLayout_6Sleep.addWidget(self.create_line_chart("Minutes_Light_Sleep", "sleep"), 1, 1, 1, 1)

        self.gridLayout_6Sleep.addWidget(self.create_line_chart("Minutes_Deep_Sleep", "sleep"), 2, 0, 1, 1)
        """

        self.gridLayout_8Sleep.addWidget(self.frame1Sleep, 0, 0, 1, 1)


        self.tabWidgetSleep.addTab(self.tab_2Sleep, "")
        self.tabWidgetSleep.repaint()
        self.ui.verticalLayout_4.addWidget(self.tabWidgetSleep)

        self.tabWidgetSleep.setCurrentIndex(0)

        self.tabWidgetSleep.setTabText(self.tabWidgetSleep.indexOf(self.tabSleep), QCoreApplication.translate("MainWindow", u"Overview", None))
        self.tabWidgetSleep.setTabText(self.tabWidgetSleep.indexOf(self.tab_2Sleep), QCoreApplication.translate("MainWindow", u"Minutes", None))

    def foods(self,table_name):
        self.ui.label_11.setText("FOODS")
        self.deleteLayout(self.ui.frame_8.layout())

        self.tabWidgetFood = QTabWidget(self.ui.frame_8)
        self.tabWidgetFood.setEnabled(True)
        self.tabWidgetFood.setStyleSheet(u"color: rgb(0, 0, 0);")
        self.tabFood = QWidget()
        self.gridLayout_7Food = QGridLayout(self.tabFood)
        self.gridLayout_7Food.setSpacing(0)
        self.gridLayout_7Food.setContentsMargins(0, 0, 0, 0)
        self.frameFood = QFrame(self.tabFood)
        self.frameFood.setObjectName(u"frame")
        sizePolicy2Food = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy2Food.setHorizontalStretch(0)
        sizePolicy2Food.setVerticalStretch(0)
        sizePolicy2Food.setHeightForWidth(self.frameFood.sizePolicy().hasHeightForWidth())
        self.frameFood.setSizePolicy(sizePolicy2Food)
        self.frameFood.setFrameShape(QFrame.StyledPanel)
        self.frameFood.setFrameShadow(QFrame.Raised)
        self.gridLayout_5Food = QGridLayout(self.frameFood)
        self.gridLayout_5Food.setSpacing(0)

        self.gridLayout_5Food.addWidget(self.create_line_chart("Calories_In",table_name), 0, 0, 1, 1)

        self.gridLayout_7Food.addWidget(self.frameFood, 0, 0, 1, 1)

        self.tabWidgetFood.addTab(self.tabFood, "")
        self.tabWidgetFood.repaint()

        self.ui.verticalLayout_4.addWidget(self.tabWidgetFood)

        self.tabWidgetFood.setCurrentIndex(0)

        self.tabWidgetFood.setTabText(self.tabWidgetFood.indexOf(self.tabFood), QCoreApplication.translate("MainWindow", u"Overview", None))
        
    def GPS(self,table_name):
        self.ui.label_11.setText("GPS")
        self.deleteLayout(self.ui.frame_8.layout())

        select_query = "SELECT `latitude`, `longitude` FROM `%s`" % (table_name)
            
        #print(select_query)
            
        self.cursor.execute(select_query)
        result = self.cursor.fetchall()
        print(result)
        self.ui.verticalLayout_4.addWidget(self.printMap(result[0][0], result[0][1]))
        QApplication.processEvents()
        


    def printMap(self, lat,lon, w='100%',h='100%'):
        coordinate = (lat, lon)
        m = folium.Map(
        	tiles='Stamen Terrain',
        	zoom_start=13,
        	location=coordinate,
            width=w,
            height = h
        )

        folium.Marker(
            location=[lat, lon]
        ).add_to(m)

        # save map data to data object
        data = io.BytesIO()
        m.save(data, close_file=False)

        webView = QWebEngineView()
        webView.setHtml(data.getvalue().decode())
        return webView
        
    


    def profile(self,table_name):
        self.ui.label_11.setText("PROFILE")
        self.deleteLayout(self.ui.frame_8.layout())

        select_query = "SELECT `gender`, `dateOfBirth`, `height`,`weight`,`fullName`,`timezone`,`age`,`averageDailySteps` FROM `%s`" % (table_name)
        print(select_query)
        self.cursor.execute(select_query)
        result = self.cursor.fetchall()
        print(result)
        
        self.tabWidgetProfile = QTabWidget(self.ui.frame_8)
        self.tabWidgetProfile.setEnabled(True)
        self.tabWidgetProfile.setStyleSheet(u"color: rgb(0, 0, 0);")
        self.tabProfile = QWidget()
        self.verticalLayout_5 = QVBoxLayout(self.tabProfile)
        self.verticalLayout_5.setSpacing(0)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.frameProfile = QFrame(self.tabProfile)
        self.frameProfile.setObjectName(u"frame")
        sizePolicy2Profile = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy2Profile.setHorizontalStretch(0)
        sizePolicy2Profile.setVerticalStretch(0)
        sizePolicy2Profile.setHeightForWidth(self.frameProfile.sizePolicy().hasHeightForWidth())
        self.frameProfile.setSizePolicy(sizePolicy2Profile)
        self.frameProfile.setFrameShape(QFrame.StyledPanel)
        self.frameProfile.setFrameShadow(QFrame.Raised)
        self.frameProfile.setStyleSheet(u"background-color: rgb(61, 80, 95)")
        self.verticalLayout_7 = QVBoxLayout(self.frameProfile)
        self.verticalLayout_7.setSpacing(0)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayoutProfile = QHBoxLayout()
        self.horizontalLayoutProfile.setSpacing(0)
        self.frame_2 = QFrame(self.frameProfile)
        self.frame_2.setFrameShape(QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Raised)


        self.label_3 = QLabel(self.frame_2)
        self.label_3.setFont(self.font1)
        self.label_3.setStyleSheet("color: white;")
        self.label_3.setText("Full Name:")
        self.label_3.setGeometry(QRect(30, 40, 59, 16))


        self.lblFullname = QLabel(self.frame_2)
        self.lblFullname.setFont(self.font)
        self.lblFullname.setStyleSheet("color: white;")
        self.lblFullname.setText(result[0][4])
        self.lblFullname.setGeometry(QRect(self.label_3.x()+100, self.label_3.y(), 59, 16))

        self.label_4 = QLabel(self.frame_2)
        self.label_4.setFont(self.font1)
        self.label_4.setStyleSheet("color: white;")
        self.label_4.setText("Date of Birth:")
        self.label_4.setGeometry(QRect(30, 70, 100, 16))

        self.lblDOB = QLabel(self.frame_2)
        self.lblDOB.setFont(self.font)
        self.lblDOB.setStyleSheet("color: white;")
        self.lblDOB.setText(result[0][1])
        self.lblDOB.setGeometry(QRect(self.label_4.x()+100, self.label_4.y(), 100, 16))


        self.label_5 = QLabel(self.frame_2)
        self.label_5.setFont(self.font1)
        self.label_5.setStyleSheet("color: white;")
        self.label_5.setText("Gender:")
        self.label_5.setGeometry(QRect(30, 100, 54, 16))

        self.lblGender = QLabel(self.frame_2)
        self.lblGender.setFont(self.font)
        self.lblGender.setStyleSheet("color: white;")
        self.lblGender.setText(result[0][0])
        self.lblGender.setGeometry(QRect(self.label_5.x()+100, self.label_5.y(), 54, 16))
        

        self.label_6 = QLabel(self.frame_2)
        self.label_6.setFont(self.font1)
        self.label_6.setStyleSheet("color: white;")
        self.label_6.setText("Age:")
        self.label_6.setGeometry(QRect(30, 130, 54, 16))

        self.lblAge = QLabel(self.frame_2)
        self.lblAge.setFont(self.font)
        self.lblAge.setStyleSheet("color: white;")
        self.lblAge.setText(result[0][6])
        self.lblAge.setGeometry(QRect(self.label_6.x()+100, self.label_6.y(), 54, 16))
        

        self.label_7 = QLabel(self.frame_2)
        self.label_7.setFont(self.font1)
        self.label_7.setStyleSheet("color: white;")
        self.label_7.setText("Height:")
        self.label_7.setGeometry(QRect(30, 160, 54, 16))

        self.lblHeight = QLabel(self.frame_2)
        self.lblHeight.setFont(self.font)
        self.lblHeight.setStyleSheet("color: white;")
        
        self.lblHeight.setText('{:.2f}'.format(round(float(result[0][2])/12,2))+" ft")
        self.lblHeight.setGeometry(QRect(self.label_7.x()+100, self.label_7.y(), 54, 16))
        

        self.label_8 = QLabel(self.frame_2)
        self.label_8.setFont(self.font1)
        self.label_8.setStyleSheet("color: white;")
        self.label_8.setText("Weight:")
        self.label_8.setGeometry(QRect(30, 190, 54, 16))

        self.lblWeight = QLabel(self.frame_2)
        self.lblWeight.setFont(self.font)
        self.lblWeight.setStyleSheet("color: white;")
        self.lblWeight.setText('{:.2f}'.format(float(result[0][3]))+" lbs")
        self.lblWeight.setGeometry(QRect(self.label_8.x()+100, self.label_8.y(), 54, 16))
        
        self.label_9 = QLabel(self.frame_2)
        self.label_9.setFont(self.font1)
        self.label_9.setStyleSheet("color: white;")
        self.label_9.setText("Timezone:")
        self.label_9.setGeometry(QRect(30, 220, 60, 16))

        self.lblTimezone = QLabel(self.frame_2)
        self.lblTimezone.setFont(self.font)
        self.lblTimezone.setStyleSheet("color: white;")
        self.lblTimezone.setText(result[0][5])
        self.lblTimezone.setGeometry(QRect(self.label_9.x()+100, self.label_9.y(), 150, 16))

        self.label_10 = QLabel(self.frame_2)
        self.label_10.setFont(self.font1)
        self.label_10.setStyleSheet("color: white;")
        self.label_10.setText("Average Daily Steps:")
        self.label_10.setGeometry(QRect(30, 250,750, 16))

        self.lblADS = QLabel(self.frame_2)
        self.lblADS.setFont(self.font)
        self.lblADS.setStyleSheet("color: white;")
        self.lblADS.setText(result[0][7])
        self.lblADS.setGeometry(QRect(self.label_10.x()+150, self.label_10.y(), 54, 16))


        self.horizontalLayoutProfile.addWidget(self.frame_2)

        self.frame_5 = QFrame(self.frameProfile)
        self.frame_5.setObjectName(u"frame_5")
        self.frame_5.setFrameShape(QFrame.StyledPanel)
        self.frame_5.setFrameShadow(QFrame.Raised)
        self.labelphoto = QLabel(self.frame_5)
        self.labelphoto.setGeometry(QRect(60, 40, 256, 256))
        pixmap = QPixmap(self.getSounds(table_name.split("_")[0])[0][0])
        self.labelphoto.setPixmap(pixmap)
        #self.labelphoto.resize(pixmap.width(), pixmap.height())
        self.labelphoto.setScaledContents(1)
        sizePolicy3 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.labelphoto.sizePolicy().hasHeightForWidth())
        self.labelphoto.setSizePolicy(sizePolicy3)

        self.horizontalLayoutProfile.addWidget(self.frame_5)


        self.verticalLayout_7.addLayout(self.horizontalLayoutProfile)


        self.verticalLayout_5.addWidget(self.frameProfile)
        

        

        self.tabWidgetProfile.addTab(self.tabProfile, "")
        self.tabWidgetProfile.repaint()

        self.ui.verticalLayout_4.addWidget(self.tabWidgetProfile)

        self.tabWidgetProfile.setCurrentIndex(0)

        self.tabWidgetProfile.setTabText(self.tabWidgetProfile.indexOf(self.tabProfile), QCoreApplication.translate("MainWindow", u"Overview", None))

    def getSounds(self,case_name):
        select_query = "SELECT `path` FROM `%s`" % (case_name+"_photos")
        print(select_query)  
        self.cursor.execute(select_query)
        return self.cursor.fetchall()
        


    def sounds(self, table_name):
        self.ui.label_11.setText("SOUNDS")
        self.deleteLayout(self.ui.frame_8.layout())

        select_query = "SELECT * FROM `%s`" % (table_name)
        print(select_query)
        self.cursor.execute(select_query)
        result = self.cursor.fetchall()
        print(result)
        
        self.tabWidgetProfile = QTabWidget(self.ui.frame_8)
        self.tabWidgetProfile.setEnabled(True)
        self.tabWidgetProfile.setStyleSheet(u"color: rgb(0, 0, 0);")
        self.tabProfile = QWidget()
        self.verticalLayout_5 = QVBoxLayout(self.tabProfile)
        self.verticalLayout_5.setSpacing(0)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.frameProfile = QFrame(self.tabProfile)
        self.frameProfile.setObjectName(u"frame")
        sizePolicy2Profile = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy2Profile.setHorizontalStretch(0)
        sizePolicy2Profile.setVerticalStretch(0)
        sizePolicy2Profile.setHeightForWidth(self.frameProfile.sizePolicy().hasHeightForWidth())
        self.frameProfile.setSizePolicy(sizePolicy2Profile)
        self.frameProfile.setFrameShape(QFrame.StyledPanel)
        self.frameProfile.setFrameShadow(QFrame.Raised)
        self.frameProfile.setStyleSheet(u"background-color: rgb(61, 80, 95)")
        self.verticalLayout_7 = QVBoxLayout(self.frameProfile)
        self.verticalLayout_7.setSpacing(0)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayoutProfile = QHBoxLayout()
        self.horizontalLayoutProfile.setSpacing(0)
        self.frame_2 = QFrame(self.frameProfile)
        self.frame_2.setFrameShape(QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Raised)

        player = QMediaPlayer(self.frame_2)
        player.setMedia(QUrl.fromLocalFile(result[0][0]))
        player.setVolume(100)
        player.play()


        self.horizontalLayoutProfile.addWidget(self.frame_2)

        self.frame_5 = QFrame(self.frameProfile)
        self.frame_5.setObjectName(u"frame_5")
        self.frame_5.setFrameShape(QFrame.StyledPanel)
        self.frame_5.setFrameShadow(QFrame.Raised)
        self.horizontalLayoutProfile.addWidget(self.frame_5)


        self.verticalLayout_7.addLayout(self.horizontalLayoutProfile)


        self.verticalLayout_5.addWidget(self.frameProfile)
        

        

        self.tabWidgetProfile.addTab(self.tabProfile, "")
        self.tabWidgetProfile.repaint()

        self.ui.verticalLayout_4.addWidget(self.tabWidgetProfile)

        self.tabWidgetProfile.setCurrentIndex(0)

        self.tabWidgetProfile.setTabText(self.tabWidgetProfile.indexOf(self.tabProfile), QCoreApplication.translate("MainWindow", u"Overview", None))


    def overview(self,tables):
        self.ui.label_11.setText("OVERVIEW")
        self.deleteLayout(self.ui.frame_8.layout())

        #set the tabs
        self.tabWidget = QTabWidget(self.ui.frame_8)
        self.tabWidget.setEnabled(True)
        self.tabWidget.setStyleSheet(u"color: rgb(0, 0, 0);")
        self.tab = QWidget()
        self.verticalLayout_5 = QVBoxLayout(self.tab)
        self.verticalLayout_5.setSpacing(0)
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.frame = QFrame(self.tab)
        sizePolicy2 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy2.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy2)
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout_10 = QVBoxLayout(self.frame)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.verticalLayout_10.setContentsMargins(0, 9, 0, 0)

        self.dateedit = QDateEdit(self.frame)
        self.dateedit.setCalendarPopup(True)
        self.dateedit.setDate(QDate.currentDate())
        self.dateedit.setMaximumDate(QDate.currentDate())
        self.dateedit.setGeometry(QRect(600, 10, 100, 22))
        self.dateedit.dateChanged.connect(lambda: self.method(tables,1)) 

        self.getDayInfo(tables)

        self.verticalLayout_10.addWidget(self.dateedit, 0, Qt.AlignRight)


        self.scrollArea_2 = QScrollArea(self.frame)
        self.scrollArea_2.setWidgetResizable(True)
        sizePolicy2.setHeightForWidth(self.scrollArea_2.sizePolicy().hasHeightForWidth())
        self.scrollArea_2.setSizePolicy(sizePolicy2)
        self.scrollArea_2.setMaximumSize(QSize(16777215, 2000))
        self.scrollArea_2.setWidgetResizable(True)
        self.scrollAreaWidgetContents_2 = QWidget()
        self.scrollAreaWidgetContents_2.setGeometry(QRect(0, 0, 711, 500))
        self.verticalLayout_6 = QVBoxLayout(self.scrollAreaWidgetContents_2)
        self.verticalLayout_6.setSpacing(0)
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.frame_2 = QFrame(self.scrollAreaWidgetContents_2)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setMinimumSize(QSize(0, 700))
        self.frame_2.setFrameShape(QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Raised)
        self.gridLayout_2 = QGridLayout(self.frame_2)
        self.gridLayout_2.setObjectName(u"gridLayout_2")

        
        
        self.groupBox = QGroupBox(self.frame_2)
        self.groupBox.setTitle("User Profile")
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setStyleSheet("QGroupBox#groupBox{ border: 1px solid black;}")

        self.label_3 = QLabel(self.groupBox)
        self.label_3.setFont(self.font1)
        self.label_3.setStyleSheet("color: black;")
        self.label_3.setText("Full Name:")
        self.label_3.setGeometry(QRect(30, 40, 59, 16))


        self.lblFullname = QLabel(self.groupBox)
        self.lblFullname.setFont(self.font)
        self.lblFullname.setStyleSheet("color: black;")
        self.lblFullname.setText(self.user[0][0][4])
        self.lblFullname.setGeometry(QRect(self.label_3.x()+100, self.label_3.y(), 59, 16))

        self.label_4 = QLabel(self.groupBox)
        self.label_4.setFont(self.font1)
        self.label_4.setStyleSheet("color: black;")
        self.label_4.setText("Date of Birth:")
        self.label_4.setGeometry(QRect(30, 70, 100, 16))

        self.lblDOB = QLabel(self.groupBox)
        self.lblDOB.setFont(self.font)
        self.lblDOB.setStyleSheet("color: black;")
        self.lblDOB.setText(self.user[0][0][1])
        self.lblDOB.setGeometry(QRect(self.label_4.x()+100, self.label_4.y(), 100, 16))


        self.label_5 = QLabel(self.groupBox)
        self.label_5.setFont(self.font1)
        self.label_5.setStyleSheet("color: black;")
        self.label_5.setText("Gender:")
        self.label_5.setGeometry(QRect(30, 100, 54, 16))

        self.lblGender = QLabel(self.groupBox)
        self.lblGender.setFont(self.font)
        self.lblGender.setStyleSheet("color: black;")
        self.lblGender.setText(self.user[0][0][0])
        self.lblGender.setGeometry(QRect(self.label_5.x()+100, self.label_5.y(), 54, 16))
        

        self.label_6 = QLabel(self.groupBox)
        self.label_6.setFont(self.font1)
        self.label_6.setStyleSheet("color: black;")
        self.label_6.setText("Age:")
        self.label_6.setGeometry(QRect(30, 130, 54, 16))

        self.lblAge = QLabel(self.groupBox)
        self.lblAge.setFont(self.font)
        self.lblAge.setStyleSheet("color: black;")
        self.lblAge.setText(self.user[0][0][6])
        self.lblAge.setGeometry(QRect(self.label_6.x()+100, self.label_6.y(), 54, 16))
        

        self.label_7 = QLabel(self.groupBox)
        self.label_7.setFont(self.font1)
        self.label_7.setStyleSheet("color: black;")
        self.label_7.setText("Height:")
        self.label_7.setGeometry(QRect(30, 160, 54, 16))

        self.lblHeight = QLabel(self.groupBox)
        self.lblHeight.setFont(self.font)
        self.lblHeight.setStyleSheet("color: black;")
        
        self.lblHeight.setText('{:.2f}'.format(round(float(self.user[0][0][2])/12,2))+" ft")
        self.lblHeight.setGeometry(QRect(self.label_7.x()+100, self.label_7.y(), 54, 16))
        

        self.label_8 = QLabel(self.groupBox)
        self.label_8.setFont(self.font1)
        self.label_8.setStyleSheet("color: black;")
        self.label_8.setText("Weight:")
        self.label_8.setGeometry(QRect(30,190, 54, 16))

        self.lblWeight = QLabel(self.groupBox)
        self.lblWeight.setFont(self.font)
        self.lblWeight.setStyleSheet("color: black;")
        self.lblWeight.setText('{:.2f}'.format(float(self.user[0][0][3]))+" lbs")
        self.lblWeight.setGeometry(QRect(self.label_8.x()+100, self.label_8.y(), 54, 16))
        
        self.label_9 = QLabel(self.groupBox)
        self.label_9.setFont(self.font1)
        self.label_9.setStyleSheet("color: black;")
        self.label_9.setText("Timezone:")
        self.label_9.setGeometry(QRect(30, 220, 60, 16))

        self.lblTimezone = QLabel(self.groupBox)
        self.lblTimezone.setFont(self.font)
        self.lblTimezone.setStyleSheet("color: black;")
        self.lblTimezone.setText(self.user[0][0][5])
        self.lblTimezone.setGeometry(QRect(self.label_9.x()+100, self.label_9.y(), 150, 16))

        self.label_10 = QLabel(self.groupBox)
        self.label_10.setFont(self.font1)
        self.label_10.setStyleSheet("color: black;")
        self.label_10.setText("Average Daily Steps:")
        self.label_10.setGeometry(QRect(30, 250,750, 16))

        self.lblADS = QLabel(self.groupBox)
        self.lblADS.setFont(self.font)
        self.lblADS.setStyleSheet("color: black;")
        self.lblADS.setText(self.user[0][0][7])
        self.lblADS.setGeometry(QRect(self.label_10.x()+150, self.label_10.y(), 54, 16))

        self.labelphoto = QLabel(self.groupBox)
        self.labelphoto.setGeometry(QRect(400, 23, 256, 256))
        pixmap = QPixmap(self.photos[0][0][0])
        self.labelphoto.setPixmap(pixmap)
        self.labelphoto.setScaledContents(1)
        sizePolicy3 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.labelphoto.sizePolicy().hasHeightForWidth())
        self.labelphoto.setSizePolicy(sizePolicy3)

        self.gridLayout_2.addWidget(self.groupBox, 0, 0, 1, 2)




        self.groupBox_2 = QGroupBox(self.frame_2)
        self.groupBox_2.setTitle("Activities")
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.groupBox_2.setStyleSheet("QGroupBox{ border: 1px solid black;}")
        #self.groupBox_2.setGeometry(QRect(20, 350, 700, 181))



        self.label_11 = QLabel(self.groupBox_2)
        self.label_11.setFont(self.font1)
        self.label_11.setStyleSheet("color: black;")
        self.label_11.setText("Calories Burned:")
        self.label_11.setGeometry(QRect(30, 40, 250, 16))


        self.lblCaloriesBurned = QLabel(self.groupBox_2)
        self.lblCaloriesBurned.setFont(self.font)
        self.lblCaloriesBurned.setStyleSheet("color: black;")
        self.lblCaloriesBurned.setGeometry(QRect(self.label_11.x()+110, self.label_11.y(),100, 16))

        self.label_12 = QLabel(self.groupBox_2)
        self.label_12.setFont(self.font1)
        self.label_12.setStyleSheet("color: black;")
        self.label_12.setText("Steps:")
        self.label_12.setGeometry(QRect(30, 70, 100, 16))

        self.lblSteps = QLabel(self.groupBox_2)
        self.lblSteps.setFont(self.font)
        self.lblSteps.setStyleSheet("color: black;")
        self.lblSteps.setGeometry(QRect(self.label_12.x()+110, self.label_12.y(), 100, 16))


        self.label_13 = QLabel(self.groupBox_2)
        self.label_13.setFont(self.font1)
        self.label_13.setStyleSheet("color: black;")
        self.label_13.setText("Distance:")
        self.label_13.setGeometry(QRect(30, 100, 54, 16))

        self.lblDistance = QLabel(self.groupBox_2)
        self.lblDistance.setFont(self.font)
        self.lblDistance.setStyleSheet("color: black;")
        self.lblDistance.setGeometry(QRect(self.label_13.x()+110, self.label_13.y(), 100, 16))
        

        self.label_14 = QLabel(self.groupBox_2)
        self.label_14.setFont(self.font1)
        self.label_14.setStyleSheet("color: black;")
        self.label_14.setText("Floors:")
        self.label_14.setGeometry(QRect(30, 130, 54, 16))

        self.lblFloors = QLabel(self.groupBox_2)
        self.lblFloors.setFont(self.font)
        self.lblFloors.setStyleSheet("color: black;")
        self.lblFloors.setGeometry(QRect(self.label_14.x()+110, self.label_14.y(), 54, 16))
        

       

        self.gridLayout_2.addWidget(self.groupBox_2, 1, 0, 1, 1)

        self.groupBox_3 = QGroupBox(self.frame_2)
        self.groupBox_3.setTitle("Sleep")
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.groupBox_3.setStyleSheet("QGroupBox{ border: 1px solid black;}")
        #self.groupBox_3.setGeometry(QRect(20, 550,  700, 181))

        self._chart_view = QtCharts.QChartView(self.groupBox_3)
        self._chart_view.setRenderHint(QPainter.Antialiasing)
        self._chart_view.setGeometry(QRect(35, 3, 300, 275))
        self._chart_view.setVisible(False)

        self.lbl_nopie = QLabel(self.groupBox_3)
        self.lbl_nopie.setFont(self.font1)
        self.lbl_nopie.setStyleSheet("color: black;")
        self.lbl_nopie.setText("No recorded data for pie chart")
        self.lbl_nopie.setGeometry(QRect(50, 100, 200, 16))
        self.lbl_nopie.setVisible(False)

        self.lbl_14 = QLabel(self.groupBox_3)
        self.lbl_14.setFont(self.font1)
        self.lbl_14.setStyleSheet("color: black;")
        self.lbl_14.setText("Time:")
        self.lbl_14.setGeometry(QRect(30, 250, 100, 16))

        self.lblTime = QLabel(self.groupBox_3)
        self.lblTime.setFont(self.font)
        self.lblTime.setStyleSheet("color: black;")
        self.lblTime.setGeometry(QRect(self.lbl_14.x()+self.lbl_14.width()+110, self.lbl_14.y(), 100, 16))
        
        self.lbl_15 = QLabel(self.groupBox_3)
        self.lbl_15.setFont(self.font1)
        self.lbl_15.setStyleSheet("color: black;")
        self.lbl_15.setText("Number of Awakenings:")
        self.lbl_15.setGeometry(QRect(30, 280, 150, 16))

        self.lblNumberOfAwakenings = QLabel(self.groupBox_3)
        self.lblNumberOfAwakenings.setFont(self.font)
        self.lblNumberOfAwakenings.setStyleSheet("color: black;")
        self.lblNumberOfAwakenings.setGeometry(QRect(self.lbl_15.x()+self.lbl_15.width()+60, self.lbl_15.y(), 54, 16))
        
        self.lbl_16 = QLabel(self.groupBox_3)
        self.lbl_16.setFont(self.font1)
        self.lbl_16.setStyleSheet("color: black;")
        self.lbl_16.setText("Time in Bed:")
        self.lbl_16.setGeometry(QRect(30, 310, 100, 16))

        self.lblTimeinBed = QLabel(self.groupBox_3)
        self.lblTimeinBed.setFont(self.font)
        self.lblTimeinBed.setStyleSheet("color: black;")
        self.lblTimeinBed.setGeometry(QRect(self.lbl_16.x()+self.lbl_16.width()+110, self.lbl_16.y(), 100, 16))

        

        self.gridLayout_2.addWidget(self.groupBox_3,1, 1, 2, 1)

        self.groupBox_4 = QGroupBox(self.frame_2)
        self.groupBox_4.setTitle("Body")
        self.groupBox_4.setObjectName(u"groupBox_4")
        self.groupBox_4.setStyleSheet("QGroupBox{ border: 1px solid black;}")

        self.label_15 = QLabel(self.groupBox_4)
        self.label_15.setFont(self.font1)
        self.label_15.setStyleSheet("color: black;")
        self.label_15.setText("Weight:")
        self.label_15.setGeometry(QRect(30, 40, 250, 16))


        self.lblWeight= QLabel(self.groupBox_4)
        self.lblWeight.setFont(self.font)
        self.lblWeight.setStyleSheet("color: black;")
        self.lblWeight.setGeometry(QRect(self.label_15.x()+110, self.label_15.y(), 100, 16))

        self.label_16 = QLabel(self.groupBox_4)
        self.label_16.setFont(self.font1)
        self.label_16.setStyleSheet("color: black;")
        self.label_16.setText("BMI:")
        self.label_16.setGeometry(QRect(30, 70, 100, 16))

        self.lblBMI = QLabel(self.groupBox_4)
        self.lblBMI.setFont(self.font)
        self.lblBMI.setStyleSheet("color: black;")
        self.lblBMI.setGeometry(QRect(self.label_16.x()+110, self.label_16.y(), 100, 16))


        self.label_17 = QLabel(self.groupBox_4)
        self.label_17.setFont(self.font1)
        self.label_17.setStyleSheet("color: black;")
        self.label_17.setText("Fat:")
        self.label_17.setGeometry(QRect(30, 100, 54, 16))

        self.lblFat = QLabel(self.groupBox_4)
        self.lblFat.setFont(self.font)
        self.lblFat.setStyleSheet("color: black;")
        self.lblFat.setGeometry(QRect(self.label_17.x()+110, self.label_17.y(), 54, 16))
        



        self.gridLayout_2.addWidget(self.groupBox_4, 2, 0, 1, 1)

        self.gridLayout_2.setRowStretch(0, 10)
        self.gridLayout_2.setRowStretch(1, 5)
        self.gridLayout_2.setRowStretch(2, 5)
        
        self.verticalLayout_6.addWidget(self.frame_2)

        self.scrollArea_2.setWidget(self.scrollAreaWidgetContents_2)

        
        self.verticalLayout_10.addWidget(self.scrollArea_2)

        self.verticalLayout_5.addWidget(self.frame)
        
        
        self.tabWidget.addTab(self.tab, "")

        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.verticalLayout_7 = QVBoxLayout(self.tab_2)
        self.verticalLayout_7.setSpacing(0)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.frame_5 = QFrame(self.tab_2)
        self.frame_5.setObjectName(u"frame_5")
        self.frame_5.setFrameShape(QFrame.StyledPanel)
        self.frame_5.setFrameShadow(QFrame.Raised)
        self.verticalLayout_8 = QVBoxLayout(self.frame_5)
        self.verticalLayout_8.setSpacing(0)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.verticalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.frame_7 = QFrame(self.frame_5)
        self.frame_7.setObjectName(u"frame_7")
        self.frame_7.setFrameShape(QFrame.StyledPanel)
        self.frame_7.setFrameShadow(QFrame.Raised)
        self.verticalLayout_11 = QVBoxLayout(self.frame_7)
        self.verticalLayout_11.setSpacing(0)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.verticalLayout_11.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_9 = QVBoxLayout()
        self.verticalLayout_9.setSpacing(0)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.frame_16 = QFrame(self.frame_7)
        self.frame_16.setObjectName(u"frame_16")
        self.frame_16.setFrameShape(QFrame.StyledPanel)
        self.frame_16.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_8 = QHBoxLayout(self.frame_16)
        self.horizontalLayout_8.setSpacing(0)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.horizontalLayout_8.setContentsMargins(9, 9, 9, 9)
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_8.addItem(self.horizontalSpacer)

        self.dateTimeEdit_2 = QDateEdit(self.frame_16)
        self.dateTimeEdit_2.setObjectName(u"dateTimeEdit_2")
        self.dateTimeEdit_2.setMaximumDate(QDate.currentDate())
        sizePolicy4 = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Minimum)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.dateTimeEdit_2.sizePolicy().hasHeightForWidth())
        self.dateTimeEdit_2.setSizePolicy(sizePolicy4)
        self.dateTimeEdit_2.setMinimumSize(QSize(136, 0))
        self.dateTimeEdit_2.setWrapping(False)
        self.dateTimeEdit_2.setFrame(True)
        self.dateTimeEdit_2.setAlignment(Qt.AlignBottom|Qt.AlignRight|Qt.AlignTrailing)
        self.dateTimeEdit_2.setButtonSymbols(QAbstractSpinBox.UpDownArrows)
        self.dateTimeEdit_2.setProperty("showGroupSeparator", False)
        self.dateTimeEdit_2.setCalendarPopup(True)
        self.dateTimeEdit_2.setDate(self.dateedit.date())
        self.dateTimeEdit_2.dateChanged.connect(lambda: self.method(tables,0)) 
        

        self.horizontalLayout_8.addWidget(self.dateTimeEdit_2)

        self.verticalLayout_9.addWidget(self.frame_16)

        self.frame_15 = QFrame(self.frame_7)
        self.frame_15.setObjectName(u"frame_15")
        self.frame_15.setFrameShape(QFrame.StyledPanel)
        self.frame_15.setFrameShadow(QFrame.Raised)
        self.verticalLayout_20 = QVBoxLayout(self.frame_15)
        self.verticalLayout_20.setObjectName(u"verticalLayout_20")
        self.verticalLayout_20.setContentsMargins(0, 0, 0, 0)


        self.verticalLayout_9.addWidget(self.frame_15)


        self.verticalLayout_9.setStretch(0, 2)
        self.verticalLayout_9.setStretch(1, 5)

        self.verticalLayout_11.addLayout(self.verticalLayout_9)


        self.verticalLayout_8.addWidget(self.frame_7)

        self.frame_12 = QFrame(self.frame_5)
        self.frame_12.setObjectName(u"frame_12")
        self.frame_12.setFrameShape(QFrame.StyledPanel)
        self.frame_12.setFrameShadow(QFrame.Raised)
        self.verticalLayout_12 = QVBoxLayout(self.frame_12)
        self.verticalLayout_12.setSpacing(0)
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.verticalLayout_12.setContentsMargins(0, 0, 0, 0)
        self.scrollArea_3 = QScrollArea(self.frame_12)
        self.scrollArea_3.setObjectName(u"scrollArea_3")
        self.scrollArea_3.setWidgetResizable(True)
        self.scrollAreaWidgetContents_3 = QWidget()
        self.scrollAreaWidgetContents_3.setObjectName(u"scrollAreaWidgetContents_3")
        self.scrollAreaWidgetContents_3.setGeometry(QRect(0, 0, 654, 418))
        self.horizontalLayout = QHBoxLayout(self.scrollAreaWidgetContents_3)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.frame_14 = QFrame(self.scrollAreaWidgetContents_3)
        self.frame_14.setObjectName(u"frame_14")
        self.frame_14.setFrameShape(QFrame.StyledPanel)
        self.frame_14.setFrameShadow(QFrame.Raised)
        self.frame_14.setStyleSheet("QFrame{ border: 1px solid black;}")
        self.pushButton = QPushButton(self.frame_14)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setStyleSheet(u"color: rgb(0, 0, 0);")
        icon4 = QIcon()
        icon4.addFile(u":/icons/icons/tag.svg", QSize(), QIcon.Normal, QIcon.On)
        self.pushButton.setIcon(icon4)
        self.pushButton.setGeometry(QRect(10, 10, 111, 71))
        self.pushButton.setFont(QFont('NovaFlat', 22))

        self.pushButton_2 = QPushButton(self.frame_14)
        self.pushButton_2.setObjectName(u"pushButton_2")
        self.pushButton_2.setStyleSheet(u"color: rgb(0, 0, 0);")
        self.pushButton_2.setIcon(icon4)
        self.pushButton_2.setGeometry(QRect(10, 70, 111, 71))
        self.pushButton_2.setFont(QFont('NovaFlat', 22))

        self.pushButton_3 = QPushButton(self.frame_14)
        self.pushButton_3.setObjectName(u"pushButton_3")
        self.pushButton_3.setStyleSheet(u"color: rgb(0, 0, 0);")
        self.pushButton_3.setIcon(icon4)
        self.pushButton_3.setGeometry(QRect(9, 130, 111, 71))
        self.pushButton_3.setFont(QFont('NovaFlat', 22))

        self.pushButton_4 = QPushButton(self.frame_14)
        self.pushButton_4.setObjectName(u"pushButton_4")
        self.pushButton_4.setStyleSheet(u"color: rgb(0, 0, 0);")
        self.pushButton_4.setIcon(icon4)
        self.pushButton_4.setGeometry(QRect(10, 190, 111, 71))
        self.pushButton_4.setFont(QFont('NovaFlat', 22))


        self.pushButton_5 = QPushButton(self.frame_14)
        self.pushButton_5.setObjectName(u"pushButton_4")
        self.pushButton_5.setStyleSheet(u"color: rgb(0, 0, 0);")
        self.pushButton_5.setGeometry(QRect(10, 240, 111, 71))
        self.pushButton_5.setFont(QFont('NovaFlat', 22))

        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"What?", None))
        self.pushButton_2.setText(QCoreApplication.translate("MainWindow", u"Where?", None))
        self.pushButton_3.setText(QCoreApplication.translate("MainWindow", u"Who?", None))
        self.pushButton_4.setText(QCoreApplication.translate("MainWindow", u"When?", None))
        self.pushButton_5.setText(QCoreApplication.translate("MainWindow", u"More Details", None))



        
        self.button_group = QButtonGroup()
        self.button_group.setObjectName(u"ButtonGroup")
        self.button_group.addButton(self.pushButton)
        self.button_group.addButton(self.pushButton_2)
        self.button_group.addButton(self.pushButton_3)
        self.button_group.addButton(self.pushButton_4)
        self.button_group.addButton(self.pushButton_5)
        self.button_group.setExclusive(True)
        self.button_group.buttonClicked.connect(self.change_right_state)


        self.horizontalLayout.addWidget(self.frame_14)

        self.custom_widget = Bar()
        self.custom_widget.clickedButton.connect(self.chosen_time)
        

        self.verticalLayout_9.addWidget(self.custom_widget)

        self.verticalLayout_9.setAlignment(self.custom_widget,Qt.AlignCenter)

        self.frame_13 = QFrame(self.scrollAreaWidgetContents_3)
        self.frame_13.setObjectName(u"frame_13")
        sizePolicy4 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.frame_13.sizePolicy().hasHeightForWidth())
        self.frame_13.setSizePolicy(sizePolicy4)
        self.frame_13.setMinimumSize(QSize(0, 400))
        self.frame_13.setFrameShape(QFrame.StyledPanel)
        self.frame_13.setFrameShadow(QFrame.Raised)
        self.verticalLayout_19 = QVBoxLayout(self.frame_13)
        self.verticalLayout_19.setObjectName(u"verticalLayout_19")
        self.verticalLayout_15 = QVBoxLayout()
        self.verticalLayout_15.setObjectName(u"verticalLayout_15")
        

        self.verticalLayout_19.addLayout(self.verticalLayout_15)


        self.horizontalLayout.addWidget(self.frame_13)

        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 3)

        self.scrollArea_3.setWidget(self.scrollAreaWidgetContents_3)

        self.verticalLayout_12.addWidget(self.scrollArea_3)


        self.verticalLayout_8.addWidget(self.frame_12)

        self.verticalLayout_8.setStretch(0, 3)
        self.verticalLayout_8.setStretch(1, 9)

        self.verticalLayout_7.addWidget(self.frame_5)


        self.tabWidget.addTab(self.tab_2, "")

        self.ui.verticalLayout_4.addWidget(self.tabWidget)

        self.tabWidget.setCurrentIndex(0)

        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("MainWindow", u"Daily Overview", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("MainWindow", u"Timeline View", None))


        self.currentButton=0
        self.currentTime=0

        self.method(tables,0)
        self.method(tables,1)
     
        
    def method(self,tables,who):
        print("Date changed to ", self.dateedit.text())
        if not who:
            self.dateedit.setDate(self.dateTimeEdit_2.date())
            self.custom_widget.reset_time_stamps()
            self.deleteLayout(self.frame_13.layout())
            
        else:
            self.dateTimeEdit_2.setDate(self.dateedit.date())
        
        self.pushButton.animateClick()      
        self.daily_overview_tab(tables) 
        self.timeline_tab()

    def getDayInfo(self,tables):
        self.user = []
        self.sleep = []
        self.heart_rate = []
        self.weight = []
        self.exercise = []
        self.gps = []
        self.activities = []
        self.body = []
        self.foods = []
        self.photos = []

        for table in tables:
            select_query = ""
            if(table[0].endswith("sleep")):
                select_query = "SELECT * FROM `%s` WHERE Start_Time LIKE '%s%%' " % (table[0],self.dateedit.date().toString("yyyy-MM-dd"))
                print(select_query)
                self.cursor.execute(select_query)
                result = self.cursor.fetchall()
                if result:
                    self.sleep.append(result)
                else: 
                    self.sleep.append([("No record",)])
                print(self.sleep)

            elif(table[0].endswith("_heart_rate_profile")):
                select_query = "SELECT * FROM `%s` WHERE dateTime LIKE '%s%%' " % (table[0],self.dateedit.date().toString("MM/dd/yy"))
                print(select_query)
                self.cursor.execute(select_query)
                result = self.cursor.fetchall()
                if result:
                    self.heart_rate.append(result)
                else: 
                    self.heart_rate.append([("No record",)])
                print(self.heart_rate)
            elif(table[0].endswith("_weight_profile")):
                select_query = "SELECT * FROM `%s` WHERE date = '%s' " % (table[0],self.dateedit.date().toString("MM/dd/yy"),)
                print(select_query)
                self.cursor.execute(select_query)
                result = self.cursor.fetchall()
                if result:
                    self.weight.append(result)
                else: 
                    self.weight.append([("No record",)])
                print(self.weight)
            elif(table[0].endswith("_exercise_profile")):
                select_query = "SELECT * FROM `%s` WHERE startTime LIKE '%s%%' " % (table[0],self.dateedit.date().toString("MM/dd/yy"))
                print(select_query)
                self.cursor.execute(select_query)
                result = self.cursor.fetchall()
                if result:
                    self.exercise.append(result)
                else: 
                    self.exercise.append([("No record",)])
                print(self.exercise)
            elif(table[0].endswith("_gps")):
                select_query = "SELECT * FROM `%s` WHERE started_at LIKE '%s%%' " % (table[0],self.dateedit.date().toString("yyyy-MM-dd"))
                print(select_query)
                self.cursor.execute(select_query)
                result = self.cursor.fetchall()
                if result:
                    self.gps.append(result)
                else: 
                    self.gps.append([("No record",)])
                print(self.gps)
            elif(table[0].endswith("activities")):
                select_query = "SELECT * FROM `%s` WHERE Date = '%s'" % (table[0],self.dateedit.date().toString("yyyy-MM-dd"))
                print(select_query)
                self.cursor.execute(select_query)
                result = self.cursor.fetchall()
                if result:
                    self.activities.append(result)
                else: 
                    self.activities.append([("No record",)])
                print(self.activities)
            elif( table[0].endswith("body")):
                select_query = "SELECT * FROM `%s` WHERE Date LIKE '%s%%' " % (table[0],self.dateedit.date().toString("yyyy-MM-dd"))
                print(select_query)
                self.cursor.execute(select_query)
                result = self.cursor.fetchall()
                if result:
                    self.body.append(result)
                else: 
                    self.body.append([("No record",)])
                print(self.body)
            elif(table[0].endswith("foods")):
                select_query = "SELECT * FROM `%s` WHERE Date LIKE '%s%%' " % (table[0],self.dateedit.date().toString("yyyy-MM-dd"))
                print(select_query)
                self.cursor.execute(select_query)
                result = self.cursor.fetchall()
                if result:
                    self.foods.append(result)
                else: 
                    self.foods.append([("No record",)])
                print(self.foods)
            elif(table[0].endswith("user_profile")):
                select_query = "SELECT `gender`, `dateOfBirth`, `height`,`weight`,`fullName`,`timezone`,`age`,`averageDailySteps` FROM `%s`" % (table[0])
                print(select_query)
                self.cursor.execute(select_query)
                result = self.cursor.fetchall()
                if result:
                    self.user.append(result)
                else: 
                    self.user.append(list([("No record",)]))
                print(self.user)
            elif(table[0].endswith("photos")):
                select_query = "SELECT `path` FROM `%s`" % (table[0])
                print(select_query)  
                self.cursor.execute(select_query)
                result = self.cursor.fetchall()
                if result:
                    self.photos.append(result)
                else: 
                    self.photos.append([("No record",)])
                print(self.photos)    
      

    def daily_overview_tab(self,tables):
        self.getDayInfo(tables)
        self.lblFullname.setText(self.user[0][0][4])
        self.lblDOB.setText(self.user[0][0][1])
        self.lblGender.setText(self.user[0][0][0])
        self.lblAge.setText(self.user[0][0][6])
        self.lblHeight.setText('{:.2f}'.format(round(float(self.user[0][0][2])/12,2))+" ft")
        self.lblWeight.setText('{:.2f}'.format(float(self.user[0][0][3]))+" lbs")
        self.lblTimezone.setText(self.user[0][0][5])
        self.lblADS.setText(self.user[0][0][7])

        print(self.activities)
        if self.activities[0][0] == ("No record",):
            for i in range(9):
                self.activities[0][0]+=("No record",)
        print(self.activities)

        if self.activities[0][0][1] == "No record":
            self.lblCaloriesBurned.setText(self.activities[0][0][1])
        else:
            self.lblCaloriesBurned.setText(self.activities[0][0][1]+" kcals")
        self.lblSteps.setText(self.activities[0][0][2])

        if self.activities[0][0][3]== "No record":
            self.lblDistance.setText(self.activities[0][0][3])
        else:
            self.lblDistance.setText(self.activities[0][0][3]+" miles")
        self.lblFloors.setText(self.activities[0][0][4])


        print(self.body)
        if self.body[0][0] == ("No record",):
            for i in range(4):
                self.body[0][0]+=("No record",)
        print(self.body)

        if self.body[0][0][1]== "No record":
            self.lblWeight.setText(self.body[0][0][1])
        else:
            self.lblWeight.setText(self.body[0][0][1]+" lbs")

        self.lblBMI.setText(self.body[0][0][3])
        self.lblFat.setText(self.body[0][0][2])

        self.sleep_pie_chart()

         
    def sleep_pie_chart(self):

        self.usable_list =()
        
        print("sleep",self.sleep)
        for i in self.sleep:
            if i[0] != ("No record",):
                self.usable_list = i[0]
        if not self.usable_list:
            for k in range(9):
                self.usable_list+=("No record",)

        print(self.usable_list)
        if self.usable_list[3] != "No record":
            self.lbl_nopie.setVisible(False)
            self.series = QtCharts.QPieSeries()

            self.series.append('Awake', float(self.usable_list[4]))
            self.series.append('Asleep', float(self.usable_list[3]))

            self.series.setLabelsVisible()

            self.series.setLabelsPosition(QtCharts.QPieSlice.LabelOutside)
            self.series.slices()[0].setLabelColor(Qt.red)
            self.series.slices()[1].setLabelColor(Qt.red)
            for slice in self.series.slices():
                slice.setLabel("{:.2f}%".format(100 * slice.percentage()))

            self.chart = QtCharts.QChart()
            self.chart.addSeries(self.series)
            self.chart.setTitle('Sleep Minutes')
            self.chart.setBackgroundBrush(QBrush(QColor("transparent")))


            self._chart_view.setChart(self.chart)
            self._chart_view.setVisible(True)
            
        else: 
            self._chart_view.setVisible(False)
            self.lbl_nopie.setVisible(True)

        lblTimeText = self.usable_list[0].split()[1]+" - "+self.usable_list[1].split()[1]
        if self.usable_list[0] == "No record": 
            lblTimeText=self.usable_list[0] 
        self.lblTime.setText(lblTimeText)
        self.lblNumberOfAwakenings.setText(self.usable_list[4])
        if self.usable_list[5] == "No record": 
            self.lblTimeinBed.setText(self.usable_list[5])
        else:
            self.lblTimeinBed.setText(self.usable_list[5]+" minutes")
         

    def timeline_tab(self):
        for i in self.sleep:
            for k in i:
                if k != ('No record',):
                    self.custom_widget._add_timestamp(QTime.fromString(k[0].split(' ')[1],"h:mmAP"),ArtifactType.sleepStart,k)
                    self.custom_widget._add_timestamp(QTime.fromString(k[1].split(' ')[1],"h:mmAP"),ArtifactType.sleepFinish,k)
                    print(">>",k[0])
        for i in self.heart_rate:
            for k in i:
                if k != ('No record',):
                    self.custom_widget._add_timestamp(QTime.fromString(k[0].split(' ')[1],"hh:mm:ss"),ArtifactType.heart_rate,k)
                    print(">>",k[0])
        for i in self.weight:
            for k in i:
                if k != ('No record',):
                    self.custom_widget._add_timestamp(QTime.fromString(k[4][:-3],"hh:mm"),ArtifactType.weight,k)
                    print(">>",k[4][:-3])
        for i in self.exercise:
            for k in i:
                if k != ('No record',):
                    self.custom_widget._add_timestamp(QTime.fromString(k[4].split(' ')[1][:-3],"hh:mm"),ArtifactType.exercise,k)
                    print(">>",k[4])
        for i in self.gps:
            for k in i:
                if k != ('No record',):
                    self.custom_widget._add_timestamp(QTime.fromString(k[17].split('T')[1][:5],"hh:mm"),ArtifactType.gps,k)
                    print(">>",k[17].split('T')[1][:5])

    
    def change_right_state(self, button):
        self.deleteLayout(self.frame_13.layout())

        self.pushButton.setStyleSheet(u"color: rgb(0, 0, 0)")
        self.pushButton_2.setStyleSheet(u"color: rgb(0, 0, 0)")
        self.pushButton_3.setStyleSheet(u"color: rgb(0, 0, 0)")
        self.pushButton_4.setStyleSheet(u"color: rgb(0, 0, 0)")
        self.pushButton_5.setStyleSheet(u"color: rgb(0, 0, 0)")

        button.setStyleSheet(u"color: rgb(0, 0, 0);font-weight: bold;")


        if button.objectName() == "pushButton": #0
            print("What?")
            self.currentButton=0
        elif button.objectName() == "pushButton_2": #1
            print("Where?")
            self.currentButton=1
        elif button.objectName() == "pushButton_3": #2
            print("Who?")
            self.currentButton=2
        elif button.objectName() == "pushButton_4": #3
            print("When?")
            self.currentButton=3
        elif button.objectName() == "pushButton_5": #4
            print("More Details")
            self.currentButton=4

        if(self.currentTime != 0):
            self.chosen_time(self.currentTime)
        

    @Slot(ButtonInfo)   
    def chosen_time(self, button):
        
        self.currentTime = button
        
        print(self.currentTime.query, self.currentTime.time)

        self.deleteLayout(self.frame_13.layout())
        
        
        if self.currentButton == 0:     #What
            self.lblright_state = QLabel()
            self.lblright_state.setGeometry(QRect(30, 5, 59, 16))
            self.lblright_state.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
            self.frame_13.layout().addWidget(self.lblright_state)
            if button.type == ArtifactType.sleepStart:
                self.lblright_state.setText("Sleep session started. ")
            elif button.type == ArtifactType.sleepFinish:
                self.lblright_state.setText("Sleep session finished.")
            elif button.type == ArtifactType.exercise:
                self.lblright_state.setText("New activity started. \n\nType: "+button.query[1]+".")
            elif button.type == ArtifactType.gps:
                self.lblright_state.setText("New GPS record. ")
            else:
                self.lblright_state.setText("New ¨"+button.type.name+"¨ measurement.")
            #self.pushButton.animateClick()
        elif self.currentButton == 1:   #Where
            if button.type == ArtifactType.gps:
                """ fig = Figure(width=200, height=400)
                m = folium.Map(location=[button.query[13],button.query[14]], zoom_start=13)
                fig.add_child(m) """
                overview_map = self.printMap(button.query[13],button.query[14],'75%')
                overview_map.setGeometry(QRect(30, 5, 59, 16))
                self.frame_13.layout().addWidget(overview_map)
                QApplication.processEvents()
            else:
                self.lblright_state.setText("No location record")
            #self.pushButton_2.animateClick()
        elif self.currentButton == 2:     #Who
            self.groupBox = QGroupBox()
            self.groupBox.setTitle("User Profile")
            self.groupBox.setObjectName(u"groupBox")
            self.groupBox.setStyleSheet("QGroupBox#groupBox{ border: 1px solid black;}")
            self.groupBox.setGeometry(QRect(0, 0, 200, 400))
            self.frame_13.layout().addWidget(self.groupBox)
        
            self.label_3 = QLabel(self.groupBox)
            self.label_3.setFont(self.font1)
            self.label_3.setStyleSheet("color: black;")
            self.label_3.setText("Full Name:")
            self.label_3.setGeometry(QRect(30, 40, 59, 16))


            self.lblFullname = QLabel(self.groupBox)
            self.lblFullname.setFont(self.font)
            self.lblFullname.setStyleSheet("color: black;")
            self.lblFullname.setText(self.user[0][0][4])
            self.lblFullname.setGeometry(QRect(self.label_3.x()+100, self.label_3.y(), 59, 16))

            self.label_4 = QLabel(self.groupBox)
            self.label_4.setFont(self.font1)
            self.label_4.setStyleSheet("color: black;")
            self.label_4.setText("Date of Birth:")
            self.label_4.setGeometry(QRect(30, 70, 100, 16))

            self.lblDOB = QLabel(self.groupBox)
            self.lblDOB.setFont(self.font)
            self.lblDOB.setStyleSheet("color: black;")
            self.lblDOB.setText(self.user[0][0][1])
            self.lblDOB.setGeometry(QRect(self.label_4.x()+100, self.label_4.y(), 100, 16))


            self.label_5 = QLabel(self.groupBox)
            self.label_5.setFont(self.font1)
            self.label_5.setStyleSheet("color: black;")
            self.label_5.setText("Gender:")
            self.label_5.setGeometry(QRect(30, 100, 54, 16))

            self.lblGender = QLabel(self.groupBox)
            self.lblGender.setFont(self.font)
            self.lblGender.setStyleSheet("color: black;")
            self.lblGender.setText(self.user[0][0][0])
            self.lblGender.setGeometry(QRect(self.label_5.x()+100, self.label_5.y(), 54, 16))
            

            self.label_6 = QLabel(self.groupBox)
            self.label_6.setFont(self.font1)
            self.label_6.setStyleSheet("color: black;")
            self.label_6.setText("Age:")
            self.label_6.setGeometry(QRect(30, 130, 54, 16))

            self.lblAge = QLabel(self.groupBox)
            self.lblAge.setFont(self.font)
            self.lblAge.setStyleSheet("color: black;")
            self.lblAge.setText(self.user[0][0][6])
            self.lblAge.setGeometry(QRect(self.label_6.x()+100, self.label_6.y(), 54, 16))
            

            self.label_7 = QLabel(self.groupBox)
            self.label_7.setFont(self.font1)
            self.label_7.setStyleSheet("color: black;")
            self.label_7.setText("Height:")
            self.label_7.setGeometry(QRect(30, 160, 54, 16))

            self.lblHeight = QLabel(self.groupBox)
            self.lblHeight.setFont(self.font)
            self.lblHeight.setStyleSheet("color: black;")
            
            self.lblHeight.setText('{:.2f}'.format(round(float(self.user[0][0][2])/12,2))+" ft")
            self.lblHeight.setGeometry(QRect(self.label_7.x()+100, self.label_7.y(), 54, 16))
            

            self.label_8 = QLabel(self.groupBox)
            self.label_8.setFont(self.font1)
            self.label_8.setStyleSheet("color: black;")
            self.label_8.setText("Weight:")
            self.label_8.setGeometry(QRect(30,190, 54, 16))

            self.lblWeight = QLabel(self.groupBox)
            self.lblWeight.setFont(self.font)
            self.lblWeight.setStyleSheet("color: black;")
            self.lblWeight.setText('{:.2f}'.format(float(self.user[0][0][3]))+" lbs")
            self.lblWeight.setGeometry(QRect(self.label_8.x()+100, self.label_8.y(), 54, 16))
            
            self.label_9 = QLabel(self.groupBox)
            self.label_9.setFont(self.font1)
            self.label_9.setStyleSheet("color: black;")
            self.label_9.setText("Timezone:")
            self.label_9.setGeometry(QRect(30, 220, 60, 16))

            self.lblTimezone = QLabel(self.groupBox)
            self.lblTimezone.setFont(self.font)
            self.lblTimezone.setStyleSheet("color: black;")
            self.lblTimezone.setText(self.user[0][0][5])
            self.lblTimezone.setGeometry(QRect(self.label_9.x()+100, self.label_9.y(), 150, 16))

            self.label_10 = QLabel(self.groupBox)
            self.label_10.setFont(self.font1)
            self.label_10.setStyleSheet("color: black;")
            self.label_10.setText("Average Daily Steps:")
            self.label_10.setGeometry(QRect(30, 250,750, 16))

            self.lblADS = QLabel(self.groupBox)
            self.lblADS.setFont(self.font)
            self.lblADS.setStyleSheet("color: black;")
            self.lblADS.setText(self.user[0][0][7])
            self.lblADS.setGeometry(QRect(self.label_10.x()+150, self.label_10.y(), 54, 16))

            self.labelphoto = QLabel(self.groupBox)
            self.labelphoto.setGeometry(QRect(230, 23, 240, 240))
            pixmap = QPixmap(self.photos[0][0][0])
            self.labelphoto.setPixmap(pixmap)
            self.labelphoto.setScaledContents(1)
            sizePolicy3 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            sizePolicy3.setHorizontalStretch(0)
            sizePolicy3.setVerticalStretch(0)
            sizePolicy3.setHeightForWidth(self.labelphoto.sizePolicy().hasHeightForWidth())
            self.labelphoto.setSizePolicy(sizePolicy3)
        elif self.currentButton == 3:    #When
            self.lblright_state = QLabel()
            self.lblright_state.setGeometry(QRect(30, 5, 59, 16))
            self.lblright_state.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
            self.frame_13.layout().addWidget(self.lblright_state)
            if button.type == ArtifactType.sleepStart:
                self.lblright_state.setText("Started at "+button.query[0]+", ended at " + button.query[1]+". \n\nDuration of: " + str(timedelta(microseconds=int(button.query[5])))+" hours.")
            elif button.type == ArtifactType.sleepFinish:
                self.lblright_state.setText("Started at "+button.query[0]+", ended at " + button.query[1]+". \n\nDuration of: " + str(timedelta(microseconds=int(button.query[5])))+" hours.")
            elif button.type == ArtifactType.exercise:
                self.lblright_state.setText("Started at "+button.time.toString("hh:mm")+", ended at "+ button.time.addMSecs(int(button.query[3])).toString("hh:mm")+". \n\nDuration of: " + str(timedelta(milliseconds=int(button.query[3])))+".")
            elif button.type == ArtifactType.gps:
                self.lblright_state.setText("Started at "+button.time.toString("hh:mm")+", ended at "+ button.k[17].split('T')[1][:5]+".")
                #QTime.fromString(k[17].split('T')[1][:5],"hh:mm")
            #self.pushButton_4.animateClick()
        elif self.currentButton == 4:    #More Details
            self.lblright_state = QLabel()
            self.lblright_state.setGeometry(QRect(30, 5, 59, 16))
            self.lblright_state.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
            self.frame_13.layout().addWidget(self.lblright_state)
            self.lblright_state.setText("New ¨"+button.type+"¨ measurement.")
            #self.pushButton_5.animateClick()

    
        


    def start_end_sleep_records(self):
        select_query = "SELECT `Start Time`, `End Time` FROM `sleep`" 
            
        self.cursor.execute(select_query)
        result = self.cursor.fetchall()
       

        start_time = defaultdict(list)
        end_time = defaultdict(list)
        for row in result:
            print(row)

            start_day = row[0][8:10]
            start_hour = convert(row[0].split()[1])
            print("start time" , start_day , start_hour)

            start_time[start_day].append(start_hour)

            end_day = row[1][8:10]
            end_hour = convert(row[1].split()[1])
            
            print("end time " , end_day , end_hour)

            end_time[end_day].append(end_hour)

        print(start_time)
        print(end_time)


    def show_map(self):
        coordinate = (37.8199286, -122.4782551)
        m = folium.Map(
        	tiles='Stamen Terrain',
        	zoom_start=13,
        	location=coordinate
        )
        # save map data to data object
        data = io.BytesIO()
        m.save(data, close_file=False)

        webView = QWebEngineView()
        webView.setHtml(data.getvalue().decode())
        return webView

    def create_line_chart(self, column, table):
      #  self.model = Qmode
        select_query = "SELECT `Date`, `%s` FROM `%s`" % (column,table)
            
        #print(select_query)
            
        self.cursor.execute(select_query)
        result = self.cursor.fetchall()
       
        self.series = QtCharts.QLineSeries()

        values=[]
        for row in result:
            try:
                values.append(float(row[1].replace(',','')))
                self.series.append(QPointF(float(row[0][-2:]),float(row[1].replace(',',''))))
                print(row[0][-2:], float(row[1].replace(',','')))
            except:
                values.append(row[1])
                self.series.append(QPointF(float(row[0][-2:]),row[1]))
                print(row[0][-2:], row[1])

        
        self.chart = QtCharts.QChart()
       
        self.chart.addSeries(self.series)
        self.chart.setTitle(column)
        self.chart.createDefaultAxes()

        self.axisY = QtCharts.QValueAxis()
        self.chart.setAxisY(self.axisY, self.series)
        if column == "Calories_Burned" or column == "Calories_In":
            self.axisY.setTitleText("KCals")
        if column == "Steps":
            self.axisY.setTitleText("no. of steps")
        if column == "Distance":
            self.axisY.setTitleText("Km")
        if column == "Floors":
            self.axisY.setTitleText("")
        if column == "Fat":
            self.axisY.setTitleText("%")
        if column == "Weight":
            self.axisY.setTitleText("Lbs")
        
        
        self.chart.legend().hide()
        self.chart.legend().setAlignment(Qt.AlignBottom)

        

        self.chartView = QtCharts.QChartView(self.chart)
        self.chartView.setRenderHint(QPainter.Antialiasing)

        self.chart.setAnimationOptions(QtCharts.QChart.AllAnimations)

        self.chartView.chart().setTheme(QtCharts.QChart.ChartThemeDark)


        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.chartView.sizePolicy().hasHeightForWidth())
        self.chartView.setSizePolicy(sizePolicy)
        self.chartView.setMinimumSize(QSize(0, 300))
        return self.chartView

    def create_bar_graph(self):
        select_query = "SELECT `Date`, `Steps` FROM activities"
        self.cursor.execute(select_query)
        result = self.cursor.fetchall()
        self.lineSeries = QtCharts.QLineSeries()
        cal_values=[]
        for row in result:
            cal_values.append(float(row[1].replace(',','')))
            self.lineSeries.append(QPointF(float(row[0][-2:]),float(row[1].replace(',',''))))
            print(row[0][-2:], float(row[1].replace(',','')))

        self.chart = QtCharts.QChart()
        self.chart.addSeries(self.lineSeries)
        self.chart.setTitle("Steps")


        self.chart.createDefaultAxes()
        self.axisY = QtCharts.QValueAxis()
        self.chart.setAxisY(self.axisY, self.lineSeries)
        self.axisY.setRange(0, max(cal_values)) 

        self.chart.legend().setVisible(True)
        self.chart.legend().setAlignment(Qt.AlignBottom)

        self.chartView = QtCharts.QChartView(self.chart)
        self.chartView.setRenderHint(QPainter.Antialiasing)

        self.chart.setAnimationOptions(QtCharts.QChart.AllAnimations)

        self.chartView.chart().setTheme(QtCharts.QChart.ChartThemeDark)


        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.chartView.sizePolicy().hasHeightForWidth())
        self.chartView.setSizePolicy(sizePolicy)
        self.chartView.setMinimumSize(QSize(0, 300))
        self.ui.bar_charts_cont.addWidget(self.chartView, 0, 0, 9, 9)
        self.ui.frame_18.setStyleSheet(u"background-color: transparent")



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
