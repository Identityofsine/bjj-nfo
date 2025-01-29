#main

import os
import re
import sys
from appmeta.appmeta import AppMeta
from nfo.nfo import NFODocument
from search.search import SearchEngine
from search.services.bjjfanatics import BJJFanatics
from search.services.submeta import SubMeta

bjj = SearchEngine(
	[
		BJJFanatics(1),
		SubMeta()
	]
)

def sanitize_filename(filename: str) -> str:
    # Replace problematic characters like ':' with '_'
    return re.sub(r'[\/:*?"<>|]', '_', filename)

def split_time_string(time_str: str) -> str:
    """
    Splits a time string like "0:00 - 1:24" into "1:24".
    Leaves strings like "1:24" unchanged.
    
    Args:
        time_str (str): The input time string.
    
    Returns:
        str: The cleaned time string.
    """
    if " - " in time_str:
        # Split the string and take the second part
        return time_str.split(" - ")[1]
    else:
        # Return the string as is
        return time_str



def main():

	chaptermode = False
	#get args
	args = sys.argv[1:]
	if len(args) == 0:
		print("Usage: python main.py [path]")
		return
	path = args[0]
	commandargs = args[1:]
	if "-h" in commandargs or "--help" in commandargs:
		print("Usage: python main.py [path] -hc")
		return

	if "-c" in commandargs:
		chaptermode = True

	dir = os.listdir(path)
	print(f"Files in {path}")
	for file in dir:
		if os.path.isfile(f"{path}/{file}"):
			continue
		print(f"{file}")
			
	c = input("Is this okay? [Y/N]\n")
	if c != "Y" and c != "y":
		return 
	
	foldermeta = AppMeta(f"{path}/folder.json")
	for file in dir:
		if os.path.isfile(f"{path}/{file}"):
			continue
		print("\n")
		metadata = AppMeta(f"{path}/{file}/data.json")
		submetaOnly = False
		if foldermeta.get_data()['submeta'] is not None:
			submetaOnly = True
		if metadata.should_ignore():
				print(f"Ignoring {file}")
				continue
		if chaptermode:
			if metadata.first:
				print(f"Please process - {file} before using chapter mode")
				continue
			result = bjj.search(file, submetaOnly)[0].results[0] 
			if result is None:
				print(f"Could not find {file}")
				continue
			print(f"Selected: {result.title}")
			if result.episodes is None or len(result.episodes) == 0:
				print(f"No episodes found for {file}")
				continue
			print(f"Episodes found: {len(result.episodes)}")
			#filter o		
			for i in range(len(result.episodes)):
				episode = result.episodes[i]
				for c in range(len(episode.chapters)):
					chapter = episode.chapters[c]
					chapter.time = split_time_string(chapter.time)
					print(f"[{i}] - {chapter}")
		else:
			if metadata.get_data()['name'] != "":
				print(f"Already processed {file} - {metadata.get_data()['name']}")
				continue
			result = search(file, submetaOnly)
			if result is None:
				metadata.update_data(ignore=True)
				continue
			print(f"Selected: {result}")
			nfo = NFODocument("tvshow")
			nfo.add_instructional_result(result.results[0])
			try:
				# change the name of the folder to the title of the instructional
				os.rename(f"{path}/{file}", f"{path}/{sanitize_filename(result.results[0].title)}")
				nfo.save(f"{path}/{sanitize_filename(result.results[0].title)}/tvshow.nfo")
				metadata.change_path(f"{path}/{sanitize_filename(result.results[0].title)}/data.json")
				metadata.update_data(name=result.results[0].title, ignore=False, submeta=foldermeta.get_data()['submeta'])
			except Exception as e:
				print(f"Error: {e}")
			continue

def search(name, submetaOnly = False):
	try:
		results = bjj.search(name, submetaOnly)
		i = 0
		for result in results:
			print(f"[{i}] - {result.resultsToString()}")
			i += 1
		print(f"[{i}] - Search by keyword")
		print(f"[{i + 1}] - Ignore")
		index = input("Enter the closest match: ")
		index = int(index)
		if index == i:
			return search(input("Enter search query: "))
		elif index == i + 1:
			return None
		while index < 0 or index >= len(results):
			index = int(input("Enter the closest match: "))
		
		return results[index]
	except Exception as e:
		print(f"Error: {e}")
		return None
	


main()
