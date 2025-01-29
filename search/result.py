
from typing import List


class Chapter():
	def __init__(self, title, time):
		self.title = title
		self.time = time
	
	def __str__(self):
		return f"{self.title} - {self.time}"


class EpisodeResult():
	def __init__(self, title, chapters: List[Chapter]):
		self.title = title
		self.chapters = chapters

	def __str__(self):
		return f"{self.title} - {self.chapters}"
	

class Review():
	def __init__(self, score, total):
		self.score = score
		self.total = total

"""
InstructionalResult is a class that holds the result of a bjj instructional query. This is what is expected throughout the program when a search is made. Various sources of search results will return this exact object. 

This class is meant to be subclassed by the various sources of search results.

Usage:
	result = InstructionalResult("title", "url", "source", "image", "instructor", Review(5, 5), "category", [])

"""
class InstructionalResult():
	def __init__(self, title, description = "", url = "", source = "", image = "", instructor: List[str] = [], review = None, category: List[str] = [], episodes: List[EpisodeResult] =[]):
		self.title = title
		self.url = url
		self.description = description
		self.source = source
		self.image = image
		self.instructor = instructor
		self.review = review
		self.category = category
		self.episodes = episodes

	def episodesToString(self):
		return "".join([f"{episode.title} - {episode.chapters}" for episode in self.episodes])
	
	def __str__(self):
		return f"{self.title} - {self.description} - {self.url} - {self.source} - {self.image} - {self.instructor} - {self.review} - {self.category} - {self.episodesToString()}"



