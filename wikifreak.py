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
# Function to map WikiMedia Commons uploads to their corresponding WikiData Entities (Q#s)
#

def get_q_numbers (wc_page_id, verbose=False):
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
        return [];

    data_statements = data['entities'][wb_entity_id]['statements']

    # Check if 'P180' (depicts) property exists
    if 'P180' not in data_statements or not data_statements['P180']:
        print(f"No 'depicts' statements for Wikimedia Commons Page ID: {wc_page_id}")
        return [];

    # Isolate depicts with the `depicts` property value
    depicts = data_statements['P180'];

    q_numbers = [];
    for x in range(len(depicts)):
        depicts_data = depicts[x]['mainsnak'];
        wd_item = depicts_data['datavalue']['value'];
        wd_item_id = wd_item['id'];
        q_numbers.append(wd_item_id);

    if verbose:
        print(f'Commons Page ID:{wc_page_id} -> Depicts:{q_numbers}');

    return q_numbers;


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
        print(f'No depicts label found for {wd_item_id}');
        return None;

    return label;


#
# Define function that will construct a convenient dataframe by repeatedly making calls to the wiki commons/data APIs
# until a sufficiently large data set has been collected.
# • Note that the number of calls ≥ number of rows in returned dataframe
# • To create a CSV containing the returned dataframe:
#       df = create_df(25);
#       df.to_csv('df_wiki.csv');
#
#
# >>> df = create_df(10, verbose=False, csv_name='wahoo_for_you.csv')
#   wiki_commons_id                                      wiki_data_q                                            depicts
# 0       132900617               [Q22698, Q188509, Q34442, Q967166]                        [park, suburb, road, Hythe]
# 1       116975754  [Q11451, Q1006733, Q1639395, Q30121, Q16542738]  [agriculture, grassland, bridle path, pasture,...
# 2       146501368                                           [Q525]                                              [Sun]
# 3        20439034                               [Q836934, Q448018]                             [cheongsam, Hiro Saga]
# 4       110956109                                      [Q20204357]                            [St. Ägidius (Grafing)]
# 5       130031795                 [Q1081138, Q105889895, Q1894394]         [historic site, religious site, Martinhoe]
# 6       108706552                              [Q1468524, Q179351]                 [city center, City of Westminster]
# 7       106966797                       [Q1311670, Q12280, Q29245]            [rail infrastructure, bridge, Hastings]
# 8        55368967                                      [Q38284967]                           [Aqueduct of Agia Irini]
# 9        23636550                                      [Q17404929]                           [Kerkstraat 14, Leveroy]

def create_df (row_count_wanted, verbose=False, csv_name=''):
    '''
        Parameters:
            • row_count_wanted [int]: Specify the desired number of rows for the resulting dataframe to contain.
            • verbose [bool]: Print the dataframe each time we add a new row as it is being built.
            • csv_name [str]: Create a csv file named `csv_name` with the depicts dataframe.
        Notes:
            • It's possible that the number of elements in the `wiki_data_q` column might not equal the number of elements in the corresponding `depicts` column (?)
        Example Call:
            • df = create_df(10, verbose=False, csv_name='example_call')
    '''
    df_wiki = pd.DataFrame({'wiki_commons_id':[], 'wiki_data_q':[], 'depicts':[]});

    df_row_count = 0;
    enough_rows = False;

    while not enough_rows:
        row = {'wiki_commons_id':'', 'wiki_data_q':'', 'depicts':''};
        wc_page_ids = get_random_commons_ids(10*row_count_wanted); print(f'\nTrying Commons ID Batch:\n{wc_page_ids}');

        for wc_page_id in wc_page_ids:
            q_numbers = get_q_numbers(wc_page_id);
            if q_numbers:
                wd_depicts_statements = [get_wikidata_label(x) for x in q_numbers];

                if wd_depicts_statements:
                    row['wiki_commons_id']  = wc_page_id;
                    row['wiki_data_q']      = q_numbers;
                    row['depicts']          = wd_depicts_statements;

                    if verbose:
                        print(f'Row: {row}');

                    df_row = pd.DataFrame.from_dict(row, orient='index').T;

                    df_wiki = pd.concat([df_wiki, df_row], ignore_index=True);

                    if verbose:
                        print(f'Updated DataFrame:\n{df_wiki}');

                    df_row_count = df_wiki.shape[0];

                    if df_row_count >= row_count_wanted:
                        enough_rows = True;
                        break;

    #
    # If desired, create the csv file
    #

    if csv_name:
        # Add the file handle if the user forgot to specify
        if not csv_name.endswith('.csv'):
            csv_name = csv_name + '.csv';
        df_wiki.to_csv(csv_name, index=False);
    return df_wiki;






#
# Depicts Example 1: Marie Curie c. 1920s.jpg (https://commons.wikimedia.org/w/index.php?curid=61396200)
#

# Commons Page ID:61396200 -> WikiData Item ID:Q7186
wc_page_id = 61396200;
wd_item_id = get_q_numbers(wc_page_id);



#
# Depicts Example 2: German Sugar Cubes (https://commons.wikimedia.org/wiki/File:Würfelzucker_--_2018_--_3582.jpg)
#

# Commons Page ID:71048738 -> WikiData Item ID:Q1042920
wc_page_id = 71048738;
wd_item_id = get_q_numbers(wc_page_id);


#
# Example: Get Random File on Commons and Fetch Its Depicts Statements
# 	• Note: this might return an error if the random commons file does not have any depicts statements
#

wc_page_id = get_random_commons_ids(num_files=1);
wd_item_id = get_q_numbers(wc_page_id);