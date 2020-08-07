'''
Blackjack card game. Built this as a milestone project in my Python training course
Double Downs still a work in progress
'''
from console import clear
import random

#Playing Card attributes
suits = ["Hearts","Diamonds","Clubs","Spades"]
ranks = ["Two","Three","Four","Five","Six","Seven","Eight","Nine","Ten","Jack","Queen","King","Ace"]
values = {"Two":2,"Three":3,"Four":4,"Five":5,"Six":6,"Seven":7,"Eight":8,"Nine":9,"Ten":10,"Jack":10,"Queen":10,"King":10,"Ace":11}

class Card:
	def __init__(self,suit,rank):
		self.suit = suit
		self.rank = rank
		self.value = values[rank]
		
	def __str__(self):
		return f"{self.rank} of {self.suit}"
		
class Deck:
	def __init__(self):
		self.all_cards = []
		for suit in suits:
			for rank in ranks:
				self.all_cards.append(Card(suit,rank))
				
	def shuffle(self):
		random.shuffle(self.all_cards)
		
	def deal_card(self):
		return self.all_cards.pop()
		
class Table:
	def __init__(self):
		self.bets = {}
		self.cards = {}
		self.scores = {}
		
	def current_bets(self):
		clear()
		print("Current Bets:")
		for player in sorted(self.bets):
			print(f"{player:<{10}}: {self.bets[player]}")
		print("\n")
		
	def players_cards(self,player_score):
		for player in sorted(self.cards):
			player_cards = ""
			if player != "Dealer":
				for card in self.cards[player]:
					player_cards += f"{str(card)}\n"
				print(f"{player}'s Hand: ({player_score[player]})")
				print(f"{player_cards}\n")
	
	def dealers_cards(self,full_hand = False,dealer_score = int()):
		dealer_cards = ""
		if full_hand:
			for card in self.cards["Dealer"]:
				dealer_cards += f"{str(card)}\n"
		else:
			dealer_cards += str(self.cards["Dealer"][0])	
		print(f"Dealer's Hand: ({dealer_score})")
		print(f"{dealer_cards}\n")
		print("--------------------\n")
		
	def display(self,dealer_hand = False):
		if dealer_hand:
			clear()
			table.current_bets()
			table.dealers_cards(True,self.scores["Dealer"])
			table.players_cards(self.scores)
		else:
			clear()
			table.current_bets()
			table.dealers_cards(dealer_score = table.cards["Dealer"][0].value)
			table.players_cards(self.scores)
			
	def clear(self):
		for player in current_players:
			self.bets[player.name] = ""
			self.cards[player.name] = []
			self.scores[player.name] = ""
		
		self.cards["Dealer"] = []
		self.scores["Dealer"] = ""
		
class Player:
	def __init__(self,name,chips):
		self.name = name
		self.chips = chips
		self.split = False
		self.quit = False
		
	def bet(self):
		print(f"{self.name}, you have {self.chips} chips")
			
		while True:
			try:
				player_bet = int(input("Please enter your bet. [Number of chips]: "))
			except:
				continue
			if not isinstance(player_bet,int):
				print("Please enter a numerical bet")
			
			if self.chips - player_bet >= 0:
				self.chips -= player_bet
				break
			else:
				player_bet = "overdrawn"
				print(f"You cannot bet more than {player.chips}")
					
		table.bets[self.name] = player_bet
			
	def player_actions(self):
		while True:
			table.display()
			cards = table.cards[self.name]
			actions = ["Stay","Hit"]
		
			if table.scores[self.name] == "Bust!":
				break
			elif table.scores[self.name] == "Blackjack!":
				break
			elif self.split == True:
				dealer.deal_card(self.name)
				break
			
			print("--------------------\n")
			print(f"{self.name}'s turn")
			print("Stay")
			print("Hit")
			if len(cards) == 2 and cards[0].rank == cards[1].rank:
					if self.chips - table.bets[self.name] >= 0:
						print("Split")
						actions.append("Split")
			#print("Double Down")
			action = ""
			while action not in actions:
				action = input("Please choose an action: ")
				
			if action == "Stay":
				break
			elif action == "Hit":
				dealer.deal_card(self.name)
			elif action == "Split":
				if action not in actions:
					continue
				else:
					self.chips -= table.bets[self.name]
					split_index = current_players.index(self) + 1
					split_player = Player(f"{self.name}-split",0)
					current_players.insert(split_index,split_player)
					table.cards[f"{self.name}-split"] = []
					table.cards[f"{self.name}-split"].append(cards.pop(1))
					table.bets[f"{self.name}-split"] = table.bets[self.name]
					self.split = True
					current_players[split_index].split = True
					table.scores[f"{self.name}-split"] = dealer.check_score((table.cards[f"{self.name}-split"]))
		
	def cash_out(self):
		print(f"{self.name}, continue playing?")
		response = ""
		while response not in ["y", "n"]:
			response = input("Yes or No(cash out) [y/n]: ")
		return response
		
class Dealer:
	def __init__(self):
		self.deck = Deck()
		
	def shuffle(self):
		self.deck.shuffle()
		
	def deal_card(self,player):
		table.cards[player].append(self.deck.deal_card())
		table.scores[player] = self.check_score((table.cards[player]))
		
	def check_score(self,cards):
		total = 0
		ace = False
		for card in cards:
			if card.rank == "Ace":
				ace = True
			total += card.value
		if total > 21:
			if ace:
				total -= 10
				if total <= 21:
					return total
				else:
				 return "Bust!"
			else:
				return "Bust!"
		elif total == 21:
			if len(cards) == 2:
				return "Blackjack!"
			else:
				return 21
		else:
			return total
			
	def payout(self,player):
		dealer_score = table.scores["Dealer"]
		player_score = table.scores[player.name]
		bet = table.bets[player.name]
		
		if player_score == "Bust!":
			return
		elif dealer_score == "Blackjack!":
			if player_score == "Blackjack!":
				player.chips += bet
		elif player_score == "Blackjack!":
			player.chips += bet * 2.5
		elif dealer_score == "Bust!":
			player.chips += bet * 2
		elif player_score == dealer_score:
			player.chips += bet
		elif player_score > dealer_score:
			player.chips += bet * 2
		
		if "split" in player.name:
			player_index = current_players.index(player) - 1
			current_players[player_index].chips += player.chips
class Game:

	def __init__(self):
		self.player_chips = 100
		
	def player_setup(self):
		global current_players
		current_players = []
		
		#Get number of players and their names
		num_of_players = 0
		while num_of_players not in (range(1,8)):
			try:
				num_of_players = int(input("Please enter the number of players [1-7]: "))
			except:
				continue
			if not isinstance(num_of_players,int):
				print("Please enter a number of players between 1 and 7")
				
		for num in range(1,num_of_players + 1):
			player_name = input(f"Please enter Player {num}'s name: ")
			current_players.append(Player(player_name,self.player_chips))
			table.cards[player_name] = []
		table.cards["Dealer"] = []
		
	def remove_player(self,player):
		current_players.remove(player)
		del table.bets[player.name]
		del table.cards[player.name]
		del table.scores[player.name]
		print(f"{player.name} has left the table with {player.chips} chips")
			
	def StartGame(self,start = True):
		while start:
			clear()
			print("Welcome to the game of Blackjack!")
			
			#Setup the card table
			global table
			table = Table()
			
			#Setup the players
			self.player_setup()
			
			while True:
			
				#Setup Dealer
				global dealer
				dealer = Dealer()
			
				#Shuffle Deck
				dealer.shuffle()
			
				#Place bets
				for player in current_players:
					table.current_bets()
					player.bet()
				
				table.current_bets()
				
				#Deal cards
				cards_dealt = 0
				while cards_dealt < 2:
					for player in current_players:
						dealer.deal_card(player.name)
					dealer.deal_card("Dealer")
					cards_dealt += 1
				
				#Player actions
				for player in current_players:
					player.player_actions()
				
				#Dealer plays
				table.display(True)
				
				while True:
					if table.scores["Dealer"] in ["Bust!","Blackjack!"]:
						break
					elif table.scores["Dealer"] >= 17:
						break
						
					dealer.deal_card("Dealer")
					table.display(True)
			
				#Award winners
				for player in current_players:
					dealer.payout(player)
				
				#Play again?
				for player in current_players:
					if player.chips == 0:
						player.quit = True
					elif "split" in player.name:
						player.quit = True
					else:	
						response = player.cash_out()
						if response == "n":
							player.quit = True
						
				for player in reversed(current_players):
					if player.quit == True:
						self.remove_player(player)
						
				if len(current_players) == 0:
					break
				
				table.clear()
				
			break
			
if __name__ == "__main__":
	blackjack = Game()
	blackjack.StartGame()
	
