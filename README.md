# Baseball Analysis

In this project, I am attempting to predicting if the Home Team Wins in baseball games. This is using the baseball.sql dataset you may obtain from this link: https://teaching.mrsharky.com/data/baseball.sql.tar.gz. This dataset is 1.2 GB which should be manageable for most computers if you want to recreate my results. 

This dataset does have many errors such as repeated columns, missing data, duplicate data, etc. However, the features that I have chosen do not pull from the tables with many errors. I did not use the box score table which has a lot of data target leakage and removed the game with two starting pitchers on 1 team. These are the features I created:

- difference in Avg_Score_Diff: not good
- pitches per inning: ideally, less ppi means higher chance of winning
- team batting average: common baseball metric for batters, but unsure if we've seen it applied to a whole team before
- BABIP : a more accurate version of batting average based on balls in play
- Pythag: a win ratio similar to Avg_Score_Diff (no really, they are like 99% correlated)
- CERA, PTB, and DICE : all pitcher evaluation stats
- OBP, XBH, ISO: batting stats that take into account how many bases are run (weight factors for doubles, triples, HRs)
- Avg pitches thrown per game, avg innings pitched

All of these rolling averages are over the span of 365 days. In addition, because there is a rolling average, there tends to be a lot of NaN values. Teams' first games, new starting pitcher, etc. So for the purposes of this analysis, I have made The NaNs the column mean in the Pandas DataFrame,
I performed some exploratory data analysis in Python using Plotly to graph the data. One example is here:

![Innings Pitched Unclipped](https://github.com/tbui0525/bda_602/assets/82955352/da7e8cba-75ef-433f-924e-cc4e6b5b33ef)

This is the graph of innnings pitched of the starting pitcher. Here we see an clear upward trend in the data. Or do we? If you look at the edges of the histogram bins, it is clear that there are very little data in the outer bins, i.e. outliers. When we clip the data to the 5th and 95th percentiles, we see that the upward trend goes away, leaving that downard trend in the original graph.

![Innings Pitched Clipped](https://github.com/tbui0525/bda_602/assets/82955352/043c287a-1343-446d-a46c-f3ee279abd9c)

This, to me, is shocking. It would make sense to me, at least, that if you have a good starting pitcher, you let them pitch 6-7 innings. This is known as a quality start for a reason right? Yet, according to the data, if the home starting pitcher on average pitches more innings than the away starting pitcher, then the home team is more likely to lose. This trend is not only prevalent in the innings_pitched feature, but all of my features. You know what they say, one is an incident, two is a coincidence, three is a statistic (or something like that):

WHIP

![WHIP unclipped](https://github.com/tbui0525/bda_602/assets/82955352/9d51b13e-8a3a-4acc-9d49-858d46594721)

![WHIP clipped](https://github.com/tbui0525/bda_602/assets/82955352/a4f60e8c-3551-44d2-9735-80f756cc50ec)

OBA

![OBA unclipped](https://github.com/tbui0525/bda_602/assets/82955352/c77ede12-1374-4ba7-9894-58040252d4a4)


![OBA clipped](https://github.com/tbui0525/bda_602/assets/82955352/32b1e365-b6c7-458c-86eb-8423f181705a)

Here is the original analysis between predictor and response before clipping.

![baseball](https://github.com/tbui0525/bda_602/assets/82955352/78f67416-d341-44ad-9c94-931cb9841caa)

and if we compare that to running EDA on the clipped dataset, we return this table:

![clipped baseball](https://github.com/tbui0525/bda_602/assets/82955352/f9ae489a-3bfe-4895-8be4-36a1cf564742)

Doing this gives us a good idea of which features will be helpful. I also made a correlation table to see how much overlap there will be in the features. Why use two features that are practically the same when you could just use one? 

![Correlation Plot](https://github.com/tbui0525/bda_602/assets/82955352/9e8b96d7-8c82-42a9-b9a5-dc615c6ee25e)

Clearly variables such as Pythag and Avg_Score_Diff are very similar as well as average pitches thrown with average pitches per inning, and OBA and Whip scoring the highest. This would probably mean that some of those variables will be dropped when we do our modelling.

Rather than going with a buttload of models, I decided to lean in on the feature aspect of modelling. You can make twenty different models with the same features, but their AUCs can only differ by so much.
So here is a Punnet Square on how I decided to make my four base models:

| | Logit | Random Forest |
| --- | --- | ---|
| OG | OG Logit | OG Random Forest|
| PCA | PCA Logit | PCA Random Forest|

And after running the original model, I get the following AUC values:


| | Logit | Random Forest |
| --- | --- | ---|
| OG | 52.8 | 49.7 (how? just flip the 0s and 1s) |
| PCA | 53.5| 49.8 (again, makes 0 sense to me too) |

Given this terminal output:

                         Logit Regression Results 
                         
==============================================================================
Dep. Variable:          Home_Team_Win   No. Observations:                12516

Model:                          Logit   Df Residuals:                    12501

Method:                           MLE   Df Model:                           14

Date:                Tue, 09 May 2023   Pseudo R-squ.:                 0.01312

Time:                        14:27:02   Log-Likelihood:                -8412.3

converged:                       True   LL-Null:                       -8524.2

Covariance Type:            nonrobust   LLR p-value:                 7.846e-40

===================================================================================

                      coef    std err          z      P>|z|      [0.025      0.975]
                      
-----------------------------------------------------------------------------------

const               0.3167      0.018     17.321      0.000       0.281       0.352

diff_OBA           15.6353      3.747      4.172      0.000       8.290      22.980

diff_XBH            0.7739      0.152      5.078      0.000       0.475       1.073
diff_Score_Diff     0.4005      0.312      1.285      0.199      -0.210       1.011
diff_inn_p         -0.9028      0.162     -5.558      0.000      -1.221      -0.584
diff_thrown        -0.3054      0.411     -0.744      0.457      -1.110       0.500
diff_ppi            2.1165      2.094      1.011      0.312      -1.988       6.221
diff_CERA        -6.61e-06   3.96e-05     -0.167      0.867   -8.43e-05     7.1e-05
diff_PTB            0.0006      0.001      1.033      0.302      -0.001       0.002
diff_Pythag        -2.9521      2.967     -0.995      0.320      -8.768       2.864
diff_ISO          -12.6189      2.316     -5.449      0.000     -17.158      -8.080
diff_WHIP          -2.0677      0.394     -5.253      0.000      -2.839      -1.296
diff_OBP            2.6015      0.304      8.568      0.000       2.006       3.197
diff_BABIP         -8.5542      1.745     -4.903      0.000     -11.974      -5.135
diff_DICE        4.243e-05   1.69e-05      2.515      0.012    9.37e-06    7.55e-05
===================================================================================
Logistic ROC AUC Score:  0.5284504323650231

I found some key features to eliminate from the model: batting average, Score_Diff, pitches thrown, pitcher per inning, CERA, PTB, and Pythag.

As for the PCA model, this is the Logit results from that end:

              Logit Regression Results                          
==============================================================================
Dep. Variable:          Home_Team_Win   No. Observations:                12516
Model:                          Logit   Df Residuals:                    12508
Method:                           MLE   Df Model:                            7
Date:                Tue, 09 May 2023   Pseudo R-squ.:                0.005335
Time:                        15:12:17   Log-Likelihood:                -8478.7
converged:                       True   LL-Null:                       -8524.2
Covariance Type:            nonrobust   LLR p-value:                 7.860e-17
==============================================================================
                 coef    std err          z      P>|z|      [0.025      0.975]
------------------------------------------------------------------------------
const          0.3152      0.018     17.347      0.000       0.280       0.351
x1             0.0017      0.009      0.184      0.854      -0.016       0.019
x2            -0.0200      0.011     -1.879      0.060      -0.041       0.001
x3             0.0128      0.012      1.065      0.287      -0.011       0.037
x4             0.1025      0.015      6.721      0.000       0.073       0.132
x5            -0.0384      0.016     -2.348      0.019      -0.070      -0.006
x6             0.0323      0.021      1.518      0.129      -0.009       0.074
x7            -0.1419      0.025     -5.752      0.000      -0.190      -0.094
==============================================================================
Logistic ROC AUC Score:  0.5356303470182473





