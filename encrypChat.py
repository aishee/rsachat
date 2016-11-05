"""
encryptChat.py
"""

import sys
import socket
import threading
import encrypt as RSA
import datetime
import os

def Server(host, port):
    """
    Create the server instance, set up the Server
    """
    port = int(port)
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((host, port))
        server.listen(5)

        print "* Waiting for partner to join conversation....*\n"
        conn, client_addr = server.accept()

        print "* Client attempting to connect...*\n"
    except Exception:
        pass

    #Wait to receive client's public key
    recvIsComplete = False
    key = ""
    while not recvIsComplete:
        key += conn.recv(1024)
        if key.strip("~") and key[0] == "~" and key[-1] == "~":
            recvIsComplete = True
    key = key.strip("~").split(',')
    publicTuple = (key[0], key[1])
    print "* Client\'s Public key received *"

    #Send public key to Client
    e, d, c = RSA.keygen()
    sendPublic = str(d) + ',' + str(c)
    conn.send("~" + sendPublic + "~")
    print "* Public key send *"

    privateTuple = (e, c)

    #Receiving test string to make sure encryption is working properly
    recvIsComplete = False
    data = ""
    while not recvIsComplete:
        data += conn.recv(1024)
        if data.strip("~") and data[0] == "~" and data[-1] == "~":
            recvIsComplete = True
    key = key.strip("~").split(',')
    publicTuple = (key[0], key[1])
    print "* Client\s Public Key received *"

    #Send public key to Client
    e, d, c = RSA.keygen()
    sendPublic = str(d) + ',' + str(c)
    conn.send("~" + sendPublic + "~")
    print "* Public Key send *"

    privateTuple = (e, c)
    #Receiving test string to make sure encryption is working properly
    recvIsComplete = False
    data = ""
    while not recvIsComplete:
        data += conn.recv(1024)
        if data.strip("~") and data[0] == "~" and data[-1] == "~":
            recvIsComplete = True
    data = decrypt(data.strip("~"), publicTuple)
    if data != "~Client:Client:abcdefghijklmnopqrstuvwxyz~":
        print "\n* Encryption could not be verified! Please try to reconnect....*\n"
        conn.send("~ABORT~")
        connClose(conn)
        return
    #Sending test string to make sure encryption is working properly
    data = "~Server:abcdefghijklmnopqrstuvwxyz~"
    data = encrypt(data.strip(), privateTuple)
    conn.send("~" + data + "~")

    print "\n* Connected to chat: *\n"
    print "1. Type your messages bellow and hit Enter to send"
    print "2. Type \'file()\' and hit Enter to send a file in the current directory"
    print "3. Type \'quit()\' and hit Enter to leave the conversation\n"

    ReadThread = Thread_Manager('read', conn, publicTuple, None)
    WriteThread = Thread_Manager('write', conn, None, privateTuple)

    ReadThread.start()
    WriteThread.start()

    #Wait until client disconnects
    ReadThread.join()
    print "\n* Your partner has left the conversation. Press any key to quit....*\n"

    #Stop the write threads
    WriteThread.stopWrite()
    WriteThread.join()

    #Shut down client Connection
    try:
        conn.shutdown(socket.SHUT_RDWR)
        conn.close()
    except:
        #Connection already closed
        pass

    #Shutdown server
    connClose(server)


def Client(host, port):
    """
    Creates the client instance, sets up the client
    """
    port = int(port)

def encrypt(data, private):
    """
    Encrypts incoming data with given private key
    """
    encrypted_data = ""
    for i in range(0, len(data)):
        encrypted_data += str(RSA.endecrypt(ord(data[i]), private[0], private[1])) + ","
    return encrypted_data

def decrypt(data, public):
    """
    Decrypts input integer list into sentences
    """

    words = data.split(",")
    decrypted_data = ""
    for i in range(0, len(words) - 1):
        decrypted_data += str(RSA.decode(RSA.endecrypt(words[i], public[0], public[1])))
    return decrypted_data

def connClose(conn):
    """
    Closes given connection
    """
    try:
        print "* Closing all sockets and exiting..."
        conn.shutdown(socket.SHUT_RDWR)
        conn.close()
    except:
        #Connection already closed
        pass

class Thread_Manager(threading.Thread):
    """
    Creates threads for asynchronoues reading and writing
    """
    def __init__(self,action, conn, public, private):
        """
        Constructor for Thread_Manager class
        """
        threading.Thread.__init__(self)
        self.action = action.lower()
        self.conn = conn
        self.dowrite = True
        self.exitcode = 'quit()'

        if public is not None:
            self.setPublic(public)
        if private is not None:
            self.setPrivate(private)

        def run(self):
            """
            Invoked when new thread is executed
            """
            if self.action == 'read':
                self.read()
            elif self.action == 'file':
                self.file()
            else:
                self.write()
    def setPublic(self, public):
        """
        Sets public key from other party for decryption
        """
        self.public = public

    def setPrivate(self, private):
        """
        Sets private key for encryption
        """

        self.private = private

    def stopWrite(self):
        """
        Terminates the write loops
        """
        self.dowrite = False

    def read(self):
        """
        Responsble for reading in data from the client and displaying stdout
        """

        global doRead
        recvIsComplete = False
        data = ""
        while not recvIsComplete and doRead:
            data += self.conn.recv(1024)
            if data.strip("~") and data[0] == "~" and data[-1] == "~":
                recvIsComplete = True
        data = decrypt(data.strip("~"), self.public)

        while doRead and data.strip() != self.exitcode and len(data) > 0:
            if data.strip().split(":")[0] = "#FILE":
                print "\n* Receiving file...*"
                self.saveFile(data.strip())
            else:
                print "<Message>", data.strip()

            recvIsComplete = False
            data = ""
            while not recvIsComplete and doRead:
                data += self.conn.recv(1024)
                if data.strip("~") and data[0] == "~" and data[-1] == "~":
                    recvIsComplete = True
            data = decrypt(data.strip("~"), self.public)

        self.stopWrite

    def saveFile(self, data):
        """
        Reads in file from client and creates the file in the local directory
        """

        try:
            filename, extension = os.path.splitext(data.split(":")[1])
            filename = filename.replace(extension, "")
            newname = filename + "_" + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            newFile = open(newname, "wb")
            data = data.replace("#FILE:" + filename + extension + ":", "")
            newFile.write(data)
            print "* File \"%s\" received *" %(newname)
        except:
            print "* File NOT received *"

    def write(self):
        """
        Reads in data from stdin and sends to client
        """
        global doRead
        while self.dowrite:
            data = sys.stdin.readline()
            if data.strip() == self.exitcode:
                print "\n* Leaving conversation....(Waiting for partner's response) *\n"
                self.stopWrite
                doRead = False
            elif data.strip() == "file()":
                FileThread = Thread_Manager('file', self.conn, None, self.private)
                FileThread.start()
                FileThread.join()
                continue
            data = encrypt(data.strip(), self.private)
            self.conn.send("~" + data + "~")

    def file(self):
        """
        Reads and sends file data
        """
        try:
            filename = str(raw_input("\nOnly files located in your current directory are accessible\n Enter filname including extension: "))
            f = open(filename, "r")
            print "* Encrypting file... (Large files will take time) *"
            data = encrypt("#FILE:" + filename + ":" + f.read(), self.private)
            f.close()
            print "* Sending file \"%s\"....*" % filename
            self.conn.send("~" + data + "~")
            print "* File sent"
        except IOError:
            print "* File " + filename + " does not exists *"
