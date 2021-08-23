# ASER Test

# step-by-step extraction

from pprint import pprint
from aser.extract.aser_extractor import SeedRuleASERExtractor, DiscourseASERExtractor

text = "I came here for breakfast before a conference, I was excited to try some local breakfast places. I think the highlight of my breakfast was the freshly squeezed orange juice: it was very sweet, natural, and definitely the champion of the day. I ordered the local fresh eggs on ciabatta with the house made sausage. I would have given a four if the bread had been toasted, but it wasnt. The sausage had good flavor, but I would have liked a little salt on my eggs. All in all a good breakfast. If I am back in town I would try the pastries, they looked and smelled amazing."
text = "On my way to work I stopped to get some coffee. I went through the drive through and placed my order. I paid the cashier and patiently waited for my drink. When she handed me the drink, the lid came off and spilled on me. The coffee hurt and I had to go home and change clothes."
# text = "The coffee hurt and I had to go home and change clothes."
print("Text:")
print(text)
# corenlp_path="/Users/zhifanshangguan/stanza_corenlp"
# corenlp_path="stanford-corenlp-3.9.2"
aser_extractor = DiscourseASERExtractor(
  corenlp_path="/Users/zhifanshangguan/stanza_corenlp", corenlp_port=9000
)

print("-" * 80)
print("In-order:")
pprint(aser_extractor.extract_from_text(text, in_order=True))

# print("-" * 80)
# print("Out-of-Order:")
# results = aser_extractor.extract_from_text(text, in_order=False)
# pprint(results)

# eventualities, relations = results