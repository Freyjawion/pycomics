#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import QMainWindow, QTextEdit, QAction, QApplication, QFileDialog ,QLabel
from PyQt5.QtGui import QIcon, QPixmap


class Example(QMainWindow):

    def __init__(self):
        super().__init__()
        
        self.initUI()
        
        
    def initUI(self):               
        
        self.ImageViewer = QLabel()
        self.setCentralWidget(self.ImageViewer)

        exitAction = QAction(QIcon('icon\\logout.png'), 'Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)

        OpenAction = QAction(QIcon('icon\\file.png'), 'Open', self)
        OpenAction.setShortcut('Ctrl+O')
        OpenAction.setStatusTip('Open Files')
        OpenAction.triggered.connect(self.showDialog)

        self.statusBar()

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(OpenAction)
        fileMenu.addAction(exitAction)
        
        toolbar = self.addToolBar('Toolbar')
        toolbar.addAction(OpenAction)
        toolbar.addAction(exitAction)
        
        self.setGeometry(50, 50, 800, 600)
        self.setWindowTitle('Pycomics')    
        self.show()

    def showDialog(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', '/home')
        if fname[0]:
            self.pixmap = QPixmap(fname[0])
            self.ImageViewer.setPixmap(self.pixmap)
            self.resize(self.pixmap.width(),self.pixmap.height())

        
        
if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())