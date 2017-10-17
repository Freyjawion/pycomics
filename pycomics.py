#!/usr/bin/python3
# -*- coding: utf-8 -*-

import configparser
import os
import sys
import zipfile

import rarfile
from PyQt5.QtCore import QItemSelectionModel, Qt, QTimer
from PyQt5.QtGui import QIcon, QImage, QPixmap
from PyQt5.QtWidgets import (QAction, QActionGroup, QApplication, QFileDialog,
                             QLabel, QMainWindow, QMessageBox, QScrollArea,
                             QTextEdit)

import listmgr
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
        pass

    def closeEvent(self,event):
        self.SaveConfig()

    def resizeEvent(self,event):
        self.ResizeViewer()

    def InitConfig(self):
        config = configparser.ConfigParser()
        config.read('pycomics.ini')
        
        self.path = config.get('DEFAULT','path',fallback='')
        self.folder = config.get('DEFAULT','folder',fallback='')
        self.SortOrder = config.getint('DEFAULT','sortorder',fallback=0)
        self.SortAlg = config.getint('DEFAULT','sortalg',fallback=0)
        self.ALastScene.setChecked(config.getboolean('DEFAULT','lastscene',fallback=False))
        self.AOriSize.setChecked(config.getboolean('DEFAULT','orisize',fallback=False))
        self.AFitScreen.setChecked(config.getboolean('DEFAULT','fitscreen',fallback=False))
        self.AFitHeight.setChecked(config.getboolean('DEFAULT','fitheight',fallback=False))
        self.AFitWidth.setChecked(config.getboolean('DEFAULT','fitwidth',fallback=False))
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
        config.set('DEFAULT','sortorder',str(self.SortOrder))
        config.set('DEFAULT','sortalg',str(self.SortAlg))
        config.set('DEFAULT','lastscene', str(self.ALastScene.isChecked()))
        config.set('DEFAULT','isarchive', str(self.IsArchive))
        config.set('DEFAULT','archiveindex', str(self.IndexInArchive))
        config.set('DEFAULT','orisize', str(self.AOriSize.isChecked()))
        config.set('DEFAULT','fitscreen', str(self.AFitScreen.isChecked()))
        config.set('DEFAULT','fitheight', str(self.AFitHeight.isChecked()))
        config.set('DEFAULT','fitwidth', str(self.AFitWidth.isChecked()))
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
        self.ListDialog = listmgr.ListManager()
        self.ListDialog.SortOrder[self.SortOrder].click()
        self.ListDialog.SortAlg[self.SortAlg].click()

    def InitUI(self):
        self.ImageViewer = QLabel()
        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidget(self.ImageViewer)
        self.setCentralWidget(self.scrollArea)
        self.scrollArea.setAlignment(Qt.AlignCenter)
        self.setWindowTitle(__Title__ + ' ' + __Version__)
        self.setGeometry(self.initx,self.inity ,self.initwidth,self.initheight)
        self.AllFiles = []
        self.show()
        if self.initwindowstate == 1:
            self.setWindowState(Qt.WindowMinimized)
        elif self.initwindowstate == 2:
            self.setWindowState(Qt.WindowMaximized)
        elif self.initwindowstate == 3:
            self.setWindowState(Qt.WindowMaximized)
            self.setWindowState(Qt.WindowMinimized)

    def InitActions(self):
        self.AExit = QAction(QIcon('icon' + os.sep + 'logout.png'), 'Exit', self)
        self.AExit.setShortcut('ESC')
        self.AExit.setStatusTip('Exit application')
        self.AExit.triggered.connect(self.close)

        self.AOpen = QAction(QIcon('icon' + os.sep + 'file.png'), 'Open Files', self)
        self.AOpen .setShortcut('Ctrl+O')
        self.AOpen .setStatusTip('Open Files')
        self.AOpen .triggered.connect(self.OpenFile)

        self.AOpenFolder = QAction(QIcon('icon' + os.sep + 'file.png'), 'Open Folder', self)
        self.AOpenFolder .setShortcut('Ctrl+O')
        self.AOpenFolder .setStatusTip('Open Folder')
        self.AOpenFolder .triggered.connect(self.OpenFolder)

        self.APrev = QAction(QIcon('icon' + os.sep + 'file.png'), 'PreviousPage', self)
        self.APrev .setShortcut('Left')
        self.APrev .setStatusTip('PreviousPage')
        self.APrev .triggered.connect(self.PrevPage)

        self.ANext = QAction(QIcon('icon' + os.sep + 'file.png'), 'NextPage', self)
        self.ANext .setShortcut('Right')
        self.ANext .setStatusTip('NextPage')
        self.ANext .triggered.connect(self.NextPage)

        self.AFirst = QAction(QIcon('icon' + os.sep + 'file.png'), 'FirstPage', self)
        self.AFirst .setShortcut('home')
        self.AFirst .setStatusTip('FirstPage')
        self.AFirst .triggered.connect(self.FirstPage)

        self.ALast = QAction(QIcon('icon' + os.sep + 'file.png'), 'LastPage', self)
        self.ALast .setShortcut('end')
        self.ALast .setStatusTip('LastPage')
        self.ALast .triggered.connect(self.LastPage)

        self.ALastScene = QAction(QIcon('icon' + os.sep + 'file.png'),'Last Scene',self,checkable=True)
        self.ALastScene .setCheckable = True
        self.ALastScene .setStatusTip('LastScene')

        self.AOriSize = QAction(QIcon('icon' + os.sep + 'file.png'),'Original Size',self,checkable=True)
        self.AOriSize .setCheckable = True
        self.AOriSize .setStatusTip('Original Size')

        self.AFitScreen = QAction(QIcon('icon' + os.sep + 'file.png'),'Fit Screen',self,checkable=True)
        self.AFitScreen .setCheckable = True
        self.AFitScreen .setStatusTip('FitScreen')

        self.AFitHeight = QAction(QIcon('icon' + os.sep + 'file.png'),'Fit Height',self,checkable=True)
        self.AFitHeight .setCheckable = True
        self.AFitHeight .setStatusTip('FitHeight')

        self.AFitWidth = QAction(QIcon('icon' + os.sep + 'file.png'),'Fit Width',self,checkable=True)
        self.AFitWidth .setCheckable = True
        self.AFitWidth .setStatusTip('FitWidth')

        self.AFitGroup = QActionGroup(self)
        self.AFitGroup.addAction(self.AOriSize)
        self.AFitGroup.addAction(self.AFitScreen)
        self.AFitGroup.addAction(self.AFitHeight)
        self.AFitGroup.addAction(self.AFitWidth)
        self.AOriSize.setChecked(True)
        self.AFitGroup.triggered.connect(self.ResizeViewer)

        self.APwdManager = QAction(QIcon('icon' + os.sep + 'file.png'), 'Password Manager', self)
        self.APwdManager .setStatusTip('Password Manager')
        self.APwdManager .triggered.connect(self.ShowPwdManager)

        self.AListManager = QAction(QIcon('icon' + os.sep + 'file.png'), 'List Manager', self)
        self.AListManager .setStatusTip('List Manager')
        self.AListManager .triggered.connect(self.ShowListManager)

    def InitMenu(self):
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(self.AOpen)
        fileMenu.addAction(self.AOpenFolder)
        fileMenu.addAction(self.AExit)

        fileMenu = menubar.addMenu('&View')
        fileMenu.addAction(self.AFirst)
        fileMenu.addAction(self.APrev)
        fileMenu.addAction(self.ANext)
        fileMenu.addAction(self.ALast)

        fileMenu = menubar.addMenu('&Settings')
        fileMenu.addAction(self.APwdManager)
        fileMenu.addAction(self.ALastScene)

    def InitToolbar(self):
        self.toolBar = self.addToolBar('Toolbar')
        self.toolBar.setMovable(False)
        self.toolBar.addAction(self.AOpen)
        self.toolBar.addAction(self.AOpenFolder)
        self.toolBar.addAction(self.AListManager)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.AFirst)
        self.toolBar.addAction(self.APrev)
        self.toolBar.addAction(self.ANext)
        self.toolBar.addAction(self.ALast)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.AOriSize)
        self.toolBar.addAction(self.AFitScreen)
        self.toolBar.addAction(self.AFitHeight)
        self.toolBar.addAction(self.AFitWidth)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.ALastScene)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.AExit)

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
        if self.ALastScene.isChecked() and self.path:
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
            self.AllFiles = self.GetAllFiles(self.folder)
        else:
            self.AllFiles = self.GetAllFiles(folder)
        if len(self.AllFiles) == 0:
            return
        if fname:
            self.fileindex = self.AllFiles.index(path)
        else:
            self.fileindex = 0
            path = self.AllFiles[0]
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
            fname = self.AllFiles[self.fileindex]
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
            self.StatusPath.setText(self.AllFiles[self.fileindex])
            self.StatusFilename.setText(fname)
            self.StatusIndex.setText(str(self.IndexInArchive+1) + '/' + str(len(self.AllFilesInArchive)))
        else:
            fname = self.AllFiles[self.fileindex]
            self.StatusPath.setText(fname)
            self.StatusFilename.setText(os.path.split(fname)[1])
            self.StatusIndex.setText(str(self.fileindex+1) + '/' + str(len(self.AllFiles)))

        try:
            h = str(self.pixmap.height())
            w = str(self.pixmap.width())
            self.StatusSize.setText(w + '*' + h)
        except:
            pass

    def ResizeViewer(self):
        try:
            if self.AOriSize.isChecked():
                scale = 1
            else:
                viewh = self.height() - self.menuBar().height() - self.toolBar.height() - self.statusBar().height() -2
                vieww = self.width() -2
                hscale=viewh/self.pixmap.height()
                wscale=vieww/self.pixmap.width()
                if self.AFitScreen.isChecked():
                    scale = min(hscale,wscale)
                elif self.AFitWidth.isChecked():
                    scale = wscale
                elif self.AFitHeight.isChecked():
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
        file_paths = self.ListDialog.Sort(file_paths,self.SortOrder,self.SortAlg)
        return file_paths

    def GetAllFilesInArchive(self,namelist):
        support_file = []
        for files in namelist:
                if self.SupportFileInArchive(files):
                    support_file.append(files)
        file_paths = self.ListDialog.Sort(support_file,self.SortOrder,self.SortAlg)
        return file_paths

    def PrevPage(self):
        if self.IsArchive:
            if self.IndexInArchive>0:
                self.IndexInArchive -=1
                self.ShowImage()
            else:
                if self.fileindex>0:
                    self.CloseArchive()
                    self.fileindex -=1
                    self.LoadFile(self.AllFiles[self.fileindex])
        else:
            if self.fileindex>0:
                self.fileindex -=1
                self.LoadFile(self.AllFiles[self.fileindex])

    def NextPage(self):
        if self.IsArchive:
            if self.IndexInArchive < len(self.AllFilesInArchive)-1:
                self.IndexInArchive +=1
                self.ShowImage()
            else:
                if self.fileindex < len(self.AllFiles)-1:
                    self.CloseArchive()
                    self.fileindex +=1
                    self.LoadFile(self.AllFiles[self.fileindex])
        else:
            if self.fileindex < len(self.AllFiles)-1:
                self.fileindex +=1
                self.LoadFile(self.AllFiles[self.fileindex])

    def FirstPage(self):
        if self.IsArchive:
            self.IndexInArchive = 0
            self.ShowImage()
        else:
            self.fileindex = 0
            self.LoadFile(self.AllFiles[self.fileindex])

    def LastPage(self):
        if self.IsArchive:
            self.IndexInArchive = len(self.AllFilesInArchive)-1
            self.ShowImage()
        else:
            self.fileindex = len(self.AllFiles)-1
            self.LoadFile(self.AllFiles[self.fileindex])

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

    def ShowListManager(self):
        if self.IsArchive:
            self.ListDialog.list = self.AllFilesInArchive
            self.ListDialog.path = self.AllFilesInArchive[self.IndexInArchive]
        else:
            self.ListDialog.list = self.AllFiles
            self.ListDialog.path = self.path
        if self.ListDialog.exec_():
            self.SortOrder = self.ListDialog.OrderGroup.checkedId()
            self.SortAlg = self.ListDialog.AlgGroup.checkedId()
            if self.IsArchive:
                self.ListDialog.Sort(self.AllFilesInArchive,self.SortOrder,self.SortAlg)
                self.IndexInArchive = self.ListDialog.index
                self.ShowImage()
            else:
                if self.AllFiles:
                    self.LoadFile(self.ListDialog.path)

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
