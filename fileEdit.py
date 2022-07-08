from hashlib import new
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon,QStandardItem,QStandardItemModel
import PyQt5.QtCore
from PyQt5.Qt import *
from File import *
import time
import os
import pickle
from MyWidget import MyListWidget

class editForm(QWidget):
    _signal = PyQt5.QtCore.pyqtSignal(str)
    def __init__(self, name, data):
        super().__init__()
        self.resize(1200,800)
        self.setWindowTitle(name)
        self.name=name
        self.setWindowIcon(QIcon('img/file.png'))
        
        self.resize(412, 412)
        self.text_edit = QTextEdit(self) # 实例化一个QTextEdit对象
        self.text_edit.setText(data) # 设置编辑框初始化时显示的文本
        self.text_edit.setPlaceholderText("在此输入文件内容") # 设置占位字符串
        self.text_edit.textChanged.connect(self.changeMessage) # 判断文本是否发生改变
        self.initialData=data

        self.h_layout = QHBoxLayout()
        self.v_layout = QVBoxLayout()
        

        self.v_layout.addWidget(self.text_edit)
        self.v_layout.addLayout(self.h_layout)
        
        self.setLayout(self.v_layout)

        #self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setWindowModality(PyQt5.QtCore.Qt.ApplicationModal)
        #self.statusBar().showMessage('共'+str(len(self.text_edit.toPlainText()))+'字')


    def closeEvent(self, event):
        #如果打开后没有修改，则直接关闭即可
        if self.initialData==self.text_edit.toPlainText():
            event.accept()
            return

        reply=QMessageBox()
        reply.setWindowTitle('提醒')
        reply.setText('您想将更改保存到'+self.name+'吗？')
        reply.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Ignore)
        buttonY = reply.button(QMessageBox.Yes)
        buttonY.setText('保存')
        buttonN = reply.button(QMessageBox.No)
        buttonN.setText('不保存')
        buttonI=reply.button(QMessageBox.Ignore)
        buttonI.setText('取消')

        reply.exec_()

        if reply.clickedButton()==buttonI:
            event.ignore()
        elif reply.clickedButton()==buttonY:
            self._signal.emit(self.text_edit.toPlainText())
            event.accept()
        else:
            event.accept()

    def changeMessage(self):
        #self.statusBar().showMessage('共'+str(len(self.text_edit.toPlainText()))+'字')
        pass

    def button_slot(self, button):
        if button == self.save_button:
            choice = QMessageBox.question(self, "Question", "Do you want to save it?", QMessageBox.Yes | QMessageBox.No)
            if choice == QMessageBox.Yes:
                with open('First text.txt', 'w') as f:
                    f.write(self.text_edit.toPlainText())
                self.close()
            elif choice == QMessageBox.No:
                self.close()
        elif button == self.clear_button:
            self.text_edit.clear()


class attributeForm(QWidget):
    def __init__(self, name, isFile, createTime, updateTime, node, child=0):
        super().__init__()
        self.resize(1200,800)
        self.setWindowTitle('属性')
        self.name=name
        self.setWindowIcon(QIcon('img/attribute.png'))
        self.permission = node.permission_group
        self.permission.append(node.owner)
        self.resize(412, 412)
        self.permission = list(set(self.permission))
        grid=QGridLayout()

        #图片
        if isFile:
            self.icon=QPixmap('img/file.png')
        else:
            self.icon=QPixmap('img/folder.png')
        
        lbl=QLabel(self)
        lbl.setPixmap(self.icon)
        grid.addWidget(lbl, 0,0)

        #文件名
        fileName=QLabel(self)
        fileName.setText('名称:'+self.name)
        font=QFont()
        font.setPointSize(14)
        fileName.setFont(font)

        grid.addWidget(fileName,1,0)

        #权限显示
        permission = QLabel(self)
        permission.setText('权限拥有者:'+ '、'.join(self.permission))
        permission.setFont(font)
        
        grid.addWidget(permission, 2, 0)
        
        #创建时间
        createLabel=QLabel(self)
        year=str(createTime.tm_year)
        month=str(createTime.tm_mon)
        day=str(createTime.tm_mday)
        hour=str(createTime.tm_hour)
        hour=hour.zfill(2)
        minute=str(createTime.tm_min)
        minute=minute.zfill(2)
        second=str(createTime.tm_sec)
        second=second.zfill(2)
        createLabel.setText('创建时间：'+year+'年'+
        month+'月'+
        day+'日 '+hour+':'+
        minute+':'+second)
        createLabel.setFont(font)

        grid.addWidget(createLabel,3,0)

        #更新时间
        if isFile:
            updateLabel=QLabel(self)
            year=str(updateTime.tm_year)
            month=str(updateTime.tm_mon)
            day=str(updateTime.tm_mday)
            hour=str(updateTime.tm_hour)
            hour=hour.zfill(2)
            minute=str(updateTime.tm_min)
            minute=minute.zfill(2)
            second=str(updateTime.tm_sec)
            second=second.zfill(2)
            updateLabel.setText('修改时间：'+year+'年'+
            month+'月'+
            day+'日 '+hour+':'+
            minute+':'+second)
            updateLabel.setFont(font)

            grid.addWidget(updateLabel,4,0)
        
        else:
            updateLabel=QLabel(self)
            updateLabel.setText('内部共'+str(child)+'个项目')
            updateLabel.setFont(font)

            grid.addWidget(updateLabel,4,0)

        self.setLayout(grid)
        self.setWindowModality(PyQt5.QtCore.Qt.ApplicationModal)


class shareForm(QDialog):
    def __init__(self, node, user, dict):
        super().__init__()  
        self.init_ui(node, user, dict)
        self.node = node
        
    def init_ui(self, node, user, dict:dict):
        self.setWindowTitle('文件管理系统---共享用户选择')
        self.setWindowIcon(QIcon('img/folder.ico'))
        
        self.users = list(dict.keys())
        self.users.remove(user)
        self.users.remove('root')
        self.v_layout = QVBoxLayout()
        self.h_layout = QHBoxLayout()
        self.setLayout(self.v_layout)
        self.label_ = QLabel('勾选所有想要操作的用户', self)
        self.v_layout.addWidget(self.label_)
        self.ok_button = QPushButton('加入共享组', self)
        self.no_button = QPushButton('移出共享组', self)
        self.L_btn = self.get_L_btn()
        self.v_layout.addLayout(self.h_layout)
        self.h_layout.addWidget(self.ok_button)
        self.h_layout.addWidget(self.no_button)
        self.ok_button.clicked.connect(self.deal)
        self.no_button.clicked.connect(self.deq)
    
    def get_L_btn(self):
        L_btn=[]
        for i in range(len(self.users)):
           L_btn.append(QCheckBox(self.users[i], self))
           self.v_layout.addWidget(L_btn[-1])
        return L_btn
    
    def deal(self):
        permg = []
        for i in range(len(self.L_btn)):
            if self.L_btn[i].isChecked():
                permg.append(self.users[i])
        self.node.permission_group.extend(permg)
        self.node.permission_group = list(set(self.node.permission_group))
        self.close()
    
    def deq(self):
        for i in range(len(self.L_btn)):
            if self.L_btn[i].isChecked():
                if self.users[i] in self.node.permission_group:
                    self.node.permission_group.remove(self.users[i])
        self.close()
                    
'''            
class Node(object):
    def __init__(self):
        self.permission_group = []      

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dict_ = {
        'hzt':1,
        'zzx':2,
        'zdz':2,
        'cjh':3
    }
    user = 'hzt'
    node = Node()
    frame = shareForm(node, user, dict_)
    frame.show()
    exit(app.exec_())
'''    