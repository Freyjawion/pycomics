#!/usr/bin/python3
# -*- coding: utf-8 -*-

import configparser
import os
import sys
import zipfile

import rarfile
from natsort import natsorted, ns
from PyQt5.QtCore import QItemSelectionModel, Qt, QTimer
from PyQt5.QtGui import QIcon, QImage, QPixmap
from PyQt5.QtWidgets import (QAction, QActionGroup, QApplication, QFileDialog,
                             QLabel, QMainWindow, QMessageBox, QScrollArea,
                             QTextEdit)

import pwdmgr

__Title__ = 'Pycomics'
__Version__ = 'alpha 0.10'



class Pycomics(QMainWindow):

    def __init__(self):
        super().__init__()

        self.InitActions()
        self.InitConfig()
        self.InitDialog()
        self.InitMenu()
        self.InitToolbar()
        self.InitStatusbar()
        self.InitUI()

    def showEvent(self,event):
        if self.initwindowstate == 1:
            self.setWindowState(Qt.WindowMinimized)
        elif self.initwindowstate == 2:
            self.setWindowState(Qt.WindowMaximized)
        elif self.initwindowstate == 3:
            self.setWindowState(Qt.WindowMaximized)
            self.setWindowState(Qt.WindowMinimized)

    def closeEvent(self,event):
        self.SaveConfig()

    def resizeEvent(self,event):
        self.ResizeViewer()

    def InitConfig(self):
        config = configparser.ConfigParser()
        config.read('pycomics.ini')
        
        self.path = config.get('DEFAULT','path',fallback='')
        self.folder = config.get('DEFAULT','folder',fallback='')
        self.A_LastScene.setChecked(config.getboolean('DEFAULT','lastscene',fallback=False))
        self.A_OriSize.setChecked(config.getboolean('DEFAULT','orisize',fallback=False))
        self.A_FitScreen.setChecked(config.getboolean('DEFAULT','fitscreen',fallback=False))
        self.A_FitHeight.setChecked(config.getboolean('DEFAULT','fitheight',fallback=False))
        self.A_FitWidth.setChecked(config.getboolean('DEFAULT','fitwidth',fallback=False))
        self.IsArchive = config.getboolean('DEFAULT','isarchive',fallback=False)
        self.IndexInArchive = config.getint('DEFAULT','archiveindex',fallback=0)
        self.initx = config.getint('DEFAULT','x',fallback=50) 
        self.inity = config.getint('DEFAULT','y',fallback=50) 
        self.initheight = config.getint('DEFAULT','height',fallback = 600) or 600
        self.initwidth = config.getint('DEFAULT','width',fallback = 800) or 800
        self.initwindowstate = config.getint('DEFAULT','windowstate',fallback=0)

    def SaveConfig(self):
        config = configparser.ConfigParser()
        config.read('pycomics.ini')
        window_state = str(int(self.windowState()))
        config.set('DEFAULT','path',self.path)
        config.set('DEFAULT','folder',self.folder)
        config.set('DEFAULT','lastscene', str(self.A_LastScene.isChecked()))
        config.set('DEFAULT','isarchive', str(self.IsArchive))
        config.set('DEFAULT','archiveindex', str(self.IndexInArchive))
        config.set('DEFAULT','orisize', str(self.A_OriSize.isChecked()))
        config.set('DEFAULT','fitscreen', str(self.A_FitScreen.isChecked()))
        config.set('DEFAULT','fitheight', str(self.A_FitHeight.isChecked()))
        config.set('DEFAULT','fitwidth', str(self.A_FitWidth.isChecked()))
        config.set('DEFAULT','windowstate',window_state)
        if window_state == '0':
            config.set('DEFAULT','x',str(self.geometry().x()))
            config.set('DEFAULT','y',str(self.geometry().y()))
            config.set('DEFAULT','height',str(self.geometry().height()))
            config.set('DEFAULT','width',str(self.geometry().width()))

        with open('pycomics.ini','w') as configfile:
            config.write(configfile)

    def InitDialog(self):
        self.PwdDialog = pwdmgr.PwdManager()

    def InitUI(self):
        self.ImageViewer = QLabel()
        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidget(self.ImageViewer)
        self.setCentralWidget(self.scrollArea)
        self.scrollArea.setAlignment(Qt.AlignCenter)
        self.setWindowTitle(__Title__ + ' ' + __Version__)
        self.setGeometry(self.initx,self.inity ,self.initwidth,self.initheight)
        self.show()

    def InitActions(self):
        self.A_Exit = QAction(QIcon('icon' + os.sep + 'logout.png'), 'Exit', self)
        self.A_Exit.setShortcut('ESC')
        self.A_Exit.setStatusTip('Exit application')
        self.A_Exit.triggered.connect(self.close)

        self.A_Open = QAction(QIcon('icon' + os.sep + 'file.png'), 'Open Files', self)
        self.A_Open .setShortcut('Ctrl+O')
        self.A_Open .setStatusTip('Open Files')
        self.A_Open .triggered.connect(self.OpenFile)

        self.A_OpenFolder = QAction(QIcon('icon' + os.sep + 'file.png'), 'Open Folder', self)
        self.A_OpenFolder .setShortcut('Ctrl+O')
        self.A_OpenFolder .setStatusTip('Open Folder')
        self.A_OpenFolder .triggered.connect(self.OpenFolder)

        self.A_Prev = QAction(QIcon('icon' + os.sep + 'file.png'), 'PreviousPage', self)
        self.A_Prev .setShortcut('Left')
        self.A_Prev .setStatusTip('PreviousPage')
        self.A_Prev .triggered.connect(self.PrevPage)

        self.A_Next = QAction(QIcon('icon' + os.sep + 'file.png'), 'NextPage', self)
        self.A_Next .setShortcut('Right')
        self.A_Next .setStatusTip('NextPage')
        self.A_Next .triggered.connect(self.NextPage)

        self.A_First = QAction(QIcon('icon' + os.sep + 'file.png'), 'FirstPage', self)
        self.A_First .setShortcut('home')
        self.A_First .setStatusTip('FirstPage')
        self.A_First .triggered.connect(self.FirstPage)

        self.A_Last = QAction(QIcon('icon' + os.sep + 'file.png'), 'LastPage', self)
        self.A_Last .setShortcut('end')
        self.A_Last .setStatusTip('LastPage')
        self.A_Last .triggered.connect(self.LastPage)

        self.A_PwdManager = QAction(QIcon('icon' + os.sep + 'file.png'), 'Password Manager', self)
        self.A_PwdManager .setStatusTip('Password Manager')
        self.A_PwdManager .triggered.connect(self.ShowPwdManager)

        self.A_LastScene = QAction(QIcon('icon' + os.sep + 'file.png'),'Last Scene',self,checkable=True)
        self.A_LastScene .setCheckable = True
        self.A_LastScene .setStatusTip('LastScene')

        self.A_OriSize = QAction(QIcon('icon' + os.sep + 'file.png'),'Original Size',self,checkable=True)
        self.A_OriSize .setCheckable = True
        self.A_OriSize .setStatusTip('Original Size')

        self.A_FitScreen = QAction(QIcon('icon' + os.sep + 'file.png'),'Fit Screen',self,checkable=True)
        self.A_FitScreen .setCheckable = True
        self.A_FitScreen .setStatusTip('FitScreen')

        self.A_FitHeight = QAction(QIcon('icon' + os.sep + 'file.png'),'Fit Height',self,checkable=True)
        self.A_FitHeight .setCheckable = True
        self.A_FitHeight .setStatusTip('FitHeight')

        self.A_FitWidth = QAction(QIcon('icon' + os.sep + 'file.png'),'Fit Width',self,checkable=True)
        self.A_FitWidth .setCheckable = True
        self.A_FitWidth .setStatusTip('FitWidth')

        self.A_FitGroup = QActionGroup(self)
        self.A_FitGroup.addAction(self.A_OriSize)
        self.A_FitGroup.addAction(self.A_FitScreen)
        self.A_FitGroup.addAction(self.A_FitHeight)
        self.A_FitGroup.addAction(self.A_FitWidth)
        self.A_OriSize.setChecked(True)
        self.A_FitGroup.triggered.connect(self.ResizeViewer)

    def InitMenu(self):
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(self.A_Open)
        fileMenu.addAction(self.A_OpenFolder)
        fileMenu.addAction(self.A_Exit)

        fileMenu = menubar.addMenu('&View')
        fileMenu.addAction(self.A_First)
        fileMenu.addAction(self.A_Prev)
        fileMenu.addAction(self.A_Next)
        fileMenu.addAction(self.A_Last)

        fileMenu = menubar.addMenu('&Settings')
        fileMenu.addAction(self.A_PwdManager)
        fileMenu.addAction(self.A_LastScene)

    def InitToolbar(self):
        self.toolBar = self.addToolBar('Toolbar')
        self.toolBar.setMovable(False)
        self.toolBar.addAction(self.A_Open)
        self.toolBar.addAction(self.A_OpenFolder)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.A_First)
        self.toolBar.addAction(self.A_Prev)
        self.toolBar.addAction(self.A_Next)
        self.toolBar.addAction(self.A_Last)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.A_OriSize)
        self.toolBar.addAction(self.A_FitScreen)
        self.toolBar.addAction(self.A_FitHeight)
        self.toolBar.addAction(self.A_FitWidth)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.A_LastScene)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.A_Exit)

    def InitStatusbar(self): 
        statusbar = self.statusBar()
        self.StatusPath = QLabel()
        self.StatusFilename = QLabel()
        self.StatusIndex = QLabel()
        self.StatusSize = QLabel()
        statusbar.addWidget(self.StatusPath)
        statusbar.addPermanentWidget(self.StatusFilename)
        statusbar.addPermanentWidget(self.StatusIndex)
        statusbar.addPermanentWidget(self.StatusSize)

    def InitLastScene(self):
        if self.A_LastScene.isChecked() and self.path:
            self.LoadFile(self.path)

    def ShowOpenFileDialog(self):
        path = QFileDialog.getOpenFileName(self, 'Open File','', 'Support Files (*.png *.jpeg *.jpg *.bmp *.zip *.rar *.7z);;Images (*.png *.jpeg *.jpg *.bmp);;Zip (*.zip)')
        if path[0]:
            return os.path.realpath(path[0])

    def ShowOpenFolderDialog(self):
        path = QFileDialog.getExistingDirectory(self, 'Open Folder','', QFileDialog.ShowDirsOnly)
        if path:
            return os.path.realpath(path)

    def OpenFile(self):
        filepath = self.ShowOpenFileDialog()
        if filepath:
            self.folderpath = ''
            self.CloseArchive()
            self.LoadFile(filepath)

    def OpenFolder(self):
        folder = self.ShowOpenFolderDialog()
        if folder:
            self.folderpath = folder
            self.CloseArchive()
            self.LoadFile(folder)

    def LoadFile(self,path):
        if os.path.isdir(path):
            folder = path
            fname = ''
        elif os.path.isfile(path):
            folder,fname = os.path.split(path)
        else:
            self.LoadFailed()
            return
        if self.folder:
            if not os.path.isdir(self.folder):
                self.folder = folder
            self.allfiles = self.GetAllFiles(self.folder)
        else:
            self.allfiles = self.GetAllFiles(folder)
        if len(self.allfiles) == 0:
            return
        if fname:
            self.fileindex = self.allfiles.index(path)
        else:
            self.fileindex = 0
            path = self.allfiles[0]
            fname = os.path.basename(path)
        self.path = path
        self.IsArchive,self.ext = self.IsCompressed(path)
        if self.IsArchive:
            if self.ext == '.zip':
                self.ArchiveFile = zipfile.ZipFile(path, 'r')
                AcrhiveFileList = self.ArchiveFile.namelist()
                self.ArchiveInfo = self.ArchiveFile.infolist()
                self.IsEncrypted = self.ArchiveInfo[0].flag_bits & 0x1 
                if self.IsEncrypted:
                    self.Pass,self.Pwd = self.DecryptArchive(self.ArchiveFile)
                    if self.Pass:
                        pass
                    else:
                        self.LoadFailed()
                        return
                else: 
                    self.Pwd = None
                self.AllFilesInArchive = self.GetAllFilesInArchive(AcrhiveFileList)
                self.ShowImage()
            elif self.ext == '.rar':
                self.ArchiveFile = rarfile.RarFile(path, 'r')
                AcrhiveFileList = self.ArchiveFile.namelist()
                self.ArchiveInfo = self.ArchiveFile.infolist()
                self.IsEncrypted = self.ArchiveInfo[0].needs_password()
                if self.IsEncrypted:
                    self.Pass,self.Pwd = self.DecryptArchive(self.ArchiveFile)
                    if self.Pass:
                        pass
                    else:
                        self.LoadFailed()
                        return
                else: 
                    self.Pwd = None
                self.AllFilesInArchive = self.GetAllFilesInArchive(AcrhiveFileList)
                self.ShowImage()
            elif self.ext == '.7z':
                self.Pass = False
                self.LoadFailed()
            else:
                self.Pass = False
                self.LoadFailed()
        else:
            self.IndexInArchive = 0
            self.ShowImage()

    def ShowImage(self):
        if self.IsArchive:
            fname = self.AllFilesInArchive[self.IndexInArchive]
            data =self.ArchiveFile.read(fname,self.Pwd)
            self.pixmap = QPixmap.fromImage(QImage.fromData(data))
        else:
            fname = self.allfiles[self.fileindex]
            self.pixmap = QPixmap(fname)

        if self.pixmap.isNull():
            self.LoadFailed()
            self.UpdateStatus()
        else:
            self.ImageViewer.setPixmap(self.pixmap)
            self.UpdateStatus()
            self.ResizeViewer()

    def UpdateStatus(self):
        if self.IsArchive:
            fname = self.AllFilesInArchive[self.IndexInArchive]
            self.StatusPath.setText(self.allfiles[self.fileindex])
            self.StatusFilename.setText(fname)
            self.StatusIndex.setText(str(self.IndexInArchive+1) + '/' + str(len(self.AllFilesInArchive)))
        else:
            fname = self.allfiles[self.fileindex]
            self.StatusPath.setText(fname)
            self.StatusFilename.setText(os.path.split(fname)[1])
            self.StatusIndex.setText(str(self.fileindex+1) + '/' + str(len(self.allfiles)))

        try:
            h = str(self.pixmap.height())
            w = str(self.pixmap.width())
            self.StatusSize.setText(w + '*' + h)
        except:
            pass

    def ResizeViewer(self):
        try:
            if self.A_OriSize.isChecked():
                scale = 1
            else:
                viewh = self.height() - self.menuBar().height() - self.toolBar.height() - self.statusBar().height() -2
                vieww = self.width() -2
                hscale=viewh/self.pixmap.height()
                wscale=vieww/self.pixmap.width()
                if self.A_FitScreen.isChecked():
                    scale = min(hscale,wscale)
                elif self.A_FitWidth.isChecked():
                    scale = wscale
                elif self.A_FitHeight.isChecked():
                    scale = hscale
                else:
                    scale = 1

            self.ImageViewer.resize(self.pixmap.width()*scale,self.pixmap.height()*scale)
            self.ImageViewer.setScaledContents(True)
            self.pixmap.scaled(self.ImageViewer.size(),Qt.KeepAspectRatio, transformMode = Qt.SmoothTransformation)
            self.ImageViewer.setAlignment(Qt.AlignCenter)
        except:
            pass

    def SupportFile(self,fname):
        supportext =['.jpg','.png','.jpeg','.bmp','.zip','.rar','.7z']
        ext = os.path.splitext(fname)[1]
        if ext in supportext:
            return True
        else:
            return False
    
    def SupportFileInArchive(self,fname):
        supportext =['.jpg','.png','.jpeg','.bmp']
        ext = os.path.splitext(fname)[1]
        if ext in supportext:
            return True
        else:
            return False

    def IsCompressed(self,fname):
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
                if self.SupportFile(filepath):
                    file_paths.append(filepath)
        file_paths = natsorted(file_paths,alg=ns.PATH)
        return file_paths

    def GetAllFilesInArchive(self,namelist):
        support_file = []
        for files in namelist:
                if self.SupportFileInArchive(files):
                    support_file.append(files)
        file_paths = natsorted(support_file,alg=ns.PATH)
        return support_file

    def PrevPage(self):
        if self.IsArchive:
            if self.IndexInArchive>0:
                self.IndexInArchive -=1
                self.ShowImage()
            else:
                if self.fileindex>0:
                    self.CloseArchive()
                    self.fileindex -=1
                    self.LoadFile(self.allfiles[self.fileindex])
        else:
            if self.fileindex>0:
                self.fileindex -=1
                self.LoadFile(self.allfiles[self.fileindex])

    def NextPage(self):
        if self.IsArchive:
            if self.IndexInArchive < len(self.AllFilesInArchive)-1:
                self.IndexInArchive +=1
                self.ShowImage()
            else:
                if self.fileindex < len(self.allfiles)-1:
                    self.CloseArchive()
                    self.fileindex +=1
                    self.LoadFile(self.allfiles[self.fileindex])
        else:
            if self.fileindex < len(self.allfiles)-1:
                self.fileindex +=1
                self.LoadFile(self.allfiles[self.fileindex])

    def FirstPage(self):
        if self.IsArchive:
            self.IndexInArchive = 0
            self.ShowImage()
        else:
            self.fileindex = 0
            self.LoadFile(self.allfiles[self.fileindex])

    def LastPage(self):
        if self.IsArchive:
            self.IndexInArchive = len(self.AllFilesInArchive)-1
            self.ShowImage()
        else:
            self.fileindex = len(self.allfiles)-1
            self.LoadFile(self.allfiles[self.fileindex])

    def LoadPwd(self):
        if not os.path.exists(r'password.pwd'):
            open("password.pwd","wb").close()
        if self.ext == '.zip':
            pwdf = open('password.pwd','rb')
        else:
            pwdf = open('password.pwd','r')
        self.PwdList = pwdf.read().splitlines()
        pwdf.close()

    def DecryptArchive(self,archivefile):
        self.LoadPwd()
        self.IsPwdChanged = True
        IsPwdFound = False
        while self.IsPwdChanged and not IsPwdFound:
            for password in self.PwdList:
                try:
                    data = self.ArchiveFile.read(self.ArchiveInfo[0].filename,password)
                    IsPwdFound = True
                    return IsPwdFound,password
                except:
                    pass
            self.ShowPwdManager()
        return IsPwdFound,None

    def LoadFailed(self):
        if self.IsArchive and not self.Pass:
            self.IsArchive = False

        self.UpdateStatus()

        self.ImageViewer.setText("Can not load %s" % self.StatusFilename.text())
        self.ImageViewer.resize(300,50)
        self.ImageViewer.setAlignment(Qt.AlignCenter)

    def ShowPwdManager(self):
        if self.PwdDialog.exec_():
            self.IsPwdChanged = True
            self.LoadPwd()
        else:
            self.IsPwdChanged = False

    def CloseArchive(self):
        self.IndexInArchive = 0
        try:
            self.ArchiveFile.close()
        except AttributeError:
            pass

def run():
    app = QApplication(sys.argv)
    ex = Pycomics()
    QTimer.singleShot(1, ex.InitLastScene)
    sys.exit(app.exec_())
