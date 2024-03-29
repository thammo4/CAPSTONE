import requests;
import pandas as pd;


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

def get_q_number (wc_page_id):
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

    # Check if the entity exists and has statements
    if 'entities' not in data or wb_entity_id not in data['entities'] or 'statements' not in data['entities'][wb_entity_id]:
        print(f"No data available for Wikimedia Commons Page ID: {wc_page_id}")
        return None

    data_statements = data['entities'][wb_entity_id]['statements']

    # Check if 'P180' (depicts) property exists
    if 'P180' not in data_statements or not data_statements['P180']:
        print(f"No 'depicts' statements for Wikimedia Commons Page ID: {wc_page_id}")
        return 0;

    # Assuming 'P180' exists and has at least one entry
    depicts = data_statements['P180'][0]

    # Extract relevant information pertaining to the `Depicts` statement
    depicts_data = depicts['mainsnak']

    # Isolate the WikiData Item
    wd_item = depicts_data['datavalue']['value']

    # Extract the WikiData Item ID Corresponding to the original Commons File
    wd_item_id = wd_item['id']

    print(f'Commons Page ID:{wc_page_id} -> WikiData Item ID:{wd_item_id}')
    return wd_item_id


def get_wikidata_label (wd_item_id):
    api_url = 'https://www.wikidata.org/w/api.php';
    api_params = {
        'action':'wbgetentities',
        'ids': wd_item_id,
        'format': 'json',
        'props': 'labels',
        'languages': 'en'
    };

    r = requests.get(api_url, api_params);
    data = r.json();

    if 'entities' in data and wd_item_id in data['entities'] and 'labels' in data['entities'][wd_item_id] and 'en' in data['entities'][wd_item_id]['labels']:
        label = data['entities'][wd_item_id]['labels']['en']['value'];
    else:
        # label = 'label not found';
        print(f'No depicts label found for {wd_item_id}');
        return None;

    return label;


#
# Define function that will construct a convenient dataframe by repeatedly making calls to the wiki commons/data APIs
# until a sufficiently large data set has been collected.
# • Note that the number of calls ≥ number of rows in returned dataframe
# • To create a CSV containing the returned dataframe:
#       df = siki_wiki(25);
#       df.to_csv('df_wiki.csv');
#

def siki_wiki (row_count_wanted):
    '''
        Parameters:
            • row_count_wanted [int]: Specify the desired number of rows for the resulting dataframe to contain.
    '''
    df_wiki = pd.DataFrame({'wiki_commons_id':[], 'wiki_data_id':[], 'depicts':[]});

    df_row_count = 0;
    enough_rows = False;

    while not enough_rows:
        row = {'wiki_commons_id':'', 'wiki_data_id':'', 'depicts':''};
        wc_page_ids = get_random_commons_ids(25); print(f'Commons IDs:\n{wc_page_ids}');

        for wc_page_id in wc_page_ids:
            wd_q_number = get_q_number(wc_page_id);
            if wd_q_number != 0:
                wd_depicts_statement = get_wikidata_label(wd_q_number);

                if wd_depicts_statement:
                    row['wiki_commons_id'] = wc_page_id;
                    row['wiki_data_id'] = wd_q_number;
                    row['depicts'] = wd_depicts_statement;
                    print(f'Row: {row}');

                    df_row = pd.DataFrame.from_dict(row, orient='index').T;

                    df_wiki = pd.concat([df_wiki, df_row], ignore_index=True); print(f'Updated DataFrame:\n{df_wiki}');

                    df_row_count = df_wiki.shape[0];

                    if df_row_count >= row_count_wanted:
                        enough_rows = True;
                        break;

    return df_wiki;


#
# Depicts Example 1: Marie Curie c. 1920s.jpg (https://commons.wikimedia.org/w/index.php?curid=61396200)
#

# Commons Page ID:61396200 -> WikiData Item ID:Q7186
wc_page_id = 61396200;
wd_item_id = get_q_number(wc_page_id);



#
# Depicts Example 2: German Sugar Cubes (https://commons.wikimedia.org/wiki/File:Würfelzucker_--_2018_--_3582.jpg)
#

# Commons Page ID:71048738 -> WikiData Item ID:Q1042920
wc_page_id = 71048738;
wd_item_id = get_q_number(wc_page_id);


#
# Example: Get Random File on Commons and Fetch Its Depicts Statements
# 	• Note: this might return an error if the random commons file does not have any depicts statements
#

wc_page_id = get_random_commons_ids(num_files=1);
wd_item_id = get_q_number(wc_page_id);