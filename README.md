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

Given the terminal output, I found some key features to eliminate from the model: batting average, Score_Diff, pitches thrown, pitcher per inning, CERA, PTB, and Pythag. As for the PCA model, we can drop x1 (the feature with the most variation), x3, and x6. By doing that, we have our improved 4 base models through feature reduction as such:


| | Logit | Random Forest |
| --- | --- | ---|
| OG | 52.8 | 50 |
| PCA | 54.1 (Yay! 54 barrier broken!)| 50.5|

From here, it was less about deleting features, but adding good ones. So, let's take a look at one of my best features, OBP. Looking at this mean of response plot, it seems that there are two slops. Before the 0 make, all of the data is below the red line with some up and down fluctuation. After the -0.01 mark though, there is a clear change in trajectory, moving upwards with a high magnitude slope. So by adding this line in our code:

``` python3
  newer_data["OBP_hinge"] = [max(0, i-0.01) for i in data["diff_OBP"].tolist()]
```
which was inspired from here: https://teaching.mrsharky.com/sdsu_fall_2020_lecture10.html#/3/15/12

This led a significant improvement in the model. Having a new feature means I would have to redo the PCA analysis to preserve the orthonormality of the features and whatnot. So, reduced features plus one new knot point later and this is the result we are left with:

| | Logit | Random Forest |
| --- | --- | ---|
| OG | 54.2 | 49.5 |
| PCA | 55 (Yay! 55 barrier broken!)| 49.9|

Again, random forests are somehow still giving me an AUC \times 100 of under 50 so... it should just flip the inequalities splitting the branches.


Overall, pretty decently happy with my results. I know there is a lot more to do given the time and effort. Maybe could have created some crazy new feature or used some wild model like XGBoost, but as for now, predicting Home_Team_Wins over the natural win rate (about 54% according to Bing) shows some good progress.

![54percent](https://github.com/tbui0525/bda_602/assets/82955352/97b71ef1-c202-46bb-b585-db7f42cdd9a7) 



