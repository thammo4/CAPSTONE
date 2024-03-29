def get_random_commons_ids(num_files=1):
    api_url = 'https://commons.wikimedia.org/w/api.php'
    api_params = {
        'action': 'query',
        'list': 'random',
        'rnnamespace': 6,  # namespace=6 is for files
        'rnlimit': num_files,
        'format': 'json'
    }

    r = requests.get(url=api_url, params=api_params)
    data = r.json()['query']['random']

    wc_page_ids = [wc_file['id'] for wc_file in data]

    if num_files == 1:
        wc_page_ids = wc_page_ids[0]

    return wc_page_ids

#
# Function to map WikiMedia Commons uploads to their corresponding WikiData Entities
#

def get_q_number(wc_page_id):
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
        return None

    data_statements = data['entities'][wb_entity_id]['statements']

    # Check if 'P180' (depicts) property exists
    if 'P180' not in data_statements or not data_statements['P180']:
        return 0

    # Assuming 'P180' exists and has at least one entry
    depicts = data_statements['P180'][0]

    # Extract relevant information pertaining to the `Depicts` statement
    depicts_data = depicts['mainsnak']

    # Check if 'datavalue' key exists in depicts_data
    if depicts_data and 'datavalue' in depicts_data and 'value' in depicts_data['datavalue']:
        wd_item = depicts_data['datavalue']['value']
        wd_item_id = wd_item['id']
        return wd_item_id
    else:
        return None

    # Extract the WikiData Item ID Corresponding to the original Commons File
    wd_item_id = wd_item['id']

    return wd_item_id

def get_wikidata_label(wd_item_id):
    api_url = 'https://www.wikidata.org/w/api.php'
    api_params = {
        'action': 'wbgetentities',
        'ids': wd_item_id,
        'format': 'json',
        'props': 'labels',
        'languages': 'en'
    }

    r = requests.get(api_url, api_params)
    data = r.json()

    if 'entities' in data and wd_item_id in data['entities'] and 'labels' in data['entities'][wd_item_id] and 'en' in data['entities'][wd_item_id]['labels']:
        label = data['entities'][wd_item_id]['labels']['en']['value']
    else:
        return None

    return label

def get_wikidata_description(wd_item_id):
    api_url = 'https://www.wikidata.org/w/api.php'
    api_params = {
        'action': 'wbgetentities',
        'ids': wd_item_id,
        'format': 'json',
        'props': 'descriptions',
        'languages': 'en'
    }

    r = requests.get(api_url, api_params)
    data = r.json()

    if 'entities' in data and wd_item_id in data['entities'] and 'descriptions' in data['entities'][wd_item_id] and 'en' in data['entities'][wd_item_id]['descriptions']:
        description = data['entities'][wd_item_id]['descriptions']['en']['value']
    else:
        return None

    return description

def get_wikidata_object_name(wd_item_id):
    api_url = 'https://www.wikidata.org/w/api.php'
    api_params = {
        'action': 'wbgetentities',
        'ids': wd_item_id,
        'format': 'json',
        'props': 'labels',
        'languages': 'en'
    }

    r = requests.get(api_url, api_params)
    data = r.json()

    if 'entities' in data and wd_item_id in data['entities'] and 'labels' in data['entities'][wd_item_id] and 'en' in data['entities'][wd_item_id]['labels']:
        object_name = data['entities'][wd_item_id]['labels']['en']['value']
    else:
        return None

    return object_name

def get_wikidata_categories(wd_item_id):
    api_url = 'https://www.wikidata.org/w/api.php'
    api_params = {
        'action': 'wbgetentities',
        'ids': wd_item_id,
        'format': 'json',
        'props': 'claims',
        'languages': 'en'
    }

    r = requests.get(api_url, api_params)
    data = r.json()

    if 'entities' in data and wd_item_id in data['entities'] and 'claims' in data['entities'][wd_item_id] and 'P373' in data['entities'][wd_item_id]['claims']:
        categories = [claim['mainsnak']['datavalue']['value'] for claim in data['entities'][wd_item_id]['claims']['P373']]
    else:
        return None

    return categories

#
# Define function that will construct a convenient dataframe by repeatedly making calls to the wiki commons/data APIs
# until a sufficiently large data set has been collected.
# • Note that the number of calls ≥ number of rows in returned dataframe
# • To create a CSV containing the returned dataframe:
#       df = siki_wiki(25);
#       df.to_csv('df_wiki.csv');
#

def siki_wiki(row_count_wanted):
    df_wiki = pd.DataFrame({'file_name': [], 'wiki_commons_id': [], 'wiki_data_id': [], 'depicts': [], 'description': [], 'object_name': [], 'categories': []})

    df_row_count = 0
    enough_rows = False

    while not enough_rows:
        row = {'file_name': '', 'wiki_commons_id': '', 'wiki_data_id': '', 'depicts': '', 'description': '', 'object_name': '', 'categories': ''}
        wc_page_ids = get_random_commons_ids(25)

        for wc_page_id in wc_page_ids:
            wd_q_number = get_q_number(wc_page_id)
            if wd_q_number != 0:
                wd_depicts_statement = get_wikidata_label(wd_q_number)
                if wd_depicts_statement:
                    wd_description = get_wikidata_description(wd_q_number)
                    wd_object_name = get_wikidata_object_name(wd_q_number)
                    wd_categories = get_wikidata_categories(wd_q_number)
                    if wd_description:
                        row['file_name'] = f'File:{wc_page_id}.jpg'  # Assuming JPG format for simplicity
                        row['wiki_commons_id'] = wc_page_id
                        row['wiki_data_id'] = wd_q_number
                        row['depicts'] = wd_depicts_statement
                        row['description'] = wd_description
                        row['object_name'] = wd_object_name if wd_object_name else 'NA'
                        row['categories'] = wd_categories if wd_categories else 'NA'

                        df_row = pd.DataFrame.from_dict(row, orient='index').T
                        df_wiki = pd.concat([df_wiki, df_row], ignore_index=True)

                        df_row_count = df_wiki.shape[0]
                        if df_row_count%10==0:
                            print(df_row_count)

                        if df_row_count >= row_count_wanted:
                            enough_rows = True
                            break

    return df_wiki

# Example usage:
df = siki_wiki(1000)
df.to_csv('raw_data_1.csv')