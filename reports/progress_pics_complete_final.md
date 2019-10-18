# /r/progresspics project

### Goals

r/progresspics is an active subreddit where people post before and after pictures that typically document weight loss.  Here is a summary of the characteristics of people who post to r/progresspics as well as a preliminary effort to see if there are any correlations between the characteristics of the Redditor who posted and the amount of weight they lost and/or the popularity of their posts.

### Data Cleaning

r/progresspics recommends that Redditors title their submission in a particular format that includes their sex, age, height, starting weight, ending weight and the time duration of the weight change.

###### Format:
Gender/Age/Height \[Weight Before > Weight After = Total amount lost\](Time period in months) Personal Title

###### Sample Entry:
"M/26/6'0 \[190lbs&gt;175lbs=15lbs loss\] (-2.5 years). All natural hard work."

 From Google's BigQuery, the title, author, timestamp, score, and the number of comments for all 27,464 posts made to r/progresspics in 2018 was downloaded, then a custom script was used to extract the relevant information from the title of each post.  Despite many formatting irregularities the sex, age, height_in, start_weight, and end_weight was extracted from the titles of 20,065 posts.  Since many users did not include the duration of the weight change (period_months) that information was only available for 12,517 posts.  Several other features were derived including the difference between ending and starting weight (weight_diff), if the post included a "Not Safe for Work" tag (NSFW), the number of times the post author posted to the subreddit in 2018 (num_posts), the rate of weight loss (rate), and the normalized rate of weight loss (norm_rate). Finally, from the timestamp, multiple date descriptors including the month and day of the week (dayofweek) were extracted.

### Initial Data Exploration

#### Sex

r/progresspics users are 48% male and 52% female.

During my initial exploration, I looked at the sex and age of the r/progresspics users and compared these demographics to those of the whole Reddit user population and the general adult US population (https://www.techjunkie.com/demographics-reddit/).  This is an imperfect comparison since Reddit is used by people worldwide, not just those residing in the US.

While Reddit users, in general, are more likely to be male, the percentage of male and female r/progresspics users more closely matched the US general population indicating that r/progresspics users skew more female than the general Reddit population.

![Comparison of sex demographics](figures/pp_sex_compare.png)


#### Age

The average age of an r/progresspics user is 26.1 years and that is consistent for both males (26.1 years) and females (26.2 years). The youngest and oldest users in 2018 were 10 years old and 68 years old respectively.  The majority of users (66.8%) are in their 20s.

![Age histogram of male and female users](figures/pp_m_f_age_comparision.png)

Reddit users tend to be younger than the general US adult population and r/progresspics users follow that same trend.

![Comparision of age ranges](figures/pp_age_comparison.png)

#### Height and weight

The height ranges of the male and female r/progresspics users appear normally distributed with an average male height of 70.9 inches (~ 5'11'') and an average female height of 65.3 inches (~5'5'').

![Height ranges of male and female users](figures/pp_height_range.png)

The distributions of the average starting weights for male and female r/progresspics users were differently shaped with the female starting weights forming a tighter peak then the males.  Both distributions had tails extending towards higher weights.  The average starting male weight was 243.2 lbs and the average starting female weight was 206.7 lbs.

![Starting weight comparison](figures/pp_starting_weight.png)

The male and female ending weight distributions were more similarly shaped.  The average male ending weight was 195.2 lbs and the average female ending weight is 163.4 lbs.

![Ending weight comparision](figures/pp_ending_weight.png)

####  Pounds lost and gained

People use r/progresspics to report their efforts at both losing and gaining weight.  In this data set, 18083 users (90%) reported weight loss, 1778 users (9%) reported weight gain, while 204 (1%) reported no weight change.  The average male loser lost 61.9 lbs and the average female loser lost 46.0 lbs, while the average male gainer gained 28.2 lbs and the average female gainer gained 19.7 lbs. The largest weight loss reported by a male was 500 lbs and the largest weight loss for a female was 316 lbs.

![Histogram of weight_diff](figures/pp_histogram_weight_diff.png)

#### Duration of weight loss

The length of time over which weight loss occurred could be determined for 12,517 r/progresspics users.  The max period of weight loss reported was 16 years, but most of the users (98.4%) reported the duration of weight loss to be 6 or fewer years and a majority (67.4%) indicated the weight loss time frame was one year or less.  The histogram below shows the weight loss duration for users whose weight loss occurred over 6 years or less.  Spikes are visible at 12, 24, 36, 48, and 60 months indicating that users prefer to post to r/progresspics on the anniversary of the beginning of their weight loss journey.

![progress pics weight loss duration](figures/pp_weight_loss_duration.png)

#### Rate of weight loss

The raw rate of weight loss was determined by dividing the amount of weight loss by the duration of the weight-loss period.  Overall r/progresspics users, the raw rate of weight loss was 5.8 lbs/month with men losing weight at an average rate of  6.6 lbs/month and women at 5.1 lbs/month.  The weight loss rate distribution shown below confirms that men lose weight at a faster rate than women.

![raw weight loss](figures/pp_raw_weight_loss_rates.png)

### Regression analyses

#### Weight loss
I first looked to see if there was a simple linear relationship between the weight loss of an r/progresspics user and any of the following features using the larger dataset: age, sex, height_in, start_weight, and end_weight.  Variables that describe the post to r/progresspics were not considered since they are factors unrelated to the weight loss process. Since the focus is weight loss, the datasets used in these regression analyses were filtered to only contain posts where the weight_diff was > 0. While all the features had significant p-values (<0.05), only one feature (start_weight) had a large R<sup>2</sup> value (0.56).  The remainder were below 0.05.

|              |   R-sqr |   F-statistic |   F-stat p-value |   t-test |   t-test p-value |
|--------------|---------|---------------|------------------|----------|------------------|
| start_weight |   0.561 |       23119   |                0 |   152.05 |                0 |
| height_in    |   0.051 |         973.4 |                0 |    31.2  |                0 |
| end_weight   |   0.051 |         963.7 |                0 |    31.04 |                0 |
| sex          |   0.039 |         726.8 |                0 |   -26.96 |                0 |
| age          |   0.029 |         549.3 |                0 |    23.44 |                0 |

I then repeated the analysis using the smaller dataset that included the additional weight change duration variables (period_months and rate).  Again all the features had p-values below (0.05) and starting_weight had the largest R<sup>2</sup> value (0.59).  The next largest was the rate at 0.12.

|               |   R-sqr |   F-statistic |   F-stat p-value |   t-test |   t-test p-value |
|---------------|---------|---------------|------------------|----------|------------------|
| start_weight  |   0.592 |       16257.9 |                0 |   127.51 |                0 |
| rate          |   0.115 |        1453.7 |                0 |    38.13 |                0 |
| period_months |   0.07  |         844.7 |                0 |    29.06 |                0 |
| end_weight    |   0.063 |         755.3 |                0 |    27.48 |                0 |
| height_in     |   0.058 |         691.8 |                0 |    26.3  |                0 |
| sex           |   0.041 |         479.2 |                0 |   -21.89 |                0 |
| age           |   0.029 |         336.3 |                0 |    18.34 |                0 |


Since starting weight, based on R<sup>2</sup> values, looks like the best feature in our dataset to explain the variation in weight loss, diagnostic plots were run to see if this model fulfills the assumptions of a simple linear regression model.  The larger dataset was used.

![weight_diff vs start_weight](figures/pp_data_start_weight.png)

While the regression plot shows that there is a linear relationship between the amount of weight loss and the starting weight, the residuals vs fit plot shows a fanning effect indicating heteroskedasticity and non-constant error variance.  The probability plot shows that the residuals have a heavy tailed, normal distribution.

Next, multiple linear regression analyses were used to see if there were any combinations of features that could explain the variation in weight loss better than start_weight alone.  For these analyses, the end_weight variable was removed since when combined with start_weight, a 100% accurate model was generated.  This is an expected outcome as the dependent variable, weight_diff is calculated by subtracting end_weight from start_weight.

Combining the various features using the best subsets and forward stepwise procedures produced multiple linear regression models with modestly higher R<sup>2</sup>-adjusted values than the start_weight model alone. For the larger dataset, including height_in raised the R<sup>2</sup>-adjusted from 0.56 to 0.58.

Results of forward stepwise model selection procedure using the large dataset:

|   num_predictors | predictors                    |   R_sqr_adj |
|------------------|-------------------------------|----------------|
|                1 | start_weight              |       0.561116 |
|                2 | start_weight, height_in |       0.582855 |

Results of best subsets model selection procedure using the large dataset:

|   num_predictors | predictors                           |   R_sqr_adj  |
|------------------|--------------------------------------|----------------|
|                1 | start_weight                    |      0.561116  |
|                1 | height_in                       |      0.0510323 |
|                2 | height_in, start_weight        |      0.582855  |
|                2 | sex, start_weight              |      0.569348  |
|                3 | sex, height_in, start_weight |      0.582862  |
|                3 | age, height_in, start_weight |      0.582832  |


 For the smaller duration data set, the best R<sup>2</sup>-adjusted value was achieved with a model that contained all 6 variables, but as it was only 0.055 above start_weight alone, thus the simple start_weight only model still seems like the best option.

Results of forward stepwise model selection procedure using the smaller duration dataset:

 |   num_predictors | predictors                                                    |   R_sqr_adj |
|------------------|---------------------------------------------------------------|----------------|
|                1 | start_weight                                              |       0.592325 |
|                2 | start_weight, period_months                             |       0.617422 |
|                3 | start_weight, period_months, height_in                |       0.635927 |
|                4 | start_weight, period_months, height_in, rate        |       0.64751  |
|                5 | start_weight, period_months, height_in, rate, age |       0.647878 |

Results of best subsets model selection procedure using the smaller duration dataset:

|   num_predictors | predictors                                                    |   R_sqr_adj |
|------------------|---------------------------------------------------------------|----------------|
|                1 | start_weight                                             |       0.592325 |
|                1 | rate                                                     |       0.114917 |
|                2 | start_weight, period_months                             |       0.617422 |
|                2 | height_in, start_weight                                 |       0.611752 |
|                3 | height_in, start_weight, period_months                |       0.635927 |
|                3 | start_weight, period_months, rate                     |       0.630557 |
|                4 | height_in, start_weight, period_months, rate        |       0.64751  |
|                4 | sex, start_weight, period_months, rate              |       0.637775 |
|                5 | age, height_in, start_weight, period_months, rate |       0.647878 |
|                5 | sex, height_in, start_weight, period_months, rate |       0.647479 |

The observation that a linear regression model explaining weight_diff using the variables period_months and rate did not have an R<sup>2</sup>-adjusted approaching 1.0 points to a problem with the data.  The most likely issue is the period_months variable.  The method used to extract period_months from the post title focused on finding units of time (weeks, months, years) in the title and using any number found immediately before the time unit to calculate the period_months. However, people often included a unit of time in reference to things besides how long they have been changing their weight ie how long they have been going to the gym, how long they have been on a keto diet, etc.  In the future, a better algorithm to extract period_months will be developed.

Finally, the start_weight and weight_diff variables were transformed in various ways to see if the model could be improved.  For example, repeating the analysis using the log of start_weight improved the normality plot, but it lowered the R<sup>2</sup> value and did not improve the residuals vs fitted values plot.

#### r/progresspics post popularity

The popularity of a Reddit post can be approximated by its score, which is the number of upvotes a post received minus the number of downvotes, or by the number of comments (num_comments) left.  Though r/progresspics is primarily an image-driven forum, I was curious if any of the demographic information pulled from the title could be used to predict the popularity of a particular post.  However, after doing both single and multiple linear regressions as well as various feature transformations, I was unable to identify any single feature or combination of features that made a meaningful contribution to the variation seen in either the score or the number of comments.  Though most features had significant p_values, they did not meet model conditions required to trust a linear regression result since there was either no linear relationship or the residual errors were either not independent, not normally distributed, or did not have equal variance.

Below I show the results of the linear regression experiments using the smaller duration dataset for the score variable only.  The num_comments results are not showm though they are equally uninformative.

Results of simple linear regression for the score variable using the smaller duration dataset:

|               |   R-sqr |   F-statistic |   F-stat p-value |   t-test |   t-test p-value |
|---------------|---------|---------------|------------------|----------|------------------|
| weight_diff   |   0.047 |         620.7 |           0      |    24.91 |           0      |
| sex           |   0.022 |         279.3 |           0      |    16.71 |           0      |
| start_weight  |   0.016 |         204.3 |           0      |    14.29 |           0      |
| num_posts     |   0.009 |         114.9 |           0      |    10.72 |           0      |
| height_in     |   0.008 |         102.9 |           0      |   -10.14 |           0      |
| age           |   0.006 |          76.8 |           0      |     8.76 |           0      |
| rate          |   0.005 |          59.5 |           0      |     7.71 |           0      |
| period_months |   0.004 |          52.5 |           0      |     7.25 |           0      |
| NSFW          |   0.002 |          21.4 |           0      |    -4.62 |           0      |
| end_weight    |   0.001 |           7.3 |           0.0069 |    -2.7  |           0.0069 |
| month         |   0     |           0.3 |           0.6086 |     0.51 |           0.6086 |
| dayofweek     |   0     |           1.6 |           0.2052 |     1.27 |           0.2052 |


Results of forward stepwise selection procedure using the smaller duration dataset:

|   num_predictors | predictors                                                                                                |   R_sqr_adj|
|------------------|-----------------------------------------------------------------------------------------------------------|----------------|
|                1 | weight_diff                                                                                          |      0.0471801 |
|                2 | weight_diff, sex                                                                                    |      0.0722321 |
|                3 | weight_diff, sex, num_posts                                                                       |      0.0753598 |
|                4 | weight_diff, sex, num_posts, rate]                                                               |      0.0780075 |
|                5 | weight_diff, sex, num_posts, rate, NSFW                                                       |      0.0797578 |
|                6 | weight_diff, sex, num_posts, rate, NSFW, age]                                                |      0.080418  |
|                7 | weight_diff, sex, num_posts, rate, NSFW, age, start_weight                              |      0.0807254 |
|                8 | weight_diff, sex, num_posts, rate, NSFW, age, start_weight, end_weight]                  |      0.0807254 |
|                9 | weight_diff, sex, num_posts, rate, NSFW, age, start_weight, end_weight, period_months |      0.0809603 |




Results of best subsets model selection procedure using the smaller duration dataset:

|   num_predictors | predictors                                                                                                |    R_sqr_adj |
|------------------|-----------------------------------------------------------------------------------------------------------|----------------|
|                1 | weight_diff                                                                                          |      0.0471801 |
|                1 | sex                                                                                                  |      0.0217483 |
|                2 | sex,  weight_diff                                                                                   |      0.0722321 |
|                2 | height_in, weight_diff                                                                              |      0.0603118 |
|                3 | sex, weight_diff, num_posts                                                                       |      0.0753598 |
|                3 | sex, weight_diff, rate                                                                            |      0.0743664 |
|                4 | sex, weight_diff, num_posts, rate                                                               |      0.0780075 |
|                4 | sex, weight_diff, NSFW, num_posts)                                                               |      0.0771947 |
|                5 | sex, weight_diff, NSFW, num_posts, rate                                                       |      0.0797578 |
|                5 | sex, weight_diff, NSFW, num_posts, period_months                                              |      0.0789345 |
|                6 | age, sex, weight_diff, NSFW, num_posts, rate)                                                |      0.080418  |
|                6 | sex, weight_diff, NSFW, num_posts, period_months, rate                                      |      0.0800593 |
|                7 | age, sex, start_weight, weight_diff, NSFW, num_posts, rate                                |      0.0807254 |
|                7 | age, sex, end_weight, weight_diff, NSFW, num_posts, rate                                  |      0.0807254 |
|                8 | age, sex, start_weight, end_weight, NSFW, num_posts, period_months, rate                |      0.0809603 |
|                8 | age, sex, end_weight, weight_diff, NSFW, num_posts, period_months, rate                 |      0.0809603 |
|                9 | age, sex, start_weight, end_weight, weight_diff, NSFW, num_posts, period_months, rate |      0.0809603 |
|                9 | age, sex, height_in, start_weight, weight_diff, NSFW, num_posts, period_months, rate  |      0.0809052 |

The failure of this linear regression analysis is likely due to either a lack of a linear relationship between the dependent and independent variables and/or that the feature set did not contain any pertinent dependent variables.  Though future analysis may produce different results, the current conclusion is that simple identifiers like sex, age, or amount of weight loss do not have a linear correlation to the popularity of a post.


### Previous work

 Medium user acedb analyzed a smaller dataset of ~700 posts and their results can be found [here][ec6949e2].

  [ec6949e2]: https://medium.com/@acedb/what-is-being-posted-on-r-progresspics-an-initial-analysis-351e43b5d7c4 "r/progesspics analysis"

  ### Future work
  - Apply more sophisticated models to attempt to identify a relationship between the 'title' features and weight loss and/or post popularity.
  - Repeat the extraction of the period_months feature and check the results
  - Extract features related to the pictures contained in each post to use in future modeling efforts.
  - Download and process additional years of progress_pics data to see if the characteristics of the users have changed over time.  These datasets could also be used to validate future predictive models.
  - Analyze the comments associated with each post.  Often the user who made the post will provide details of their weight change protocol in the comments.  These comments could be identified and analyzed using natural language processing algorithms to gain insights into the techniques used during successful weight loss or gain.  Seeing how these techniques change over time would also be of interest.
