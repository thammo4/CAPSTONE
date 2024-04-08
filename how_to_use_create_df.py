# Ensure that the wikifreak.py function is in your working directory (mac: ls | grep wikifreak)

from wikifreak import *

print('EXAMPLES - WIKIFREAK DATAFRAMES');

#
# EXAMPLES - HOW TO CREATE DATAFRAME WITH WIKIMEDIA_COMMONS_ID, WIKIDATA_ID (Q#), DEPICTS LABEL
#

#
# 1. Create a dataframe with 15 rows from wikimedia commons along with all of their associated wikidata Q#s and depicts labels.
#

sam_bankman_fried = create_df(15, verbose=False);
print(f'\nSBF DATAFRAME\n {sam_bankman_fried}');
print('-------');


#
# 2. Create a dataframe with 25 rows from wikimedia commons and their wikidata Q#s and depicts labels.
# 		• Note - if you accidentally include or forget to include the `.csv` file handler, the create_df function has you covered either way
#

bernie_madoff = create_df(25, verbose=False, csv_name='example_wiki_data');
print(f'\nMADOFF DATAFRAME\n {bernie_madoff}');
print('--------');


#
# 3. Create a dataframe with 5 rows from wikimedia commons, their corresponding Q#s, and depicts statements.
# 		• Set argumemt `verbose=True` to print the contents of the dataframe-to-be-returned after each new row is added
# 		• Do not output a csv document
#

allen_stanford = create_df(5, verbose=True);
print(f'\nSTANFORD DATAFRAME\n {allen_stanford}');
print('----------');



