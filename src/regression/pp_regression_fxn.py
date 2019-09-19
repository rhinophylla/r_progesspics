import pandas as pd
import numpy as np
import itertools
import time
import statsmodels.api as sm
import matplotlib.pyplot as plt
import seaborn as sns
import scipy as sp
import logging


def linear_regression(y, df, exclude):
    """Generates a simple linear regression model for the provided dependent variable and each independent variable in the provided dataframe, but not included in the exclude list.  Prints the summary of each model and returns a dataframe containing model information.

    Arguments:
    y -- column name of the dependent variable; provide a string
    df -- Pandas dataframe that contains the data for the dependent and independent variables; provide a df
    exclude --  column name(s) to be excluded from the analysis; provide a list of strings or an empty list if there are no columns to exclude

    Returns:
    results_df -- Pandas dataframe that contains information about each model generated including the F-statistic, F-statistic p-value, t-test, t-test p-value, and R-squared value.
    """
    logger = logging.getLogger("thelogger")
    exclude_cols = []
    results = {}
    exclude_cols.append(y)
    exclude_cols.extend(exclude)
    logger.info('y = {}'.format(y))
    logger.info("excluded features: {}".format(exclude_cols))
    logger.info("df shape: {}".format(df.shape))
    features = [col for col in df.columns if col not in exclude_cols]
    for feat in features:
        logger.info("F is".format(feat))
        str1 = "{0} ~ {1}".format(y, feat)
        reg_model = sm.OLS.from_formula(str1, df).fit()
        results[feat] = [round(reg_model.rsquared, 3), round(reg_model.fvalue, 1), round(reg_model.f_pvalue, 4), round(reg_model.tvalues[1], 2), round(reg_model.pvalues[1], 4)]
        logger.info('X = {}'.format(feat.upper()))
        logger.info(reg_model.summary())
    results_df = pd.DataFrame.from_dict(results, columns=["R-sqr", "F-statistic", "F-stat p-value", 't-test', 't-test p-value'], orient='index')
    logger.info('Results: {}'.format(results_df))
    return results_df


def lin_regr_diagnostic_plots(y, x, df):
    """Generates diagnostic plots used to evaluate a simple linear regression model. The plots include a scatter plot
    of the independent variable vs the dependent variable to evaluate linearity, a scatter plot of the standardized
    residuals vs fitted values to evaluate error variance, and a probability plot to evaluate error normality.

    Arguments:
    y -- column name of the dependent variable; provide a string
    x -- column name of the independent variable; provide a string
    df -- Pandas dataframe that contains the data for the dependent and independent variables; provide a df

    Returns:
    None
    """
    str1 = "{0} ~ {1}".format(y, x)
    reg_model = sm.OLS.from_formula(str1, df).fit()
    fit_values = pd.Series(reg_model.fittedvalues, name="fitted_values")
    residuals = pd.Series(reg_model.resid, name="residuals")
    norm_residuals = pd.Series(reg_model.get_influence().resid_studentized_internal, name="Standardized Residual")

    fig = plt.figure(constrained_layout=True, figsize=(8,8))
    gs = fig.add_gridspec(2, 2)
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.set_title("Regression plot")
    sns.regplot(x, y, df, line_kws={'color':'r'}, ci=None, ax=ax1)
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.set_title("Standardized residuals vs Fit plot")
    sns.regplot(fit_values, norm_residuals, line_kws={'color':'r'}, ci=None, ax=ax2)
    ax3 = fig.add_subplot(gs[0:, -1])
    sp.stats.probplot(norm_residuals, plot=ax3, fit=True)
    fig.suptitle('y = {}, x = {}'.format(y, x, df), fontsize=14)

    return fig

# These functions implement the "best subsets" regression procedure

def process_subset(y, feature_set, df):
    """Generates a linear regression model and returns the number of independent variables it contains, the
    names of the independent variables, the model, and the model's RSS value, R-squared value, and R-squared-adjusted
    value.
    """
    str1 = str(y) + ' ~ ' + ' + '.join(list(feature_set))
    model = sm.OLS.from_formula(str1, df)
    regr = model.fit()
    RSS = ((regr.predict(df[list(feature_set)]) - df[y]) ** 2).sum()
    R_squared = regr.rsquared
    R_squared_adj = regr.rsquared_adj
    return {"num_predictors": len(feature_set), "predictors": feature_set, "RSS": RSS, "rsquared": R_squared, "rsquared_adj": R_squared_adj, "model":regr}

def get_best(y, df, features, k):
    """Generates all possible combinations of independent variables, generates linear regression models using the
    variable combinations and returns those with the highest R-squared-adjusted values.
    """
    results = []
    for combo in itertools.combinations(features, k):
        #print("combo:", combo)
        inv_results = process_subset(y, combo, df)
        #print("results:", inv_results["rsquared_adj"])
        results.append(inv_results)
    models = pd.DataFrame(results)
    best_model = models.nlargest(2, "rsquared_adj")
    #print("Best model", best_model)
    return best_model

def subset_linear_regression(y, df, exclude):
    """Generates regression models using all possible combinations of independent variables, then chooses the models
    with the highest R-squared-adj values.

    Arguments:
    y -- column name of the dependent variable; provide a string
    df -- Pandas dataframe that contains the data for the dependent and independent variables; provide a df
    exclude --  column name(s) to be excluded from the analysis; provide a list of strings or an empty list if
        there are no columns to exclude

    Returns:
    models -- Pandas dataframe that contains information about the two (or one) model(s) with the highest R-squared adj
    value from the independent variable combinations.  For example, if there are 4 independent variables, the function
    will return the two models with the highest R-squared-adj. value if one, two, and three independent variables are
    included as well as the single model that contains four predictors. The returned information includes the number of
    independent variables, the names of the independent variables, the model, and the model's RSS value,
    R-squared value, and R-squared-adjusted value.
    """
    models = pd.DataFrame(columns=["num_predictors", "predictors", "RSS", "rsquared", "rsquared_adj", "model"])
    exclude_cols = []
    exclude_cols.append(y)
    exclude_cols.extend(exclude)
    features = [f for f in df.columns if f not in exclude_cols]
    for i in range(1, len(features)):
        #print("i:", i)
        models = pd.concat([models, get_best(y, df, features, i)], sort=True)
    return models

# These functions implement the "forward stepwise" regression procedure

def process_subset_ttest(y, feature_set, df):
    """Generates a linear regression model and returns the t-test p-values for all the included independent variables.
    """
    str1 = str(y) + ' ~ ' + ' + '.join(list(feature_set))
    model = sm.OLS.from_formula(str1, df)
    regr = model.fit()
    summary = regr.summary().tables[1]
    pvals = regr.pvalues
    results_series = pd.Series(pvals)
    #print(results_series)
    return results_series

def process_best_model(y, feature_set, df):
    """Generates a linear regression model and returns the number of independent variables it contains, the names of the independent variables, the model, and the model's RSS value, R-squared value, and R-squared-adjusted value.
    """
    str1 = str(y) + ' ~ ' + ' + '.join(list(feature_set))
    model = sm.OLS.from_formula(str1, df)
    regr = model.fit()
    RSS = ((regr.predict(df[list(feature_set)]) - df[y]) ** 2).sum()
    R_squared = regr.rsquared
    R_squared_adj = regr.rsquared_adj
    return {"num_predictors": len(feature_set), "predictors": feature_set, "RSS": RSS, "rsquared": R_squared, "rsquared_adj": R_squared_adj, "model":regr}

def forward_stepwise(y, predictors, y_and_exclude, df):
    """Takes the existing regression model and adds each remaining independent variable to it one at a time.  Compares the t-test p-values of new models and identifies the lowest t-test p-value.  If all variables are below the
    0.15 signficance level, the included predictors are returned.  If the t-test p-values any of the previously included variables now fall below the 0.15 level, they are removed and the remaining predictors are returned.
    """
    remaining_predictors = [p for p in df.columns if p not in predictors and p not in y_and_exclude]
    #print("remaining predictors: ", remaining_predictors)
    results = []
    for p in remaining_predictors:
        #print("p:", p)
        results.append(process_subset_ttest(y, (predictors + [p]), df))
        # results is a list of pd Series
    #print("results:", results)
    low_pvalue = 0.15
    index_of_best_series = False
    new_predictors = []
    count = 0
    for i in range(len(results)):
        #print("last value:", results[i][-1].item())
        current = results[i][-1].item()
        if current < 0.15:
            count =+ 1
            if current < low_pvalue:
                low_pvalue = current
                index_best_series = i
    if count == 0:
        for index, value in results[0][:-1].iteritems():
            #print("count = 0, index:", index, "value:", value)
            if index != "Intercept":
                new_predictors.append(index)
        return(new_predictors)
    for index, value in results[index_best_series].iteritems():
        #print("index:", index, "value:", value)
        if index != "Intercept":
            if value < 0.15:
                new_predictors.append(index)
    #print("new_predictors:", new_predictors)
    return(new_predictors)

def stepwise_linear_regression(y, df, exclude):
    """First, individually evaluates independent variables in a linear regression model. The independent variable with the lowest t-test p-value becomes the starting model.  Then the remainder of the independent variables are individually added to the starting model.  If none have a significant t-test p-value then the process ends, but if one or many do, the one with the lowest t-test p-value is retained and a new starting model is established (after it is determined that the original independent variable still has a significant t-test p-value).  This process is repeated until no newly added independent variablies have a significant t-test p-value.  The best model from each step is returned.

    Arguments:
    y -- column name of the dependent variable; provide a string
    df -- Pandas dataframe that contains the data for the dependent and independent variables; provide a df
    exclude --  column name(s) to be excluded from the analysis; provide a list of strings or an empty list if there are no columns to exclude

    Returns:
    models_step -- Pandas dataframe that contains information about best model identified at each step of the process. The returned information includes the number of independent variables, the names of the independent variables, the model, and the model's RSS value, R-squared value, and R-squared-adjusted value.
    """
    y_and_exclude = []
    y_and_exclude.append(y)
    y_and_exclude.extend(exclude)
    dep_var = df.shape[1] - len(y_and_exclude)
    #print(dep_var)
    old_predictors = []
    step = 0
    best_models = []
    new_predictors = forward_stepwise(y, old_predictors, y_and_exclude, df)
    best_predictors = [new_predictors]
    #print("1st comparision:", old_predictors, new_predictors)
    while old_predictors != new_predictors:
        step += 1
        #print("step", step)
        old_predictors = new_predictors
        #print('old_predictors:', old_predictors)
        if len(old_predictors) == dep_var:
            break
        new_predictors = forward_stepwise(y, old_predictors, y_and_exclude, df)
        #print('new_predictors:', new_predictors)
        best_predictors.append(new_predictors)
    #print("best_predictors:", best_predictors)
    for predictor_list in best_predictors[:-1]:
        #print("predictor_list:", predictor_list)
        if predictor_list[-1] == None:
            pass
        else:
            best_models.append(process_best_model(y, predictor_list, df))
    models_step = pd.DataFrame(best_models)
    return models_step
