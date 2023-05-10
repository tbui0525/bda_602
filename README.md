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

I performed some exploratory data analysis in Python using Plotly to graph the data. One example is here:

![Innings Pitched Unclipped](https://github.com/tbui0525/bda_602/assets/82955352/da7e8cba-75ef-433f-924e-cc4e6b5b33ef)

This is the graph of innnings pitched of the starting pitcher. Here we see an clear upward trend in the data. Or do we? If you look at the edges of the histogram bins, it is clear that there are very little data in the outer bins, i.e. outliers. When we clip the data to the 5th and 95th percentiles, we see that the upward trend goes away, leaving that downard trend in the original graph.

![Innings Pitched Clipped](https://github.com/tbui0525/bda_602/assets/82955352/043c287a-1343-446d-a46c-f3ee279abd9c)

This, to me, is shocking. It would make sense to me, at least, that if you have a good starting pitcher, you let them pitch 6-7 innings. This is known as a quality start for a reason right? Yet, according to the data, if the home starting pitcher on average pitches more innings than the away starting pitcher, then the home team is more likely to lose. This trend is not only prevalent in the innings_pitched feature, but all of my features. Just for a few examples, I will put down my other best features here:

WHIP

![WHIP unclipped](https://github.com/tbui0525/bda_602/assets/82955352/9d51b13e-8a3a-4acc-9d49-858d46594721)

![WHIP clipped](https://github.com/tbui0525/bda_602/assets/82955352/a4f60e8c-3551-44d2-9735-80f756cc50ec)


