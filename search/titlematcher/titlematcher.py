from typing import List, Tuple, TypedDict, cast
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

class Entry(TypedDict):
	title: str
	index: int

class TitleMatcher:
		def __init__(self, search_query: str, title_list: List[Entry]):
			self.search_query = search_query
			self.title_list = title_list

		def get_best_matches(self, limit: int = 5) -> List[Tuple[str, int, int]]:
			"""
			Returns the best matches for the search query from the title list, sorted by similarity.
			:param limit: The maximum number of results to return (default: 5).
			:return: A list of tuples with the matched title and its similarity score.
			"""
			titles = [entry['title'] for entry in self.title_list]
			best_matches = process.extract(self.search_query, titles, scorer=fuzz.token_sort_ratio, limit=limit)
			best_matches_translated = []

			for best_match in best_matches:
				for entry in self.title_list:
					if best_match[0] == entry['title']:
						#i hate this
						best_matches_translated.append((best_match[0], best_match[1], entry['index']))
						break
			
			return best_matches_translated
