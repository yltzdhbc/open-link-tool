# coding:utf-8
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QWidget,
    QGraphicsDropShadowEffect,
    QTreeWidgetItem,
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
from PyQt5.QtCore import Qt, QModelIndex, QSize  # 添加这一行
from resource.ui.Ui_FirmwareUpgradeInterface import Ui_FirmwareUpgradeInterface


class TreeNode:
    def __init__(self, tree_widget, parent_item):
        self.tree_widget = tree_widget
        self.parent_item = parent_item

        # # 创建根节点
        # self.item = QTreeWidgetItem(parent_item, [name, "", "", ""])
        # self.tree_widget.addTopLevelItem(self.item)
        # # 创建根节点的按钮
        # self.button = PushButton("全部升级")
        # self.button.setFont(QFont("Arial", 10))  # 设置字体和大小
        # self.button.setStyleSheet("width: 100px;")
        # self.button.clicked.connect(lambda: self.on_button_clicked(name))
        # self.tree_widget.setItemWidget(self.item, 3, self.button)
        # # 创建子节点
        # self.progress_bars = []
        # # 创建子节点
        # for i in range(child_count):
        #     child_item = QTreeWidgetItem(self.item, [f"Child {i + 1}", "v10.0.0.1", "v5.0.0.2", "", "", "未升级"])
        #     self.item.addChild(child_item)
        #     # 创建子节点的按钮
        #     child_button = PushButton("升级")
        #     child_button.setFont(QFont("Arial", 10))  # 设置字体和大小
        #     child_button.setStyleSheet("width: 80px;")
        #     child_button.clicked.connect(lambda checked, index=i: self.on_button_clicked(f"{name} - Child {index + 1}"))
        #     self.tree_widget.setItemWidget(child_item, 3, child_button)
        #     # 创建进度条并添加到子节点的第五列
        #     progress_bar = ProgressBar()
        #     progress_bar.setValue(50)  # 初始值
        #     progress_bar.setAlignment(Qt.AlignCenter)  # 居中对齐
        #     self.tree_widget.setItemWidget(child_item, 4, progress_bar)
        #     # 将进度条保存到列表中以便后续访问
        #     self.progress_bars.append(progress_bar)

    def create_info_list(self, name, child_count):
        # 创建根节点
        self.item = QTreeWidgetItem(self.parent_item, [name, "", "", ""])
        self.tree_widget.addTopLevelItem(self.item)
        # 创建根节点的按钮
        self.button = PushButton("全部升级")
        self.button.setFont(QFont("Arial", 10))  # 设置字体和大小
        self.button.setStyleSheet("width: 100px;")
        self.button.clicked.connect(lambda: self.on_button_clicked(name))
        self.tree_widget.setItemWidget(self.item, 3, self.button)
        # 创建子节点
        self.progress_bars = []
        # 创建子节点
        for i in range(child_count):
            child_item = QTreeWidgetItem(
                self.item, [f"Module {i + 1}", "None", "None", "", "", "未升级", ""]
            )
            self.item.addChild(child_item)
            # 创建子节点的按钮
            child_button = PushButton("升级")
            child_button.setFont(QFont("Arial", 10))  # 设置字体和大小
            child_button.setStyleSheet("width: 80px;")
            child_button.clicked.connect(
                lambda checked, index=i: self.on_button_clicked(
                    f"{name} - Child {index + 1}"
                )
            )
            self.tree_widget.setItemWidget(child_item, 3, child_button)
            # 创建进度条并添加到子节点的第五列
            progress_bar = ProgressBar()
            progress_bar.setValue(50)  # 初始值
            progress_bar.setAlignment(Qt.AlignCenter)  # 居中对齐
            self.tree_widget.setItemWidget(child_item, 4, progress_bar)
            # 将进度条保存到列表中以便后续访问
            self.progress_bars.append(progress_bar)

            if i == 0:
                child_item.setText(0, "灯板")
            elif i == 1:
                child_item.setText(0, "主板")
            elif i == 2:
                child_item.setText(0, "底板")
        # 获取根节点并遍历其子节点
        # self.get_child_nodes(self.item)

    # def get_child_nodes(self, parent_item):
    #     # 获取子节点数量
    #     child_count = parent_item.childCount()
    #     print(f"Number of child nodes: {child_count}")
    #     # 遍历并输出每个子节点的文本
    #     for i in range(child_count):
    #         child_item = parent_item.child(i)
    #         print(f"Child {i+1}: {child_item.text(0)} | {child_item.text(1)} | {child_item.text(2)}")

    def on_button_clicked(self, name):
        print(f"{name} button clicked!")

    def set_progress(self, child_index, value):
        """设置指定子节点的进度条进度值"""
        if 0 <= child_index < len(self.progress_bars):
            self.progress_bars[child_index].setValue(value)

    def set_info(self, child_index, app_version, loader_version):
        child_item = self.item.child(child_index)
        child_item.setText(1, hex(app_version))  # app
        child_item.setText(2, hex(loader_version))  # app
        print(f" {child_item.text(0)} | {child_item.text(1)} | {child_item.text(2)}")

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
        self.treeWidget.setColumnCount(6)
        self.treeWidget.setHeaderLabels(
            ["名称", "App版本", "Loader版本", "升级", "进度", "状态", " "]
        )

        # 添加根节点和子节点
        # self.node = TreeNode(self.treeWidget, None, "制冰机1")
        self.node = TreeNode(self.treeWidget, None)
        self.node.create_info_list("制冰机", 3)

        self.node.set_progress(0, 0)
        self.node.set_progress(1, 0)
        self.node.set_progress(2, 0)

        # 默认展开所有节点
        self.treeWidget.expandAll()
        # 设置第一列宽度
        self.treeWidget.setColumnWidth(0, 140)
