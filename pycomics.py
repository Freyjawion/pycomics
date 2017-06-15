#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import os
from PyQt5.QtCore import Qt, QItemSelectionModel
from PyQt5.QtWidgets import QMainWindow, QTextEdit, QAction, QApplication, QFileDialog, QLabel, QLineEdit
from PyQt5.QtWidgets import QScrollArea, QMessageBox, QListView, QDialog, QHBoxLayout, QVBoxLayout, QPushButton
from PyQt5.QtGui import QIcon, QPixmap, QImage, QStandardItem, QStandardItemModel 
import zipfile
import rarfile
from io import StringIO
from natsort import natsorted, ns
from operator import itemgetter

__Title__ = 'Pycomics'
__Version__ = 'beta 0.01'


class Pycomics(QMainWindow):

    def __init__(self):
        super().__init__()
        
        self.InitUI()
        self.InitActions()
        self.InitMenus()
        self.InitToolbar()
        self.InitStatusbar()

        self.PwdDialog = PwdManager()
             
    def InitUI(self):               
        
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

        self.OpenAction = QAction(QIcon('icon' + os.sep + 'file.png'), 'Open Files', self)
        self.OpenAction .setShortcut('Ctrl+O')
        self.OpenAction .setStatusTip('Open Files')
        self.OpenAction .triggered.connect(self.OpenFile)

        self.OpenFAction = QAction(QIcon('icon' + os.sep + 'file.png'), 'Open Folder', self)
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

        self.PwdManager = QAction(QIcon('icon' + os.sep + 'file.png'), 'Password Manager', self)
        self.PwdManager .setStatusTip('Password Manager')
        self.PwdManager .triggered.connect(self.ShowPwdManager)

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

        fileMenu = menubar.addMenu('&Settings')
        fileMenu.addAction(self.PwdManager)

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
        self.IsArchive,self.ext = self.IsCompressed(fname)
        if self.IsArchive:
            
            if self.ext == '.zip':
                self.ArchiveFile = zipfile.ZipFile(fname, 'r')
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
                self.IndexInArchive = 0
                self.ShowImage()
            elif self.ext == '.rar':
                self.ArchiveFile = rarfile.RarFile(fname, 'r')
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
                self.IndexInArchive = 0
                self.ShowImage()
            elif self.ext == '.7z':
                self.LoadFailed()
            else:
                self.LoadFailed()
        else:
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
            self.ImageViewer.setText("Can not load %s." % fname)
        else:
            self.ImageViewer.setPixmap(self.pixmap)
            self.ResizeViewer()

        if self.IsArchive:
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
                    self.ArchiveFile.close()
                    self.fileindex -=1
                    self.LoadFile()
        else:
            if self.fileindex>0:
                self.fileindex -=1
                self.LoadFile()

    def NextPage(self):
        if self.IsArchive:
            if self.IndexInArchive < len(self.AllFilesInArchive)-1:
                self.IndexInArchive +=1
                self.ShowImage()
            else:
                if self.fileindex < len(self.allfiles)-1:
                    self.ArchiveFile.close()
                    self.fileindex +=1
                    self.LoadFile()
        else:
            if self.fileindex < len(self.allfiles)-1:
                self.fileindex +=1
                self.LoadFile()

    def FirstPage(self):
        if self.IsArchive:
            self.IndexInArchive = 0
            self.ShowImage()
        else:
            self.fileindex = 0
            self.LoadFile()

    def LastPage(self):
        if self.IsArchive:
            self.IndexInArchive = len(self.AllFilesInArchive)-1
            self.ShowImage()
        else:
            self.fileindex = len(self.allfiles)-1
            self.LoadFile()

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
        for password in self.PwdList:
            try:
               data = self.ArchiveFile.read(self.ArchiveInfo[0].filename,password)
               return True,password
            except:
                pass
        return False,None

    def LoadFailed(self):
        if self.IsArchive:
            self.IsArchive = False
        fname = self.allfiles[self.fileindex]
        self.ImageViewer.setText("Can not load %s." % fname)
        self.filenamestatus.setText(os.path.split(fname)[1])
        self.indexstatus.setText(str(self.fileindex+1) + '/' + str(len(self.allfiles)))
        self.ImageViewer.resize(300,50)
        self.ImageViewer.setAlignment(Qt.AlignCenter)

    def ShowPwdManager(self):
        self.PwdDialog.exec_()


class PwdManager(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowTitleHint)
        self.PwdViewer = QListView()
        self.PwdViewer.clicked.connect(self.ClickPwd)
        self.AddButton = QPushButton('Add')
        self.AddButton.clicked.connect(self.AddPwd)
        self.DelButton = QPushButton('Delete')
        self.DelButton.clicked.connect(self.DelPwd)
        self.PwdBox = QLineEdit()
        self.PwdBox.textEdited.connect(self.PwdChanged)


    def showEvent(self,event):
        self.setWindowTitle('Password Manager')
        self.setFixedSize(400,300)

        vbox = QVBoxLayout()
        vbox.addWidget(self.AddButton)
        vbox.addWidget(self.DelButton)
        vbox.addStretch(1)     
        hbox = QHBoxLayout()
        hbox.addWidget(self.PwdViewer)
        hbox.addLayout(vbox)
        MainBox = QVBoxLayout()
        MainBox.addWidget(self.PwdBox)
        MainBox.addLayout(hbox)
        self.setLayout(MainBox)
        self.center()
        self.LoadPwdToList()
        if self.Model.rowCount() == 0:
            self.AddPwd()

    def closeEvent(self,event):
        self.RemoveEmpty()
        pwdf = open('password.pwd','w')
        for index in range(self.Model.rowCount()):
            pwdf.write(self.Model.data(self.Model.index(index,0))+'\n')
        pwdf.close()

    def center(self):
        frameGm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

    def LoadPwdToList(self):
        if not os.path.exists(r'password.pwd'):
            open("password.pwd","wb").close()
        pwdf = open('password.pwd','r')
        pwdlist = pwdf.read().splitlines()
        pwdf.close()
        self.Model = QStandardItemModel(self.PwdViewer)
        for pwd in pwdlist:
            item = QStandardItem(pwd)
            item.setEditable(False)
            self.Model.appendRow(item)
        self.PwdViewer.setModel(self.Model)
        self.PwdViewer.setCurrentIndex(self.Model.index(0,0))
        self.GetPwd(self.PwdViewer.currentIndex())

    def ClickPwd(self,index):
        self.RemoveEmpty()
        if self.Model.rowCount() == 0:
            self.AddPwd()
        self.GetPwd(index)
    
    def GetPwd(self,index):
        self.PwdBox.setText(self.Model.data(index))
        self.PwdBox.setFocus()

    def PwdChanged(self):
         self.Model.setData(self.PwdViewer.currentIndex(),self.PwdBox.text())
         if self.PwdBox.text() == '':
            self.DelPwd()

    def DelPwd(self):
        self.Model.removeRow(self.PwdViewer.currentIndex().row())
        self.GetPwd(self.PwdViewer.currentIndex())
        if self.Model.rowCount() == 0:
            self.AddPwd()
        
    def AddPwd(self):
        item = QStandardItem()
        item.setEditable(False)
        self.Model.appendRow(item)
        self.PwdViewer.setCurrentIndex(self.Model.index(self.Model.rowCount()-1,0))
        self.GetPwd(self.PwdViewer.currentIndex())

    def RemoveEmpty(self):
        for item in self.Model.findItems('',Qt.MatchFixedString):
            self.Model.removeRow(item.row())
            

def main():
    app = QApplication(sys.argv)
    ex = Pycomics()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
