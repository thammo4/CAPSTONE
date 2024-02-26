import requests


#
# Function to obtain an arbitrary list of Page IDs for Wikimedia Commons files
#

def get_random_commons_ids (num_files=1):
    api_url = 'https://commons.wikimedia.org/w/api.php';
    api_params = {
    	'action':'query',
    	'list':'random',
    	'rnnamespace':6, # namespace=6 is for files
    	'rnlimit':num_files,
    	'format':'json'
    };

    r = requests.get(url=api_url, params=api_params);
    data = r.json()['query']['random'];

    wc_page_ids = [wc_file['id'] for wc_file in data];

    if num_files == 1:
    	wc_page_ids = wc_page_ids[0];

    return wc_page_ids;


#
# Function to map WikiMedia Commons uploads to their corresponding WikiData Entities
#

def get_depicts_statements(wc_page_id):
    # Construct the WikiBase Entity ID
    wb_entity_id = f'M{wc_page_id}'

    # Configure API Settings for GET Request to Commons API
    api_url = 'https://commons.wikimedia.org/w/api.php'
    api_params = {
        'action': 'wbgetentities',
        'ids': wb_entity_id,
        'format': 'json',
        'props': 'claims'
    }

    # Make GET Request to Commons API
    response = requests.get(url=api_url, params=api_params)
    data = response.json()

    #
    # NOTE - Need to rewrite data_statements,...,wd_item_id  for fault tolerance
    # `	• If we query for random files uploaded to commons, many of them will not have any statements (or, if they have statements, they may lack depicts P180)
    # 	• Add boolean check somewhere below so that we check for existence of contents for data['entities'][wb_entity_id]
    # 	• If data['entities'][wb_entity_id] doesnt exist, make the function bail on the subsequent operations
    #
    # Example of issue that arises when a commons file does not have any `depicts` statements:
	# 	>>> get_random_commons_ids()
	# 	107162291
	# 	>>> get_depicts_statements(107162291)
	# 	Traceback (most recent call last):
	# 	  File "<stdin>", line 1, in <module>
	# 	  File "/Users/thammons/Desktop/msds/capstone/CAPSTONE/wikifreak.py", line 54, in get_depicts_statements
	# 	    depicts = data_statements['P180'][0]
	# 	              ~~~~~~~~~~~~~~~^^^^^^^^
	# 	KeyError: 'P180'

    # Extract the Properties Associated with the Commons File
    data_statements = data['entities'][wb_entity_id]['statements']

    # Extract the `Depicts` Property
    depicts = data_statements['P180'][0]

    # Extract relevant information pertaining to the `Depicts` statement
    depicts_data = depicts['mainsnak']

    # Isolate the WikiData Item
    wd_item = depicts_data['datavalue']['value']

    # Extract the WikiData Item ID Corresponding to the original Commons File
    wd_item_id = wd_item['id']

    print(f'Commons Page ID:{wc_page_id} -> WikiData Item ID:{wd_item_id}');
    return wd_item_id

#
# Depicts Example 1: Marie Curie c. 1920s.jpg (https://commons.wikimedia.org/w/index.php?curid=61396200)
#

# Commons Page ID:61396200 -> WikiData Item ID:Q7186
wc_page_id = 61396200;
wd_item_id = get_depicts_statements(wc_page_id);



#
# Depicts Example 2: German Sugar Cubes (https://commons.wikimedia.org/wiki/File:Würfelzucker_--_2018_--_3582.jpg)
#

# Commons Page ID:71048738 -> WikiData Item ID:Q1042920
wc_page_id = 71048738;
wd_item_id = get_depicts_statements(wc_page_id);


#
# Example: Get Random File on Commons and Fetch Its Depicts Statements
# 	• Note: this might return an error if the random commons file does not have any depicts statements
#

wc_page_id = get_random_commons_id(num_files=1);
wd_item_id = get_depicts_statements(wc_page_id);