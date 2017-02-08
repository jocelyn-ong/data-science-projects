import pandas as pd
import numpy as np

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

data_dictionary = pd.read_csv("data_dictionary.csv")

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

    # get card one from player
    player_card_one = player_hand[0]

    # Change it to numerics
    if dealer_open in ["J", "Q", "K"]:
        dealer_open = 10
    elif dealer_open == "A":
        dealer_open = 1

    if player_card_one in ["J", "Q", "K"]:
        player_card_one = 10
    elif player_card_one == "A":
        player_card_one = 1

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
            player_hit = 1
            player_num_hits += 1
            game_deck.deal(player_hand)

        # If strategy is random, randomize hit for 18 and below
        if strategy == 0:
            while calculate_points(player_hand.copy()) <= 18:
                if np.random.random() < 0.5:
                    player_hit = 1
                    player_num_hits += 1
                    game_deck.deal(player_hand)
        # If strategy is recommended, stand on 17 and above
        else:
            if dealer_open <= 6:
                while calculate_points(player_hand.copy()) <= 16:
                    player_hit = 1
                    player_num_hits += 1
                    game_deck.deal(player_hand)

        # update player's final and busts
        player_final = calculate_points(player_hand.copy())
        player_busts = player_final > 21
        # dealer's turn

        # If player didn't bust
        if not player_busts:
            # If dealer < 17, hit
            while calculate_points(dealer_hand.copy()) < 17:
                dealer_hit = 1
                dealer_num_hits += 1
                game_deck.deal(dealer_hand)

            # If dealer has a soft 17, hit
            if calculate_points(dealer_hand.copy()) == 17:
                if "A" in dealer_hand:
                    dealer_copy = dealer_hand.copy()
                    dealer_copy.remove("A")
                    if calculate_points(dealer_copy.copy()) == 6:
                        dealer_hit = 1
                        dealer_num_hits += 1
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

    return np.array([num_decks, dealer_open, dealer_initial, dealer_hit, dealer_num_hits, dealer_final, int(dealer_busts), player_card_one, player_initial, player_hit, player_num_hits, player_final, int(player_busts),             player_loses, draw, player_wins, strategy, str(dealer_hand), str(player_hand)])

def gen_data(num_decks=1, df_size=5000, strategy=0):
    return np.array([sim_game(num_decks=num_decks, strategy=strategy) for _ in range(df_size)])

def gen_df(data):
    tmp = pd.DataFrame(data, columns=data_dictionary.Feature.values)
    tmp[tmp.columns.values[:-2]] = tmp[tmp.columns.values[:-2]].astype(int)
    return tmp

if __name__ == '__main__':
    df = gen_df(gen_data(num_decks=4))
    sub = gen_df(gen_data(num_decks=4, strategy=1))
    df = pd.concat([df,sub])

    # Combine old files
    try:
        old_df = pd.read_csv("blackjack.csv")
        df = pd.concat([old_df, df])
    except:
        pass
    df.to_csv("blackjack.csv", index=False)
