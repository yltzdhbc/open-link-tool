# coding:utf-8
from typing import Union
import sys

from PyQt5.QtCore import Qt, QSize, QRect
from PyQt5.QtGui import QIcon, QPainter, QColor
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QApplication

from qfluentwidgets.common.config import qconfig

from qfluentwidgets.common.config import qconfig
from qfluentwidgets.common.icon import FluentIconBase
from qfluentwidgets.common.router import qrouter
from qfluentwidgets.common.style_sheet import FluentStyleSheet, isDarkTheme, setTheme, Theme
from qfluentwidgets.common.animation import BackgroundAnimationWidget
from qfluentwidgets.components.widgets.frameless_window import FramelessWindow
# from ..components.widgets.frameless_window import FramelessWindow
from qfluentwidgets.components.navigation import (NavigationInterface, NavigationBar, NavigationItemPosition,
                                     NavigationBarPushButton, NavigationTreeWidget)
# from .stacked_widget import StackedWidget

from qframelesswindow import TitleBar, TitleBarBase

from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QPushButton

from qfluentwidgets.window.fluent_window import FluentWindowBase
from qfluentwidgets.window.fluent_window import FluentTitleBar
from PyQt5 import QtCore, QtGui, QtWidgets
from qfluentwidgets import BodyLabel, CardWidget, ComboBox, IconWidget, LargeTitleLabel,PushButton, RadioButton, StrongBodyLabel, SubtitleLabel, TransparentToolButton, TogglePushButton
import resource_rc

# class myComboBox(ComboBox):
#     def showPopup(self):
#         self.parent().update_serial_ports()  # 在下拉菜单显示前更新串口列表
#         super().showPopup()  # 调用基类方法显示下拉列表

# class ToggleToolButton(ToolButton):
#     """ Toggle tool button

#     Constructors
#     ------------
#     * ToggleToolButton(`parent`: QWidget = None)
#     * ToggleToolButton(`icon`: QIcon | str | FluentIconBase, `parent`: QWidget = None)
#     """

#     def _postInit(self):
#         self.setCheckable(True)
#         self.setChecked(False)

#     def _drawIcon(self, icon, painter, rect):
#         if not self.isChecked():
#             return ToolButton._drawIcon(self, icon, painter, rect)

#         PrimaryToolButton._drawIcon(self, icon, painter, rect, QIcon.On)
        

class myFluentWindow(FluentWindowBase):
    """ Fluent window """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitleBar(FluentTitleBar(self))

        self.navigationInterface = NavigationInterface(self, showReturnButton=True)

        # self.hBoxLayout 是整个屏幕中的大布局，水平排列
        # 创建一个竖直的布局
        self.mySerialLayout = QVBoxLayout()
        # 竖直布局中添加导航栏
        self.mySerialLayout.addWidget(self.navigationInterface)
        # 接着添加按钮组
        
        spacerItem11 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.mySerialLayout.addItem(spacerItem11)
        
        _translate = QtCore.QCoreApplication.translate
        self.gridLayout_serial = QtWidgets.QGridLayout()
        self.gridLayout_serial.setObjectName("gridLayout_serial")
        self.pushButtonSerial = PushButton()  # TogglePushButton PushButton
        self.pushButtonSerial.setObjectName("pushButtonSerial")
        self.gridLayout_serial.addWidget(self.pushButtonSerial, 1, 1, 1, 1)
        self.pushButtonSerial.setText(_translate("SeetingsInterface", "打开"))

        # self.radioButtonSerial = RadioButton()
        # self.radioButtonSerial.setObjectName("radioButtonSerial")
        # self.gridLayout_serial.addWidget(self.radioButtonSerial, 0, 0, 1, 1)
        # self.radioButtonSerial.setText(_translate("SeetingsInterface", "串口"))

        self.comboBoxSerial = ComboBox()
        self.comboBoxSerial.setObjectName("comboBoxSerial")
        self.gridLayout_serial.addWidget(self.comboBoxSerial, 1, 0, 1, 1)
        self.mySerialLayout.addLayout(self.gridLayout_serial)
        
        # self.labelSerialSelected = BodyLabel("已选择")
        # self.labelSerialSelected.setTextColor(QColor(0, 0, 255), QColor(255, 255, 255))  # 浅色主题，深色主题
        # self.labelSerialSelected.setObjectName("labelSerialSelected")
        # self.gridLayout_serial.addWidget(self.labelSerialSelected, 0, 1, 1, 1)
        
        

        spacerItem12 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.mySerialLayout.addItem(spacerItem12)
        
        # self.gridLayout_4 = QtWidgets.QGridLayout()
        # self.gridLayout_4.setObjectName("gridLayout_4")
        # self.radioButtonWifi = RadioButton()
        # self.radioButtonWifi.setObjectName("radioButtonWifi")
        # self.gridLayout_4.addWidget(self.radioButtonWifi, 0, 0, 1, 1)
        # self.pushButtonWifi = PushButton()
        # self.pushButtonWifi.setObjectName("pushButtonWifi")
        # self.gridLayout_4.addWidget(self.pushButtonWifi, 1, 1, 1, 1)
        # self.comboBoxWifi = ComboBox()
        # self.comboBoxWifi.setObjectName("comboBoxWifi")
        # self.gridLayout_4.addWidget(self.comboBoxWifi, 1, 0, 1, 1)
        # self.mySerialLayout.addLayout(self.gridLayout_4)
        # self.radioButtonWifi.setText(_translate("SeetingsInterface", "WIFI"))
        # self.pushButtonWifi.setText(_translate("SeetingsInterface", "打开"))
        
        # 将自己的竖直的布局添加到大的框架中
        self.hBoxLayout.addLayout(self.mySerialLayout)

        self.widgetLayout = QHBoxLayout()
        self.hBoxLayout.addLayout(self.widgetLayout)
        self.hBoxLayout.setStretchFactor(self.widgetLayout, 1)

        self.widgetLayout.addWidget(self.stackedWidget)
        self.widgetLayout.setContentsMargins(0, 48, 0, 0)
        
        self.navigationInterface.displayModeChanged.connect(self.titleBar.raise_)
        self.titleBar.raise_()

    def addSubInterface(self, interface: QWidget, icon: Union[FluentIconBase, QIcon, str], text: str,
                        position=NavigationItemPosition.TOP, parent=None, isTransparent=False) -> NavigationTreeWidget:
        """ add sub interface, the object name of `interface` should be set already
        before calling this method

        Parameters
        ----------
        interface: QWidget
            the subinterface to be added

        icon: FluentIconBase | QIcon | str
            the icon of navigation item

        text: str
            the text of navigation item

        position: NavigationItemPosition
            the position of navigation item

        parent: QWidget
            the parent of navigation item

        isTransparent: bool
            whether to use transparent background
        """
        if not interface.objectName():
            raise ValueError("The object name of `interface` can't be empty string.")
        if parent and not parent.objectName():
            raise ValueError("The object name of `parent` can't be empty string.")

        interface.setProperty("isStackedTransparent", isTransparent)
        self.stackedWidget.addWidget(interface)

        # add navigation item
        routeKey = interface.objectName()
        item = self.navigationInterface.addItem(
            routeKey=routeKey,
            icon=icon,
            text=text,
            onClick=lambda: self.switchTo(interface),
            position=position,
            tooltip=text,
            parentRouteKey=parent.objectName() if parent else None
        )

        # initialize selected item
        if self.stackedWidget.count() == 1:
            self.stackedWidget.currentChanged.connect(self._onCurrentInterfaceChanged)
            self.navigationInterface.setCurrentItem(routeKey)
            qrouter.setDefaultRouteKey(self.stackedWidget, routeKey)

        self._updateStackedBackground()

        return item

    def resizeEvent(self, e):
        self.titleBar.move(46, 0)
        self.titleBar.resize(self.width()-46, self.titleBar.height())
