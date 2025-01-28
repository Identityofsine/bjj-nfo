#main

from nfo.nfo import NFODocument
from search.search import SearchEngine
from search.services.bjjfanatics import BJJFanatics

bjj = SearchEngine(
	[
		BJJFanatics(1)
	]
)

results = bjj.search("Leg Lock Lachlan Giles")

i = 0
for result in results:
	print(f"[{i}] {result}")
	i += 1

metadata = NFODocument("tvshow")
metadata.add_instructional_result(results[0].results[0])

print(metadata)

