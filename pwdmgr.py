#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import (QApplication, QDialog, QHBoxLayout, QLineEdit,
                             QListView, QPushButton, QVBoxLayout)


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
