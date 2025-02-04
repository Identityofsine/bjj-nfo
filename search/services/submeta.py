from typing import List, Optional, TypedDict, Union, cast

import requests

from search.result import EpisodeResult, InstructionalResult
from search.search import SearchSource
from search.services.bjjfanatics import API_LINK
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

class CoursesSearchResult(TypedDict):
	courses: List[Course]

class GetCoursesPageResponse(TypedDict):
	result: CoursesPageResult



end_point = "https://b.submeta.io/api"
def create_request_object(offset: int, creatorHandle: str, search: str ="") -> dict:
	obj = {
		"operationName": "SearchCourses",
		"variables": {
			"creatorHandle": creatorHandle,
			"searchTerm": search,
			"offset": offset,
			"limit": 10000
		},
	  "query": "query SearchCourses($searchTerm: String, $creators: [String], $filter: CourseFilter, $offset: Int, $limit: Int) {\n  result: searchCourses(\n    searchTerm: $searchTerm\n    creators: $creators\n    filter: $filter\n    offset: $offset\n    limit: $limit\n  ) {\n    courses {\n      ... on Course {\n        ...CourseFieldsForCards\n        ...UserCourseFields\n        __typename\n      }\n      __typename\n    }\n    pageInfo {\n      hasNextPage\n      hasPreviousPage\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment CourseFieldsForCards on Course {\n  ...BaseCourseFields\n  duration\n  category\n  authors {\n    id\n    handle\n    name\n    role\n    bio\n    __typename\n  }\n  contentCount {\n    videos\n    __typename\n  }\n  isNew\n  lastContent\n  chapterCount\n  charge\n  __typename\n}\n\nfragment BaseCourseFields on Course {\n  id\n  title\n  slug\n  description\n  level\n  publishedAt\n  category\n  cover {\n    fileName\n    __typename\n  }\n  charge\n  vimeo\n  authors {\n    id\n    handle\n    name\n    bio\n    role\n    connectAccountId\n    prices {\n      ...SubscriptionPriceFields\n      __typename\n    }\n    avatar {\n      fileName\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment SubscriptionPriceFields on Price {\n  ...BasePriceFields\n  id\n  billingPeriod\n  __typename\n}\n\nfragment BasePriceFields on Price {\n  id\n  currency\n  unitAmount\n  status\n  connectAccountId\n  __typename\n}\n\nfragment UserCourseFields on Course {\n  progress\n  lastContent\n  __typename\n}",
	}
	return obj

def create_episode_request_object(course: Course, creatorHandle: str) -> dict:

	obj = {
		"operationName": "GetCourse",
		"variables": {
			"courseId": str(course["id"]),
		},
		"query": "query GetCourse($courseSlug: String, $creatorHandle: String, $courseId: ID) {\n  result: getCourse(\n    courseSlug: $courseSlug\n    creatorHandle: $creatorHandle\n    courseId: $courseId\n  ) {\n    course {\n      id\n      ...EntireCourseLoggedOut\n      __typename\n    }\n    errors {\n      ...ErrorsFields\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment EntireCourseLoggedOut on Course {\n  ...CourseFields\n  chapters {\n    ...ChapterFields\n    contents {\n      ... on Video {\n        id\n        title\n        duration\n        __typename\n      }\n      ... on Group {\n        id\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  prices {\n    ...BasePriceFields\n    __typename\n  }\n  __typename\n}\n\nfragment CourseFields on Course {\n  ...BaseCourseFields\n  duration\n  contentCount {\n    videos\n    exercises\n    __typename\n  }\n  __typename\n}\n\nfragment BaseCourseFields on Course {\n  id\n  title\n  slug\n  description\n  level\n  publishedAt\n  category\n  cover {\n    fileName\n    __typename\n  }\n  charge\n  vimeo\n  authors {\n    id\n    handle\n    name\n    bio\n    role\n    connectAccountId\n    prices {\n      ...SubscriptionPriceFields\n      __typename\n    }\n    avatar {\n      fileName\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment SubscriptionPriceFields on Price {\n  ...BasePriceFields\n  id\n  billingPeriod\n  __typename\n}\n\nfragment BasePriceFields on Price {\n  id\n  currency\n  unitAmount\n  status\n  connectAccountId\n  __typename\n}\n\nfragment ChapterFields on Chapter {\n  id\n  hidden\n  title\n  order\n  __typename\n}\n\nfragment ErrorsFields on ErrorOutput {\n  key\n  message\n  __typename\n}\n" 
	}
	return obj



class SubMeta(SearchSource):

	courseIndex: List[Course] = []

	def __init__(self, limit = 1):
		super().__init__("SubMeta")
		#self.courseIndex = self.get_all_courses("lachlangiles")
		self.limit = limit
	
	def search(self, query) -> List[InstructionalResult] | None:
		print(f"Searching SubMeta for {query}")
		c = self.search_for_course(query, "lachlangiles")
		b = self.match_course(c, query)
		if b is None:
			return None
		results = []
		for course in b:
			results.append(self.course_to_instructional_result(course))
		return results

	def search_for_course(self, query: str, creatorHandle: str) -> List[Course]:
		requestbody = create_request_object(0, creatorHandle, query)
		r = requests.post(end_point, json=requestbody)
		response = r.json()
		data = response["data"]
		if data is None:
			return []
		result = cast(CoursesSearchResult, data["result"])
		if result is None:
			return []
		courses = result["courses"]
		return courses


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

	def match_course(self, course: List[Course], query: str) -> Optional[List[Course]]:
		titlematcher = TitleMatcher(query, [Entry(title=c["title"], index=i) for i, c in enumerate(course)])
		best_matches = titlematcher.get_best_matches()
		if len(best_matches) == 0:
			return None

		if self.limit > 1:
			results = []
			i = 0
			for match in best_matches:
				if i >= self.limit:
					break
				results.append(course[match[2]])
				i += 1
			return results
		else: 
			best_match = best_matches[0]
			return [course[best_match[2]]]

	def course_to_instructional_result(self, course: Course) -> InstructionalResult:
		return InstructionalResult(
			title=course["title"],
			source="SubMeta",
			description=course["description"] or '',
			category=[course["category"] or '', course["level"] or '', ],
			image=f"https://optimg.submeta.io/uploads/{course["cover"]["fileName"]}",
			instructor=[c["name"] for c in course["authors"]],
			episodes=self.get_episodes_from_course(course)
		)

	def get_episodes_from_course(self, course: Course) -> List[EpisodeResult]:
		body = create_episode_request_object(course, "lachlangiles")

		r = requests.post(end_point, json=body)
		if r.status_code != 200:
			print(f"Error: {r.status_code}")
			return []

		data = r.json()["data"]
		if data is None:
			return []
		result = data["result"]
		if result is None:
			return []
		course = cast(Course, result["course"])
		if course is None:
			return []
		chapters = course["chapters"]
		if chapters is None:
			return []

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

		return episodes
