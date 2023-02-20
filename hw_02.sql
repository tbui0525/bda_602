USE baseball;



#HISTORIC_BA
#DROP TEMPORARY TABLE historic_ba;
CREATE TABLE historic_ba (batter varchar(6), Hits int, atBats int, BA float)
SELECT bc.batter, sum(bc.Hit) as Hits,
       sum(bc.atBat) as atBats, sum(bc.Hit)/sum(bc.atBat) as BA
FROM batter_counts bc
JOIN game
    on bc.game_id = game.game_id
    GROUP BY bc.batter
    HAVING sum(bc.atBat) != 0;



SELECT *
FROM historic_ba
    LIMIT 0,20;
#ANNUAL_BA
#DROP TEMPORARY TABLE annual_ba
CREATE TABLE annual_ba (batter varchar(6), batting_year year, Hits int, atBats int, BA float)
SELECT bc.batter,year(game.local_date) as batting_year, sum(bc.Hit) as Hits,
       sum(bc.atBat) as atBats, sum(bc.Hit)/sum(bc.atBat) as BA
FROM batter_counts bc
JOIN game
    on bc.game_id = game.game_id
    GROUP BY bc.batter, year(game.local_date)
    HAVING sum(bc.atBat) != 0;

SELECT *
FROM annual_ba
LIMIT 0,20;

SELECT *
FROM historic_ba
LIMIT 0,20;

#ROLLING AVERAGE
DROP TEMPORARY TABLE each_day_ba;
CREATE TEMPORARY TABLE each_day_ba (batter int, game_id int,
local_date date, Hits int, atBats int, index(batter, game_id))
SELECT bc.batter, game.game_id as game_id, date(game.local_date) as local_date, sum(bc.Hit) as Hits,
       bc.atBat as atBats
FROM batter_counts bc
JOIN game
    on bc.game_id = game.game_id
    GROUP BY bc.batter, game.local_date;



CREATE TABLE ROLLING_BA (batter int, game_id int,local_date date, first_date date,
last_date date,  Total_Hits int, Total_atBats int, BA float)
SELECT bc.batter,
       bc.game_id,

       date(game.local_date) 'local_date',
    MIN(each_day_ba.local_date) 'first_date',
    MAX(each_day_ba.local_date) 'last_date',
    SUM(each_day_ba.Hits) 'Total_Hits',
    SUM(each_day_ba.atBats) 'Total_atBats',
    SUM(each_day_ba.Hits)/SUM(each_day_ba.atBats) as 'BA'
FROM each_day_ba
JOIN batter_counts bc on bc.batter = each_day_ba.batter
JOIN game on game.game_id = bc.game_id
WHERE date(game.local_date) > date(each_day_ba.local_date)
and  date_sub(date(game.local_date), INTERVAL 101 DAY) <= each_day_ba.local_date
#https://mariadb.com/kb/en/date_sub/ where I got date_sub
#101 because 100 days starting from previous day
GROUP BY bc.batter, bc.game_id
HAVING SUM(each_day_ba.atBats) !=0;



SELECT * FROM ROLLING_BA
LIMIT 0,20;

