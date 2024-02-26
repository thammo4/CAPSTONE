import requests

#
# SUMMARY OF CONTENTS:
#
# This Python script retrieves the 'Depicts' (P180) information for the Wikimedia Commons file "Marie Curie c. 1920s.jpg".
# The process involves making an API request to Wikimedia Commons using the wbgetentities module with the Wikibase entity ID corresponding to the page ID of the Commons file.
# The script then extracts the relevant data from the JSON response.
#
# The final output `wd_item_id` holds the Wikidata item ID ('Q7186') associated with the 'Depicts' property of the Commons file.
# This ID represents the main subject or object depicted in the image.
#
# Reference:
# 	• https://commons.wikimedia.org/wiki/Commons:Depicts#Searching_depicts_statements
# 	• https://chat.openai.com/share/a089bdca-c7a2-43a5-9c37-19293d3e17d5
#


#
# Unique identifier for image uploaded to commons
# Example: 
# 	• `Marie Curie c. 1920s.jpg`
# 	• https://commons.wikimedia.org/w/index.php?curid=61396200
#

wc_page_id = 61396200;



#
# Construct the WikiBase Entity ID to which the commons' file corresponds
# 	• WikiBase Entity IDs constructed by prepending `M` to commons page id
# 	• Commons.page_id = 61396200 -> WikiBase.Entity_ID = M61396200
#

wb_entity_id = f'M{wc_page_id}';


#
# Configure API Settings for GET Request to Commons API
# 	• Define endpoint URL
# 	• Define query parameters
#

api_url = 'https://commons.wikimedia.org/w/api.php';
api_params = {
	'action': 'wbgetentities',
	'ids': wb_entity_id,
	'format': 'json',
	'props':'claims'
};

#
# Make GET Request to Commons API
#
# >>> data
# {'entities': {'M61396200': {'type': 'mediainfo', 'id': 'M61396200', 'statements': {'P180': [{'mainsnak': {'snaktype': 'value', 'property': 'P180', 'hash': 'ee52ae08f1e141cefa51d0d2df36c318434227d8', 'datavalue': {'value': {'entity-type': 'item', 'numeric-id': 7186, 'id': 'Q7186'}, 'type': 'wikibase-entityid'}}, 'type': 'statement', 'id': 'M61396200$1b2859f7-40ad-dac8-1b97-56fe264c0640', 'rank': 'normal'}], 'P1163': [{'mainsnak': {'snaktype': 'value', 'property': 'P1163', 'hash': '723d30b878d4a8deb968b0db429888e5353661a2', 'datavalue': {'value': 'image/jpeg', 'type': 'string'}}, 'type': 'statement', 'id': 'M61396200$A5B7EAF4-5A79-4014-A538-DA0A5EB1FD07', 'rank': 'normal'}], 'P6216': [{'mainsnak': {'snaktype': 'value', 'property': 'P6216', 'hash': 'f69dc45ce9c48664155022498b34100d801bd549', 'datavalue': {'value': {'entity-type': 'item', 'numeric-id': 19652, 'id': 'Q19652'}, 'type': 'wikibase-entityid'}}, 'type': 'statement', 'id': 'M61396200$2F40DA5D-89DE-4B2B-8134-0DD6B05FEEE6', 'rank': 'normal'}]}}}, 'success': 1}
# >>> data.keys()
# dict_keys(['entities', 'success'])
#

r = requests.get(url=api_url, params=api_params);
data = r.json();


#
# Extract the Properties Associated with the Commons File
#
# >>> data_statements.keys()
# dict_keys(['P180', 'P1163', 'P6216'])
# 	• P180: `Depicts`
# 	• P1163: `MIME Type`
# 	• P6216: `Copyright Status`
#
# >>> data_statements
# {'P180': [{'mainsnak': {'snaktype': 'value', 'property': 'P180', 'hash': 'ee52ae08f1e141cefa51d0d2df36c318434227d8', 'datavalue': {'value': {'entity-type': 'item', 'numeric-id': 7186, 'id': 'Q7186'}, 'type': 'wikibase-entityid'}}, 'type': 'statement', 'id': 'M61396200$1b2859f7-40ad-dac8-1b97-56fe264c0640', 'rank': 'normal'}], 'P1163': [{'mainsnak': {'snaktype': 'value', 'property': 'P1163', 'hash': '723d30b878d4a8deb968b0db429888e5353661a2', 'datavalue': {'value': 'image/jpeg', 'type': 'string'}}, 'type': 'statement', 'id': 'M61396200$A5B7EAF4-5A79-4014-A538-DA0A5EB1FD07', 'rank': 'normal'}], 'P6216': [{'mainsnak': {'snaktype': 'value', 'property': 'P6216', 'hash': 'f69dc45ce9c48664155022498b34100d801bd549', 'datavalue': {'value': {'entity-type': 'item', 'numeric-id': 19652, 'id': 'Q19652'}, 'type': 'wikibase-entityid'}}, 'type': 'statement', 'id': 'M61396200$2F40DA5D-89DE-4B2B-8134-0DD6B05FEEE6', 'rank': 'normal'}]}
#

data_statements = data['entities'][wb_entity_id]['statements'];


#
# Extract the `Depicts` Property
# Note: regarding zero-indexing of `data_statements['P180']`
# 	• I'm not sure why, but `data_statements['P180']` returns a single-element list whose value is the desired dictionary 
# 	• It's possible that this list could contain multiple elements for a different file
#
# >>> depicts.keys()
# dict_keys(['mainsnak', 'type', 'id', 'rank'])
#
# >>> depicts
# {'mainsnak': {'snaktype': 'value', 'property': 'P180', 'hash': 'ee52ae08f1e141cefa51d0d2df36c318434227d8', 'datavalue': {'value': {'entity-type': 'item', 'numeric-id': 7186, 'id': 'Q7186'}, 'type': 'wikibase-entityid'}}, 'type': 'statement', 'id': 'M61396200$1b2859f7-40ad-dac8-1b97-56fe264c0640', 'rank': 'normal'}

depicts = data_statements['P180'][0];


#
# Extract relevant information pertaining to the `Depicts` statement
#
# >>> depicts_data.keys()
# dict_keys(['snaktype', 'property', 'hash', 'datavalue'])
#
# >>> depicts_data
# {'snaktype': 'value', 'property': 'P180', 'hash': 'ee52ae08f1e141cefa51d0d2df36c318434227d8', 'datavalue': {'value': {'entity-type': 'item', 'numeric-id': 7186, 'id': 'Q7186'}, 'type': 'wikibase-entityid'}}
#

depicts_data = depicts['mainsnak'];



#
# Isolate the WikiData Item
#
# >>> wd_item.keys()
# dict_keys(['entity-type', 'numeric-id', 'id'])
#
# >>> wd_item
# {'entity-type': 'item', 'numeric-id': 7186, 'id': 'Q7186'}
#

wd_item = depicts_data['datavalue']['value'];


#
# Extract the WikiData Item ID Corresponding to the original Commons File
#
# >>> wd_item_id
# 'Q7186'
#

wd_item_id = wd_item['id'];