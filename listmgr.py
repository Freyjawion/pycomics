#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os

from natsort import natsorted, ns
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import (QApplication, QButtonGroup, QDialog, QHBoxLayout,
                             QListView, QPushButton, QRadioButton, QVBoxLayout,QLabel)


class ListManager(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowTitleHint)
        self.setWindowTitle('List Manager')
        self.setFixedSize(400,300)
        self.ListViewer = QListView()
        self.ListViewer.clicked.connect(self.ClickList)
        self.ListViewer.doubleClicked.connect(self.Ok)
        self.OkButton = QPushButton('OK')
        self.OkButton.clicked.connect(self.Ok)
        self.CancelButton = QPushButton('Cancel')
        self.CancelButton.clicked.connect(self.Cancle)
        sortorderlable = QLabel('Sort Order')
        self.SortOrder = [QRadioButton("Asc"), QRadioButton("Desc")]
        self.OrderGroup = QButtonGroup()
        sortalglable = QLabel('Sort Algorithm')
        self.SortAlg = [QRadioButton("Path"), QRadioButton("Natural")]
        self.AlgGroup = QButtonGroup()

        hbox1 = QHBoxLayout()
        hbox2 = QHBoxLayout()
        vbox1 = QVBoxLayout()
        vbox2 = QVBoxLayout()
        vbox3 = QVBoxLayout()
        mainbox = QVBoxLayout()

        vbox1.addWidget(sortorderlable)
        for i in range(len(self.SortOrder)):
            vbox1.addWidget(self.SortOrder[i])
            self.OrderGroup.addButton(self.SortOrder[i],i)
            self.SortOrder[i].clicked.connect(self.ClickRadioButton)
        vbox2.addWidget(sortalglable)
        for i in range(len(self.SortAlg)):
            vbox2.addWidget(self.SortAlg[i])
            self.AlgGroup.addButton(self.SortAlg[i],i)
            self.SortAlg[i].clicked.connect(self.ClickRadioButton)

        vbox3.addLayout(vbox1)
        vbox3.addLayout(vbox2)
        vbox3.addStretch(1)
        hbox1.addWidget(self.ListViewer)
        hbox1.addLayout(vbox3)
        hbox2.addStretch(1)
        hbox2.addWidget(self.OkButton)
        hbox2.addWidget(self.CancelButton)
        mainbox.addLayout(hbox1)
        mainbox.addLayout(hbox2)
        self.setLayout(mainbox)

    def showEvent(self,event):
        self.center()
        self.LoadListToView()


    def closeEvent(self,event):
        self.Cancle()

    def center(self):
        frameGm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

    def LoadListToView(self):
        self.index = self.list.index(self.path)
        self.Model = QStandardItemModel(self.ListViewer)
        for file in self.list:
            item = QStandardItem(file)
            item.setEditable(False)
            self.Model.appendRow(item)
        self.ListViewer.setModel(self.Model)
        self.ListViewer.setCurrentIndex(self.Model.index(self.index,0))

    def ClickList(self,index):
        self.path = self.Model.data(index)
        self.index = self.list.index(self.path)

    def ClickRadioButton(self):
        self.list = self.Sort(self.list,self.OrderGroup.checkedId(),self.AlgGroup.checkedId())
        self.LoadListToView()

    def Ok(self):
        self.accept()

    def Cancle(self):
        self.reject()

    def Sort(self,list,sortid,algid):
        if sortid == 0:
            isreverse = False
        else:
            isreverse = True

        if algid == 0:
            sortalg = ns.PATH
        else:
            sortalg = 0

        return natsorted(list,alg=sortalg,reverse=isreverse)
