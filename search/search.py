from abc import ABC, abstractmethod, abstractproperty
from typing import List, TypedDict

from search.result import InstructionalResult


class SearchResult():
	source: str
	results: List[InstructionalResult]

	def __init__(self, source, results):
		self.source = source
		self.results = results

	def resultsToString(self):
		return "".join([result.title for result in self.results])

	def __str__(self):
		return f"{self.source} - {self.resultsToString()}"

"""
SearchSource is an abstract class that represents a source of search results from a certian source.

Such an example is the BJJFanatics website, which provides results for a search query using their internal search engine. 

To implement a new source of search results, you must subclass this class and implement the search method.
"""
class SearchSource(ABC):

	def __init__(self, source, limit = 1):
		self.source = source
		self.limit = limit
		pass

	"""
	Searches for a query and returns the results.
	"""
	@abstractmethod
	def search(self, query) -> List[InstructionalResult] | None:
		pass

class SearchEngine():

	def __init__(self, sources: list[SearchSource]):
		self.sources = sources

	def search(self, query) -> List[SearchResult]:
		results = []
		for source in self.sources:
			result = source.search(query)
			if result is not None:
				for rr in result:
					results.append(SearchResult(source.source, [rr]))
		return results 
