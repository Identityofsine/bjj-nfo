from bs4 import BeautifulSoup

from typing import List, Optional, TypedDict, cast
from search.result import EpisodeResult, InstructionalResult
from search.search import SearchSource
import requests

from search.titlematcher import titlematcher
from search.titlematcher.titlematcher import TitleMatcher

#types

class Thumbnail(TypedDict):
	image: Optional[str] 
	urls : Optional[List[str]]

class Review(TypedDict):
	average_score: float
	total_reviews: int

class BJJFanaticsVideo(TypedDict):
		id: int
		title: str
		url: str
		image: str
		product_type: str
		thumbnail: List[Thumbnail]
		video_thumbs: List[str]
		price: float
		site: str
		compare_at_price: float
		authors: List[str]
		categories: List[str]
		sub_categories: List[str]
		published_at: str
		tags: List[str]
		shopify_status: str
		review: Review
		search_identifier: str
		_updated_from: str
		_updated_at: str
		
class BJJFanaticsQuery(TypedDict):
	videos: List[BJJFanaticsVideo]
	totalResults: int
	ids: List[int]


#class
API_LINK = "https://bjjfanatics-msigw.ondigitalocean.app/v4/products/search?term=%REPLACE%&qtyBestSellers=5&qtyNewReleases=3&qtyAll=10000"

def toEntry(videos: List[BJJFanaticsVideo]) -> List[titlematcher.Entry]:
	entries = []
	for i, video in enumerate(videos):
		entries.append(titlematcher.Entry(title=video["title"], index=i))
	return entries



class BJJFanatics(SearchSource):

	lastSearch = ""
	cachedHTML = None 

	def __init__(self, limit = 1):
		super().__init__("BJJFanatics", limit)
	
	def search(self, query) -> List[InstructionalResult] | None:
		queryObject = self.query(query)
		if queryObject is None:
			return None
		best_result = self.get_best_result(query, queryObject)
		if best_result is None:
			return None
		results = []
		for video in best_result:
			print(f"Fetching data for {video['title']}...")
			results.append(self.toInstructionalResult(video))
		print(f"BJJFanatics - Done")
		return results

	def query(self, name) -> BJJFanaticsQuery | None:
		try:
			print(f"Querying BJJFanatics for {name}")
			link = API_LINK.replace("%REPLACE%", name.replace(" ", "%20"))
			response = requests.get(link)
			json = response.json()
			obj = cast(BJJFanaticsQuery, json)
			return obj
		except Exception as e:
			print(f"BJJFanatics Error[query]: {e}")
			return None
		
	def get_best_result(self, title: str, queryResult: BJJFanaticsQuery) -> List[BJJFanaticsVideo] | None:
		entries = toEntry(queryResult["videos"])
		titlematcher = TitleMatcher(title, entries)
		best_matches = titlematcher.get_best_matches()
		if len(best_matches) == 0:
			return []

		if self.limit > 1:
			results = []
			i = 0
			for match in best_matches:
				if i >= self.limit:
					break
				results.append(queryResult["videos"][match[2]])
				i += 1
			return results
		else:
			best_match = best_matches[0]
			return [queryResult["videos"][best_match[2]]]

	def get_description(self, video: BJJFanaticsVideo) -> str:
		content = self.get_video_page(video)
		description = content.find("div", {"class": "product_description"})
		if description is None:
			return ""
		text = ""
		# add all text in the description	from header tags, paragraphs, and list items
		for tag in description.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p", "li"]):
			text += tag.get_text() + "\n"
		return text

	def get_video_page(self, video: BJJFanaticsVideo) -> BeautifulSoup:
		if self.cachedHTML is None or video["url"] != self.lastSearch:
			r = requests.get(video["url"])
			if r.status_code != 200:
				return ""
			html = r.text
			content = BeautifulSoup(html, "html.parser")
			self.cachedHTML = content
		return self.cachedHTML


	def get_episodes(self, video: BJJFanaticsVideo) -> List[EpisodeResult]:
		try:
			content = self.get_video_page(video)
			list = []
			if content == "":
				return list
			# find the div that contains the episodes
			list_div = "product__course-content-accordion"
			episodes = content.find("div", {"class": list_div})
			if episodes is None or len(episodes.contents) == 0:
				return list
			episode_name = episodes.find_all("h3", {"class": "product__course-title"})
			episode_chapters = episodes.find_all("figure", {"class": "table"})
			if len(episode_name) != len(episode_chapters):
				return list
			for i in range(len(episode_name)):
				chapters = []
				for chapter in episode_chapters[i].find_all("tr"):
					tds = chapter.find_all("td")
					chapter_title = tds[0].get_text()
					chapter_time = tds[1].get_text()
					chapters.append({"title": chapter_title, "time": chapter_time})
				list.append(EpisodeResult(title=episode_name[i].get_text(), chapters=chapters))

			return list
		except Exception as e:
			print(f"BJJFanatics Error[get_episodes]: {e}")
			return []
		

	def toInstructionalResult(self, video: BJJFanaticsVideo) -> InstructionalResult:
		return InstructionalResult(
			title=video["title"],
			description=self.get_description(video),
			url=video["url"],
			source="BJJFanatics",
			image=video["image"],
			instructor=video["authors"],
			review=Review(average_score=video["review"]["average_score"], total_reviews=video["review"]["total_reviews"]),
			category=video["categories"],
			#to be implemented
			episodes=self.get_episodes(video)
		)

		

