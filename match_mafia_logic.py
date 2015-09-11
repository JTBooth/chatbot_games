__author__ = 'rbooth'

import socket
import sys
import random
import Queue

server = "irc.rizon.net"       #settings
channel = "#turingFight"
botnick = "MysteryRobot"




class Game:
    def __init__(self):
        self.player_set = set()
        self.player_list = []
        self.mode = "IDLE" # IDLE, REGISTER, PLAY
        self.owner = ""
        self.hand_size = 4
        self.current_turn = 0
        self.num_targets = 3
        self.legal_moves = ("S<1", "S<2", "S<3", "S>1", "S>2", "S>3", "LA", "LB", "LC", "LD", "P", "0")


    def input(self, sender, message):
        print "sender:", sender, "message:", message
        print "current mode is", self.mode

        if message == "\help":
            print "mode is", self.mode
            print "send (\play matchMafia) to join (if possible)"
            print "send (\players) to see current players"
            print "send (\start) to start game"

        if self.mode == "IDLE":
            print "reacting to IDLE mode"
            if message == "\play turingFight":
                broadcast("registration for turingFight is open")
                self.owner = sender
                self.player_set.add(sender)
                self.mode = "REGISTER"

        elif self.mode == "REGISTER":
            print "reacting to REGISTER mode"
            if message == "\play matchMafia":

                self.player_set.add(sender)
            if message == "\players":
                sendstring = "players so far: " + ', '.join(list(self.player_set))
                print "broadcasting", sendstring
                broadcast(sendstring)
                print self.player_set
            elif message == "\start" and sender == self.owner:
                broadcast("registration closed; game has started")
                self.mode = "PLAY"
                self.setup()
                broadcast("turn order is: " + str(self.player_order))
                broadcast(self.player_order[self.current_turn] + ", you're up first!")
                self.display()

        elif self.mode == "PLAY":
            print "reacting to PLAY mode"
            if sender == self.player_order[self.current_turn]:
                print "order from turn holder"
                if message in self.legal_moves:
                    print "legal move"
                    self.turing_machine.push((message, sender))
                    self.advance_turn()
                    self.turing_machine.pop_and_execute()
                    self.display()

    def display(self):
        broadcast("tape:  " + self.turing_machine.tape_string())
        broadcast("stack: " + self.turing_machine.queue_string())
        for player in self.player_order:
            broadcast(player + ": " + str(self.player_dict[player].targets))

    def setup(self):
        self.player_order = list(self.player_set)
        self.player_dict = {owner: Player(self.hand_size, self.num_targets) for owner in self.player_order}
        self.turing_machine = TuringMachine(13, 2)
        for i in range(2):
            self.turing_machine.queue.push("0")

    def advance_turn(self):
        self.current_turn += 1
        if self.current_turn >= len(self.player_order):
            self.current_turn = 0


class TuringMachine:
    def __init__(self, tape_length, queue_visible_length):
        self.tape = ["X" for dummy in range(tape_length)]
        self.queue = VisibleQueue(queue_visible_length)
        self.head_pos = int(tape_length/2)
        self.print_head = "X"

    def shift_head(self, move):
        self.head_pos += move
        if self.head_pos > len(self.tape):
            self.head_pos -= len(self.tape)
        elif self. head_pos < 0:
            self.head_pos += len(self.tape)

    def push(self, item):
        self.queue.push(item)

    def pop_and_execute(self):
        item = self.queue.pop()[0]
        self.execute(item)

    def execute(self, item):
        broadcast("executing " + item)
        if item[0] == "S":
            if item[1] == "<":
                self.shift_head(-int(item[2]))
            if item[1] == ">":
                self.shift_head(+int(item[2]))
        if item[0] == "L":
            self.print_head = item[1]
        if item[0] == "P":
            self.tape[self.head_pos] = self.print_head

    def queue_string(self):
        return self.queue.view()

    def tape_string(self):
        disp_list = list(self.tape)
        disp_list[self.head_pos] = "[" + disp_list[self.head_pos] + "]"
        return str(disp_list)


class VisibleQueue:
    def __init__(self, visible_length, blank = " "):
        self.queue = []
        self.visible_length = visible_length
        self.blank = blank

    def push(self, item):
        self.queue.append(item)

    def pop(self):
        item = self.queue[0]
        self.queue = self.queue[1:]
        return item

    def view(self):
        ret_val = []
        for i in range(len(self.queue)):
            if i < self.visible_length:
                ret_val.append(self.queue[i])
            else:
                ret_val.append(self.blank)
        return str(ret_val)


class Player:
    def __init__(self, name, num_targets):
        self.targets = [random_goal_string() for dummy in range(num_targets)]
        self.name = name

    def send(self, message):
        pm(self.name, message)


def random_card():
    cards = ("S<1", "S<2", "S<3", "S>1", "S>2", "S>3", "LA", "LB", "LC", "LD", "P")
    return random.choice(cards)


def random_goal_string():
    length = random.choice(range(3, 4))
    return ''.join([random.choice(["A", "B", "C", "D"]) for dummy in range(length)])

myGame = Game()

registration_open = False
while 1:                 # puts it in a loop
    text=irc.recv(2040)  # receive the text
    print text           # print text to console
    if ("PRIVMSG " + botnick) in text or ("PRIVMSG " + channel) in text:
        sender = text[1:text.index("!")]
        message = text[text[1:].index(":")+2:].replace("\r\n", "")
        myGame.input(sender, message)

    if text.find('PING') != -1:                          # check if 'PING' is found
        irc.send('PONG ' + text.split()[1] + '\r\n')     # returns 'PONG' back to the server (prevents pinging out!)

