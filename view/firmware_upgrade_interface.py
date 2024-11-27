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
    QLabel,
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
    BodyLabel,
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
        self._status_label = []
        self._child_item = []
        # 创建子节点
        for i in range(child_count):  # name app loader HW SN 按钮 进度 状态 保留
            child_item = QTreeWidgetItem(self.item, [f" ", " ", " ", "", " ", "", ""])
            child_item.setDisabled(True)
            self.item.addChild(child_item)
            # 创建子节点的按钮
            child_button = PushButton("升级")
            font = QFont("微软雅黑", 10)
            child_button.setFont(font)  # 设置字体和大小
            # 设置按钮的样式
            child_button.setStyleSheet(
                """
                QPushButton {
                    color: black;  /* 文字颜色为白色 */
                    background-color: #29F1FF;  /* 激活状态下背景颜色为 #FFF129 */
                    border: 0px solid #C0C0C0;  /* 设置边框颜色为浅灰色，宽度为2像素 */
                    border-radius: 5px;  /* 设置圆角半径为15像素 */
                }
                QPushButton:disabled {
                    color: darkgray;  /* 禁用状态下文字为深灰色 */
                    background-color: lightgray;  /* 禁用状态下背景为浅灰色 */
                }
            """
            )
            status_label = QLabel('')
            status_label.setStyleSheet("""
                QLabel {
                    color: white;                          /* 文字颜色为白色 */
                    background-color: #3498db;             /* 背景颜色（浅蓝色） */
                    font-size: 10pt;                        /* 字体大小为 10 */
                    font-family: 'Microsoft YaHei';         /* 字体为微软雅黑 */
                    padding: 1px;                          /* 增加内边距，让文字不贴边 */
                    border-radius: 15px;                    /* 设置圆角效果 */
                 }
            """)
            status_label.setAutoFillBackground(True)
            self.tree_widget.setItemWidget(child_item, self.COL_STATE, status_label)
            child_button.clicked.connect(lambda checked, index=i: self.on_button_clicked(f"{index}"))
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
            self._status_label.append(status_label)

    def on_button_clicked(self, name):

        print(f"{name} button clicked!")
        idx = int(name)
        print(f"idx: {idx}")
        self.set_upgrade_state_str(idx, "启动中")
        self.button_download_signal.emit(name)
        self.set_progress(idx, 0)
        # self._start_upload_button[idx].setDisabled(True)

    def set_button_state(self, idx, on_off):
        if on_off == "off":
            self._start_upload_button[idx].setDisabled(True)
        else:
            self._start_upload_button[idx].setEnabled(True)

    def set_progress(self, child_index, value):
        """设置指定子节点的进度条进度值"""
        if 0 <= child_index < len(self.progress_bars):
            self.progress_bars[child_index].setValue(value)

    def set_selected_state(self, child_index, on_off):
        child_item = self.item.child(child_index)
        child_item.setSelected(on_off)

    def set_upgrade_state_str(self, idx, str):
        print(f"set_upgrade_state_str: {str}, idx:{idx}")
        # child_item = self.item.child(idx)
        # child_item.setText(self.COL_STATE, str)
        self._status_label[idx].setText(str)
        # child_item.setSelected(True)

    def uint32_to_str(self, uint32):
        a = (uint32 >> 24) & 0xFF  # 提取最高 8 位
        b = (uint32 >> 16) & 0xFF  # 提取第二高 8 位
        c = (uint32 >> 8) & 0xFF  # 提取第三高 8 位
        d = uint32 & 0xFF  # 提取最低 8 位
        return f"v{a}. {b}. {c}. {d}"

    def set_info(self, child_index, app_version, loader_version, HW, SN):
        child_item = self.item.child(child_index)
        child_item.setText(self.COL_VER_APP, self.uint32_to_str(app_version))
        child_item.setText(self.COL_VER_LOADER, self.uint32_to_str(loader_version))
        # child_item.setText(self.COL_STR_HW, hex(HW))
        child_item.setText(self.COL_STR_SN, str(SN))
        self.set_selected_state(child_index, True)
        print(
            f" {child_item.text(0)} | {child_item.text(1)} | {child_item.text(2)} | {child_item.text(3)} | {child_item.text(4)}"
        )
        # self._start_upload_button[child_index].setEnabled(True)

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

    def createModuleTree(self, root_name, child_num, child_name):
        # 添加根节点和子节点
        self.node = TreeNode(self.treeWidget, None)
        self.node.create_info_list(root_name, child_num)
        for i in range(child_num):
            self.node.set_progress(i, 0)
            self.node._child_item[i].setText(self.node.COL_TREE_NAME, child_name[i])
            self.node._start_upload_button[i].setDisabled(True)
            
        # 默认展开所有节点
        self.treeWidget.expandAll()
        # 设置第一列宽度
        self.treeWidget.setColumnWidth(0, 150)
