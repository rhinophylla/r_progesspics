'''
This script processes and extracts relavent features from r/progresspics post
titles then generates summary visualizations. A default dataset is included, though users can provide their own .cvs file. To run correctly, the .cvs file must include the following columns which are all available to download from Google's BigQuery:  'title', 'score', 'num_comments', 'author', 'timestamp'
'''
import os
import pandas as pd
import matplotlib.pyplot as plt
import src.features.pp_feature_building as feat
import numpy as np
import time
import logging


# Set up logging
# Create custom logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Create handlers
ch = logging.StreamHandler()
fh = logging.FileHandler('progresspics analysis.log', mode='w')
ch.setLevel(logging.INFO)
fh.setLevel(logging.INFO)

# Create formatters and add to handlers
c_format = logging.Formatter('%(message)s')
f_format = logging.Formatter('%(message)s')
ch.setFormatter(c_format)
fh.setFormatter(f_format)

logger.addHandler(ch)
logger.addHandler(fh)

logger.info("As this script runs, it will print status updates and key analysis points to the console as well as save them in a log file called progresspics_analysis.log for future reference. \n")

# Importing data from .csv file
logger.info("This script processes and extracts features from r/progresspics post titles, then generates summary visualizations. \n ")

file = input(str("Type a file path for .csv file you wish to process.  If '2018' is entered, the program will run using the included 2018 r/progresspics data.  "))

logger.info("Importing raw data. \n")
if file == "2018":
    pp_data = pd.read_csv("data/pp_data_2018_raw.csv")
else:
    pp_data = pd.read_csv(file)

logger.info("{} rows, {} columns imported. \n".format(pp_data.shape[0], pp_data.shape[1]))

# Extracting the raw sex, age, height, and weights from the title column
logger.info("Adding and populating the 'raw_sex', 'raw_age', 'raw_height', and 'raw_weights' columns.\n")

pp_data = pp_data.reindex(columns=['title', 'raw_sex', 'raw_age', 'raw_height', 'raw_weights', 'score', 'timestamp','id', 'num_comments', 'created_utc', 'author', 'permalink'])

pp_data[["raw_sex", "raw_age", "raw_height", "raw_weights"]] = pp_data.apply(lambda row: feat.get_stats_ver6(row["title"]), axis=1, result_type="expand")

pp_data = pp_data[pp_data["raw_height"] != 'unknown']
pp_data = pp_data[pp_data["raw_height"].str.len() <= 6]

logger.info("After removing rows with incorrectly formatted titles, {} rows remain. \n".format(pp_data.shape[0]))
time.sleep(5)

# Extracting the raw starting weights and ending weights from the raw_weight column
logger.info("Adding and populating the start_weight and end_weight columns. \n")

pp_data = pp_data.reindex(columns=['title', 'raw_sex', 'raw_age', 'raw_height', 'raw_weights', 'start_weight', 'end_weight','score','timestamp', 'id', 'num_comments', 'created_utc', 'author','permalink'])

pp_data[["start_weight", "end_weight"]] = pp_data.apply(lambda row: feat.get_weights_ver2(row["raw_weights"]), axis=1, result_type="expand")

pp_data = pp_data[pp_data['start_weight'] != 'unknown']

logger.info("After removing rows with incorrectly formatted weights, {} rows remain. \n".format(pp_data.shape[0]))
time.sleep(5)

# Cleaning the raw_sex column
logger.info("Cleaning the raw_sex column then adding the results to the new sex column. 0 is male and 1 is female. \n")

pp_data = pp_data.reindex(columns=['title', 'raw_sex', 'sex', 'raw_age', 'raw_height', 'raw_weights', 'start_weight', 'end_weight','score','timestamp', 'id', 'num_comments', 'created_utc', 'author','permalink'])

pp_data["sex"] = pp_data["raw_sex"].apply(feat.clean_sex)

sex_unknown = pp_data[pp_data["sex"] == 'unknown']
sex_unknown.columns = ['title', 'raw_age', 'sex', 'raw_sex', 'raw_height', 'raw_weights', 'start_weight', 'end_weight', 'score', 'timestamp', 'id', 'num_comments', 'created_utc', 'author', 'permalink']
sex_unknown.loc[:, "sex"] = sex_unknown.loc[:, "raw_sex"].apply(feat.clean_sex)
sex_unknown = sex_unknown.reindex(columns=['title', 'raw_sex', 'sex', 'raw_age', 'raw_height', 'raw_weights', 'start_weight', 'end_weight', 'score', 'timestamp', 'id', 'num_comments', 'created_utc', 'author', 'permalink'])
pp_data.update(sex_unknown)
pp_data = pp_data[(pp_data["sex"] == "M")|(pp_data["sex"] == "F")]

pp_data["sex"] = pp_data['sex'].apply(lambda s: 1 if s == "F" else 0)

logger.info("After removing rows where the sex could not be determined, {} rows remain. \n".format(pp_data.shape[0]))
time.sleep(5)

# Cleaning the raw_age column
logger.info("Cleaning the raw_age column.\n")

pattern = r"([0-9]{2})"
age_info = pp_data[(pp_data["raw_height"].str.match(pattern))&(pp_data["raw_height"].str.len() == 2)]

logger.info("Identified {} rows where the age is in the height column and vice versa. Fix by switching column names.\n".format(age_info.shape[0]))

age_info.columns = ['title', 'raw_height', 'raw_sex', 'sex', 'raw_age', 'raw_weights', 'start_weight', 'end_weight', 'score', 'timestamp', 'id', 'num_comments', 'created_utc', 'author', 'permalink']
pp_data.update(age_info)

pp_data = pp_data[pp_data["raw_age"].str.len() == 2]
pattern = r"(^[0-9]{2}?)"
pp_data = pp_data[pp_data["raw_age"].str.match(pattern)]
pp_data["raw_age"] = pd.to_numeric(pp_data["raw_age"], errors='coerce')

logger.info("After removing rows where raw_age did not contain a 2-digit integer, {} rows remain.\n".format(pp_data.shape[0]))
time.sleep(5)

# Cleaning the raw_height column
logger.info("Cleaning the raw_height column and storing height in inches in the new height_in column.\n")

pp_data["num_height"] = pp_data["raw_height"].apply(feat.number_height)
pp_data["height_in"] = pp_data["num_height"].apply(feat.height_inches)
pp_data.loc[:,"height_in"] = pd.to_numeric(pp_data["height_in"], errors='coerce')
pp_data = pp_data[(pp_data["height_in"] > 54) & (pp_data["height_in"] < 85)]

logger.info("After removing rows with incorrectly formatted height_in entries, {} rows remain.\n".format(pp_data.shape[0]))
time.sleep(5)

# Cleaning the weight columns
logger.info("Cleaning the start_weight and end_weight columns and storing the weights in pounds in the new_start_weight and new_end_weight columns.\n")

pp_data = pp_data.reindex(columns=['title', 'raw_age', 'raw_sex', 'sex', 'raw_height', 'num_height', 'height_in', 'raw_weights','start_weight', 'new_start_weight', 'end_weight', 'new_end_weight', 'score', 'timestamp', 'id',
'num_comments', 'created_utc', 'author', 'permalink', ], fill_value=0)

pp_data.shape
pp_data.loc[:,"start_weight"] = pd.to_numeric(pp_data["start_weight"], errors='coerce')
pp_data.loc[:,"end_weight"] = pd.to_numeric(pp_data["end_weight"], errors='coerce')

pattern = r"=\s*\d+\s*KG"
pp_data.loc[pp_data.title.str.contains(pattern, case=False), "new_start_weight"] = pp_data.loc[pp_data.title.str.contains(pattern, case=False), "start_weight"] * 2.20462
pp_data.loc[pp_data.title.str.contains(pattern, case=False), "new_end_weight"] = pp_data.loc[pp_data.title.str.contains(pattern, case=False), "end_weight"] * 2.20462

pp_data.loc[(pp_data.start_weight < 130) & pp_data.title.str.contains("kg", case=False) & (pp_data.new_start_weight == 0), "new_start_weight"] = pp_data.loc[(pp_data.start_weight < 130) & pp_data.title.str.contains("kg", case=False) & (pp_data.new_start_weight == 0), "start_weight"] * 2.20462
pp_data.loc[(pp_data.start_weight < 130) & pp_data.title.str.contains("kg", case=False) & (pp_data.new_end_weight == 0), "new_end_weight"] = pp_data.loc[(pp_data.start_weight < 130) & pp_data.title.str.contains("kg", case=False) & (pp_data.new_end_weight == 0), "end_weight"] * 2.20462

pp_data.loc[(pp_data.new_start_weight == 0), "new_start_weight"] = pp_data.loc[(pp_data.new_start_weight == 0), "start_weight"]
pp_data.loc[(pp_data.new_end_weight == 0), "new_end_weight"] = pp_data.loc[(pp_data.new_end_weight == 0), "end_weight"]

pp_data = pp_data[pp_data["new_start_weight"] <= 1000]
pp_data = pp_data[pp_data['new_end_weight'] >= 70]
pp_data = pp_data[pp_data['new_end_weight'] < 1000]

logger.info("After removing rows with incorrectly formatted start_weight or end_weight entries, {} rows remain.\n".format(pp_data.shape[0]))
time.sleep(5)

# Calculating the amount of weight gained or lost
logger.info("Calculating the amount of weight gained or lost and storing the results in the new weight_diff column. \n")

pp_data["weight_diff"] = pp_data["new_start_weight"] - pp_data["new_end_weight"]

pp_data = pp_data.reindex(columns=['title', 'raw_age', 'raw_sex', 'sex', 'raw_height', 'num_height', 'height_in', 'raw_weights', 'start_weight', 'new_start_weight', 'end_weight', 'new_end_weight', 'weight_diff', 'score', 'timestamp', 'id', 'num_comments', 'created_utc', 'author', 'permalink'])

pp_data = pp_data[pp_data['weight_diff'] >= -90]
pp_data = pp_data[pp_data['weight_diff'] < 599]

logger.info("After removing outlier weight_diff entries caused by r/progresspics user entry error, {} rows remain.\n".format(pp_data.shape[0]))
time.sleep(5)

# Adding date time columns
logger.info("After converting the timestamp to the datetime format, populate the following new columns:  month, year, day, dayofweek, date, time. \n")

pp_data["timestamp"] = pd.to_datetime(pp_data["timestamp"])

pp_data["month"] = pp_data["timestamp"].dt.month
pp_data["year"] = pp_data["timestamp"].dt.year
pp_data["day"] = pp_data["timestamp"].dt.day
pp_data["dayofweek"] = pp_data["timestamp"].dt.dayofweek
pp_data["date"] = pp_data["timestamp"].dt.date
pp_data["time"] = pp_data["timestamp"].dt.time

pp_data = pp_data.reindex(columns=['title', 'raw_age', 'sex', 'height_in', 'new_start_weight', 'new_end_weight', 'weight_diff', 'NSFW', 'num_posts', 'score', 'num_comments', 'timestamp', 'id', 'created_utc', 'author', 'permalink', 'month', 'year', 'day', 'dayofweek', 'date', 'time', 'raw_sex', 'raw_height', 'num_height', 'raw_weights', 'start_weight', 'end_weight'])

pp_data.columns = (['title', 'age', 'sex', 'height_in', 'start_weight', 'end_weight', 'weight_diff', 'NSFW', 'num_posts', 'score', 'num_comments', 'timestamp', 'id', 'created_utc', 'author', 'permalink', 'month', 'year', 'day', 'dayofweek', 'date', 'time', 'raw_sex', 'raw_height', 'num_height', 'raw_weights', 'raw_start_weight', 'raw_end_weight'])

logger.info("Reorder and rename some columns so that the names of the columns are easier to use. New column names and order: 'title', 'age', 'sex', 'height_in', 'start_weight', 'end_weight', 'weight_diff', 'score', 'timestamp', 'id', 'num_comments', 'created_utc', 'author', 'permalink', 'month', 'year', 'day', 'dayofweek', 'date', 'time', 'raw_sex', 'raw_height', 'num_height', 'raw_weights', 'raw_start_weight', 'raw_end_weight'\n")

pp_data.columns

time.sleep(5)

# Extract a (NSFW) not safe for work feature
logger.info("Extracting an NSFW feature.  A 1 in this column indicates that the title of the post contains the NSFW (not safe for work) acronym, while a 0 indicates that it did not. \n")

NSFW2 = pp_data[pp_data.title.str.contains("NSFW", case=False)]
pp_data["NSFW"] = pp_data["title"].apply(feat.nsfw)

time.sleep(5)

# Extract a multiple postings feature
logger.info("Extract a num_posts feature.  For each row, determine how many times the author posted to r/progresspics in 2018 and put that number to the num_posts column.\n")

pp_data["num_posts"] = pp_data.groupby(['author'])['sex'].transform('count')

author = pp_data[pp_data["author"] == "[deleted]"]
author.loc[:, "num_posts"] = 1
pp_data.update(author)

logger.info("{} rows have the author given as '[deleted]'. For those rows, set num_posts equal to 1.\n".format(author.shape[0]))
time.sleep(5)

logger.info("Currently, the dataset has {} rows. \n".format(pp_data.shape[0]))

logger.info("Removing all starting and intermediate columns so that only processed features remain. \n")

pp_data_pro = pp_data.reindex(columns=['age', 'sex', 'height_in', 'start_weight', 'end_weight','weight_diff', 'score', 'num_comments', 'month', 'dayofweek', 'NSFW', "num_posts"])

#Save processed dataframe to cvs file
file_name = input("What you would like to call that file that contains your processed dataset?  Make sure to include the file extenstion .csv \n")

pp_data_pro.to_csv(file_name, index=False)

logger.info("Saving dataframe to {} file.\n".format(file_name))

time.sleep(5)

# Extract time frame of weight change in weeks and months
logger.info("Extract the amount of time over which the weight change took place.  Many r/progresspics users failed to include this information in their post titles so this will be a smaller dataset compared to the one that was just saved.\n")

logger.info("Save duration of weight loss in two new columns, period_weeks and period_months.\n")

units_of_measure = ['days', 'day', 'weeks', 'week', 'months', 'months', 'year', 'years']
duration = pp_data["title"].apply(lambda sentence: any(word in sentence for word in units_of_measure))
pp_duration = pp_data[duration]

pp_duration = pp_duration.reindex(columns=['title', 'age', 'sex', 'height_in', 'start_weight', 'end_weight', 'weight_diff', 'period_weeks', 'period_months','NSFW', 'num_posts', 'score', 'num_comments', 'timestamp', 'id',' created_utc', 'author', 'permalink', 'month', 'year', 'day', 'dayofweek', 'date', 'time', 'raw_sex', 'raw_height', 'num_height', 'raw_weights', 'raw_start_weight', 'raw_end_weight'])

pp_duration['period_weeks'] = pp_duration["title"].apply(lambda s: feat.get_duration_weeks(s))
pp_duration['period_months'] = pp_duration["title"].apply(lambda s: feat.get_duration_months(s))

pp_duration = pp_duration[pp_duration["period_weeks"] != "unknown"]
pp_duration = pp_duration[pp_duration["period_weeks"] >= 1]
pp_duration = pp_duration[pp_duration["period_weeks"] <= 850]

logger.info("After processing, {} rows remain. \n".format(pp_duration.shape[0]))

time.sleep(5)

# Calculate rate of weight loss
logger.info("Calculate the rate of weight loss and the normalized rate of weight loss. Store the values in the new rate and norm_rate columns.\n")

pp_duration["rate"] = pp_duration['weight_diff']/pp_duration["period_months"]
pp_duration['norm_rate'] = pp_duration["weight_diff"]/pp_duration["start_weight"]/pp_duration["period_months"]

pp_duration = pp_duration[(pp_duration["rate"] < 30) & (pp_duration["rate"] > -30)]

logger.info("After trimming rows with extreme rates caused by user entry error, {} rows remain. \n".format(pp_duration.shape[0]))

logger.info("Removing all starting and intermediate columns so that only processed features remain. \n")

pp_duration_pro = pp_duration.reindex(columns=['age', 'sex', 'height_in', 'start_weight', 'end_weight', 'weight_diff', 'score', 'num_comments', 'month', 'dayofweek', 'NSFW', "num_posts", "period_months", 'rate', 'norm_rate'])

file_name2 = input("What you would like to call that file that contains your second processed dataset?  Make sure to include the file extenstion .csv  \n")

pp_duration_pro.to_csv(file_name2, index=False)

logger.info("Saving dataframe to {} file.\n".format(file_name2))
time.sleep(5)


'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The remainder of the code calculates summary statistics for the extracted features and generates data visualizations.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

logger.info("Moving onto an exploration of the data. \n")

logger.info("Creating a directory called 'plots' in the current directory to store the visualizations that will be generated during this analysis. \n")

os.mkdir("plots")

logger.info("Exploratory data analysis will first be performed on the larger dataset without the features related to weight change duration. \n")
time.sleep(5)

plt.style.use('ggplot')

# sex analysis

logger.info("Analyzing the number of male and female users. \n")
sex_counts = pp_data["sex"].value_counts()
males = sex_counts[0]/pp_data["sex"].count()
females = sex_counts[1]/pp_data["sex"].count()

logger.info("The dataset contains {0} males ({1}%) and {2} females ({3}%).\n".format(sex_counts[0], (round(males, 3)*100), sex_counts[1], (round (females, 3)*100)))

logger.info("Generating a plot that compares the number of male and female r/progresspics users to the number of males and females in the general Reddit user population and the US adult population.")
logger.info("Saving plot as pp_sex_compare.png \n")

US_sex_dict = {"male":  0.49, "female": 0.51}
reddit_sex_dict = {"male":  0.67, "female": 0.33}
pp_sex_dict = {"male":  males, "female": females}

ind = np.arange(2)
width = 0.30

fig, ax = plt.subplots()
ax.bar(ind, list(US_sex_dict.values()), width, align="center", label = "US adult population")
ax.bar(ind + width, list(reddit_sex_dict.values()), width, align="center", label = "Reddit population")
ax.bar(ind + 2*width, list(pp_sex_dict.values()), width, align="center", label = "r/progress_pics population")
ax.set_xticks(ind + width)
ax.set_xticklabels(list(US_sex_dict.keys()))
ax.set_ylim(0, 1)
ax.legend()
ax.set(title="Frequency of males and females in various populations", ylabel="frequency")

fig.savefig("plots/pp_sex_compare.png")
time.sleep(5)

#age analysis
logger.info("Analyzing the ages \n")

pp_males = pp_data[pp_data["sex"] == 0]
pp_females = pp_data[pp_data["sex"] == 1]

age_mean = pp_data['age'].mean()
mean_male_age = pp_males["age"].mean()
mean_female_age = pp_females["age"].mean()
age_min = pp_data['age'].min()
age_max = pp_data['age'].max()
twenties = pp_data[(pp_data["age"] >= 20) & (pp_data["age"] < 30)].shape[0]/pp_data.shape[0]

logger.info("The average age of the r/progresspics users is {0} years, while the average male age is {1} years and the average female age is {2} years.".format(round(age_mean, 1), round(mean_male_age, 1), round(mean_female_age, 1)))

logger.info("The oldest user is {0} years old and the youngest is {1} years old. A majority ({2}%) are in their 20s. \n".format(round(age_max, 0), round(age_min, 0), round(twenties * 100, 1)))

logger.info("Generating a plot that compares the age distributions of males and females.")
logger.info("Saving plot as pp_m_f_age_comparision.png \n")

fig, ax = plt.subplots()
ax.hist([pp_females["age"], pp_males["age"],], label=["female", "male"], bins=np.arange(0, 80, 5))
ax.set(xlabel="age (years)", ylabel="number of users", title="Distribution of male and female r/progresspics users' ages")
ax.legend()

fig.savefig("plots/pp_m_f_age_comparision.png")

logger.info("Generating a plot that compares the age distributions of r/progresspics users to that of the general Reddit user population and the US adult population.")
logger.info("Saving plot as pp_age_comparison.png \n")

pp_adults = pp_data[pp_data["age"] >=18]
adults18_29 = pp_adults[(pp_adults["age"] >=18)&(pp_adults["age"] <=29)].shape[0]/pp_adults.shape[0]
adults30_49 = pp_adults[(pp_adults["age"] >=30)&(pp_adults["age"] <=49)].shape[0]/pp_adults.shape[0]
adults50_64 = pp_adults[(pp_adults["age"] >=50)&(pp_adults["age"] <=64)].shape[0]/pp_adults.shape[0]
adults65 = pp_adults[(pp_adults["age"] >=65)].shape[0]/pp_adults.shape[0]

# Adult demographic info from 2016:  https://www.techjunkie.com/demographics-reddit/
US_age_dict = {"18-29":  0.22, "30-49": 0.34, "50-64": 0.25, "65+": 0.19}
reddit_age_dict = {"18-29":  0.64, "30-49": 0.29, "50-64": 0.06, "65+": 0.01}
pp_age_dict = {"18-29":  adults18_29, "30-49": adults30_49, "50-64": adults50_64, "65+": adults65}

ind = np.arange(4)
width = 0.30

fig, ax = plt.subplots()
ax.bar(ind, list(US_age_dict.values()), width, align="center", label = "US adult population")
ax.bar(ind + width, list(reddit_age_dict.values()), width, align="center", label = "Reddit population")
ax.bar(ind + 2*width, list(pp_age_dict.values()), width, align="center", label = "r/progress_pics population")
ax.set_xticks(ind + width)
ax.set_xticklabels(list(US_age_dict.keys()))
ax.set_ylim(0, 1)
ax.legend()
ax.set(title="Frequency of adults in various population age ranges", xlabel="age range (years)", ylabel="frequency")

fig.savefig("plots/pp_age_comparison.png")
time.sleep(5)

# Height analysis
logger.info("Analyzing the heights \n")

mean_height_male = round(pp_males["height_in"].mean(), 1)
mean_height_female = round(pp_females["height_in"].mean(), 1)

logger.info("The mean female height is {0} inches while the mean male height is {1} inches. \n".format(mean_height_female, mean_height_male))

logger.info("Generating a plot that shows the height distributions of male and female users.")
logger.info("Saving plot as pp_height_range.png \n")

fig, ax = plt.subplots()
ax.hist(pp_females["height_in"], label=["female"], bins=np.arange(50, 80, 1), alpha=0.5)
ax.hist(pp_males["height_in"], label=["male"], bins=np.arange(50, 80, 1), alpha=0.5)
ax.set(xlabel="height (inches)", ylabel="number of users", title="Distribution of female and male r/progresspics users' heights")
ax.legend()

fig.savefig("plots/pp_height_range.png")
time.sleep(5)

#Starting and ending weight analysis
logger.info("Analyzing starting and ending weights \n")

mean_start_male = round(pp_males["start_weight"].mean(), 1)
mean_start_female = round(pp_females["start_weight"].mean(), 1)

logger.info("The mean female starting weight is {0} lbs while the mean male starting weight is {1} lbs. \n".format(mean_start_female, mean_start_male))

logger.info("Generating a plot that shows the starting weight distributions of the male and female users.")
logger.info("Saving plot as pp_starting_weight.png \n")

fig, ax = plt.subplots()
ax.hist(pp_females["start_weight"], label=["female"], bins = np.arange(50, 1000, 10), alpha=0.5)
ax.hist(pp_males["start_weight"], label=["male"], bins=np.arange(50, 1000, 10), alpha=0.5)
ax.set(xlabel="starting weight (pounds)", ylabel="number of users", title="Distribution of female and male r/progresspics users' starting weights")
ax.legend()

fig.savefig("plots/pp_starting_weight.png")

mean_end_male = round(pp_males["end_weight"].mean(), 1)
mean_end_female = round(pp_females["end_weight"].mean(), 1)

logger.info("The mean female ending weight is {0} lbs while the mean male ending weight is {1} lbs. \n".format(mean_end_female, mean_end_male))

logger.info("Generating a plot that shows the ending weight distributions of the male and females users.")
logger.info("Saving plot as pp_starting_weight.png \n")

fig, ax = plt.subplots()
ax.hist(pp_females["end_weight"], label=["female"], bins = np.arange(50, 1000, 10), alpha=0.5)
ax.hist(pp_males["end_weight"], label=["male"], bins=np.arange(50, 1000, 10), alpha=0.5)
ax.set(xlabel="ending weight (pounds)", ylabel="number of users", title="Distribution of female and male r/progresspics users' ending weights")
ax.legend()

fig.savefig("plots/pp_ending_weight.png")
time.sleep(5)

# Analysis of weight loss and weight gain
logger.info("Analyzing changes in weight for r/progresspics users \n")

total_entries = pp_data['weight_diff'].count()
lost_weight = pp_data[pp_data["weight_diff"] > 0]["weight_diff"].count()
per_lost = round(lost_weight/total_entries * 100, 1)
gain_weight = pp_data[pp_data["weight_diff"] < 0]["weight_diff"].count()
per_gain = round(gain_weight/total_entries * 100, 1)
same_weight = pp_data[pp_data["weight_diff"] == 0]["weight_diff"].count()
per_same = round(same_weight/total_entries * 100, 1)

logger.info("Of {0} users, {1} lost weight ({2}%), {3} gained weight ({4}%), and {5} stayed the same ({6}%). \n".format(total_entries, lost_weight, per_lost, gain_weight, per_gain, same_weight, per_same))

pp_lost = pp_data[pp_data["weight_diff"] > 0]
pp_gain = pp_data[pp_data["weight_diff"] < 0]
pp_male_lost = pp_lost[pp_lost['sex'] == 0]
pp_female_lost = pp_lost[pp_lost['sex'] == 1]
pp_male_gain = pp_gain[pp_gain['sex'] == 0]
pp_female_gain = pp_gain[pp_gain['sex'] == 1]

pp_male_gain.loc[:, "weight_diff"] = pp_male_gain.loc[:, "weight_diff"] * -1
pp_female_gain.loc[:, "weight_diff"] = pp_female_gain.loc[:, "weight_diff"] * -1

mean_loss_male = pp_male_lost['weight_diff'].mean()
mean_loss_female = pp_female_lost['weight_diff'].mean()
mean_gain_male = pp_male_gain['weight_diff'].mean()
mean_gain_female = pp_female_gain['weight_diff'].mean()
max_male_loss = pp_male_lost["weight_diff"].max()
max_female_loss = pp_female_lost["weight_diff"].max()

logger.info('The mean female weight loss was {0} lbs while the mean male weight loss was {1} lbs.'.format(round(mean_loss_female, 1), round(mean_loss_male, 1)))
logger.info('The mean female weight gain was {0} lbs while the mean male weight gain was {1} lbs.'.format(round(mean_gain_female, 1), round(mean_gain_male, 1)))
logger.info('The largest amount of weight loss by a female and male respectively was {0} lbs {1} lbs. \n '.format(round(max_female_loss, 1), round(max_male_loss, 1)))

logger.info("Generating a plot that shows the distributions of weight loss and weight gain by male and females users.")
logger.info("Saving plot as pp_histogram_weight_diff.png \n")

fig, [ax1, ax2] = plt.subplots(1, 2, sharey=True)
ax1.hist(pp_female_lost["weight_diff"], bins = np.arange(0, 300, 10), label="females", alpha=0.5)
ax1.hist(pp_male_lost["weight_diff"], bins = np.arange(0, 300, 10), label="males", alpha=0.5)
ax1.set(xlabel="pounds lost", ylabel="number of users")
ax2.hist(pp_female_gain["weight_diff"], bins = np.arange(0, 300, 10), label='females', alpha=0.5)
ax2.hist(pp_male_gain["weight_diff"], bins = np.arange(0, 300, 10), label='males', alpha=0.5)
ax2.set(xlabel="pounds gained")
fig.suptitle("Distributions of weight change by r/progresspics users")
ax2.legend()

fig.savefig("plots/pp_histogram_weight_diff.png")
time.sleep(5)

# Analysis of the duration of weight loss
logger.info("Analyzing the duration of weight loss using the smaller dataset ({} rows) which contains the users for which a weight change period could be determined. \n".format(pp_duration.shape[0]))


dur_loss = pp_duration[pp_duration["weight_diff"] > 0]
dur_male_loss = dur_loss[dur_loss['sex'] == 0]
dur_female_loss = dur_loss[dur_loss['sex'] == 1]
dur_loss_lt72 = dur_loss[dur_loss["period_months"]<=72]

max_duration = dur_loss["period_months"].max()
years_lt6 = dur_loss[dur_loss['period_months'] <= 72].shape[0]
per_years_lt6 = round(years_lt6/dur_loss.shape[0] * 100, 1)
years_lt1 = dur_loss[dur_loss['period_months'] <= 12].shape[0]
per_years_lt1 = round(years_lt1/dur_loss.shape[0] *100, 1)

logger.info("The longest period of weight loss reported was {} years. \n".format(max_duration))
logger.info("The percentage of users whose weight loss took 6 or fewer years was {0}%, while the percentage who reported weight loss over one year or less was {1}%.\n".format(per_years_lt6, per_years_lt1))

logger.info("Generating a plot that shows a histogram of the duration of weight loss for all users.")
logger.info("Saving plot as pp_weight_loss_duration.png \n")

fig, ax = plt.subplots()
ax.hist(dur_loss_lt72["period_months"], bins = np.arange(0, 70, 3))
ax.xaxis.set_major_locator(plt.MultipleLocator(3))
ax.set(xlabel="months", ylabel="number of users", title="Duration of the weight loss")

fig.savefig("plots/pp_weight_loss_duration.png")
time.sleep(5)

# Analysis of rate of weight loss
logger.info("Analyzing the rate of weight loss \n")

loss_rate = round(dur_loss["rate"].mean(), 1)
male_loss_rate = round(dur_male_loss["rate"].mean(), 1)
female_loss_rate = round(dur_female_loss["rate"].mean(), 1)

logger.info("The mean rate of weight loss for all users is {0} lbs/month. Males lost weight at a mean rate of {1} lbs/month and females at a rate of {2} lbs/month. \n".format(loss_rate, male_loss_rate, female_loss_rate))

logger.info("Generating a plot that shows the distributions of weight loss rates for all males and females.")
logger.info("Saving plot as pp_weight_loss_duration.png \n")

fig, ax = plt.subplots(1, 1)
ax.hist(dur_female_loss["rate"], bins = np.arange(0, 30, 1), label='females', alpha = 0.5)
ax.hist(dur_male_loss["rate"], bins = np.arange(0, 30, 1), label='males', alpha = 0.5)
ax.legend()
ax.set(title="Distribution of female and male r/progresspics users' weight loss rates", xlabel="weight loss rates (pounds/month)", ylabel="number of users")

fig.savefig("plots/pp_raw_weight_loss_rates.png")

logger.info("Preliminary data analysis is now complete.")
