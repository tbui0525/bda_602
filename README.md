# Baseball Analysis

In this project, I am attempting to predicting if the Home Team Wins in baseball games. This is using the baseball.sql dataset you may obtain from this link: https://teaching.mrsharky.com/data/baseball.sql.tar.gz. This dataset is 1.2 GB which should be manageable for most computers if you want to recreate my results. 

This dataset does have many errors such as repeated columns, missing data, duplicate data, etc. However, the features that I have chosen do not pull from the tables with many errors. I did not use the box score table which has a lot of data target leakage and removed the game with two starting pitchers on 1 team. 
