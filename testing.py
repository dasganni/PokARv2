from Poker_Game import *
from enum import Enum

c1 = poker_card(Ranks.Ten, Suits.Hearts)
c2 = poker_card(Ranks.Ten, Suits.Hearts)
c3 = poker_card(Ranks.Ace, Suits.Hearts)
c4 = poker_card(Ranks.Ace, Suits.Hearts)
c5 = poker_card(Ranks.Queen, Suits.Hearts)

h1 = Hand([c1,c2,c3,c4])

h1.print_hand()
h1.get_hand()

#print(h1.is_royal() and h1.is_flush())
#print(h1.is_flush())
print(h1.name)