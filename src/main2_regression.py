'''
This script runs simple linear regressions and generates simple linear regression diagnostic plots. It also runs the forward stepwise and best subsets multiple linear regression model selection procedures.  Two default datasets that contain features related to r/progresspics are included though users can also provide their own .cvs file.
'''

import pandas as pd
import src.regression.pp_regression_fxn as regr
import logging


# Set up logging
# Create custom logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Create handlers
ch = logging.StreamHandler()
fh = logging.FileHandler('linear regression analysis.log', mode='w')
ch.setLevel(logging.INFO)
fh.setLevel(logging.INFO)

# Create formatters and add to handlers
c_format = logging.Formatter('%(message)s')
f_format = logging.Formatter('%(message)s')
ch.setFormatter(c_format)
fh.setFormatter(f_format)

logger.addHandler(ch)
logger.addHandler(fh)

# Load data
logger.info("This script generates simple linear regression models, produces diagnostic plots for simple linear regression models, and identifies robust multiple linear regression models using best subsets or forward stepwise model finding procedures. \n ")

# Importing data from .csv file
file = input(str("Type a file path for .csv file that contains data for the independent and dependent variables.  If 'data' is entered, the program will run using the included large 2018 r/progresspics dataset.  If 'duration' is entered, the program will run using the smaller 2018 r/progresspics dataset (which includes the weight change time duration variables.) \n"))

logger.info("Importing raw data. \n")
if file == "data":
    data = pd.read_csv("data/pp_data_2018_processed.csv")
elif file == "duration:":
    data = pd.read_csv("data/pp_duration_2018_processed.csv")
else:
    data = pd.read_csv(file)

logger.info("{} rows, {} columns imported. \n".format(data.shape[0], data.shape[1]))

logger.info("Your dataset contains the following columns: {} \n".format( data.columns))

# Simple linear regression
logger.info("Simple Linear Regression using your selected dataset. \n")

dependent_var = input("Which column do you want to use as the dependent variable in your simple linear regression?  ")

exclude_input = input("Which columns do you want to exclude from your analysis? Please enter column names separated by commas.  If none, enter none.  ")

if exclude_input == 'none':
    exclude_cols = []
else:
    exclude_cols = exclude_input.split(',')

regr.linear_regression(dependent_var, data, exclude_cols)

# Diagnostic plots

logger.info("Diagnostic plots")

plot_input = input("Would you like to run diagnostic plots for one of your independent variables? Enter yes or no.  ")

if plot_input == 'yes':
    independent_var = input("Which column do you want to use as the independent variable in your diagnostic plots?  ")
    fig = regr.lin_regr_diagnostic_plots(dependent_var, independent_var, data)
    plot_title = input("What do you want to call the diagnostic plot file? Make sure the file extension is .png  ")
    fig.savefig(plot_title)
    logger.info('\n')

# Multiple linear regression
logger.info("Multiple Linear Regression using your selected dataset.\n")

dependent_var = input("Which column do you want to use as the dependent variable in your multiple linear regression?  ")

exclude_input = input("Which columns do you want to exclude from your analysis? Please enter column names separated by commas.  If none, enter none.  ")

if exclude_input == 'none':
    exclude_cols = []
else:
    exclude_cols = exclude_input.split(',')

logger.info("The scrip will now run two types of multiple linear regression variable selection procedures:  best subsets and forward stepwise. \n")


stepwise = regr.stepwise_linear_regression(dependent_var, data, exclude_cols)
logger.info("Results of stepwise multiple linear regression variable selection: \n")
logger.info(stepwise)
logger.info('\n')

subset = regr.subset_linear_regression(dependent_var, data, exclude_cols)
logger.info("Results of best subsets multiple linear regression variable selection: \n")
logger.info(subset)
