import requests
import csv

# def get_random_commons_image():
def get_marie_curie_image():
	# Get a list of random image titles from Wikimedia Commons
	commons_api_url = 'https://commons.wikimedia.org/w/api.php?action=query&titles=File:Marie Curie c. 1920s.jpg&prop=pageprops&format=json'
	response = requests.get(commons_api_url)
	data = response.json()
	random_images = data.get('query', {}).get('random', [])
	return random_images

def get_image_metadata():
	# Get image metadata from Commons API
	image_title = 'File:Marie_Curie_c._1920s.jpg'
	commons_api_url = f'https://commons.wikimedia.org/w/api.php?action=query&titles={image_title}&prop=imageinfo&iiprop=extmetadata&format=json'
	response = requests.get(commons_api_url)
	data = response.json()
	pages = data.get('query', {}).get('pages', {})
	page_id = next(iter(pages))
	metadata = pages[page_id].get('imageinfo', [{}])[0].get('extmetadata', {})
	return metadata


#
# This "should" return wikidata item IDs (e.g. Q#s), but nothing is returned
# We are unsure how to map a wikimedia commons entry to wikidata properties
#

def get_wikidata_entity_id(file_name):
	# Get Wikidata entity ID from Commons API
	commons_api_url = f'https://commons.wikimedia.org/w/api.php?action=query&titles={file_name}&prop=imageinfo&iiprop=extmetadata&format=json'
	response = requests.get(commons_api_url)
	data = response.json()
	pages = data.get('query', {}).get('pages', {})
	page_id = next(iter(pages))
	wikidata_entity_id = pages[page_id].get('imageinfo', [{}])[0].get('extmetadata', {}).get('wikibase_item', {}).get('value')
	return wikidata_entity_id


# 
# Cannot run this function because we cannot retrieve the wikidata ids
#

def get_wikidata_statements(wikidata_entity_id):
	# Get depicts statements from Wikidata API
	wikidata_api_url = f'https://www.wikidata.org/w/api.php?action=wbgetentities&format=json&ids={wikidata_entity_id}'
	response = requests.get(wikidata_api_url)
	data = response.json()
	statements = data.get('entities', {}).get(wikidata_entity_id, {}).get('claims', {}).get('P180', [])
	return statements