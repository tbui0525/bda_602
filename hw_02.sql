USE baseball;
#HISTORIC_BA
#I do not know why I kept getting a parse error
#But it went away when I used INSERT INTO, so I'mma stick with that.
DROP TABLE IF EXISTS historic_ba;

CREATE TABLE historic_ba(
    batter INT,
    BA FLOAT
)
;

INSERT INTO historic_ba
SELECT
    batter AS batter,
    SUM(Hit) / NULLIF(SUM(atBat), 0) AS BA
#NULLIF statement comes from w3schools.com/sql/sql_null_values.asp
FROM batter_counts bc
    JOIN game
        ON bc.game_id = game.game_id
GROUP BY bc.batter
;
#I got this code to turn NULLs into 0's from this website
#
UPDATE historic_ba SET BA = 0 WHERE BA IS NULL;

#ANNUAL_BA
DROP TABLE IF EXISTS annual_ba;

CREATE TABLE annual_ba(
    batter INT,
    batting_year YEAR,
    Hits INT,
    atBats INT,
    BA FLOAT
)
;
INSERT INTO annual_ba
SELECT
    batter AS batter,
    YEAR(game.local_date) AS batting_year,
    SUM(bc.Hit) AS Hits,
    SUM(bc.atBat) AS atBats,
    SUM(bc.Hit) / NULLIF(SUM(bc.atBat), 0) AS BA
FROM batter_counts bc
    JOIN game
        ON bc.game_id = game.game_id
GROUP BY bc.batter, YEAR(game.local_date)
;


UPDATE annual_ba SET BA = 0 WHERE BA IS NULL;
#ROLLING AVERAGE
DROP TEMPORARY TABLE IF EXISTS each_day_ba;
CREATE TEMPORARY TABLE each_day_ba(
    batter INT,
    game_id INT,
    local_date DATE,
    Hits INT,
    atBats INT,
    INDEX(batter, game_id)
)
;
INSERT INTO each_day_ba
SELECT
    batter AS batter,
    game.game_id AS game_id,
    DATE(game.local_date) AS local_date,
    SUM(Hit) AS Hits,
    atBat AS atBats
FROM batter_counts
    JOIN game
        ON batter_counts.game_id = game.game_id
GROUP BY batter_counts.batter, game.local_date
;

DROP TABLE IF EXISTS ROLLING_BA;
CREATE TABLE ROLLING_BA(
    batter INT,
    game_id INT,
    local_date DATE,
    first_date DATE,
    last_date DATE,
    Total_Hits INT,
    Total_atBats INT,
    BA FLOAT
)
;
INSERT INTO ROLLING_BA
SELECT
    each_day_ba.batter AS batter,
    game.game_id AS game_id,
    DATE(game.local_date) AS local_date,
    MIN(each_day_ba.local_date) AS first_date,
    MAX(each_day_ba.local_date) AS last_date,
    SUM(each_day_ba.Hits) AS Total_Hits,
    SUM(each_day_ba.atBats) AS Total_atBats,
    SUM(each_day_ba.Hits) / NULLIF(SUM(each_day_ba.atBats), 0) AS BA
FROM each_day_ba
    JOIN batter_counts ON batter_counts.batter = each_day_ba.batter
    JOIN game ON game.game_id = batter_counts.game_id
WHERE DATE(game.local_date) > DATE(each_day_ba.local_date)
    AND  DATE_SUB(DATE(game.local_date), INTERVAL 101 DAY) <= each_day_ba.local_date
#https://mariadb.com/kb/en/date_sub/ where I got date_sub
#101 because 100 days starting from previous day
GROUP BY batter_counts.batter, batter_counts.game_id
;
UPDATE ROLLING_BA SET BA = 0 WHERE BA IS NULL;
