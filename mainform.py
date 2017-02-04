#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QTextEdit, QAction, QApplication, QFileDialog ,QLabel , QScrollArea 
from PyQt5.QtGui import QIcon, QPixmap


class Pycomics(QMainWindow):

    def __init__(self):
        super().__init__()
        
        self.initUI()
        self.InitActions()
        self.InitMenus()
        self.InitToolbar()
        self.statusBar()
        
        
    def initUI(self):               
        
        self.ImageViewer = QLabel()
        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidget(self.ImageViewer)
        self.setCentralWidget(self.scrollArea)
        self.scrollArea.setAlignment(Qt.AlignCenter)
        self.setGeometry(50, 50, 800, 600)
        self.setWindowTitle('Pycomics')    
        self.show()

    def InitActions(self):
        self.ExitAction = QAction(QIcon('icon\\logout.png'), 'Exit', self)
        self.ExitAction.setShortcut('Ctrl+Q')
        self.ExitAction.setStatusTip('Exit application')
        self.ExitAction.triggered.connect(self.close)

        self.OpenAction = QAction(QIcon('icon\\file.png'), 'Open', self)
        self.OpenAction .setShortcut('Ctrl+O')
        self.OpenAction .setStatusTip('Open Files')
        self.OpenAction .triggered.connect(self.OpenFile)

    def InitMenus(self):
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(self.OpenAction)
        fileMenu.addAction(self.ExitAction)

    def InitToolbar(self):
        toolbar = self.addToolBar('Toolbar')
        toolbar.addAction(self.OpenAction)
        toolbar.addAction(self.ExitAction)

    def ShowOpenFileDialog(self):
        fname = QFileDialog.getOpenFileName(self, 'Open File', '', 'Images (*.png *.jpeg *.jpg *.bmp)')
        if fname[0]:
            return fname[0]

    def OpenFile(self):
        fname = self.ShowOpenFileDialog()
        if fname:
            self.pixmap = QPixmap(fname)
            self.ImageViewer.setPixmap(self.pixmap)
            self.ResizeViewer()

    def ResizeViewer(self):
        self.ImageViewer.resize(self.pixmap.width(),self.pixmap.height())
        self.ImageViewer.setAlignment(Qt.AlignCenter)
        
        
if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    ex = Pycomics()
    sys.exit(app.exec_())