import pandas as pd
import datetime as dt
import re
import matplotlib.pyplot as plt


def get_stats_ver6(s):
    """Processes an r/progresspics post title and extracts the sex, age, height, and weights.  Returns "unknown" if the title is formatted incorrectly and the infomation cannot be extracted.

    Arguments:
    s -- r/procresspics post tittle; provide a string

    Returns:
    sex -- sex of r/progresspics post author
    age -- age of r/progresspics post author
    height -- height of r/progresspics post author
    weights -- starting and ending weight of r/progresspics post author
    """
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
    """Extracts the starting and ending weights from a string containing both weights. If the weights cannot be identified, returns "unknown".

    Arguments:
    s -- string containing both starting and ending weights

    Returns:
    starting weight -- starting weight of r/progresspics post author
    ending weight -- ending weight of r/progresspics post author
    """
    clean_s = s.upper().lstrip().replace(' ', '')
    regex = re.compile(r"^(?:\D*?)(\d+)(?:\D*?)(\d+)")
    result = regex.search(clean_s)
    if result:
        #print((result.groups()))
        return result.group(1), result.group(2)
    else:
        return "unknown", "unknown"


def clean_sex(s):
    """Processes the sex column and returns M or F.  Returns 'unknown' if the sex column contains an age (2 digits) and cannot be processed and 'error' if the input string is empty.

    Arguments:
    s -- string that contains the sex of the r/progresspics post author

    Returns:
    "M" or "F" indicating the sex of the author.
    """
    if s.isdigit():
        return "unknown"
    try:
        if s[0] == "M" or s[0] == "F":
            return s[0]
    except IndexError:
        return "error"
    else:
        return s[-1]


def number_height(s):
    """Strips out all non digit characters from a provided string.

    Arguments:
    s -- strings

    Returns:
    number_s -- string containing only the digits found in the original string
    """
    chars = list(s)
    digit_chars = [c for c in chars if c.isdigit()]
    number_s = "".join(digit_chars)
    return number_s


def height_inches(s):
    """Processes a string containing numbers corresponding to a height and returns the height in inches.  The starting heights are in either feet and inches or centimeters.  If the first character in the string is a 1, it is assumed the height is in centimeters.  If the first character is a 4, 5, 6, or 7 it is assumed the first character of the string corresponds the feet measurement and the remainder to inches measurement. Returns "unknown" if the string is empty or starts with character other than 1, 4, 5, 6, or 7.

    Arguments:
    s -- string of numbers representing a height

    Returns:
    integer representing a height in inches
    """
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
    """Recognizes the string "NSFW" within a larger string and returns 1 if it is present and 0 if it is not.

    Arguments:
    s -- string

    Returns:
    0 if "NSFW" is not present or 1 if "NSFW" is present.
    """
    upper_s = s.upper()
    if "NSFW" in upper_s:
        return 1
    else:
        return 0


def get_duration_weeks(s):
    """Recognizes the key words "day", "week", "month", or "year" within an input string and looks for a digit immediately proceeding the key word.  Applies the function duration_in_weeks to convert the identified period of time to the number of weeks it represents.  If no key words or preceding digit can be found, returns "unknown".

    Arguments:
    s -- string

    Returns:
    a float representing a number of weeks
    """
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
    """Given a number and unit of time, converts the time duration represented to the equivalent number of weeks.

    Arguments:
    period - string containing a digit
    unit - one of the following strings: "day", "week", "month", or "year"

    Returns:
    a float representing a number of weeks
    """
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
    """Recognizes the key words "day", "week", "month", or "year" within an input string and looks for a digit immediately proceeding the key word.  Applies the function duration_in_months to convert the identified period of time to the number of months it represents.  If no key words or preceding digit can be found, returns "unknown".

    Arguments:
    s -- string

    Returns:
    a float representing a number of months
    """
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
    """Given a number and unit of time, converts the time duration represented to the equivalent number of months.

    Arguments:
    period - string containing a digit
    unit - one of the following strings: "day", "week", "month", or "year"

    Returns:
    a float representing a number of months
    """
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
