import pandas as pd
import os
import requests
import urllib.request
import numpy as np
from bs4 import BeautifulSoup

##############################################################

api_link = 'https://ghoapi.azureedge.net/api/'
json_folder = r'C:\Users\mpola\OneDrive\Desktop\Career\Proje\World Health Organization Global Health Observatory\jsons'

if not os.path.exists(json_folder):
    os.makedirs(json_folder)

csv_folder = r'C:\Users\mpola\OneDrive\Desktop\Career\Proje\World Health Organization Global Health Observatory\csv'

if not os.path.exists(csv_folder):
    os.makedirs(csv_folder)

### Downloading and processing data

# The first step is to retrieve the data available in the WHO website. Here, data is available to both download directly as csv files 
# and as json files via GHO OData API. For API downloading, we need to identify the indicator codes for the data we want in the
# 'https://ghoapi.azureedge.net/api/Indicator' page, and for this project we will be focusing on the impact
# evidence-based national guidelines/protocols/standards for the management has on probability of dying between ages 30 and 70 
# from any of cardiovascular disease, cancer, diabetes, or chronic respiratory disease

# After some manual searching, we identify the following codes as relevant to us:

indicators_list = ['NCDMORT3070', 'NCD_CCS_CRD_GUIDE', 'NCD_CCS_CANCER_GUIDE', 'NCD_CCS_DIAB_GUIDE', 'NCD_CCS_CVD_GUIDE']

for index, indicator in enumerate(indicators_list):
    file_link = api_link + indicator
    filename = json_folder + '\\' + indicator + '.json'
    
    urllib.request.urlretrieve(file_link, filename)


##############################################################


# Since the data retrieved is in json format, we will need to do a bit of manual work to convert it to a csv formant
# to be usable in BI tools like Tableau and Power BI

json_list = os.listdir(json_folder)
csv_list = []

for index, json in enumerate(json_list):
    temp_folder = json_folder + '\\' + json
    temp_json = pd.read_json(temp_folder)

    # These json files have an OData context line that does not help with our analysis, so we can drop this part without issue
    # after which we can use Pandas' json_normalize function to convert the json into a csv format with no issue
    
    csv_list.append(pd.json_normalize(temp_json['value']))


##############################################################


# The json format used in the website has entries that are not used for all indicators, and what some entries represent varies based
# on indicator. In this case, for example, Dim2 represents age groups in our first data set but this data is not segmented based on age
# groups, so for all countries this entry is simply "AGEGROUP_YEARS30-69" which tells us nothing, but for other datasets Dim2 represents the 
# death probability for the same age group, so it is a float value and a min-max window. We can drop columns that have no variation
# as they provide no information we cannot glean from other columns

for index, csv in enumerate(csv_list):

    for col in csv.columns:
        if len(csv[col].unique()) == 1:
            csv_list[index].drop(col,inplace=True,axis=1)


##############################################################


# Renaming some of the columns and string values to be more humanly readable

for index, csv in enumerate(csv_list):
    csv_list[index] = csv.rename({
        'SpatialDim': 'Spatial Dimension',
        'SpatialDimType': 'Spatial Dimension Type',
        'ParentLocation': 'Continent',
        'TimeDim': 'Year',
        'Dim1': 'Gender',
        'NumericValue': 'Probability'
        }, axis='columns').replace({
        'SEX_FMLE': 'Female',
        'SEX_BTSX': 'Both Sexes',
        'SEX_MLE': 'Male'})    


##############################################################


# At this point we have the spatial dimension column which, depending on type, contains countries as 3-letter codes,
# groups based on WHO regions or groups based on World Bank Income classifications. While the latter two are not hard to
# manually parse and adjust, as there are nearly 200 countries on the world it makes sense to use Python to find the
# corresponding countries. To that end, we use BeautifulSoup to extract the country code table from the IBAN website

iban_link = 'https://www.iban.com/country-codes'
iban_page = requests.get(iban_link)
# iban_page.raise_for_status()

soup = BeautifulSoup(iban_page.content, "html.parser")

rows = soup.find_all('tr')
iban_table = []
for row in rows:
    cols = row.find_all('td')
    cols = [x.text.strip() for x in cols]
    iban_table.append([x for x in cols if x])

iban_df = pd.DataFrame(iban_table, columns = ['Country', '2-Letter Code', '3-Letter Code', 'Numeric Code']).dropna()


for index, csv in enumerate(csv_list):
    csv_list[index]['Country Code'] = csv_list[index].loc[:, 'Spatial Dimension']
    csv_list[index]['Spatial Dimension'] = csv_list[index]['Spatial Dimension'].replace(
        to_replace = iban_df['3-Letter Code'].unique(),
        value = iban_df['Country'].unique()
    )


##############################################################



# Renaming the region names manually to be easier to read

manual_names = ['WHO European Region',
                'High Income Region',
                'WHO Eastern Mediterranian Region',
                'WHO Western Pacific Region',
                'WHO African Region',
                'Low Income Region',
                'Global',
                'WHO Region of the Americas',
                'Upper-Midle Income Region',
                'WHO South-East Asia Region',
                'Lower-Middle Income Region']

for index, csv in enumerate(csv_list):
    csv_list[index]['Spatial Dimension'] = csv_list[index]['Spatial Dimension'].replace(
        to_replace = manual_codes,
        value = manual_names
    )


##############################################################


# Even though our first dataframe, the probability frame, differs from the rest greatly, our other 4 frames follow the same format
# and make sense to be joined after some adjustments so that there are no redundant columns

col_names = ['Probability (Range)',
             'Has Chronic Respiratory Disease Guidelines?',
             'Has Cancer Guidelines?',
             'Has Diabetes Guidelines?',
             'Has Cardiovascular Disease Guidelines?']

# Renaming the columns to be both readable and to keep the different informations stored in the Value column seaparte after merging

for index, csv in enumerate(csv_list):
    csv_list[index] = csv.rename(columns={'Value': col_names[index]})

df_guidelines = pd.DataFrame(csv_list[1])

for index, csv in enumerate(csv_list):
    if index >= 2:
        df_guidelines = df_guidelines.merge(csv.set_index('Spatial Dimension')[col_names[index]], on='Spatial Dimension')

# Dividing the values in the Probability, Low and High columns of our probability dataframe since they represent percentages, 
# in order to make them consistent in Power BI

csv_list[0]['Probability'] = csv_list[0]['Probability']/100
csv_list[0]['Low'] = csv_list[0]['Low']/100
csv_list[0]['High'] = csv_list[0]['High']/100


##############################################################


# While this dataset has rows about income group aggregates, it does not have any data regarding which countries are in
# which group, so we are more limited when it comes to income-based analysis. To that end, we can directly
# retrieve this information from World Bank and append it to our existing dataframe

# wbi_index_link = 'https://datahelpdesk.worldbank.org/knowledgebase/articles/906519-world-bank-country-and-lending-groups'

# Here, using BeautifulSoup to extract the tables would be a decent approach, but these countries are listed by name formatted for
# their native language (for example, what is defined as "Turkey" in the WHO database is "Türkiye" in the World Bank
# website. So instead, we need to find the corresponding 3-letter code, which is available in the xlsx file available
# in the same link
wbi_xlsx = 'https://datacatalogapi.worldbank.org/ddhxext/ResourceDownload?resource_unique_id=DR0090755'

opener = urllib.request.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0')]
urllib.request.install_opener(opener)
urllib.request.urlretrieve(wbi_xlsx, f'{csv_folder}\\wbi_index.xlsx')

# Reading the CSV storing the group info

df_wbi = pd.read_excel(f'{csv_folder}\\wbi_index.xlsx')


##############################################################


# Cleaning the probability dataframe using the data we have and cleaning the dataframes' rows and columns

df_probability = csv_list[0].merge(df_wbi, left_on='Country Code', right_on='Code', how='left')

df_probability.drop(labels=['Id', 'Date', 'TimeDimensionBegin', 'TimeDimensionEnd', 'TimeDimensionValue', 'Code', 'Economy'], axis=1, inplace=True)
df_guidelines.drop(labels=['Id', 'Date'], axis=1, inplace=True)


##############################################################


# In order to help derive further insight from the death probability data, it makes sense to compare it to per capita GDP, given
# that the WHO database only contains the World Bank Income grouping info which is not very comprehensive

# To that end, we can retrieve this data from the World Bank website in CSV format, but the structuring for this CSV file is
# very unorthodox and will require some restructuring to work better with our WHO data

# The data is available from the link below under the license CC BY-4.0
# https://databank.worldbank.org/source/world-development-indicators/preview/on

# License URL:
# https://datacatalog.worldbank.org/public-licenses#cc-by

gdp_folder = csv_folder + r'\wbi_gdp'
files_list = os.listdir(gdp_folder)

df = []
for csv in files_list:
    df_temp = pd.read_csv(f'{gdp_folder}\\{csv}', encoding='cp1252')
    df.append(df_temp)


##############################################################


# Our first step in restructuring is to omit the unnecessary rows. This dataframe has a few rows that explain its licensing,
# aggregation method and license URL etc. which serve no purpose for our analaysis and actually make it harder to convert and process
# rows and colums that contain useful info, so we start out by stripping every row that doesn't have the series code 'NY.GDP.PCAP.CD'
# which represent per capita GDP, the data we requested from the website for this analysis.

df[1]= df[1][df[1]['Series Code'].isin(['NY.GDP.PCAP.CD'])]


##############################################################


# The next step is to use the melt function to turn the structure from having one row per country with yearly GDPs on different columns,
# into multiple rows per country, one for each year, to match our WHO data's format

df_gdp = df[1].melt(id_vars=['Country Name', 'Country Code'], value_vars=['2000 [YR2000]', '2001 [YR2001]', '2002 [YR2002]', '2003 [YR2003]',
       '2004 [YR2004]', '2005 [YR2005]', '2006 [YR2006]', '2007 [YR2007]',
       '2008 [YR2008]', '2009 [YR2009]', '2010 [YR2010]', '2011 [YR2011]',
       '2012 [YR2012]', '2013 [YR2013]', '2014 [YR2014]', '2015 [YR2015]',
       '2016 [YR2016]', '2017 [YR2017]', '2018 [YR2018]', '2019 [YR2019]',
       '2020 [YR2020]', '2021 [YR2021]', '2022 [YR2022]', '2023 [YR2023]'])


##############################################################


# Renaming the columns to be easier to interpret
df_gdp.rename(columns={
    'value' : 'GDP', 
    'variable' : 'Year'}, inplace=True)

# Dropping every row that doesn't contain GDP data
df_gdp.dropna(subset='GDP', inplace=True)

# Turning our GDP column into a numeric value
df_gdp['GDP'] = pd.to_numeric(df_gdp['GDP'])
df_gdp['GDP'] = df_gdp['GDP'].astype(int)

# Stripping the unnecessary characters from the Year column and turning to integer
df_gdp['Year'] = df_gdp['Year'].str[:4].astype(int)


##############################################################


# Merging the probability and GDP dataframes into one dataframe and dropping rows that don't contain probability data

merged_df = pd.merge(df_probability, df_gdp, on=['Year', 'Country Code'], how='outer')

merged_df.dropna(subset='Probability', inplace=True)


##############################################################


# Saving the final dataframes as csv to use in Power BI

merged_df.to_csv(f'{csv_folder}\\df_probability.csv', index=False)
df_guidelines.to_csv(f'{csv_folder}\\df_guidelines.csv', index=False)