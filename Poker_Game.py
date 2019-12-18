from enum import Enum


Ranks = Enum('Ranks', 'One Two Three Four Five Six Seven Eight Nine Ten Jack Queen King Ace none')
Suits = Enum('Suits', 'Hearts Diamonds Clubs Spades none')
Hands = Enum('Hands', 'high_card pair two_pair trips straight flush full_house quads straight_flush royal_flush none')

class poker_card:
    rank = Ranks.none
    suit = Suits.none
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
    def display(self):
        return self.rank.name + " of " + self.suit.name


    


class Hand:
    poker_cards = []
    name = Hands.none.name

    def __init__(self, poker_cards):
        self.poker_cards = poker_cards

    '''def is_hand(self):
        if len(self.poker_cards) == 5:
            return True
        else:
            return False'''

    def print_hand(self):
        handcards=''
        for c in self.poker_cards:
            handcards = handcards + c.display() + ', '
        print('Your Hand: ' + handcards)

    def is_straight(self):
        poker_card_values=[]
        if self.poker_cards and len(self.poker_cards)>=5:
    
            for c in self.poker_cards:
                poker_card_values.append(c.rank.value)
            poker_card_values.sort()

            for i in range(4):
                if poker_card_values[i] != poker_card_values[i+1]-1:
                    return False
            return True
        return False
            
    def count_rank(self,rank):
        counter = 0
        if self.poker_cards:
            for c in self.poker_cards:
                if c.rank == rank:
                    counter+=1
        return counter

    def count_suits(self,suit):
        counter = 0
        if self.poker_cards:
            for c in self.poker_cards:
                if c.suit == suit:
                    counter+=1
        return counter

    def is_royal(self):
        poker_card_values=[]
        
        if self.poker_cards and len(self.poker_cards)>=5:
            for c in self.poker_cards:
                poker_card_values.append(c.rank.value)
            poker_card_values.sort()
            if poker_card_values[0] == 10 and poker_card_values[1] == 11 and poker_card_values[2] == 12 and poker_card_values[3] == 13 and poker_card_values[4] == 14:
                return True
            else:
                return False
        return False

    def is_flush(self):
        for s in Suits:
            if self.count_suits(s) >= 5:
                return True
        return False

    def is_straight_flush(self):
       return self.is_straight() and self.is_flush()

    def is_quads(self):
        for r in Ranks:
            if self.count_rank(r) == 4:
                return True
        return False

    def is_trips(self):
        for r in Ranks:
            if self.count_rank(r) >= 3:
                return True
        return False


    def is_two_pair(self):
        pairs = 0
        for r in Ranks:
            if self.count_rank(r) == 2:
                pairs += 1
            if pairs >= 2:
               return True
        return False

    def is_pair(self):
        for r in Ranks:
            if self.count_rank(r) == 2:
                return True
        return False

    def get_highest(self):
        poker_card_values=[]
        if self.poker_cards:
            for c in self.poker_cards:
                poker_card_values.append(c.rank.value)
            poker_card_values.sort()
            return poker_card_values[4] 
        return None

    def get_hand(self):
        if self.is_royal() and self.is_flush():
            self.name = Hands.royal_flush.name
            
        elif self.is_straight_flush():
            self.name = Hands.straight_flush.name
            
        elif self.is_quads():
            self.name = Hands.quads.name
            
        elif self.is_trips() and self.is_pair():
            self.name = Hands.full_house.name
            
        elif self.is_flush():
            self.name = Hands.flush.name
            
        elif self.is_straight():
            self.name = Hands.straight.name
            
        elif self.is_trips():
            self.name = Hands.trips.name
            
        elif self.is_two_pair():
            self.name = Hands.two_pair.name
            
        elif self.is_pair():
            self.name = Hands.pair.name
            
        else:
            self.name = Hands.high_card.name

        return self.name
