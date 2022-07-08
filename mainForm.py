import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QStandardItem, QStandardItemModel
from PyQt5.QtCore import QSize
from PyQt5.Qt import *
from File import *
import time
import os
import pickle
from MyWidget import MyListWidget
from fileEdit import editForm, attributeForm, shareForm

class mainForm(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.listView = MyListWidget(self.curNode, parents=self)
        self.listView.setMinimumWidth(800)
        self.listView.setViewMode(QListView.IconMode)
        self.listView.setIconSize(QSize(72, 72))
        self.listView.setGridSize(QSize(100, 100))
        self.listView.setResizeMode(QListView.Adjust)
        self.listView.setMovement(QListView.Static)
        self.listView.setEditTriggers(QAbstractItemView.AllEditTriggers)
        self.listView.doubleClicked.connect(self.openFile)

        # 加载当前路径文件
        self.loadCurFile()
        self.grid.addWidget(self.listView, 1, 1)
        
        # 右击菜单
        self.listView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listView.customContextMenuRequested.connect(self.show_rightclicked_menu)

        # 状态栏和url更新
        self.updatePrint()
        self.lastLoc = -1
        self.curUser = ''
        self.User_pwd = {}
        

        # 其他快捷键
        QShortcut(QKeySequence(self.tr("Delete")), self, self.deleteFile)
        
    def init_ui(self):
        self.readFile()
        self.set_window()
        self.init_location()
        self.set_event()
        self.load_menu()
        self.load_tools()
        self.load_addtree()
        
    def set_window(self):
        self.resize(1200, 800)
        self.setWindowTitle('多用户多级目录文件管理系统')
        self.setWindowIcon(QIcon('img/folder.ico'))

        qr = self.frameGeometry()
        centerPlace = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(centerPlace)
        self.move(qr.topLeft())

        self.grid = QGridLayout()  # 网格布局
        self.grid.setSpacing(10)
        self.widGet = QWidget()
        self.widGet.setLayout(self.grid)
        self.setCentralWidget(self.widGet)
        
    def set_event(self):
        self.exitAction = QAction(QIcon('file.png'), '退出不保存', self)
        self.exitAction.triggered.connect(qApp.quit)
        self.exitAction.setShortcut('Ctrl+E')

        self.backAction = QAction(QIcon('img/back.png'), '&返回(Alt+4)', self)
        self.backAction.triggered.connect(self.backEvent)
        self.backAction.setShortcut('Alt+4')
        
        self.backAction_ = QAction(QIcon('img/parent.png'), '&上一层(Alt+8)', self)
        self.backAction_.triggered.connect(self.backEvent)
        self.backAction_.setShortcut('Alt+8')
        
        self.forwardAction = QAction(QIcon('img/forward.png'), '&前进(Alt+6)', self)
        self.forwardAction.triggered.connect(self.forwardEvent)
        self.forwardAction.setShortcut('Alt+6')
          
    def load_menu(self):
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('文件')
        fileMenu.addAction(self.exitAction)
        menubar.addAction('刷新', self.updatePrint)
        menubar.addAction('格式化', self.format)
        menubar.addAction('系统概述', self.introduction)

    def load_tools(self):
        self.toolBar = self.addToolBar('工具栏')
        self.toolBar.addAction(self.backAction)
        self.toolBar.addAction(self.forwardAction)
        self.toolBar.addAction(self.backAction_)

        self.forwardAction.setEnabled(False)
        self.backAction.setEnabled(False)
        
        self.toolBar.addSeparator()
        
        # 设置自动补全
        self.toolBar.addWidget(self.ptrWidget)
        self.toolBar.setMovable(False)
        
    def init_location(self):
        self.curNode = self.catalog[0]
        self.rootNode = self.curNode
        self.baseUrl = ['root']

        self.curLocation = QLineEdit()
        self.curLocation.setText('> root')
        self.curLocation.setReadOnly(True) # 设置只读
        self.curLocation.addAction(
            QIcon('img/folder.png'), QLineEdit.LeadingPosition)

        self.curLocation.setMinimumHeight(40)
        self.ptrLayout = QFormLayout()
        self.ptrLayout.addRow(self.curLocation)

        self.ptrWidget = QWidget()
        self.ptrWidget.setLayout(self.ptrLayout)
        self.ptrWidget.adjustSize()
        
    def load_addtree(self):
        self.tree = QTreeWidget()
        self.tree.setColumnCount(1)
        self.tree.setHeaderLabels(['快速访问'])
        self.buildTree()
        self.tree.setCurrentItem(self.rootItem)
        self.treeItem = [self.rootItem]
        #传递item和列号
        self.tree.itemClicked['QTreeWidgetItem*', 
                              'int'].connect(self.clickTreeItem)
        self.grid.addWidget(self.tree, 1, 0)
        
    def introduction(self):
        QMessageBox.about(self, '系统概述',
                          '本系统采用FAT和位示图融合的办法实现文件管理系统\n' +
                          '1.支持多用户，具有登录操作\n' +
                          '2.支持多级目录，同时左侧的地址栏可以快速加载某个目录\n' +
                          '3.create：右击即可选择新建文件或目录\n' +
                          '4.open：右击选中或者双击打开文件\n' +
                          '5.delete：右击选中或者通过Delete快捷键删除文件\n' +
                          '6.attribute：选中文件右击可以查看该文件属性，不选中可以查看当前所在目录的属性\n' +
                          '7.rename:右击选中需要重命名的文件或目录即可重命名\n' +
                          '8.share：右击选中即可选择进入共享功能，能够管理共享组\n'
                          )

    def clickTreeItem(self, item, column):
        ways = [item]
        # 查看所在层数
        level = 0
        temp = item

        while temp.parent() != None:
            temp = temp.parent()
            ways.append(temp)
            level += 1
        ways.reverse()
        # 使得curnode指向根节点
        while self.backEvent():
            pass
        self.baseUrl = self.baseUrl[:1]
        self.treeItem = self.treeItem[:1]

        for i in ways:
            if i == self.rootItem:
                continue
            # 从curNode中查询item
            newNode = None
            for j in self.curNode.children:
                if j.name == i.text(0):
                    newNode = j
                    break
            # 前往路径j
            if newNode.isFile:
                break
            else:
                self.curNode = newNode
                self.updateLoc()
                self.baseUrl.append(newNode.name)
                
                # 更新路径
                for j in range(self.treeItem[-1].childCount()):
                    if self.treeItem[-1].child(j).text(0) == newNode.name:
                        selectedItem = self.treeItem[-1].child(j)
                self.treeItem.append(selectedItem)
                self.tree.setCurrentItem(selectedItem)

        self.updatePrint()

        if self.curNode != self.rootNode:
            self.backAction.setEnabled(True)

        self.forwardAction.setEnabled(False)
        self.lastLoc = -1

    def updateLoc(self):
        self.loadCurFile()
        self.listView.curNode = self.curNode

    def openFile(self, modelindex: QModelIndex) -> None:
        self.listView.close_edit()
        try:
            # 双击 或 前进键
            item = self.listView.item(modelindex.row())
        except:
            # 右键
            if len(self.listView.selectedItems()) == 0:
                return
            item = self.listView.selectedItems()[-1]

        # 如果当前还可以前进,说明是前进按钮触发的
        if self.lastLoc != -1 and self.nextStep:
            item = self.listView.item(self.lastLoc)
            self.lastLoc = -1
            self.forwardAction.setEnabled(False)
        self.nextStep = False

        newNode = None # 得到要处理的node对象
        for i in self.curNode.children:
            if i.name == item.text():
                newNode = i
                break
            
        if not self.check_permission(item=newNode):
            QMessageBox.critical(self, '拒绝', '你没有该目录或该文件的权限')
            return
        
        if newNode.isFile:
            data = newNode.data.read(self.fat, self.disk)
            self.child = editForm(newNode.name, data)
            self.child._signal.connect(self.writeData2File)
            self.child.show()
            self.writeFile = newNode
        else:
            # 进下一级目录前，如果处于编辑状态，一定要取消编辑
            self.listView.close_edit()

            self.curNode = newNode
            self.updateLoc() 
            self.baseUrl.append(newNode.name)

            # 更新路径
            for i in range(self.treeItem[-1].childCount()):
                if self.treeItem[-1].child(i).text(0) == newNode.name:
                    selectedItem = self.treeItem[-1].child(i)
            self.treeItem.append(selectedItem)
            self.tree.setCurrentItem(selectedItem)
            self.backAction.setEnabled(True)

            self.updatePrint()

    def updatePrint(self):
        free = self.fat.check_free(self.disk)
        self.statusBar().showMessage(str(len(self.curNode.children))+'个项目'+
                                     '          '+
                                     '磁盘剩余空间为：'+str(free)+'B')
        s = '> root'
        for i, item in enumerate(self.baseUrl):
            if i == 0:
                continue
            s += " > " + item
        self.curLocation.setText(s)

    def rename(self):
        if len(self.listView.selectedItems()) == 0:
            return
        self.listView.editSelected(self.listView.selectedIndexes()[-1].row())
        self.updateTree()

    def deleteFile(self):
        if len(self.listView.selectedItems()) == 0:
            return
        item = self.listView.selectedItems()[-1]
        index = self.listView.selectedIndexes()[-1].row()
        # 消息盒子
        reply = QMessageBox()
        reply.setWindowTitle('提醒')
        if self.curNode.children[index].isFile:
            reply.setText('确定要删除文件'+item.text()+'吗？')
        else:
            reply.setText('确定要删除文件夹'+item.text()+'及其内部所有内容吗？')
        reply.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        buttonY = reply.button(QMessageBox.Yes)
        buttonY.setText('确定')
        buttonN = reply.button(QMessageBox.No)
        buttonN.setText('取消')
        reply.exec_()

        if reply.clickedButton() == buttonN:
            return

        self.listView.takeItem(index)
        del item
 
        self.delete_Recursive(self.curNode.children[index])
        self.curNode.children.remove(self.curNode.children[index])
        self.catalog = self.updateCatalog_Recursive(self.rootNode)

        self.updateTree()

    def delete_Recursive(self, node):
        if node.isFile:
            node.data.delete(self.fat, self.disk)
            #node.data: FCB
        else:
            for i in node.children:
                self.delete_Recursive(i)

    def updateCatalog_Recursive(self, node):
        if node.isFile:
            return [node]
        else:
            x = [node]
            for i in node.children:
                x += self.updateCatalog_Recursive(i)
            return x
        
    def check_permission(self, item=None):
        if self.curUser == 'root':
            return True
        if item == None: 
            if self.curNode.name == 'root' or self.curNode.owner == self.curUser or self.curUser in self.curNode.permission_group:
                return True
        else:
            if item.owner == self.curUser or self.curUser in item.permission_group:
                return True
        return False
    
    def createFolder(self):
        if not self.check_permission():
            QMessageBox.critical(self, '拒绝', '你没有该目录或该文件的权限')
            return
        self.item_1 = QListWidgetItem(QIcon("img/folder.png"), "新建文件夹")
        self.listView.addItem(self.item_1)
        self.listView.editLast()
        newNode = CatalogNode(self.item_1.text(), False, self.fat,
                              self.disk, time.localtime(time.time()), self.curNode)
        newNode.owner += self.curUser
        self.curNode.children.append(newNode)
        self.catalog.append(newNode)
        self.updateTree()

    def createFile(self):
        if not self.check_permission():
            return
        self.item_1 = QListWidgetItem(QIcon("img/file.png"), "新建文件")
        self.listView.addItem(self.item_1)
        self.listView.editLast()
        newNode = CatalogNode(self.item_1.text(), True, self.fat,
                              self.disk, time.localtime(time.time()), self.curNode)
        newNode.owner += self.curUser
        self.curNode.children.append(newNode)
        self.catalog.append(newNode)
        self.updateTree()

    def viewAttribute(self):
        if len(self.listView.selectedItems()) == 0:  # 查看当前路径属性
            self.child = attributeForm(self.curNode.name, False, self.curNode.createTime,
                                       self.curNode.updateTime, self.curNode, len(self.curNode.children))
            self.child.show()
            return
        else:
            # 文件夹或文件属性
            node = self.curNode.children[self.listView.selectedIndexes()[-1].row()]
            if node.isFile:
                self.child = attributeForm(
                    node.name, node.isFile, node.createTime, node.updateTime, node, 0)
            else:
                self.child = attributeForm(
                    node.name, node.isFile, node.createTime, node.updateTime, node, len(node.children))
            self.child.show()
            return

    def show_rightclicked_menu(self, point):
        menu = QMenu(self.listView)
        # 选中了一些元素
        if len(self.listView.selectedItems()) != 0:
            openFileAction = QAction(QIcon('img/open.png'), '打开')
            openFileAction.triggered.connect(self.openFile)
            menu.addAction(openFileAction)

            deleteAction = QAction(QIcon('img/delete.png'), '删除')
            deleteAction.triggered.connect(self.deleteFile)
            menu.addAction(deleteAction)

            shareAction = QAction(QIcon('img/share.png'), '共享')
            shareAction.triggered.connect(self.shareFile)
            menu.addAction(shareAction)
            
            renameAction = QAction(QIcon('img/rename.png'), '重命名')
            renameAction.triggered.connect(self.rename)
            menu.addAction(renameAction)

            viewAttributeAction = QAction(QIcon('img/attribute.png'), '属性')
            viewAttributeAction.triggered.connect(self.viewAttribute)
            menu.addAction(viewAttributeAction)

            dest_point = self.listView.mapToGlobal(point)
            menu.exec_(dest_point)
        else:
            viewMenu = QMenu(menu)
            viewMenu.setTitle('查看')
            viewMenu.setIcon(QIcon('img/look.png'))
            
            def bigIcon():
                self.listView.setIconSize(QSize(172, 172))
                self.listView.setGridSize(QSize(200, 200))
            

            def middleIcon():
                self.listView.setIconSize(QSize(72, 72))
                self.listView.setGridSize(QSize(100, 100))
                
            def smallIcon():
                self.listView.setIconSize(QSize(56, 56))
                self.listView.setGridSize(QSize(84, 84))
            
            bigIconAction = QAction(QIcon(), '大图标')   
            bigIconAction.triggered.connect(bigIcon)
            viewMenu.addAction(bigIconAction)

            middleIconAction = QAction(QIcon(), '中等图标')   
            middleIconAction.triggered.connect(middleIcon)
            viewMenu.addAction(middleIconAction)

            smallIconAction = QAction(QIcon(), '小图标')
            smallIconAction.triggered.connect(smallIcon)
            viewMenu.addAction(smallIconAction)

            menu.addMenu(viewMenu)

            createMenu = QMenu(menu)
            createMenu.setTitle('新建')

            createFolderAction = QAction(QIcon('img/folder.png'), '文件夹')
            createFolderAction.triggered.connect(self.createFolder)
            createMenu.addAction(createFolderAction)

            createFileAction = QAction(QIcon('img/file.png'), '文件')
            createFileAction.triggered.connect(self.createFile)
            createMenu.addAction(createFileAction)

            createMenu.setIcon(QIcon('img/create.png'))
            menu.addMenu(createMenu)

            shareAction = QAction(QIcon('img/share.png'), '共享')
            shareAction.triggered.connect(self.shareFile)
            menu.addAction(shareAction)
            
            refreshAction = QAction(QIcon('img/refresh.png'), '刷新')
            refreshAction.triggered.connect(self.updatePrint)
            menu.addAction(refreshAction)
            
            viewAttributeAction = QAction(QIcon('img/attribute.png'), '属性')
            viewAttributeAction.triggered.connect(self.viewAttribute)
            menu.addAction(viewAttributeAction)

            self.nextStep = False

            dest_point = self.listView.mapToGlobal(point)
            menu.exec_(dest_point)
    
    def shareFile(self):
        try:         # 双击 或 前进键
            item = self.listView.item(modelindex.row())
        except:
            # 右键
            if len(self.listView.selectedItems()) == 0:
                return
            item = self.listView.selectedItems()[-1]

        newNode = None # 得到要处理的node对象
        for i in self.curNode.children:
            if i.name == item.text():
                newNode = i
                break
        
        shareFrame = shareForm(newNode, self.curUser, self.User_pwd)
        shareFrame.exec_()
        
        with open('catalog', 'wb') as f:
            f.write(pickle.dumps(self.catalog))
        
        
    def updateTree(self):
        node = self.rootNode
        item = self.rootItem

        if item.childCount() < len(node.children): #树上的孩子数量小于文件夹的孩子数量，说明新建了
            child = QTreeWidgetItem(item)
        elif item.childCount() > len(node.children): #树上的孩子数量大于文件夹的孩子数量，说明删除了
            for i in range(item.childCount()):
                if i == item.childCount()-1:
                    item.removeChild(item.child(i))
                    break
                # 顺序是一样的，所以也一定相同名字
                # 不相同说明删除了这个 
                if item.child(i).text(0) != node.children[i].name: 
                    item.removeChild(item.child(i))
                    break
        for i in range(len(node.children)):
            self.updateTreeRecursive(node.children[i], item.child(i))
        self.updateTreeRecursive(node, item)

    def updateTreeRecursive(self, node: CatalogNode, item: QTreeWidgetItem):
        item.setText(0, node.name)
        if node.isFile:
            item.setIcon(0, QIcon('img/file.png'))
        else:
            if len(node.children) == 0:#无子树，用空文件夹图标
                item.setIcon(0, QIcon('img/folder.png'))
            else:
                item.setIcon(0, QIcon('img/folderWithFile.png'))
            if item.childCount() < len(node.children):#树上的孩子数量小于文件夹的孩子数量，说明新建了
                child = QTreeWidgetItem(item)
            elif item.childCount() > len(node.children):#树上的孩子数量大于文件夹的孩子数量，说明删除了
                for i in range(item.childCount()):
                    if i == item.childCount()-1:
                        item.removeChild(item.child(i))
                        break
                    if item.child(i).text(0) != node.children[i].name:
                        item.removeChild(item.child(i))
                        break
            for i in range(len(node.children)):
                self.updateTreeRecursive(node.children[i], item.child(i))

    def buildTree(self):
        self.tree.clear()
        self.rootItem = self.buildTreeRecursive(self.catalog[0], self.tree)
        self.tree.addTopLevelItem(self.rootItem) #将该项目作为顶级项目
        self.tree.expandAll() #展开目录树

    def buildTreeRecursive(self, node: CatalogNode, parent: QTreeWidgetItem):
        child = QTreeWidgetItem(parent)
        child.setText(0, node.name) #第0列
        if node.isFile:
            child.setIcon(0, QIcon('img/file.png'))
        else:
            if len(node.children) == 0:# 无子树，用空文件夹图标
                child.setIcon(0, QIcon('img/folder.png'))
            else:
                child.setIcon(0, QIcon('img/folderWithFile.png'))
            for i in node.children:
                self.buildTreeRecursive(i, child)
        return child
    
    def writeData2File(self, parameter):
        self.writeFile.data.update(parameter, self.fat, self.disk)
        self.writeFile.updateTime = time.localtime(time.time())
        
    def loadCurFile(self):
        self.listView.clear()
        for i in self.curNode.children:
            if i.isFile:
                self.item_1 = QListWidgetItem(QIcon("img/file.png"), i.name)
                self.listView.addItem(self.item_1)
            else:
                if len(i.children) == 0:
                    self.item_1 = QListWidgetItem(
                        QIcon("img/folder.png"), i.name)
                else:
                    self.item_1 = QListWidgetItem(
                        QIcon("img/folderWithFile.png"), i.name)
                self.listView.addItem(self.item_1)

    def format(self):
        """
        对象的格式化
        """
        # 结束编辑
        self.listView.close_edit()

        # 提示框
        reply = QMessageBox()
        reply.setWindowTitle('提醒')
        reply.setText('确定要格式化磁盘吗？(执行此操作不可恢复！)')
        reply.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        buttonY = reply.button(QMessageBox.Yes)
        buttonY.setText('确定')
        buttonN = reply.button(QMessageBox.No)
        buttonN.setText('取消')
        reply.exec_()
        reply.show()

        if reply.clickedButton() == buttonN:
            return

        self.fat = FAT()
        self.fat.fat = [-2]*blockNum
        self.disk = []
        for i in range(blockNum):
            self.disk.append(Block(i))
        self.catalog = []
        self.catalog.append(CatalogNode(
            "root", False, self.fat, self.disk, time.localtime(time.time())))
        # 写空各个表
        with open('fat', 'wb') as f:
            f.write(pickle.dumps(self.fat))
        with open('disk', 'wb') as f:
            f.write(pickle.dumps(self.disk))
        with open('catalog', 'wb') as f:
            f.write(pickle.dumps(self.catalog))

        self.hide() 
        self.winform = mainForm() #重开新窗口
        self.winform.show()

    def saveFile2loc(self):
        """
        将内存中的文件存到本地
        """
        with open('fat', 'wb') as f:
            f.write(pickle.dumps(self.fat))
        with open('disk', 'wb') as f:
            f.write(pickle.dumps(self.disk))
        with open('catalog', 'wb') as f:
            f.write(pickle.dumps(self.catalog))

    def readFile(self):
        # 读取fat表
        if not os.path.exists('fat'):
            self.fat = FAT()
            self.fat.fat = [-2]*blockNum
            # 存储fat表
            with open('fat', 'wb') as f:
                f.write(pickle.dumps(self.fat))
        else:
            with open('fat', 'rb') as f:
                self.fat = pickle.load(f)
        # 读取disk表
        if not os.path.exists('disk'):
            self.disk = []
            for i in range(blockNum):
                self.disk.append(Block(i))
            # 存储disk表
            with open('disk', 'wb') as f:
                f.write(pickle.dumps(self.disk))
        else:
            with open('disk', 'rb') as f:
                self.disk = pickle.load(f)
        # 读取catalog表
        if not os.path.exists('catalog'):
            self.catalog = []
            self.catalog.append(CatalogNode(
                "root", False, self.fat, self.disk, time.localtime(time.time())))
            # 存储
            with open('catalog', 'wb') as f:
                f.write(pickle.dumps(self.catalog))
        else:
            with open('catalog', 'rb') as f:
                self.catalog = pickle.load(f)

    def initial(self):
        # fat表
        self.fat = FAT()
        self.fat.fat = [-2]*blockNum
        # 存储fat表
        with open('fat', 'ab') as f:
            f.write(pickle.dumps(self.fat))

        # disk表
        self.disk = []
        for i in range(blockNum):
            self.disk.append(Block(i))
        # 存储disk表
        with open('disk', 'ab') as f:
            f.write(pickle.dumps(self.disk))

        # catalogNode
        self.catalog = []
        self.catalog.append(CatalogNode(
            "root", False, self.fat, self.disk, time.localtime(time.time())))
        # 存储
        with open('catalog', 'ab') as f:
            f.write(pickle.dumps(self.catalog))

    def backEvent(self):
        self.listView.close_edit()
        if self.rootNode == self.curNode:
            return False
        # 记录上次所在位置
        for i in range(len(self.curNode.parent.children)):
            if self.curNode.parent.children[i].name == self.curNode.name:
                self.lastLoc = i
                self.forwardAction.setEnabled(True)
                break
        self.curNode = self.curNode.parent
        self.updateLoc()
        self.baseUrl.pop()
        self.treeItem.pop()
        self.tree.setCurrentItem(self.treeItem[-1])
        self.updateTree()
        self.updatePrint()

        if self.curNode == self.rootNode:
            self.backAction.setEnabled(False)

        return True

    def forwardEvent(self):
        self.nextStep = True
        self.openFile(QModelIndex())

    def closeEvent(self, event):
        # 结束编辑
        self.listView.close_edit()

        reply = QMessageBox()
        reply.setWindowTitle('提醒')
        reply.setText('是否保存当前状态')
        reply.setStandardButtons(
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Ignore)
        buttonY = reply.button(QMessageBox.Yes)
        buttonY.setText('保存')
        buttonN = reply.button(QMessageBox.No)
        buttonN.setText('取消')
        buttonI = reply.button(QMessageBox.Ignore)
        buttonI.setText('不保存')

        reply.exec_()

        if reply.clickedButton() == buttonI:
            event.accept()
        elif reply.clickedButton() == buttonY:
            self.saveFile2loc()
            event.accept()
        else:
            event.ignore()
