#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import os
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QTextEdit, QAction, QApplication, QFileDialog ,QLabel , QScrollArea ,QMessageBox
from PyQt5.QtGui import QIcon, QPixmap

__Title__ = 'Pycomics'
__Version__ = 'beta 0.01'


class Pycomics(QMainWindow):
    

    def __init__(self):
        super().__init__()
        
        self.initUI()
        self.InitActions()
        self.InitMenus()
        self.InitToolbar()
        self.InitStatusbar()
             
    def initUI(self):               
        
        self.ImageViewer = QLabel()
        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidget(self.ImageViewer)
        self.setCentralWidget(self.scrollArea)
        self.scrollArea.setAlignment(Qt.AlignCenter)
        self.setGeometry(50, 50, 800, 600)
        self.setWindowTitle(__Title__ + ' ' + __Version__)    
        self.show()

    def InitActions(self):
        self.ExitAction = QAction(QIcon('icon' + os.sep + 'logout.png'), 'Exit', self)
        self.ExitAction.setShortcut('Ctrl+Q')
        self.ExitAction.setStatusTip('Exit application')
        self.ExitAction.triggered.connect(self.close)

        self.OpenAction = QAction(QIcon('icon' + os.sep + 'file.png'), 'Open', self)
        self.OpenAction .setShortcut('Ctrl+O')
        self.OpenAction .setStatusTip('Open Files')
        self.OpenAction .triggered.connect(self.OpenFile)

        self.PrevAction = QAction(QIcon('icon' + os.sep + 'file.png'), 'PreviousPage', self)
        self.PrevAction .setShortcut('Left')
        self.PrevAction .setStatusTip('PreviousPage')
        self.PrevAction .triggered.connect(self.PrevPage)

        self.NextAction = QAction(QIcon('icon' + os.sep + 'file.png'), 'NextPage', self)
        self.NextAction .setShortcut('Right')
        self.NextAction .setStatusTip('NextPage')
        self.NextAction .triggered.connect(self.NextPage)

        self.FirstAction = QAction(QIcon('icon' + os.sep + 'file.png'), 'FirstPage', self)
        self.FirstAction .setShortcut('home')
        self.FirstAction .setStatusTip('FirstPage')
        self.FirstAction .triggered.connect(self.FirstPage)

        self.LastAction = QAction(QIcon('icon' + os.sep + 'file.png'), 'LastPage', self)
        self.LastAction .setShortcut('end')
        self.LastAction .setStatusTip('LastPage')
        self.LastAction .triggered.connect(self.LastPage)

    def InitMenus(self):
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(self.OpenAction)
        fileMenu.addAction(self.ExitAction)

        fileMenu = menubar.addMenu('&View')
        fileMenu.addAction(self.FirstAction)
        fileMenu.addAction(self.PrevAction)
        fileMenu.addAction(self.NextAction)
        fileMenu.addAction(self.LastAction)

    def InitToolbar(self):
        toolbar = self.addToolBar('Toolbar')
        toolbar.addAction(self.OpenAction)
        toolbar.addAction(self.ExitAction)
        toolbar.addAction(self.FirstAction)
        toolbar.addAction(self.PrevAction)
        toolbar.addAction(self.NextAction)
        toolbar.addAction(self.LastAction)

    def InitStatusbar(self):
        self.statusbar = self.statusBar()
        self.pathstatus = QLabel()
        self.filenamestatus = QLabel()
        self.indexstatus = QLabel()
        self.statusbar.addWidget(self.pathstatus)
        self.statusbar.addPermanentWidget(self.filenamestatus)
        self.statusbar.addPermanentWidget(self.indexstatus)

    def ShowOpenFileDialog(self):
        path = QFileDialog.getOpenFileName(self, 'Open File', '', 'Support Files (*.png *.jpeg *.jpg *.bmp *.zip *.rar *.7z);;Images (*.png *.jpeg *.jpg *.bmp);;Zip (*.zip)')
        if path[0]:
            return os.path.realpath(path[0])

    def OpenFile(self):
        filepath = self.ShowOpenFileDialog()
        if filepath:
            folder,fname = os.path.split(filepath)
            self.allfiles = self.GetAllFiles(folder)
            self.fileindex = self.allfiles.index(filepath)
            self.ShowImage()

    def ShowImage(self):
        self.pixmap = QPixmap(self.allfiles[self.fileindex])
        if self.pixmap.isNull():
            QMessageBox.information(self, __Title__,"Cannot load %s." % fname)
            return
        self.ImageViewer.setPixmap(self.pixmap)
        self.ResizeViewer()
        self.pathstatus.setText(self.allfiles[self.fileindex])
        self.filenamestatus.setText(os.path.split(self.allfiles[self.fileindex])[1])
        self.indexstatus.setText(str(self.fileindex) + '/' + str(len(self.allfiles)+1))

    def ResizeViewer(self):
        self.ImageViewer.resize(self.pixmap.width(),self.pixmap.height())
        self.ImageViewer.setAlignment(Qt.AlignCenter)
    
    def supportfile(self,fname):
        supportext =['.jpg','.png','.jpeg','.bmp','.zip','.rar','.7z']
        ext = os.path.splitext(fname)[1]
        if ext in supportext:
            return True
        else:
            return False

    def GetAllFiles(self,folder):
        file_paths = []
        for root, directories, files in os.walk(folder):
            for filename in files:
                filepath = os.path.join(root, filename)
                if self.supportfile(filepath):
                    file_paths.append(filepath)
        file_paths.sort()
        return file_paths

    def PrevPage(self):
        if self.fileindex>0:
            self.fileindex -=1
            self.ShowImage()

    def NextPage(self):
        if self.fileindex < len(self.allfiles)-1:
            self.fileindex +=1
            self.ShowImage()

    def FirstPage(self):
        self.fileindex = 0
        self.ShowImage()

    def LastPage(self):
        self.fileindex = len(self.allfiles)-1
        self.ShowImage()


if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    ex = Pycomics()
    sys.exit(app.exec_())