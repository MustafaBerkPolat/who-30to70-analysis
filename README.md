# Analysis of Probability of Dying Between Ages 30 and 70 From CVD, Cancer, Diabetes or CRD 

## Overview

The Global Health Observatory, operating under World Health Organization, keeps track of probability that an individual dies of cardiovascular disease, cancer, chronic respiratory disease or diabetes inbetween ages of 30 and 70, for each year from 2000 to 2021. 
To supplement this data, WHO also tracks the existence of evidence-based national guidelines, protocols, standards for the management of these health issues. To form an analysis of risk of death from these conditions 
this data is compared to the income group categorizing and per-capita GDP of these countries over the same year, available in the World Bank Group website.

## Takeaways
  - GDP is positively correlated with survival for the most part, as countries with higher GDP tend to have lower death probabilities. This is not a very strong correlation for lower GDPs as there are many factors at play, with plenty of outliers.
  - Death probability from these illnesses has only gone down in time, for all income groups.
  - The existence of guidelines for a particular disease seems to improve survival rates anywhere between 2 to 4 point percent (10 to 25 percent relative to the probabilities)
  - There is a considerable disparity between death probabilities of countries with guidelines for all 4 diseases, but the sample size for countries that only partially have disease guidelines is small, so analyzing by guideline count on a total scale as opposed to per-guideline may not be very reliable

## Data Used

The datasets used for this analysis are as follows:
  - [GDP per capita, normalized to current year USD (available under license CC BY-4.0)](https://databank.worldbank.org/source/world-development-indicators/preview/on)
  - [Probability of dying between age 30 and exact age 70 from any of cardiovascular disease, cancer, diabetes, or chronic respiratory disease](https://www.who.int/data/gho/data/indicators/indicator-details/GHO/probability-(-)-of-dying-between-age-30-and-exact-age-70-from-any-of-cardiovascular-disease-cancer-diabetes-or-chronic-respiratory-disease)
  - [Existence of evidence-based national guidelines/protocols/standards for the management of cardiovascular diseases](https://www.who.int/data/gho/data/indicators/indicator-details/GHO/existence-of-evidence-based-national-guidelines-protocols-standards-for-the-management-of-cardiovascular-diseases)
  - [Existence of evidence-based national guidelines/protocols/standards for the management of cancer](https://www.who.int/data/gho/data/indicators/indicator-details/GHO/existence-of-evidence-based-national-guidelines-protocols-standards-for-the-management-of-cancer)
  - [Existence of evidence-based national guidelines/protocols/standards for the management of diabetes](https://www.who.int/data/gho/data/indicators/indicator-details/GHO/existence-of-evidence-based-national-guidelines-protocols-standards-for-the-management-of-diabetes)
  - [Existence of evidence-based national guidelines/protocols/standards for the management of chronic respiratory diseases](https://www.who.int/data/gho/data/indicators/indicator-details/GHO/existence-of-evidence-based-national-guidelines-protocols-standards-for-the-management-of-chronic-respiratory-diseases)

## Data Processing and Analysis

### Python Work
(Everything done in Python is described in better detail inside the script and notebook files. The notebook file serves as the combined version of all .PY script files for conveniece)
The data kept by these organizations is fairly clean, with no significant requirement for additional cleaning. Most of the work done is to make sure they're in a compatible format to be easier to work with in Power BI. The first
step is to download the health-related data directly from the [Global Health Observatory's OData API](https://ghoapi.azureedge.net/api). These files are in JSON format, so they are parsed using Pandas' json_normalize function to be compatible with the DataFrame format.
This data contains columns designed to identify what the values stored in each JSON represents, as this API contains a wide variety of information all stored in the same forat, so identifiers are dropped to avoid redundancy in data as everything we work with is in the same format.
Then the column labels for these dataframes are adjusted to be humanly readable, and then a table for 3-letter country codes and their corresponding names are mined from the IBAN website using BeautifulSoup to add to our dataframes.

Downloading the World Bank's income grouping and GDP per capita data from their website, we add the information from the first dataset into our probability dataframe using left merge, and information from the second dataset using outer merge.
World Bank's website does not permit bot downloads outside of their official APIs, so a spoofed user-agent is needed to have the permission to download the first file. 
After the cleaning and merging work, we have two separate CSV files. The first stores whether a country has evidence-based naitonal guidelines, protocols or standards for the management of aforementioned health issues measured at 2021, while the second stores the probability that an individual dies of these health issues between 30 and 70.
The second file also contains GDP information and tracks these data between the years 2000 and 2021

### Power BI Work
**The PBIX file for this work can be found inside the files for this project**

The final prepared data is imported into Power BI, and visualized with six different pages. The slicers in the last two pages allow multiple years or countries to be checked simultaneously by holding Control while selecting additional entries.

The first page covers the probability of death as it changes over the years between 2000 and 2021, categorized by World Bank income groups. To the left side of the page there are four filters for the existence of evidence-based guidelines for each individual health problem to filter these graphs.
![Probability by World Bank Income Groups Per Year (2000-2021)](https://github.com/user-attachments/assets/b7164abd-aa52-4903-aab7-2660e72c8624)

The second page covers the average probability for countries grouped by whether they have guidelines or not.
![Probabilities by Individual Guidelines ](https://github.com/user-attachments/assets/1ba36d82-ada0-4237-8ef7-80c44897af3d)

The third page covers the average probability based on how many of these diseases a country has guidelines for.
![Probabilities by Guideline Count](https://github.com/user-attachments/assets/b329f20f-56de-4f80-b450-f00f243f6ce7)

The fourth page covers the probability, GDP and income groups of countries globally on a map.
![Probabilities by Country](https://github.com/user-attachments/assets/3192647c-1b10-4faa-a39d-c8e78f55efe8)

The fifth page covers the correlation between GDP and probability of death and contains a slider to show data for specific years, with the default set to show 2000 and 2021
![Probability by GDP per Year](https://github.com/user-attachments/assets/059ad8d3-1c72-4191-a310-af4eea757140)

The final page covers the change in the probability of death over time for individual countries.
![Probability over Years per Country](https://github.com/user-attachments/assets/2ecad38f-42ee-46bc-b8ec-0d06f507b8a3)

