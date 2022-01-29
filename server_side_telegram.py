import rpyc
import rpyc.utils.server as rpc
import pymysql
import random
import smtplib
import socket
import threading

server_socket = socket.socket()
server_socket.bind(("localhost", 5051))
server_socket.listen(10)

online_usernames = [] #[x]
online_sockets = [] #[client]

def listen(client, username):
    while True:
        print("listening")
        data = client.recv(1024)
        data = data.decode()
        data = "m:"+username+" : "+data
        data = data.encode()
        for client_socket in online_sockets:
            client_socket.send(data)

def start_server():
    while True:
        client, address = server_socket.accept()
        online_sockets.append(client)
        data = ("u:"+str(online_usernames)).encode()
        for client_socket in online_sockets:
            client_socket.send(data)
        threading.Thread(target=listen, args=(client, online_usernames[-1])).start()


class TelegramService(rpyc.Service):

    def on_connect(self, conn):
        super().on_connect(conn)
        self.connection = pymysql.connect(host="localhost", port=3306, user="root", db="telegramfoghesh")
        self.cursor = self.connection.cursor()
        self.mailserver = smtplib.SMTP('smtp.gmail.com', 587)
        self.mailserver.starttls()
        self.mailserver.login('samira.developer.python@gmail.com', '12qwaszx!@')

    def exposed_register(self, username, email, password):
        SQL = "INSERT INTO users values(%s, %s, %s, 0)"
        try:
            self.cursor.execute(SQL, (username, email, password))
            self.connection.commit()
            code = self.send_activation_code(email)
            self.save_activation_code(username, code)
        except:
             return False
        else:
            return True

    def exposed_activation(self, username, code):
        SQL = "SELECT * FROM activationcode where username=%s and code=%s"
        SQL2 = "UPDATE users set enabled=1 where username=%s"
        self.cursor.execute(SQL, (username, code))
        result = self.cursor.fetchall()
        if len(result) > 0 :
            self.cursor.execute(SQL2, (username,))
            self.connection.commit()
            return True
        else:
            return False

    def exposed_login(self, username, password):
        SQL = "SELECT * FROM users where username=%s and password=%s and enabled=1"
        self.cursor.execute(SQL, (username, password))
        result = self.cursor.fetchall()
        if len(result) > 0:
            online_usernames.append(username)
            return True
        else:
            return False

    def send_activation_code(self, email):
        active_code = random.randint(10000, 99999)
        self.mailserver.sendmail('samira.developer.python@gmail.com', email, "Your activation code is " + str(active_code))
        return active_code
    def save_activation_code(self, username, active_code):
        SQL = "INSERT INTO activationcode values(%s, %s)"
        self.cursor.execute(SQL, (username, active_code))
        self.connection.commit()

if __name__ == '__main__':
    threading.Thread(target=start_server).start()
    RPC_Server = rpc.ThreadedServer(TelegramService, port=5050)
    RPC_Server.start()
