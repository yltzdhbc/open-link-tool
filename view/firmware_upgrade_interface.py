# coding:utf-8
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QWidget,
    QGraphicsDropShadowEffect,
    QTreeWidgetItem,
    QTreeWidget,
    QStyleFactory,
    QPushButton,
    QStyledItemDelegate,
    QProgressBar,
)
from qfluentwidgets import (
    FluentIcon,
    setFont,
    InfoBarIcon,
    TreeWidget,
    setTheme,
    Theme,
    TreeView,
    PushButton,
    PrimaryPushButton,
    ProgressBar,
)

from PyQt5.QtGui import QStandardItemModel, QStandardItem, QFont
from PyQt5.QtCore import Qt, QUrl, QTimer, QThread, pyqtSignal, pyqtSlot, QObject
from resource.ui.Ui_FirmwareUpgradeInterface import Ui_FirmwareUpgradeInterface


class TreeNode(QObject):
    button_download_signal = pyqtSignal(str)
    COL_TREE_NAME = 0
    COL_VER_APP = 1
    COL_VER_LOADER = 2
    # COL_STR_HW = 3
    COL_STR_SN = 3
    COL_BUTTON = 4
    COL_STATE = 5
    COL_PROGRESS = 6
    # COL_RESERVE = 8

    def __init__(self, tree_widget, parent_item):
        # 调用父类的 __init__ 方法
        super().__init__()
        self.tree_widget = tree_widget
        self.parent_item = parent_item

    def create_info_list(self, name, child_count):
        # 创建根节点
        self.item = QTreeWidgetItem(self.parent_item, [name, "", "", ""])

        self.item.setDisabled(True)
        self.tree_widget.addTopLevelItem(self.item)
        # 创建根节点的按钮
        # self.button = PushButton("全部升级")
        # self.button.setFont(QFont("Arial", 10))  # 设置字体和大小
        # self.button.setStyleSheet("width: 100px;")
        # self.button.clicked.connect(lambda: self.on_button_clicked(name))
        # self.tree_widget.setItemWidget(self.item, 3, self.button)
        # 创建子节点
        self.progress_bars = []
        self._start_upload_button = []
        self._child_item = []
        # 创建子节点
        for i in range(child_count):  # name app loader HW SN 按钮 进度 状态 保留
            child_item = QTreeWidgetItem(self.item, [f" ", " ", " ", "", " ", "", ""])
            child_item.setDisabled(True)
            self.item.addChild(child_item)
            # 创建子节点的按钮
            child_button = PushButton("升级")
            child_button.setFont(QFont("Consoals", 10))  # 设置字体和大小
            child_button.setStyleSheet("width: 100px;")
            child_button.clicked.connect(lambda checked, index=i: self.on_button_clicked(f"{name}-Module-{index + 1}"))
            self.tree_widget.setItemWidget(child_item, self.COL_BUTTON, child_button)
            # 创建进度条并添加到子节点的第五列
            progress_bar = ProgressBar()
            progress_bar.setValue(50)  # 初始值
            progress_bar.setAlignment(Qt.AlignCenter)  # 居中对齐
            self.tree_widget.setItemWidget(child_item, self.COL_PROGRESS, progress_bar)
            # 将进度条保存到列表中以便后续访问
            self.progress_bars.append(progress_bar)
            self._start_upload_button.append(child_button)
            self._child_item.append(child_item)

    def on_button_clicked(self, name):
        print(f"{name} button clicked!")
        idx = 0
        if name == "Glazer-Module-1":
            idx = 0
        elif name == "Glazer-Module-2":
            idx = 1
        elif name == "Glazer-Module-3":
            idx = 2
        print(f"{idx} idx")
        self.set_progress(idx, 0)
        self._start_upload_button[idx].setDisabled(True)
        self.button_download_signal.emit(name)

    def set_progress(self, child_index, value):
        """设置指定子节点的进度条进度值"""
        if 0 <= child_index < len(self.progress_bars):
            self.progress_bars[child_index].setValue(value)

    def set_selected_state(self, child_index):
        child_item = self.item.child(child_index)
        child_item.setSelected(True)

    def set_upgrade_state_str(self, idx, str):
        print(f"set_upgrade_state_str: {str}")
        # if str == "升级成功":
        #     self._start_upload_button[idx].setEnabled(True)

        child_item = self.item.child(idx)
        child_item.setText(self.COL_STATE, str)

    def set_info(self, child_index, app_version, loader_version, HW, SN):
        child_item = self.item.child(child_index)
        child_item.setText(self.COL_VER_APP, hex(app_version))
        child_item.setText(self.COL_VER_LOADER, hex(loader_version))
        # child_item.setText(self.COL_STR_HW, hex(HW))
        child_item.setText(self.COL_STR_SN, str(SN))
        print(
            f" {child_item.text(0)} | {child_item.text(1)} | {child_item.text(2)} | {child_item.text(3)} | {child_item.text(4)}"
        )
        self._start_upload_button[child_index].setEnabled(True)

    def remove(self):
        index = self.tree_widget.indexOfTopLevelItem(self.item)
        if index != -1:
            self.tree_widget.takeTopLevelItem(index)


class NonEditableModel(QStandardItemModel):
    def flags(self, index):
        # 只返回可选择和可查看的标志，不允许编辑
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled


class FirmwareUpgradeInterface(Ui_FirmwareUpgradeInterface, QWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.treeWidget.setColumnCount(7)
        # name app loader HW SN 按钮 进度 状态 保留
        self.treeWidget.setHeaderLabels(["名称", "App版本", "Loader版本", "SN", "升级", "状态", "进度"])

        # 添加根节点和子节点
        self.node = TreeNode(self.treeWidget, None)
        self.node.create_info_list("Glazer", 3)

        self.node.set_progress(0, 0)
        self.node.set_progress(1, 0)
        self.node.set_progress(2, 0)

        self.node._child_item[0].setText(self.node.COL_TREE_NAME, "灯板-0x0102")
        self.node._child_item[1].setText(self.node.COL_TREE_NAME, "主板-0x0100")
        self.node._child_item[2].setText(self.node.COL_TREE_NAME, "底板-0x0101")

        for i in range(3):
            self.node._start_upload_button[i].setDisabled(True)

        # 默认展开所有节点
        self.treeWidget.expandAll()
        # 设置第一列宽度
        self.treeWidget.setColumnWidth(0, 150)
