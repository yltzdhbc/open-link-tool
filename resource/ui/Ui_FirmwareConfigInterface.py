# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'd:\flame_ws\open-link-tool\resource\ui\FirmwareConfigInterface.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_FirmwareConfigInterface(object):
    def setupUi(self, FirmwareConfigInterface):
        FirmwareConfigInterface.setObjectName("FirmwareConfigInterface")
        FirmwareConfigInterface.resize(911, 807)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(FirmwareConfigInterface)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.horizontalLayout.setContentsMargins(20, 20, 20, 20)
        self.horizontalLayout.setSpacing(12)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.focusCard = CardWidget(FirmwareConfigInterface)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.focusCard.sizePolicy().hasHeightForWidth())
        self.focusCard.setSizePolicy(sizePolicy)
        self.focusCard.setMinimumSize(QtCore.QSize(380, 410))
        self.focusCard.setMaximumSize(QtCore.QSize(600, 800))
        self.focusCard.setStyleSheet("")
        self.focusCard.setObjectName("focusCard")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.focusCard)
        self.verticalLayout_3.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.verticalLayout.setObjectName("verticalLayout")
        spacerItem = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setContentsMargins(5, -1, -1, -1)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.dailyProgressLabel = SubtitleLabel(self.focusCard)
        self.dailyProgressLabel.setObjectName("dailyProgressLabel")
        self.horizontalLayout_4.addWidget(self.dailyProgressLabel)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem1)
        self.pushButton_saveConfig = PushButton(self.focusCard)
        self.pushButton_saveConfig.setObjectName("pushButton_saveConfig")
        self.horizontalLayout_4.addWidget(self.pushButton_saveConfig)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.verticalLayout_7 = QtWidgets.QVBoxLayout()
        self.verticalLayout_7.setContentsMargins(15, 10, 15, -1)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.label_0 = SubtitleLabel(self.focusCard)
        self.label_0.setMinimumSize(QtCore.QSize(0, 30))
        self.label_0.setObjectName("label_0")
        self.verticalLayout_7.addWidget(self.label_0)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label_module_0 = BodyLabel(self.focusCard)
        self.label_module_0.setMinimumSize(QtCore.QSize(0, 30))
        self.label_module_0.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_module_0.setObjectName("label_module_0")
        self.gridLayout.addWidget(self.label_module_0, 2, 0, 1, 1)
        self.lineEdit_0 = LineEdit(self.focusCard)
        self.lineEdit_0.setObjectName("lineEdit_0")
        self.gridLayout.addWidget(self.lineEdit_0, 2, 1, 1, 1)
        self.lineEdit_2 = LineEdit(self.focusCard)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.gridLayout.addWidget(self.lineEdit_2, 4, 1, 1, 1)
        self.label_module_1 = BodyLabel(self.focusCard)
        self.label_module_1.setMinimumSize(QtCore.QSize(0, 30))
        self.label_module_1.setObjectName("label_module_1")
        self.gridLayout.addWidget(self.label_module_1, 3, 0, 1, 1)
        self.label_module_2 = BodyLabel(self.focusCard)
        self.label_module_2.setMinimumSize(QtCore.QSize(0, 30))
        self.label_module_2.setObjectName("label_module_2")
        self.gridLayout.addWidget(self.label_module_2, 4, 0, 1, 1)
        self.lineEdit_4 = LineEdit(self.focusCard)
        self.lineEdit_4.setObjectName("lineEdit_4")
        self.gridLayout.addWidget(self.lineEdit_4, 6, 1, 1, 1)
        self.lineEdit_1 = LineEdit(self.focusCard)
        self.lineEdit_1.setObjectName("lineEdit_1")
        self.gridLayout.addWidget(self.lineEdit_1, 3, 1, 1, 1)
        self.lineEdit_3 = LineEdit(self.focusCard)
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.gridLayout.addWidget(self.lineEdit_3, 5, 1, 1, 1)
        self.label_module_3 = BodyLabel(self.focusCard)
        self.label_module_3.setMinimumSize(QtCore.QSize(0, 30))
        self.label_module_3.setObjectName("label_module_3")
        self.gridLayout.addWidget(self.label_module_3, 5, 0, 1, 1)
        self.label_module_4 = BodyLabel(self.focusCard)
        self.label_module_4.setMinimumSize(QtCore.QSize(0, 30))
        self.label_module_4.setObjectName("label_module_4")
        self.gridLayout.addWidget(self.label_module_4, 6, 0, 1, 1)
        self.verticalLayout_7.addLayout(self.gridLayout)
        self.verticalLayout.addLayout(self.verticalLayout_7)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem2)
        self.verticalLayout_3.addLayout(self.verticalLayout)
        self.horizontalLayout.addWidget(self.focusCard)
        self.progressCard = CardWidget(FirmwareConfigInterface)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.progressCard.sizePolicy().hasHeightForWidth())
        self.progressCard.setSizePolicy(sizePolicy)
        self.progressCard.setMinimumSize(QtCore.QSize(380, 410))
        self.progressCard.setMaximumSize(QtCore.QSize(600, 800))
        self.progressCard.setObjectName("progressCard")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.progressCard)
        self.verticalLayout_4.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setSizeConstraint(QtWidgets.QLayout.SetMinAndMaxSize)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setSizeConstraint(QtWidgets.QLayout.SetMinAndMaxSize)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setContentsMargins(15, -1, -1, -1)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        spacerItem3 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout_5.addItem(spacerItem3)
        self.yesterdayLabel = SubtitleLabel(self.progressCard)
        self.yesterdayLabel.setObjectName("yesterdayLabel")
        self.verticalLayout_5.addWidget(self.yesterdayLabel)
        spacerItem4 = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout_5.addItem(spacerItem4)
        self.label_3 = BodyLabel(self.progressCard)
        self.label_3.setObjectName("label_3")
        self.verticalLayout_5.addWidget(self.label_3)
        spacerItem5 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_5.addItem(spacerItem5)
        self.horizontalLayout_5.addLayout(self.verticalLayout_5)
        self.verticalLayout_2.addLayout(self.horizontalLayout_5)
        self.verticalLayout_4.addLayout(self.verticalLayout_2)
        self.horizontalLayout.addWidget(self.progressCard)
        spacerItem6 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem6)
        self.horizontalLayout_3.addLayout(self.horizontalLayout)

        self.retranslateUi(FirmwareConfigInterface)
        QtCore.QMetaObject.connectSlotsByName(FirmwareConfigInterface)

    def retranslateUi(self, FirmwareConfigInterface):
        _translate = QtCore.QCoreApplication.translate
        FirmwareConfigInterface.setWindowTitle(_translate("FirmwareConfigInterface", "Form"))
        self.dailyProgressLabel.setText(_translate("FirmwareConfigInterface", "固件配置"))
        self.pushButton_saveConfig.setText(_translate("FirmwareConfigInterface", "保存"))
        self.label_0.setText(_translate("FirmwareConfigInterface", "MACHINE-1"))
        self.label_module_0.setText(_translate("FirmwareConfigInterface", "MODULE1"))
        self.label_module_1.setText(_translate("FirmwareConfigInterface", "MODULE2"))
        self.label_module_2.setText(_translate("FirmwareConfigInterface", "MODULE3"))
        self.label_module_3.setText(_translate("FirmwareConfigInterface", "MODULE4"))
        self.label_module_4.setText(_translate("FirmwareConfigInterface", "MODULE5"))
        self.yesterdayLabel.setText(_translate("FirmwareConfigInterface", "固件更新说明"))
        self.label_3.setText(_translate("FirmwareConfigInterface", "<html><head/><body><p>v10.0.0.1固件更新<br/>新增：</p><p>1、1111</p><p>2、2222</p><p>3、3333</p><p>修改：</p><p>1、111</p><p>2、222</p><p>3、333</p></body></html>"))
from qfluentwidgets import BodyLabel, CardWidget, LineEdit, PushButton, SubtitleLabel
import resource_rc
