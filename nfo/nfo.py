import xml.etree.ElementTree as ET

from search.result import EpisodeResult, InstructionalResult

class NFODocument():

	def __init__(self, root: str):
		self.document = ET.ElementTree()
		self.root = ET.Element(root)
		
	def save(self, path: str):
		tree = ET.ElementTree(self.root)
		tree.write(path)
	
	def add(self, key: str, value: str, parent = None):
		if parent is None:
			ele = ET.SubElement(self.root, key)
			ele.text = value
			return ele
		else:
			ele = ET.SubElement(parent, key)
			ele.text = value
			return ele
	
	def add_list(self, key: str, values: list[str]):
		for value in values:
			self.add(key, value)
	
	def add_instructional_result(self, result: InstructionalResult):
		self.add("title", result.title)
		self.add("name", result.title)
		self.add("localtitle", result.title)
		self.add("originaltitle", result.title)
		self.add("plot", result.description)
		self.add("plotoutline", result.description)
		self.add("tagline", result.description)
		self.add_list("tag", result.category)
		self.add("thumb", result.image)
		actor = self.add("actor", "")
		if len(result.instructor) > 1:
			for instructor in result.instructor[1:]:
				actor = self.add("actor", "")
				self.add("name", instructor, actor)
				self.add("role", "Instructor", actor)
				self.add("type", "Instructor", actor)
		if result.review is not None:
			self.add("rating", str(result.review.score))
			self.add("userrating", str(result.review.score))
			self.add("votes", str(result.review.total))
		self.add("mpaa", "NR")
		pass

	def add_episode(self, episode: EpisodeResult, index: int):
		self.add("plot", episode.chapters)
		self.add("title", episode.title)
		self.add("showtitle", episode.title)
		self.add("season", "1")
		self.add("episode", str(index))



	def __str__(self):
		return ET.tostring(self.root, encoding='utf8').decode('utf8')
		

