#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import os
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QTextEdit, QAction, QApplication, QFileDialog ,QLabel , QScrollArea ,QMessageBox
from PyQt5.QtGui import QIcon, QPixmap, QImage 
import zipfile
import lzma
import rarfile
from io import StringIO

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

        self.OpenFAction = QAction(QIcon('icon' + os.sep + 'file.png'), 'Open', self)
        self.OpenFAction .setShortcut('Ctrl+O')
        self.OpenFAction .setStatusTip('Open Folder')
        self.OpenFAction .triggered.connect(self.OpenFolder)

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
        fileMenu.addAction(self.OpenFAction)
        fileMenu.addAction(self.ExitAction)

        fileMenu = menubar.addMenu('&View')
        fileMenu.addAction(self.FirstAction)
        fileMenu.addAction(self.PrevAction)
        fileMenu.addAction(self.NextAction)
        fileMenu.addAction(self.LastAction)

    def InitToolbar(self):
        toolbar = self.addToolBar('Toolbar')
        toolbar.addAction(self.OpenAction)
        toolbar.addAction(self.OpenFAction)
        toolbar.addAction(self.FirstAction)
        toolbar.addAction(self.PrevAction)
        toolbar.addAction(self.NextAction)
        toolbar.addAction(self.LastAction)
        toolbar.addAction(self.ExitAction)
        
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

    def ShowOpenFolderDialog(self):
        path = QFileDialog.getExistingDirectory(self, 'Open Folder', '', QFileDialog.ShowDirsOnly)
        if path:
            return os.path.realpath(path)

    def OpenFile(self):
        filepath = self.ShowOpenFileDialog()
        if filepath:
            folder,fname = os.path.split(filepath)
            self.allfiles = self.GetAllFiles(folder)
            self.fileindex = self.allfiles.index(filepath)
            self.LoadFile()

    def OpenFolder(self):
        folder = self.ShowOpenFolderDialog()
        if folder:
            self.allfiles = self.GetAllFiles(folder)
            self.fileindex = 0
            self.LoadFile()

    def LoadFile(self):
        fname = self.allfiles[self.fileindex]
        self.archive,ext = self.iscompressed(fname)
        if self.archive:
            if ext == '.zip':
                self.AcrhiveFile = zipfile.ZipFile(fname, 'r')
                AcrhiveFileList = self.AcrhiveFile.namelist()
                self.AllFilesInArchive = self.GetAllFilesInArchive(AcrhiveFileList)
                self.IndexInArchive = 0
                self.ShowImage()
            elif ext == '.rar':
                self.AcrhiveFile = rarfile.RarFile(fname, 'r')
                AcrhiveFileList = self.AcrhiveFile.namelist()
                self.AllFilesInArchive = self.GetAllFilesInArchive(AcrhiveFileList)
                self.IndexInArchive = 0
                self.ShowImage()
            else:
                self.ImageViewer.setText("Cannot load %s." % fname)
                self.pathstatus.setText(self.allfiles[self.fileindex])
                self.filenamestatus.setText(os.path.split(self.allfiles[self.fileindex])[1])
                self.indexstatus.setText(str(self.fileindex+1) + '/' + str(len(self.allfiles)))
        else:
            self.ShowImage()

    def ShowImage(self):
        if self.archive:
            fname = self.AllFilesInArchive[self.IndexInArchive]
            data =self.AcrhiveFile.read(fname)
            self.pixmap = QPixmap.fromImage(QImage.fromData(data))
        else:
            fname = self.allfiles[self.fileindex]
            self.pixmap = QPixmap(fname)

        if self.pixmap.isNull():
            self.ImageViewer.setText("Cannot load %s." % fname)
        else:
            self.ImageViewer.setPixmap(self.pixmap)
            self.ResizeViewer()

        if self.archive:
            self.pathstatus.setText(self.allfiles[self.fileindex])
            self.filenamestatus.setText(fname)
            self.indexstatus.setText(str(self.IndexInArchive+1) + '/' + str(len(self.AllFilesInArchive)))
        else:
            self.pathstatus.setText(fname)
            self.filenamestatus.setText(os.path.split(fname)[1])
            self.indexstatus.setText(str(self.fileindex+1) + '/' + str(len(self.allfiles)))

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

    def iscompressed(self,fname):
        compressed =['.zip','.rar','.7z']
        ext = os.path.splitext(fname)[1]
        if ext in compressed:
            return True,ext
        else:
            return False,ext

    def GetAllFiles(self,folder):
        file_paths = []
        for root, directories, files in os.walk(folder):
            for filename in files:
                filepath = os.path.join(root, filename)
                if self.supportfile(filepath):
                    file_paths.append(filepath)
        file_paths.sort()
        return file_paths

    def GetAllFilesInArchive(self,namelist):
        file_paths = []
        for files in namelist:
                if self.supportfile(files):
                    file_paths.append(files)
        file_paths.sort()
        return file_paths

    def PrevPage(self):
        if self.archive:
            if self.IndexInArchive>0:
                self.IndexInArchive -=1
                self.ShowImage()
        else:
            if self.fileindex>0:
                self.fileindex -=1
                self.LoadFile()

    def NextPage(self):
        if self.archive:
            if self.IndexInArchive < len(self.AllFilesInArchive)-1:
                self.IndexInArchive +=1
                self.ShowImage()
            else:
                if self.fileindex < len(self.allfiles)-1:
                    self.fileindex +=1
                    self.LoadFile()
        else:
            if self.fileindex < len(self.allfiles)-1:
                self.fileindex +=1
                self.LoadFile()

    def FirstPage(self):
        if self.archive:
            self.IndexInArchive = 0
            self.ShowImage()
        else:
            self.fileindex = 0
            self.LoadFile()

    def LastPage(self):
        if self.archive:
            self.IndexInArchive = len(self.AllFilesInArchive)-1
            self.ShowImage()
        else:
            self.fileindex = len(self.allfiles)-1
            self.LoadFile()


if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    ex = Pycomics()
    sys.exit(app.exec_())