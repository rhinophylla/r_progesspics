import pandas_profiling
import pandas as pd
import datetime as dt
import re
import matplotlib.pyplot as plt

# function to process title column and extract sex, age, height, and weights
def get_stats_ver6(s):
    clean_s = s.upper()
    #print(clean_s)
    clean_list = clean_s.split("/")
    if len(clean_list) < 3:
        return "unknown", "unknown", "unknown", "unknown"
    sex = clean_list[0].replace(' ', '')
    age = clean_list[1].replace(' ', '')
    weight_list = clean_list[2].split("[")
    height = weight_list[0].replace(' ', '')
    try:
        weights = weight_list[1]
    except:
        weight_list2 = weight_list[0].split("(")
        height = weight_list2[0].replace(' ', '')
        try:
            weights = weight_list2[1]
        except:
            weights = "unknown"
    if weights == "unknown":
        try:
            weights = clean_list[3]
        except:
            weights = "unknown"
    return sex, age, height, weights

def get_weights_ver2(s):
    stats = {}
    clean_s = s.upper().lstrip().replace(' ', '')
    regex = re.compile(r"^(?:\D*?)(\d+)(?:\D*?)(\d+)")
    result = regex.search(clean_s)
    if result:
        #print((result.groups()))
        return result.group(1), result.group(2)
    else:
        return "unknown", "unknown"


# clean sex processes the sex column and returns M, F or unknown if the sex column contains an age (2 digits) and cannot be processed
def clean_sex(s):
    if s.isdigit():
        return "unknown"
    try:
        if s[0] == "M" or s[0] == "F":
            return s[0]
    except IndexError:
        return "error"
    else:
        return s[-1]

# Strip out all non digit characters leaving behind just the numbers
def number_height(s):
    chars = list(s)
    digit_chars = [c for c in chars if c.isdigit()]
    number_s = "".join(digit_chars)
    return number_s

# Measurements in feet will start with 3, 4, 5, while measurements in cm will start with 1.  The function below converts num_height to the height in inches.

def height_inches(s):
    ft_list = ["4", "5", "6", "7"]
    if s == '':
        return "unknown"
    elif s[0] == "1":
        return int(s) * 0.39370079
    elif s[0] in ft_list:
        if len(s) == 1:
            return int(s) *12
        elif len(s) == 3 and s[2] == "5":
            return  (int(s[0]) * 12) + int(s[1]) + 0.5
        else:
            return (int(s[0]) * 12) + int(s[1:])
    else:
        return "unknown"

def nsfw(s):
    upper_s = s.upper()
    if "NSFW" in upper_s:
        return 1
    else:
        return 0

def get_duration_weeks(s):
    clean_s = s.lower().replace(' ', '')
    #print(clean_s)
    regex1 = re.compile(r"(\d+)(day|week|month|year)")
    regex2 = re.compile(r"(\d\.\d+)(day|week|month|year)")
    result2 = regex2.search(clean_s)
    try:
        duration2 = result2.group(1)
    except:
        result = regex1.search(clean_s)
        try:
            duration = result.group(1)
        except:
            return "unknown"
        unit = result.group(2)
        return duration_in_weeks(duration, unit)

    unit2 = result2.group(2)
    return duration_in_weeks(duration2, unit2)

def duration_in_weeks(period, unit):
    if unit.lower()[0] == 'd':
        return float(period)/7
    elif unit.lower()[0] == 'w':
        return float(period)
    elif unit.lower()[0] == "m":
        return float(period) * 4
    elif unit.lower()[0] == 'y':
        return float(period) * 52
    else:
        return "unknown"

def get_duration_months(s):
    clean_s = s.lower().replace(' ', '')
    #print(clean_s)
    regex1 = re.compile(r"(\d+)(day|week|month|year)")
    regex2 = re.compile(r"(\d\.\d+)(day|week|month|year)")
    result2 = regex2.search(clean_s)
    try:
        duration2 = result2.group(1)
    except:
        result = regex1.search(clean_s)
        try:
            duration = result.group(1)
        except:
            return "unknown"
        unit = result.group(2)
        return duration_in_months(duration, unit)

    unit2 = result2.group(2)
    return duration_in_months(duration2, unit2)

def duration_in_months(period, unit):
    if unit.lower()[0] == "d":
        return float(period)/30
    elif unit.lower()[0] == 'w':
        return float(period) * 4
    elif unit.lower()[0] == "m":
        return float(period)
    elif unit.lower()[0] == 'y':
        return float(period) * 12
    else:
        return "unknown"
