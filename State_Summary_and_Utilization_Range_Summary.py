"""
Python script, Python v 2.7
written 1/30/17 by James Novakowski

This script was developed to summarize anonymized claims data for Radial
Analytics as part of a coding assessment.

To run the script, the script file should be in the same folder as the
data file, called "data.csv".

The script will generate an output csv file called "State_Level_Summary.csv",
which will provide a summary of claims data by state, gender, and age.

Note: The current implementation of this script leaves out data points
where the state is undefined, the gender is undefined, or the age is undefined.

The sript will also generate an output file called
"Claims_Utilization_Summary.csv", whcih will provide a summary of claims data
by the Utilization Range, providing the counts of claims and the percentage
of claims that fall into each range bucket.
"""

import csv

#Create data dictionary for state summary data
data = {}
state_code = range(1,67)
for item in range(97,100):
    state_code.append(item)

for state in state_code:
    data[state] = {"male":0,
                   "female":0,
                   "age_under_65":0,
                   "age_65_to_74":0,
                   "age_over_74":0,
                   "state":str(state)
                   }

#Create data dictionary for Utilization Range data 
util_days = {}
util_code = range(0,6)
for item in util_code:
    util_days[str(item)] = 0

util_days["6_to_10"] = 0
util_days["11_to_30"] = 0
util_days["over_30"] = 0


"""
Read the data from the csv file to a dictionary.
Note: Current implementation ignores values 0: Unknown
in Gender and Age fields.

Then: Summarize the data.

Data fields coded as follows:

Gender Code from Claim
0 = Unknown
1 = Male
2 = Female

LDS Age Category
0 = Unknown
1 = <65
2 = 65 Thru 69
3 = 70 Thru 74
4 = 75 Thru 79
5 = 80 Thru 84
6 = >84

And want the following fields in the final tabulation:
State
Gender (male)
Gender (female)
Age (under 65)
Age (65-74)
Age (75 +)
"""

data_file = "data.csv"

f = open(data_file)
d = csv.DictReader(f)

for row in d:
    #print row
    age = int(row["LDS Age Category"])
    gender = int(row["Gender Code from Claim"])
    state = int(row["State Code from Claim (SSA)"])
    day_count = int(row["Claim Utilization Day Count"])
    
    #Read the data into the data nested dictionary

    if gender == 1:
        data[state]["male"] += 1
    elif gender == 2:
        data[state]["female"] += 1

    if age == 1:
        data[state]["age_under_65"] += 1
    elif age > 1 and age < 4:
        data[state]["age_65_to_74"] += 1
    elif age >= 4:
        data[state]["age_over_74"] += 1

    if day_count < 6:
        util_days[str(day_count)] += 1
    elif day_count >= 6 and day_count <= 10:
        util_days["6_to_10"] += 1
    elif day_count >= 11 and day_count <= 30:
        util_days["11_to_30"] += 1
    elif day_count > 30:
        util_days["over_30"] += 1
 
f.close()

"""
Generate an output csv file for the state claim summary data.
"""

with open("State_Level_Summary.csv", 'w') as csvfile:
    fieldnames = ['state',
                  'female',
                  'male',
                  'age_under_65',
                  'age_65_to_74',
                  'age_over_74']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writerow({'state':'State',
                     'female':'Female',
                     'male':'Male',
                     'age_under_65':'Ages < 65',
                     'age_65_to_74':'Ages 65-74',
                     'age_over_74':'Ages75+'
                     })
    for state in data:
        writer.writerow(data[state])

"""
Generate an output csv file for the utilization days summary data.
Also use this step to calculate the total claims, and the percentage
of claims falling into each utilization range bucket.
"""
total_claims = 0

for key, value in util_days.iteritems():
    total_claims += value

with open("Claims_Utilization_Summary.csv", 'w') as csvfile:
    fieldnames = ['Utilization Range',
                  'Counts',
                  'Percentages']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()

    for key, value in util_days.iteritems():
        
        if value > 0:
            percent = (value / float(total_claims)) * 100
            percent = round(percent, 2)
            percent = str(percent) + "%"
        else:
            percent = "0.00%"

        new_row = {'Utilization Range':key,
               'Counts':str(value),
               'Percentages':percent}
        writer.writerow(new_row)

    










