from Poker_Game import *
from enum import Enum

c1 = poker_card(Ranks.Queen, Suits.Hearts)
c2 = poker_card(Ranks.Ten, Suits.Hearts)
c3 = poker_card(Ranks.Jack, Suits.Hearts)
c4 = poker_card(Ranks.King, Suits.Hearts)
c5 = poker_card(Ranks.Ace, Suits.Hearts)

c6 = poker_card(Ranks.Queen, Suits.Clubs)

h1 = Hand([c1,c5,c6,c3,c4])
h2 = Hand([c1,c1,c1,c1,c1])

h1.print_hand()
h1.get_hand()
h2.get_hand()

#print(h1.is_royal() and h1.is_flush())
#print(h1.is_flush())
print(h1.name)

for c in h1.find_value(12):
    print(c.rank.name + " of " + c.suit.name)

