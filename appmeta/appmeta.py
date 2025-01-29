import json
import os
from typing import TypedDict

# submeta type --> serializable

class SubMeta(TypedDict):
	author: str #should match the author of the source ex https://submeta.io/@lachlangiles/ --> lachlangiles


class AppMeta:
	def __init__(self, file_path='data/data.json'):
		self.first = False
		self.file_path = file_path
# Ensure the directory exists
		os.makedirs(os.path.dirname(file_path), exist_ok=True)
# Initialize with default data if the file doesn't exist
		if not os.path.exists(file_path):
			self._write_data({'name': '', 'ignore': False})
			self.first = True

	def _read_data(self):
		"""Reads the JSON data from the file."""
		with open(self.file_path, 'r') as file:
			return json.load(file)

	def _write_data(self, data):
		"""Writes the JSON data to the file."""
		with open(self.file_path, 'w') as file:
			json.dump(data, file, indent=4)
	
	def change_path(self, new_path):
		"""Changes the path of the JSON file."""
		self.file_path = new_path
		os.makedirs(os.path.dirname(new_path), exist_ok=True)
		if not os.path.exists(new_path):
			self._write_data({'name': '', 'ignore': False})

	def get_data(self):
		"""Returns the current data from the JSON file."""
		return self._read_data()

	def should_ignore(self):
		"""Returns whether the file should be ignored."""
		return self._read_data()['ignore']

	def update_data(self, name=None, ignore=None, chapter=None, source=None, submeta=None):
		"""Updates the data in the JSON file."""
		data = self._read_data()
		if name is not None:
			data['name'] = name
		if ignore is not None:
			data['ignore'] = ignore
		if chapter is not None:
			data['chapter'] = chapter
		if source is not None:
			data['source'] = source
		self._write_data(data)
