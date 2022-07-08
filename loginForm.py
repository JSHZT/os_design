from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon
import qtawesome
import sys
import pickle
import sys
from PyQt5.QtWidgets import *
from mainForm import mainForm

USER_PWD = {
    }

class LoginForm(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.loadfile()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('文件管理系统--Login')
        self.setWindowIcon(QIcon('img/folder.ico'))
        self.resize(300, 200)
        
        qr = self.frameGeometry()
        centerPlace = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(centerPlace)
        self.move(qr.topLeft())
        
        self.myframe = QFrame(self)
        self.myframe.resize(300,  170)
        self.myframe.move(0, 20)
        self.acct_label = QLabel('Username:', self)
        self.psw_label = QLabel('Password:', self)
        

        self.acct_line = QLineEdit(self)
        self.psw_line = QLineEdit(self)
        self.acct_line.setPlaceholderText('Please enter your username')
        self.psw_line.setPlaceholderText('Please enter your password')
        self.psw_line.setEchoMode(QLineEdit.Password)
        self.login_button = QPushButton('Log in', self)
        self.login_button.clicked.connect(self.login)
        self.signin_button = QPushButton('Sigin in', self)
        self.signin_button.clicked.connect(self.signin)
        
        
        self.grid_layout = QGridLayout()
        self.h_layout = QHBoxLayout()
        self.v_layout = QVBoxLayout()

        self.init_layout()
        self.signin_page = SigninPage()   
    
    def loadfile(self):
        global USER_PWD
        f_read = open('user', 'rb')
        USER_PWD = pickle.load(f_read)
        f_read.close()
    
    def savefile(self):
        global USER_PWD
        f_save = open('user', 'wb')
        pickle.dump(USER_PWD, f_save)
        f_save.close()

    def init_layout(self):
        self.grid_layout.setSpacing(20)
        self.grid_layout.addWidget(self.acct_label, 0, 0, 1, 1)
        self.grid_layout.addWidget(self.acct_line, 0, 1, 1, 1)
        self.grid_layout.addWidget(self.psw_label, 1, 0, 1, 1)
        self.grid_layout.addWidget(self.psw_line, 1, 1, 1, 1)
        self.h_layout.setSpacing(40)
        self.h_layout.addWidget(self.login_button)
        self.h_layout.addWidget(self.signin_button)
        self.v_layout.addLayout(self.grid_layout)
        self.v_layout.addLayout(self.h_layout)
 
        self.myframe.setLayout(self.v_layout)

    def login(self):
        acct, psw = self.acct_line.text(), self.psw_line.text()
        if USER_PWD.get(acct) == psw:
            mainform = mainForm()
            mainform.curUser = acct
            mainform.User_pwd = USER_PWD
            mainform.show()
            self.close()
        else:
            QMessageBox.critical(self, 'Wrong', 'Wrong Username or Password!')
 
        self.acct_line.clear()
        self.psw_line.clear()

    def signin(self):
        self.signin_page.exec_()


class SigninPage(QDialog):
    def __init__(self):
        super(SigninPage, self).__init__()
        self.setWindowTitle('文件管理系统--signin')
        self.setWindowIcon(QIcon('img/folder.ico'))
        self.signin_user_label = QLabel('Username:', self)
        self.signin_pwd_label = QLabel('Password:', self)
        self.signin_pwd2_label = QLabel('Password:', self)
        self.signin_user_line = QLineEdit(self)
        self.signin_pwd_line = QLineEdit(self)
        self.signin_pwd2_line = QLineEdit(self)
        self.signin_button = QPushButton('Sign in', self)
 
        self.user_h_layout = QHBoxLayout()
        self.pwd_h_layout = QHBoxLayout()
        self.pwd2_h_layout = QHBoxLayout()
        self.all_v_layout = QVBoxLayout()
 
        self.lineedit_init()
        self.pushbutton_init()
        self.layout_init()
 
    def layout_init(self):
        self.user_h_layout.addWidget(self.signin_user_label)
        self.user_h_layout.addWidget(self.signin_user_line)
        self.pwd_h_layout.addWidget(self.signin_pwd_label)
        self.pwd_h_layout.addWidget(self.signin_pwd_line)
        self.pwd2_h_layout.addWidget(self.signin_pwd2_label)
        self.pwd2_h_layout.addWidget(self.signin_pwd2_line)
 
        self.all_v_layout.addLayout(self.user_h_layout)
        self.all_v_layout.addLayout(self.pwd_h_layout)
        self.all_v_layout.addLayout(self.pwd2_h_layout)
        self.all_v_layout.addWidget(self.signin_button)
 
        self.setLayout(self.all_v_layout)
 
    def lineedit_init(self):
        self.signin_pwd_line.setEchoMode(QLineEdit.Password)
        self.signin_pwd2_line.setEchoMode(QLineEdit.Password)
 
        self.signin_user_line.textChanged.connect(self.check_input_func)
        self.signin_pwd_line.textChanged.connect(self.check_input_func)
        self.signin_pwd2_line.textChanged.connect(self.check_input_func)
 
    def pushbutton_init(self):
        self.signin_button.setEnabled(False)
        self.signin_button.clicked.connect(self.check_signin_func)
 
    def check_input_func(self):
        if self.signin_user_line.text() and self.signin_pwd_line.text() and self.signin_pwd2_line.text():
            self.signin_button.setEnabled(True)
        else:
            self.signin_button.setEnabled(False)
 
    def check_signin_func(self):
        if self.signin_pwd_line.text() != self.signin_pwd2_line.text():
            QMessageBox.critical(self, 'Wrong', 'Two Passwords Typed Are Not Same!')
        elif self.signin_user_line.text() not in USER_PWD:
            USER_PWD[self.signin_user_line.text()] = self.signin_pwd_line.text()
            QMessageBox.information(self, 'Information', 'Register Successfully')
            self.savefile()
            self.close()
        else:
            QMessageBox.critical(self, 'Wrong', 'This Username Has Been Registered!')
 
        self.signin_user_line.clear()
        self.signin_pwd_line.clear()
        self.signin_pwd2_line.clear()
        
    def savefile(self):
        global USER_PWD
        f_save = open('user', 'wb')
        pickle.dump(USER_PWD, f_save)
        f_save.close()
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    Login = LoginForm()
    Login.show()
    exit(app.exec_())