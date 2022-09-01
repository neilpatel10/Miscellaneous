from socket import *
from threading import *
from threading import Lock
from socketserver import ThreadingMixIn
import time
import sys


# from ssl import socket_error


class ListUsers:
    def __init__(self):
        self.currUsers = []


"""server's currently logged in user list"""
current = ListUsers()

"""lock variable for threading purposes"""
lock = Lock()


class User:
    def __init__(self, username, userConnection, subs, tweets):
        self.username = username
        self.userConnection = userConnection
        self.subs = subs
        self.tweets = tweets
        self.hashCount = 0


class CliThread(Thread):
    def __init__(self, address, connection):
        Thread.__init__(self)
        self.address = address
        self.threadFlag = False
        self.connection = connection

    def run(self):
        thisuser = ""
        connection = self.connection
        while True:

            message = connection.recv(1024).decode()
            if message == "ACK":
                continue
            if not message:

                lock.acquire()
                for user in current.currUsers:
                    if thisuser == user.username:
                        current.currUsers.remove(user)

                print("user:" + thisuser + " has logged out")
                lock.release()
                break
            #             if not message :
            #                 continue
            print(message)

            """handles the login request by the client"""
            if message[0] == "n":
                lock.acquire()
                flagUser = False
                if not current.currUsers:
                    newUser = User(message[2:], connection, [], [])
                    current.currUsers.append(newUser)
                    reply = 'n"00'
                    connection.sendall(reply.encode())
                    print("user " + newUser.username + " has successfully logged in")
                    thisuser = newUser.username
                else:

                    for user in current.currUsers:
                        if user.username == message[2:]:
                            reply = 'n"11'
                            connection.sendall(reply.encode())
                            print("user already in no can do buddy")

                            flagUser = True
                    if not flagUser:
                        newUser = User(message[2:], connection, [], [])
                        current.currUsers.append(newUser)
                        reply = 'n"00'
                        connection.sendall(reply.encode())
                        print("user " + newUser.username + " has successfully logged in")
                        thisuser = newUser.username
                lock.release()
                if flagUser:
                    break

            """handles the tweet request by the client"""
            if message[0] == "t":
                spliced = [x.strip() for x in message.split('"')]
                hashtag = spliced[len(spliced) - 1]
                reply = 't"00'
                connection.sendall(reply.encode())
                connection.recv(1024)
                lock.acquire()
                for user in current.currUsers:
                    for subs_tag in user.subs:
                        if subs_tag in hashtag or subs_tag == '#ALL':
                            time.sleep(0.1)
                            connect = user.userConnection
                            #                         message[0] = 'h'
                            connect.sendall(('h"' + message[2:]).encode())
                            break

                #                         message[0] = 'w'
                newUser.tweets.append(message[2:])
                lock.release()

            """handles the gettweets request by the client"""
            if message[0] == "w":
                flagUser = False
                lock.acquire()
                for user in current.currUsers:
                    if user.username == message[2:]:
                        flagUser = True
                        connection.sendall(('w"00').encode())
                        connection.recv(1024)
                        for tweet in user.tweets:
                            connection.sendall(('w"' + tweet).encode())
                            connection.recv(1024)

                lock.release()
                if not flagUser:
                    reply = 'w"11"' + message[2:]  # changed
                    connection.sendall(reply.encode())
                else:
                    reply = 'w"01'
                    connection.sendall(reply.encode())

            """handles the subscribe request by the client"""
            if message[0] == "s":
                spliced = [x.strip() for x in message.split('"')]
                lock.acquire()
                for user in current.currUsers:
                    if user.username == spliced[1]:
                        if user.hashCount > 2 or spliced[2] in user.subs:
                            reply = 's"11"' + spliced[2]  # changed
                            connection.sendall(reply.encode())
                        else:
                            user.subs.append(spliced[2])
                            user.hashCount += 1
                            reply = 's"00'
                            connection.sendall(reply.encode())
                lock.release()

            """handles the unsubscribe request by the client"""
            if message[0] == "u":
                spliced = [x.strip() for x in message.split('"')]
                lock.acquire()
                for user in current.currUsers:
                    if user.username == spliced[1]:
                        for u_sub in user.subs:
                            if u_sub == spliced[2] or spliced[2] == "ALL":
                                user.subs.remove(u_sub)
                                user.hashCount -= 1
                reply = 'u"00'
                connection.sendall(reply.encode())

                lock.release()

            """handles the getusers request by the client"""
            if message[0] == "g":
                reply = "g"
                lock.acquire()
                for user in current.currUsers:
                    reply += '"'
                    reply += user.username
                connection.sendall(reply.encode())

                lock.release()
                # connection.recv(1024)

            """handles the exit request by the client"""
            if message[0] == "e":
                lock.acquire()
                for user in current.currUsers:
                    if message[2:] == user.username:
                        current.currUsers.remove(user)
                        reply = 'e"00'
                        connection.sendall(reply.encode())
                print("user:" + message[2:] + " has logged out")
                lock.release()
                break
        thread.threadFlag = True
        sys.exit(0)


"""makes sure that only 1 server port argument"""
if len(sys.argv) != 2:
    sys.exit("Error: ttweetser.py can only have 1 argument")

"""catches when a non integer is given as a server port input"""
try:
    portInput = int(sys.argv[1])
except ValueError:
    sys.exit("Error: Invalid port input try again.")

if 65535 < portInput < 1024:
    sys.exit("Error: Invalid port input try again.")

"""Sets up the socket and thread list"""
serSock = socket(AF_INET, SOCK_STREAM)
serSock.bind(('', portInput))
threads = []

print("Server is up and running.")
print("server is listening...")

try:
    while True:
        serSock.listen(10)
        """line below occurs when server receives a request from a client"""
        connect1, address = serSock.accept()
        thread = CliThread(address, connect1)
        print("thread is about to start")
        thread.start()
        threads.append(thread)
        for t in threads:
            if t.threadFlag:
                t.join()
                # print("User has logged out/error occurred and thread has been killed")
except KeyboardInterrupt:
    sys.exit("Keyboard Interrupt - The program will now stop")
