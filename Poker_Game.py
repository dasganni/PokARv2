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
    counting_cards = []
    name = Hands.none.name

    flush_suit = Suits.none.name


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
        return handcards

    def is_straight(self):
        poker_card_values=[]
        self.counting_cards = []
        straight_count = 0

        if self.poker_cards and len(self.poker_cards)>=5:
    
            for c in self.poker_cards:
                poker_card_values.append(c.rank.value)
            s = set(poker_card_values)
            poker_card_values = list(s)
            poker_card_values.sort()
            

            for i in range(len(poker_card_values)-1,-1,-1):
                if poker_card_values[i] == poker_card_values[i-1]+1:
                    straight_count +=1
                    self.counting_cards += self.find_value(poker_card_values[i])
                    if straight_count == 4:
                        self.counting_cards += self.find_value(poker_card_values[i-1])
                        return True
                elif poker_card_values[i] == poker_card_values[i-1]:
                    straight_count = straight_count
                else:
                    straight_count = 0
                    self.counting_cards = []
        self.counting_cards = []    
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
        self.counting_cards = []
        royal = [10,11,12,13,14]

        if self.poker_cards and len(self.poker_cards)>=5:
    
            for c in self.poker_cards:
                poker_card_values.append(c.rank.value)
            s = set(poker_card_values)
            poker_card_values = list(s)
            poker_card_values.sort()

            if list(set(poker_card_values).intersection(royal)) == royal: 
                for c in royal:
                    self.counting_cards += self.find_value(c)
                return True 
            else:
                self.counting_cards = []
                return False



    def is_flush(self):
        for s in Suits:
            if self.count_suits(s) >= 5:
                self.counting_cards = self.find_suits(s.name)
                self.flush_suit = s.name
                return True
        self.counting_cards = []
        return False

    def is_straight_flush(self):
       return self.is_flush() and self.is_straight()
      

    def is_quads(self):
        for r in Ranks:
            if self.count_rank(r) == 4:
                self.counting_cards = self.find_value(r.value)
                return True
        self.counting_cards = []
        return False

    def is_trips(self):
        for r in Ranks:
            if self.count_rank(r) >= 3:
                self.counting_cards += self.find_value(r.value)
                return True
        self.counting_cards = []
        return False


    def is_two_pair(self):
        pairs = 0
        for r in Ranks:
            if self.count_rank(r) == 2:
                self.counting_cards += self.find_value(r.value)
                pairs += 1
            if pairs >= 2:
               return True
        self.counting_cards = []
        return False

    def is_pair(self):
        for r in Ranks:
            if self.count_rank(r) == 2:
                self.counting_cards += self.find_value(r.value)
                return True
        self.counting_cards = []
        return False

    def get_highest(self):
        poker_card_values=[]
        if self.poker_cards:
            for c in self.poker_cards:
                poker_card_values.append(c.rank.value)
            poker_card_values.sort()
            self.counting_cards = self.find_value(poker_card_values[len(poker_card_values)-1])
            return self.find_value(poker_card_values[len(poker_card_values)-1]) 
        return None

    def get_hand(self):
        if self.is_flush() and self.is_royal():
            for f in self.counting_cards:
                if f.suit.name != self.flush_suit:
                    self.counting_cards.remove(f)
            self.name = Hands.royal_flush.name
            
        elif self.is_straight_flush():
            for f in self.counting_cards:
                if f.suit.name != self.flush_suit:
                    self.counting_cards.remove(f)
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
    
    def compareHands(self,hand2):
        v1 = Hands[self.name].value
        v2 = Hands[hand2.name].value

        if v1 > v2: return 1
        elif v1 < v2: return 2
        else: return 3

    def find_value(self,v):
        valuecards=[]
        for c in self.poker_cards:
            if c.rank.value == v: valuecards.append(c)
        return valuecards
    
    def find_suits(self,s):
        suitcards=[]
        for c in self.poker_cards:
            if c.suit.name == s: suitcards.append(c)
        return suitcards
        

