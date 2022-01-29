from PyQt5.QtWidgets import QApplication, QMessageBox, QInputDialog
from PyQt5.uic import loadUi
import sys
import rpyc
import socket
import threading
client = None
def listen():
    while True:
        print("called")
        data = client.recv(1024)
        print("RECEIVED")
        data = data.decode()
        type = data[0:2]
        data = data[2:]
        if type == "u:":
            data = eval(data)
            chat_panel.users_list.clear()
            chat_panel.users_list.addItems(data)
        elif type == "m:":
            chat_panel.chat_box.append(data+"\n")

def show_register_panel():
    register_panel.show()

def register():
    username = register_panel.usernamef.text()
    email = register_panel.emailf.text()
    password1 = register_panel.passwordf.text()
    password2 = register_panel.passwordf2.text()
    if password1 == password2:
        result = RPC_Service.register(username, email, password1)
        if result == False:
            message_box = QMessageBox()
            message_box.setText("Registration Failed, Please Try Again Later")
            message_box.setIcon(QMessageBox.Information)
            message_box.exec()
        else:
            code, ok = QInputDialog.getText(register_panel, "active code", "Enter your active code")
            if ok:
                result = RPC_Service.activation(username, code)
                #TODO show proper message
                register_panel.hide()
    else:
        message_box = QMessageBox()
        message_box.setText("Passwords Do Not Match")
        message_box.setIcon(QMessageBox.Warning)
        message_box.exec()
        pass

def login():
    global client
    username = login_panel.usernamef.text()
    password = login_panel.passwordf.text()
    result = RPC_Service.login(username, password)
    if result == False:
        message = QMessageBox()
        message.setText("Username or Password Is Not Correct")
        message.setIcon(QMessageBox.Warning)
        message.exec()
    else:
        chat_panel.show()
        client = socket.socket()
        client.connect(("localhost", 5051))
        threading.Thread(target=listen).start()

def send():
    print("sending..")
    message = chat_panel.messagef.text()
    message = message.encode()
    print(message)
    client.send(message)










if __name__ == '__main__':
    app = QApplication(sys.argv)
    login_panel = loadUi('ui/login.ui')
    register_panel = loadUi('ui/register.ui')
    chat_panel = loadUi('ui/chat.ui')
    login_panel.show()
    #connect to rpc service
    RPC_Service = rpyc.connect("localhost",5050).root

    #action
    login_panel.registerb.clicked.connect(show_register_panel)
    login_panel.loginb.clicked.connect(login)
    register_panel.registerb.clicked.connect(register)
    chat_panel.sendb.clicked.connect(send)
    app.exec()