from Poker_Game import *
from enum import Enum

c1 = poker_card(Ranks.Queen, Suits.Hearts)
c2 = poker_card(Ranks.Ten, Suits.Hearts)
c3 = poker_card(Ranks.Ten, Suits.Hearts)
c4 = poker_card(Ranks.King, Suits.Hearts)
c5 = poker_card(Ranks.Ace, Suits.Hearts)

c6 = poker_card(Ranks.Queen, Suits.Clubs)
c7 = poker_card(Ranks.Queen, Suits.Diamonds)

h1 = Hand([c1,c2,c3,c4,c5,c7])
h2 = Hand([c1,c1,c1,c1,c1])

h1.print_hand()
h1.get_hand()
h2.get_hand()

#print(h1.is_royal() and h1.is_flush())
#print(h1.is_flush())
print(h1.name)


for c in h1.counting_cards:
    print(c.display())

