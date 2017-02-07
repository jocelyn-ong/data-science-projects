
# coding: utf-8

# In[38]:

import pandas as pd
import numpy as np


# # Deck

# ## Requirement

# - suits not required
# - multiple decks
# - need to be able to shuffle the deck
# - need to draw a card from the deck

# ## Plan

# - class: deck
#     - can take number of decks as a variable
#     - default 1 deck
# - method: shuffle
# - method: deal
# - attribute: list of all the cards in the 'deck'

# ## Code

# In[39]:

class Deck():
    values = ["A", 2, 3, 4, 5, 6, 7, 8, 9, 10, "J", "Q", "K"]
    def __init__(self, num_decks=1, values=values):
        # Multiply values by number of suits
        # Then by number of decks
        self.num_decks = num_decks
        self.deck = values * 4 * self.num_decks
        
    def __str__(self):
        return "{} decks, {} cards left".format(self.num_decks, len(self.deck))
    
    def shuffle(self):
        np.random.shuffle(self.deck)
    
    def deal(self, hand=None):
        if hand == None:
            return self.deck.pop(0)
        else:
            hand.append(self.deck.pop(0))


# In[40]:

test = Deck()
print (test)
print (test.deck)
print (test.deal())
print (test.deck)


# # Calculate points

# ## Requirement

# - Take a hand
# - Calculate how many points there are in the hand
#     - J, Q, K are 10
#     - Ace could be 1 or 11
#         - How do we decide?
#         - If 11 doesn't bust, then 11, else 1
#             - We have to calculate the rest of the cards first

# ## Plan

# - Remove Aces in the hand
#     - Track how many Aces there were
# - Count J, Q, K as 10

# ## Code

# In[41]:

def calculate_points(hand):
    points = 0
    num_ace = 0
    
    # Deal with aces
    while "A" in hand:
        hand.remove("A")
        num_ace += 1
    
    # Deal with the rest of the hand
    for i in hand:
        try:
            # If it's a number, add it to points
            points += i
        except:
            # If it's not a number, it's a 10
            points += 10
            
    # deal with the aces
    for i in range(num_ace):
        if points + 11 <= 21:
            points += 11
        else:
            points += 1
    return points


# In[42]:

calculate_points([5, 5, "A"])


# # Simulate game

# ## Requirements

# - play one game
# - return the data we need

# In[43]:

data_dictionary = pd.read_csv("data_dictionary.csv")
data_dictionary


# ## Outcomes

# - player gets blackjack, dealer didn't
#     - player wins
# - dealer gets blackjack, player didn't
#     - player loses
# - player hits and busts
#     - player loses
# - player hits, dealer hits and busts
#     - player wins
# - player hits, dealer hits/ dealer >= hard 17
#     - player > dealer
#         - player wins
#     - player < dealer
#         - player loses
#     - player == dealer
#         - draw

# ## Plan

# - create deck
# - deal initial hand
# - check if anyone has a blackjack
# - no blackjacks, player goes first
#     - in any case, if player has anything <= 11, hit
#     - if anything 12 or higher
#         - random
#             - randomize whether to hit or not if smaller than 18
#         - recommended
#             - if dealer showing <= 6 and player <= 16, hit
# - once player is done, dealer goes
#     - if dealer has anything smaller than 17, he must hit
#     - if dealer has a soft 17, he must hit

# In[120]:

def sim_game(num_decks=1, strategy=0):
    game_deck = Deck(num_decks=num_decks)
    game_deck.shuffle()
    
    dealer_hand = []
    player_hand = []
    
    # deal 2 cards each
    for i in range(2):
        game_deck.deal(player_hand)
        game_deck.deal(dealer_hand)
        
    # get their initial points
    # copy so that our hand is not changed
    player_initial = calculate_points(player_hand.copy())
    dealer_initial = calculate_points(dealer_hand.copy())
    
    # get dealer open card
    dealer_open = dealer_hand[0]
    
    # Change it to numerics
    if dealer_open in ["J", "Q", "K"]:
        dealer_open = 10
    elif dealer_open == "A":
        dealer_open = 1
    
    dealer_hit = 0
    dealer_num_hits = 0
    player_hit = 0
    player_num_hits = 0
    player_busts = 0
    dealer_busts = 0
    dealer_final = calculate_points(dealer_hand.copy())
    player_final = calculate_points(player_hand.copy())

    
    # if anyone got a blackjack, the game should end
    if player_initial != 21 and dealer_initial != 21:
        # if neither of them got a blackjack game continues
        # the player goes first
        
        # If player <= 11, hit
        while calculate_points(player_hand.copy()) <= 11:
            player_hit += 1
            game_deck.deal(player_hand)
        
        # If strategy is random, randomize hit for 18 and below
        if strategy == 0:
            while calculate_points(player_hand.copy()) <= 18:
                if np.random.random() < 0.5:
                    player_hit += 1
                    game_deck.deal(player_hand)
        # If strategy is recommended, stand on 17 and above
        else:
            while calculate_points(player_hand.copy()) <= 16:
                if dealer_open <= 6:
                    player_hit += 1
                    game_deck.deal(player_hand)
        
        # update player's final and busts
        player_final = calculate_points(player_hand.copy())
        player_busts = player_final > 21
        # dealer's turn
        
        # If player didn't bust
        if not player_busts:
            # If dealer < 17, hit
            while calculate_points(dealer_hand.copy()) < 17:
                dealer_hit += 1
                game_deck.deal(dealer_hand)

            # If dealer has a soft 17, hit
            if calculate_points(dealer_hand.copy()) == 17:
                if "A" in dealer_hand:
                    dealer_copy = dealer_hand.copy()
                    dealer_copy.remove("A")
                    if calculate_points(dealer_copy.copy()) == 6:
                        dealer_hit += 1
                        game_deck.deal(dealer_hand)
        
        # update dealer's final and busts
        dealer_final = calculate_points(dealer_hand.copy())
        dealer_busts = dealer_final > 21
        
    player_loses = 0
    draw = 0
    player_wins = 0
    
    # Check who wins
    if player_initial == 21 and dealer_initial != 21:
        player_wins = 1
    elif dealer_initial == 21 and player_initial != 21:
        player_loses = 1
    elif player_busts:
        player_loses = 1
    elif dealer_busts:
        player_wins = 1
    elif player_final > dealer_final:
        player_wins = 1
    elif player_final < dealer_final:
        player_loses = 1
    elif player_final == dealer_final:
        draw = 1
    
    return np.array([num_decks, dealer_open, dealer_initial, dealer_hit, dealer_num_hits, dealer_final, int(dealer_busts),             player_initial, player_hit, player_num_hits, player_final, int(player_busts),             player_loses, draw, player_wins, strategy, str(dealer_hand), str(player_hand)])


# In[124]:

print (sim_game())


# # Generate a dataframe

# ## Requirements

# - run sim_game() for some number of times and save the output to a df

# In[125]:

def gen_data(num_decks=1, df_size=5000, strategy=0):
    return np.array([sim_game(num_decks=num_decks, strategy=0) for _ in range(df_size)])


# In[126]:

def gen_df(data):
    tmp = pd.DataFrame(data, columns=data_dictionary.Feature.values)
    tmp[tmp.columns.values[:-2]] = tmp[tmp.columns.values[:-2]].astype(int)
    return tmp


# In[177]:

df = gen_df(gen_data(num_decks=4))


# In[178]:

sub = gen_df(gen_data(num_decks=4, strategy=1))


# In[179]:

df = pd.concat([df,sub])


# In[180]:

# Combine old files
old_df = pd.read_csv("blackjack.csv")
df = pd.concat([old_df, df])


# In[181]:

# save to file
df.to_csv("blackjack.csv", index=False)


# # Testing our code

# In[182]:

df = pd.read_csv("blackjack.csv")


# In[183]:

df.shape


# In[139]:

# When player_loses = 1, draw = 0, player_wins = 0
print (df.draw[df.player_loses == 1].value_counts())
print (df.player_wins[df.player_loses == 1].value_counts())


# In[140]:

# When player_loses = 0, draw = 1, player_wins = 0
print (df.player_loses[df.draw == 1].value_counts())
print (df.player_wins[df.draw == 1].value_counts())


# In[141]:

# When player_loses = 0, draw = 0, player_wins = 1
print (df.player_loses[df.player_wins == 1].value_counts())
print (df.draw[df.player_wins == 1].value_counts())


# In[142]:

# When dealer_busts = 1, player_loses = 0, draw = 0, player_wins = 1
print (df.player_loses[df.dealer_busts == 1].value_counts())
print (df.draw[df.dealer_busts == 1].value_counts())
print (df.player_wins[df.dealer_busts == 1].value_counts())


# In[143]:

# When player_busts = 1, player_loses = 1, draw = 0, player_wins = 0, dealer_hit = 0, dealer_busts = 0
print (df.player_loses[df.player_busts == 1].value_counts())
print (df.draw[df.player_busts == 1].value_counts())
print (df.player_wins[df.player_busts == 1].value_counts())
print (df.dealer_hit[df.player_busts == 1].value_counts())
print (df.dealer_busts[df.player_busts == 1].value_counts())


# In[150]:

# When dealer_busts = 0 and player_busts = 0, if player_final > dealer final, player_loses = 0, draw = 0, player_wins = 1
sub = df[(df.player_busts == 0) & (df.dealer_busts == 0)]
print (sub.player_loses[sub.player_final > sub.dealer_final].value_counts())
print (sub.draw[sub.player_final > sub.dealer_final].value_counts())
print (sub.player_wins[sub.player_final > sub.dealer_final].value_counts())


# In[151]:

# When dealer_busts = 0 and player_busts = 0, if player_final = dealer final, player_loses = 0, draw = 1, player_wins = 0
print (sub.player_loses[sub.player_final == sub.dealer_final].value_counts())
print (sub.draw[sub.player_final == sub.dealer_final].value_counts())
print (sub.player_wins[sub.player_final == sub.dealer_final].value_counts())


# In[152]:

# When dealer_busts = 0 and player_busts = 0, if player_final < dealer final, player_loses = 1, draw = 0, player_wins = 0
print (sub.player_loses[sub.player_final < sub.dealer_final].value_counts())
print (sub.draw[sub.player_final < sub.dealer_final].value_counts())
print (sub.player_wins[sub.player_final < sub.dealer_final].value_counts())


# In[175]:

# When player_final <= 21, player_busts == 0
print (df.player_busts[df.player_final <= 21].value_counts())


# In[176]:

# When dealer_final <= 21, dealer_busts == 0
print (df.dealer_busts[df.dealer_final <= 21].value_counts())


# In[ ]:



