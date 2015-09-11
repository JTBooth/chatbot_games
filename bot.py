__author__ = 'rbooth'

import socket
import sys
import random
import Queue



class Game:
    def __init__(self):

        self.server = "irc.rizon.net"       #settings
        self.channel = "#ZAP"
        self.botnick = "ZAPRobot"
        self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #defines the socket
        print "connecting to:"+self.server
        self.irc.connect((self.server, 6667))                                                         #connects to the server
        self.irc.send("USER "+ self.botnick +" "+ self.botnick +" "+ self.botnick +" :This is a fun bot!\n") #user authentication
        self.irc.send("NICK "+ self.botnick +"\n")            #sets nick
        self.irc.send("PRIVMSG nickserv :iNOOPE\r\n")    #auth
        self.irc.send("JOIN "+ self.channel +"\n")            #join the chan
        self.custom_init()

        while 1:                 # puts it in a loop
            text=self.irc.recv(2040)  # receive the text
            print text           # print text to console
            if ("PRIVMSG " + self.botnick) in text or ("PRIVMSG " + self.channel) in text:
                sender = text[1:text.index("!")]
                message = text[text[1:].index(":")+2:].replace("\r\n", "")
                print sender
                print message
                self.input(sender, message)

            if text.find('PING') != -1:                          # check if 'PING' is found
                self.irc.send('PONG ' + text.split()[1] + '\r\n')     # returns 'PONG' back to the server (prevents pinging out!)


    def input(self, sender, message):
        self.pm(sender, "I received " + message)

    def custom_init(self):
        pass

    def pm(self, user, message):
        sendstring = ":" + self.botnick + "!cgiirc@B712F00B.E110F191.7DA5C03C.IP PRIVMSG " + user + " :" + str(message) + "\n"
        self.irc.send(sendstring)


    def broadcast(self, message):
        sendstring = ":" + self.botnick + "!cgiirc@B712F00B.E110F191.7DA5C03C.IP PRIVMSG " + self.channel + " :" + str(message) + "\n"
        self.irc.send(sendstring)


