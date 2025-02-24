#! /usr/bin/env python3

import random
from typing import List
from mcts import mcts
import json
from typing import Tuple
from collections import defaultdict 
from multiprocessing import Pool, cpu_count

# ********************************************************
# CS 370 HW #3  DUE Thursday, 2/20/2020 at 11:59 pm
#                via gradescope

# ********************************************************
# Name: Tony Munene Kinyua
# Email address: munene.kinyua@yale.edu
# ********************************************************

# This file may be opened in python 3

# ********************************************************
# ** problem 0 ** (1 easy point) 
# Replace the number 0 in the definition below to indicate
# the number of hours you spent doing this assignment
# Decimal numbers (eg, 6.237) are fine.  Exclude time
# spent reading.

def hours():
    return 4

# ********************************************************
# here we write the blackjack playing code
# ********************************************************

# initialize some useful global variables
global in_play
in_play = False
global outcome
outcome = " start game"
score = 0

# define globals for cards
SUITS = ('C', 'S', 'H', 'D')
RANKS = ('A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K')
VALUES = {'A':1, '2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8, '9':9, 'T':10, 'J':10, 'Q':10, 'K':10}


# define card class
class Card:
    def __init__(self, suit, rank):
        if (suit in SUITS) and (rank in RANKS):
            self.suit = suit
            self.rank = rank
        else:
            self.suit = None
            self.rank = None
            print ("Invalid card: ", suit, rank)

    def __str__(self):
        return self.suit + self.rank

    def get_suit(self):
        return self.suit

    def get_rank(self):
        return self.rank
    
    def __hash__(self):
        return hash(str(self))

# define hand class
       
class Hand:
    def __init__(self):
        self.cards = []

    def __str__(self):
        ans = "Hand contains "
        for i in range(len(self.cards)):
            ans += str(self.cards[i]) + " "
        return ans
        # return a string representation of a hand

    def add_card(self, card):
        self.cards.append(card)
        # add a card object to a hand

    def get_value(self):
        value = 0
        aces = False
        for c in self.cards:
            rank = c.get_rank()
            v = VALUES[rank]
            if rank == 'A': aces = True
            value += v
        if aces and value < 12: value += 10
        return value
        # count aces as 1, if the hand has an ace, then add 10 to hand value if it doesn't bust
        # compute the value of the hand, see Blackjack video
   
# define deck class 
class Deck:
    def __init__(self):
        self.deck = []
        for s in SUITS:
            for r in RANKS:
                self.deck.append(Card(s, r))
        # create a Deck object

    def shuffle(self):
        random.shuffle(self.deck)
        # shuffle the deck 

    def deal_card(self):
        return self.deck.pop()
        # deal a card object from the deck

    def deal_card_not_in_list(self, cards: List[Card]) -> Card:
        """
            - Return a card that is not in the list of cards
        """
        card = random.choice(self.deck)
        while card in cards:
            card = random.choice(self.deck)
        return card
    
    def sample_two_cards_for_hand_value(self, hand_value=int) -> Tuple[Card, Card]:
        """
            - Return a tuple of two cards that sum to hand_value
        """
        seen_values = set()
        for card in self.deck:
            # Ace card can have value 1 or 11
            if card.rank == 'A' and hand_value > 11:
                complement_card_value = hand_value - 11
            else:
                complement_card_value = hand_value - VALUES[card.get_rank()]
            if complement_card_value in seen_values:
                for card2 in self.deck:
                    if VALUES[card2.get_rank()] == complement_card_value:
                        return (card, card2)
            seen_values.add(VALUES[card.get_rank()])
        return None
                

    def __str__(self):
        ans = "The deck: "
        for c in self.deck:
            ans += str(c) + " "
        return ans
        # return a string representing the deck

            

#define event handlers for buttons
def deal():
    global outcome, in_play, theDeck, playerhand, househand, score
    if in_play:
        outcome = "House winds by default!"
        score -= 1
    else:
        outcome = "Hit or stand?"
    in_play = True
    theDeck = Deck()
    theDeck.shuffle()
    #print theDeck
    playerhand = Hand()
    househand = Hand()
    playerhand.add_card(theDeck.deal_card())
    playerhand.add_card(theDeck.deal_card())
    househand.add_card(theDeck.deal_card())
    househand.add_card(theDeck.deal_card())
    print ("Player", playerhand, "Value:", playerhand.get_value())
    print ("House",  househand, "Value:", househand.get_value())
    #print theDeck

def hit():
    global in_play, score, outcome
    if in_play:
        playerhand.add_card(theDeck.deal_card())
        val = playerhand.get_value()
        print ("Player", playerhand, "Value:", val)
        if val > 21: 
            outcome = "You are busted! House wins!"
            in_play = False
            score -= 1
            print (outcome, "Score:", score)
    # if the hand is in play, hit the player
   
    # if busted, assign a message to outcome, update in_play and score
       
def stand():
    global score, in_play, outcome
    if playerhand.get_value() > 21:
        outcome = "You are busted."
        return None
    if not in_play:
        outcome = "Game is over."
        return None
    val = househand.get_value()
    while(val < 17):
        househand.add_card(theDeck.deal_card())
        val = househand.get_value()  
        print ("House:", househand, "Value:", val)
    if (val > 21):
        print ("House is busted!")
        if playerhand.get_value() > 21:
            outcome = "House is busted, but House wins tie game!"
            score -= 1
        else: 
            outcome = "House is busted! Player wins!"
            score += 1
    else:
        if (val == playerhand.get_value()):
            outcome = "House wins ties!"
            score -= 1
        elif (val > playerhand.get_value()):
            outcome = "House wins!"
            score -= 1
        else:
            outcome = "Player wins!"
            score += 1
    in_play = False
    print (outcome, "Score:", score)
    # if hand is in play, repeatedly hit dealer until his hand has value 17 or more
    # assign a message to outcome, update in_play and score


# get things rolling
# deal()

############################################

'''

Whenever the player is asked if it wants another card, the program
calls the hitme() function.  The hitme() function below decides
randomly, either yes or no, with equal probability.

Your function should be smart.  It should decide based on the results
of your Monte Carlo simulation of a boatload of hands.

The parameters to hitme are:
    hitme(playerhand.cards, househand.cards[0]):

'''
def hitme(playerhand: List[Card], houseupcard: Card) -> bool:
    """ 
        - Return True if player should hit, False otherwise. 
        - Choice to hit or not is based on a probability lookup table
    """
    with open('blackjack.json', 'r') as f:
        strategy = json.load(f)
        player_hand = Hand()
        house_hand = Hand()
        for card in playerhand: 
            player_hand.add_card(card)
        if player_hand.get_value() > 16 or (11 < player_hand.get_value() < 17 and 1 < VALUES[houseupcard.get_rank()] < 7):
            # Always stand when hand value is 17 or greater
            return False
        else:
            house_hand.add_card(houseupcard)
            # Sample house down card
            playerhand.append(houseupcard)
            sampled_card = Deck().deal_card_not_in_list(playerhand)
            house_hand.add_card(sampled_card)
            if house_hand.get_value() == 21: return True
            return strategy[str(player_hand.get_value())][str(house_hand.get_value())] == "hit"

def hitme_random(playerhand: List[Card], houseupcard: Card) -> bool:
    """
        - Baseline random agent 
    """
    return random.choice(["hit", "stand"]) == "hit"
''' 

You need to run simulatations to see for a given playerhand and
houseupcard, does it pay to get another card?  Run lots of simulations
and build up a table or matrix or something so that the hitme()
function can simply look up the odds for a given
playerhand/houseupcard pair.

'''

def simulate_trial(player_hand_value, house_hand_value):
    deck = Deck()
    player_cards = deck.sample_two_cards_for_hand_value(player_hand_value)
    house_cards = deck.sample_two_cards_for_hand_value(house_hand_value)
    player_hand = Hand()
    player_hand.add_card(player_cards[0])
    player_hand.add_card(player_cards[1])
    house_hand = Hand()
    house_hand.add_card(house_cards[0])
    house_hand.add_card(house_cards[1])
    return mcts(house_hand, player_hand)

def simulate_hand_values(player_hand_value, house_hand_value, trials):
    strategy_count = {"hit": 0, "stand": 0}
    for _ in range(trials):
        strategy = simulate_trial(player_hand_value, house_hand_value)
        strategy_count[strategy] += 1
    best_strategy = max(strategy_count, key=strategy_count.get)
    return (player_hand_value, house_hand_value, best_strategy)

def sim(trials):
    """
        - Run trials(100,000+) number of Monte Carlo simulations to generate a probability table for hitme() function
    
    """
    possible_hand_values = [i for i in range(4, 21)]
    json_object = defaultdict(dict)

    # Use multiprocessing to parallelize simulations
    with Pool(cpu_count()) as pool:
        results = pool.starmap(
            simulate_hand_values,
            [(player_hand_value, house_hand_value, trials // (len(possible_hand_values) ** 2))
              for player_hand_value in possible_hand_values
              for house_hand_value in possible_hand_values
            ]
        )
        # Aggregate results
        for player_hand_value, house_hand_value, best_strategy in results:
            json_object[player_hand_value][house_hand_value] = best_strategy
            print(f"Completed iteration: player_hand_value {player_hand_value}, house_hand_value {house_hand_value}")
        # Write results to file
        with open('blackjack.json', 'w') as f:
            json.dump(json_object, f)
        print("Simulation Complete!")
    return


'''

play() should run automatically trials times, and report the
percentage that the player wins.  Here is some skeleton code.  You
need to modify it to track how many times the player wins and return
that winning percentage.

'''

def play(trials=100000):
    global score
    prev_score, wins = 0, 0
    for _ in range(trials):
        deal()
        if hitme(playerhand.cards, househand.cards[0]):
            hit()
        else:
            stand()
        stand()
        wins += 1 if ((score - prev_score) > 0) else 0
        prev_score = score
    print(f"Winning percentage: {(wins/trials) * 100}")
    return
    

'''

There are no public test cases.  You are invited to write your own.

Here is one test you should run:

Set hitme() to the random strategy above and play 1000 trials.  Then
switch to your trained strategy and run another 1000 trials.  If the
random strategy outperforms your strategy, that's bad.


'''

if __name__ == "__main__":
    random.seed(19)
    play()
         
