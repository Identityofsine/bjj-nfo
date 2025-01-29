from typing import List, Optional, TypedDict, Union, cast

import requests

from search.result import EpisodeResult, InstructionalResult
from search.search import SearchSource
from search.titlematcher.titlematcher import Entry, TitleMatcher
from search.result import Chapter as ChapterResult

#episodes 

class Price(TypedDict):
	amount: int

class Video(TypedDict):
    id: str
    title: str
    duration: int

class Group(TypedDict):
    id: str

class Chapter(TypedDict):
    contents: List[Union[Video, Group]]
    id: str
    hidden: bool
    title: str
    order: int

class Avatar(TypedDict):
	fileName: Optional[str]

class Creator(TypedDict):
	avatar: Optional[Avatar]
	bio: Optional[str]
	connectAccountId: Optional[str]
	handle: str
	id: Optional[str]
	name: str
	prices: Optional[List[Price]]
	role: str

class ContentCount(TypedDict):
	videos: int

class Cover(TypedDict):
	fileName: str

class Course(TypedDict):
	id: str
	title: str
	slug: str
	description: Optional[str]
	level: str
	publishedAt: Optional[str]
	category: str
	cover: Cover
	charge: str
	vimeo: Optional[str]
	authors: List[Creator]
	contentCount: ContentCount
	isNew: bool
	lastContent: Optional[str]
	chapterCount: Optional[int]
	duration: float
	progress: Optional[float]
	chapters: Optional[List[Chapter]]

class CourseGrouping(TypedDict):
	groupingTitle: str
	totalCount: int
	courses: List[Course]

class ErrorsFields(TypedDict):
	key: str
	message: str

class CoursesPageResult(TypedDict):
	groupings: List[CourseGrouping]
	hasMore: bool
	errors: Optional[List[ErrorsFields]]

class GetCoursesPageResponse(TypedDict):
	result: CoursesPageResult


end_point = "https://b.submeta.io/api"
def create_request_object(offset: int, creatorHandle: str) -> dict:
	obj = {
		"operationName": "GetCoursesPage",
		"variables": {
			"creatorHandle": creatorHandle,
			"offset": offset
		},
		"query": "query GetCoursesPage($creatorHandle: String, $offset: Int) {\n  result: getCoursesPage(creatorHandle: $creatorHandle, offset: $offset) {\n    groupings {\n      ...BaseCourseGrouping\n      __typename\n    }\n    hasMore\n    errors {\n      ...ErrorsFields\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment BaseCourseGrouping on CourseGrouping {\n  groupingTitle\n  totalCount\n  courses {\n    ...CourseFieldsForCards\n    ...UserCourseFields\n    __typename\n  }\n  __typename\n}\n\nfragment CourseFieldsForCards on Course {\n  ...BaseCourseFields\n  duration\n  category\n  authors {\n    id\n    handle\n    name\n    role\n    bio\n    __typename\n  }\n  contentCount {\n    videos\n    __typename\n  }\n  isNew\n  lastContent\n  chapterCount\n  charge\n  __typename\n}\n\nfragment BaseCourseFields on Course {\n  id\n  title\n  slug\n  description\n  level\n  publishedAt\n  category\n  cover {\n    fileName\n    __typename\n  }\n  charge\n  vimeo\n  authors {\n    id\n    handle\n    name\n    bio\n    role\n    connectAccountId\n    prices {\n      ...SubscriptionPriceFields\n      __typename\n    }\n    avatar {\n      fileName\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment SubscriptionPriceFields on Price {\n  ...BasePriceFields\n  id\n  billingPeriod\n  __typename\n}\n\nfragment BasePriceFields on Price {\n  id\n  currency\n  unitAmount\n  status\n  connectAccountId\n  __typename\n}\n\nfragment UserCourseFields on Course {\n  progress\n  lastContent\n  __typename\n}\n\nfragment ErrorsFields on ErrorOutput {\n  key\n  message\n  __typename\n}\n"
	}
	return obj

class SubMeta(SearchSource):

	courseIndex: List[Course] = []

	def __init__(self):
		super().__init__("SubMeta")
		self.courseIndex = self.get_all_courses("lachlangiles")
	
	def search(self, query) -> List[InstructionalResult] | None:
		print(f"Searching SubMeta for {query}")
		c = self.get_all_courses(query)
		b = self.match_course(c, query)
		return [self.course_to_instructional_result(b)] if b is not None else None

	def get_all_courses(self, creatorHandle: str, offset: int = 0) -> List[Course]:
		if len(self.courseIndex) > 0:
			return self.courseIndex
		courses = []
		requestbody = create_request_object(offset, creatorHandle)
		r = requests.post(end_point, json=requestbody)
		response = r.json()
		data = response["data"]
		if data is None:
			return courses
		result = cast(GetCoursesPageResponse, data)["result"]
		if result is None:
			return courses
		groupings = result["groupings"]
		if groupings is None:
			return courses
		for grouping in groupings:
			courses.extend(grouping["courses"])
		if result["hasMore"]:
			courses.extend(self.get_all_courses(creatorHandle, offset + 3))
		return courses

	def match_course(self, course: List[Course], query: str) -> Optional[Course]:
		titlematcher = TitleMatcher(query, [Entry(title=c["title"], index=i) for i, c in enumerate(course)])
		best_matches = titlematcher.get_best_matches()
		if len(best_matches) == 0:
			return None
		best_match = best_matches[0]
		return course[best_match[2]]

	def course_to_instructional_result(self, course: Course) -> InstructionalResult:
		return InstructionalResult(
			title=course["title"],
			description=course["description"] or '',
			category=[course["category"] or '', course["level"] or '', ],
			image=f"https://optimg.submeta.io/uploads/{course["cover"]["fileName"]}",
			instructor=[c["name"] for c in course["authors"]],
			episodes=self.get_episodes_from_course(course)
		)

	def get_episodes_from_course(self, course: Course) -> List[EpisodeResult]:
		author = course["authors"][0]
		if author["handle"] is None:
			return []
		url = f"https://submeta.io/_next/data/vG6OAhPes7Gnc-d38RYqf/@lachlangiles/courses/{course['slug']}.json?username={author['handle']}"
		r = requests.get(url)
		if r.status_code != 200:
			return []
		pageProps = r.json()["pageProps"]
		course = pageProps["course"]
		chapters = cast(List[Chapter], course["chapters"])
		#each chapter acts as a video
		episodes = []
		for episode in chapters:
			chapterMarks = []
			for chapter in episode["contents"]:
				if "duration" in chapter:
					chapterMarks.append(ChapterResult(
						title=chapter["title"], 
						time=str(chapter["duration"]
					)))
			episodes.append(EpisodeResult(title=episode["title"], chapters=chapterMarks))
		print(episodes)

		return episodes
