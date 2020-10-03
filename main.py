# Created by Hao Jin on 2020/10/03.
# Copyright (c) 2020 Hao Jin. All rights reserved.

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import (QTableWidgetItem, QSizePolicy, QVBoxLayout, QWidget,
    QLabel, QGridLayout)
from PyQt5.QtCore import Qt
from gui import Ui_MainWindow  # import generated file
import sys
import json
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Qt5Agg') # Make sure that we are using QT5
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# config
DEBUG = True
fileConfig = 'config.json'
totalChannel = 32

plt.rc('font', family='serif', serif='Times')
plt.rc('text', usetex=True)
plt.rc('xtick', labelsize=8)
plt.rc('ytick', labelsize=8)
plt.rc('axes', labelsize=8)


# basic canvas for matplotlib figure
class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        fig.subplots_adjust(left=.1, bottom=.16, right=.99, top=.97)
        self.axes = fig.add_subplot(111)
        self.compute_initial_figure()
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Fixed)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        pass

# static figure
class MyStaticMplCanvas(MyMplCanvas):
    """Simple canvas with a sine plot."""
    def compute_initial_figure(self):
        t = np.arange(0.0, 5.0, 0.01)
        s = np.sin(2*np.pi*t)
        self.axes.plot(t, s)


# # static channel plot
# class StaticChannelPlot(MyMplCanvas):
#     """ static channel plot, data from file"""
#     def computer_initial_figure(self):


class MyMainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.readJson()

        # set channels
        for i in range(totalChannel):
            exec("self.ui.checkBox_"+str(i+1)+".stateChanged.connect(lambda: self.channelState(self.ui.checkBox_"+str(i+1)+"))", {'self': self})
            if i+1 in self.config["channels"]:
                exec("self.ui.checkBox_"+str(i+1)+".setChecked(True)")
        self.ui.btnSelectAll.clicked.connect(self.channelSelectAll)
        self.ui.btnSelectNone.clicked.connect(self.channelSelectNone)
        
        # set data from file or real-time
        if self.config["dataFromFile"]:
            self.ui.rbDataFromFile.setChecked(True)
            self.ui.btnLoad.setEnabled(True)
            self.ui.btnConn.setEnabled(False)
            self.ui.btnDisconn.setEnabled(False)
        else:
            self.ui.rbRealTimeData.setChecked(True)
            self.ui.btnLoad.setEnabled(False)
            self.ui.btnConn.setEnabled(True)
            self.ui.btnDisconn.setEnabled(True)
        self.ui.rbDataFromFile.toggled.connect(lambda: self.dataSource(self.ui.rbDataFromFile))

        # set time series plot
        self.grid = QGridLayout()
        # self.vbox = QVBoxLayout()
        self.ui.scrollAreaWidgetContents.setLayout(self.grid)
        self.setTimeSeriesPlot()
        self.ui.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.ui.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.ui.btnSetTimeSeriesPlot.clicked.connect(self.setTimeSeriesPlot)

        # self.setWindowIcon(QtGui.QIcon("./assets/zju.jpg"))
    
    def setTimeSeriesPlot(self):
        for i in reversed(range(self.grid.count())): 
            # print(self.grid.itemAt(i).widget())
            self.grid.itemAt(i).widget().setParent(None)
        widget = QWidget() 
        j = 0
        for i in range(totalChannel):
            if i+1 in self.config["channels"]:
                exec("self.channel"+str(i+1)+"Plot = MyStaticMplCanvas(widget, width=6.8, height=1.2, dpi=100)", 
                    {'self': self, 'MyStaticMplCanvas': MyStaticMplCanvas, 'widget': widget})
                exec("self.grid.addWidget(self.channel"+str(i+1)+"Plot, j, 1)", {'self': self, 'j': j, '1': int(1)})
                j += 1
        # self.vbox.addStretch(1)
    
    def dataSource(self, rb):
        """
        choose the source of data
        - data from file
        - real-time data
        """
        if rb.isChecked():
            self.ui.rbDataFromFile.setChecked(True)
            self.ui.btnLoad.setEnabled(True)
            self.ui.btnConn.setEnabled(False)
            self.ui.btnDisconn.setEnabled(False)
            self.config["dataFromFile"] = True
            print(self.config["dataFromFile"])
        else:
            self.ui.rbRealTimeData.setChecked(True)
            self.ui.btnLoad.setEnabled(False)
            self.ui.btnConn.setEnabled(True)
            self.ui.btnDisconn.setEnabled(True)
            self.config["dataFromFile"] = False
            print(self.config["dataFromFile"])
    
    def channelState(self, cb):
        """
        update the channel list when checkboxes' state change
        """
        channel = int(cb.text().split()[1])
        if cb.isChecked():
            if channel not in self.config["channels"]:
                self.config["channels"].append(channel) 
                print(self.config["channels"])
        else:
            if channel in self.config["channels"]:
                self.config["channels"].remove(channel) 
                print(self.config["channels"])
        # self.setTimeSeriesPlot()

    def channelSelectAll(self):
        """
        select all the channels
        """
        for i in range(totalChannel):
            exec("self.ui.checkBox_"+str(i+1)+".setChecked(True)")

    def channelSelectNone(self):
        """
        deselect all the channels
        """
        for i in range(totalChannel):
            exec("self.ui.checkBox_"+str(i+1)+".setChecked(False)")

    def test(self):
        print("just a test")

    def readJson(self):
        """
        reda config data from json file
        """
        try:
            with open(fileConfig) as f:
                self.config = json.load(f)
                if DEBUG:
                    print("load config: ", self.config)
        except FileNotFoundError:
            self.config = {
                "channels": [],
                "dataFromFile": True
            }
            with open(fileConfig, 'w') as f:
                json.dump(self.config, f, indent=4)

    def fileQuit(self):
        """
        save config data to json file
        """
        with open(fileConfig, 'w') as f:
            json.dump(self.config, f, indent=4)
        self.close()
    
    def closeEvent(self, ce):
        self.fileQuit()

    

app = QtWidgets.QApplication([])
application = MyMainWindow()
application.show()
sys.exit(app.exec())