__author__ = 'rbooth'

from bot import Game

class ZAPGame(Game):
    def custom_init(self):
        self.players = []
        self.phase = "idle"
        self.game_over = False
        self.broadcast("Hi! I'm the ZAP bot. Send me \"!classic n\" to start a classic game with n players.")

        while 1:
            text = self.irc.recv(2040)
            if text.find('PING') != -1:                          # check if 'PING' is found
                self.irc.send('PONG ' + text.split()[1] + '\r\n')     # returns 'PONG' back to the server (prevents pinging out!)
            print text
            if "!" in text:
                sender = text[1:text.index("!")]
                message = text[text[1:].index(":")+2:].replace("\r\n", "")
                self.input(sender, message)
            else:
                print "non-message text"

    def initialize(self):
        self.game_state = {player: {"zombies":100, "points":0} for player in self.players}
        self.broadcast(self.game_state)
        self.this_turn_orders = {player: None for player in self.players}

    def ask_for_orders(self):
        for player in self.players:
            if self.game_mode == "classic":
                self.pm(player, "please submit your Zombie Allocation in the format: \"!za 22 14 5\"")
                self.pm(player, "1 in 10 zombies, rounded down, will die in transit. You recieve 3 zombies every round.")

    def input(self, sender, message):

        print "sender:", sender
        print "message:", message
        if message == "!debug":
            print self.phase
            print self.players
            print self.game_state
            return
        if self.phase == "idle":
            if "!classic n" == message:
                self.broadcast("You cheeky fuck. So funny. I bet your life is full of meaning.")
            elif "!classic" in message:
                try:
                    num = int(message.replace("!classic ", ""))
                    self.broadcast("Registration is open with " + str(num) + " players")
                    self.broadcast("Say !join to join the next ZAP game or !cancel to cancel it")
                    self.max_players = num
                    self.phase = "registration"
                    self.game_mode = "classic"
                except:
                    self.broadcast("Your number sucks, try again")

        if self.phase == "registration":

            if message == "!join":
                if len(self.players) < self.max_players:
                    self.broadcast(sender + " has joined the game")
                    self.players.append(sender)
                if len(self.players) == self.max_players:
                    self.phase = "play"
                    self.ask_for_orders()
                    if self.max_players == 2:
                        self.broadcast("Game set: " + self.players[0] + " vs " + self.players[1])
                    else:
                        self.broadcast("Game set! Players: " + str(self.players))
                    self.initialize()
            elif message == "!cancel":
                self.phase = "idle"
                self.players = []
                self.broadcast("Hi! I'm the ZAP bot. Send me \"!classic n\" to start a classic game with n players.")

        elif self.phase == "play" and sender in self.players and message.startswith("!za"):
            try:
                nums = parse_za(message)
                if len(nums) != 3:
                    self.pm(sender, "please don't get fancy. there are three battlefields. zombies are ints. you sent: " + message)
                if sum(nums) > self.game_state[sender]["zombies"]:
                    self.pm(sender, "you allocated " + str(nums) + ", but you only have " + str(self.game_state[sender]["zombies"]) + " zombies")
                    return
                else:
                    print "parsed numbers correctly"
                self.this_turn_orders[sender] = nums
                print "this turn orders:", self.this_turn_orders
                if None not in self.this_turn_orders.values():
                    print "everyone's orders are in"
                    self.broadcast(str(self.this_turn_orders))
                    for battlefield_num in range(3):
                        max_alloc = max([x[battlefield_num] for x in self.this_turn_orders.values()])
                        winners = [player for player in self.players if self.this_turn_orders[player][battlefield_num] == max_alloc]
                        losers = [player for player in self.players if player not in winners]
                        self.broadcast("in battlefield " + str(battlefield_num) + ", the winner(s): " + str(winners))
                        for winner in winners:
                            self.game_state[winner]["points"] += 1

                        for loser in losers:
                            self.game_state[loser]["zombies"] -= self.this_turn_orders[loser][battlefield_num]
                        if self.game_over:
                            self.phase = "idle"
                            self.broadcast("Hi! I'm the ZAP bot. Send me \"!classic n\" to start a classic game with n players.")

                    for player in self.players:

                        if self.game_state[player]["points"] >= 5:
                            self.broadcast(str(player) + " is a winner")
                            self.game_over = True
                        self.game_state[player]["zombies"] -= int(0.1*sum(self.this_turn_orders[player]))
                        self.game_state[player]["zombies"] = max(self.game_state[player]["zombies"], 0) + 3
                    self.broadcast(str(self.game_state))
                    self.this_turn_orders = {player: None for player in self.players}
                    self.ask_for_orders()


            except:
                self.pm(sender, "your zombie allocation sucks, try again")
def parse_za(za):
    try:
        nums = za.replace("!za ", "")
        nums = [int(x) for x in nums.split()]
        return nums
    except:
        return []




