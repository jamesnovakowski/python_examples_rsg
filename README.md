# python_examples_rsg

The files contained in this folder are some efforts at data manipulation and automated data quality assessment using Python.

The referenced data files have been excluded.

###Google Directions Output Compare_UTA_TEST.py
This script was used to automatically assess the quality of survey data.
The collected data represents a survey respondent's path through a transit system.
The path data was then compared with all possible Google Directions trip paths from the respondent Origin to Destination, and a quality assessment was provided on how closely the survey trip path matched with the Google Directions output.

The purpose of the script was to pre-screen the survey data in order to focus cleaning efforts on high-quality records, and expand cleaning efforst to low-quality records as resources permitted.

### Process_Transit-Path_Cleaned_Data UTA - Post Direction Assignment-UPDATED.py
This script matches survey trip data to the shapefile library, and ensures that survey data can be matched to the shapefile.

###Stop Snapping - Post-Direction Assignment.py
This script further cleans the trip data by ensuring reported boarding and alighting locations reported in the survey data match up with a bus or train stop.
