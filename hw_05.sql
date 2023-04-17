# RUN THIS BEFORE PYTHON SCRIPT
# SETTING UP FOR CALCULATING BA IN PYSPARK
DROP TABLE IF EXISTS team_ba;
CREATE TABLE team_ba(
    team_id INT,
    home_team INT,
    game_id INT,
    local_date DATE,
    Hits INT,
    Doubles INT,
    Triples INT,
    HR INT,
    Sac_Fly INT,
    atBats INT,
    XBH INT,
    runs INT,
    opp_runs INT,
    Score_Diff INT,
    Home_Team_Win INT,
    INDEX(team_id, game_id)
)
;
INSERT INTO team_ba
SELECT
    tbc.team_id AS team_id,
    tbc.homeTeam AS home_team,
    game.game_id AS game_id,
    DATE(game.local_date) AS local_date,
    tbc.Hit AS Hits,
    tbc.`Double` AS Doubles,
    tbc.Triple AS Triples,
    tbc.Home_Run AS HR,
    tbc.Sac_Fly AS Sac_Fly,
    tbc.atBat AS atBats,
    tbc.`Double` + tbc.Triple + tbc.Home_Run AS XBH,
    tbc.finalScore AS runs,
    tbc.opponent_finalScore AS opp_runs,
    tbc.finalScore - tbc.opponent_finalScore AS Score_Diff,
    1 - ((tbc.win + tbc.homeTeam) % 2) AS Home_Team_Win
# Math breakdown for equation above.
# Win + HomeTeam = 2. 2%2=0, 1-0=1
# Win + !HomeTeam = 1. 1%2=1. 1-1=0
# Lose + HomeTeam = 1. 1%2=1. 1-1=0
# Lose + !HomeTeam =0. 0%2=0, 1-0=1
FROM team_batting_counts tbc
    JOIN game
        ON tbc.game_id = game.game_id
GROUP BY tbc.team_id, game.local_date
;

# Innings Pitched by Starting Pitcher Only
DROP TABLE IF EXISTS pitch_stats;


CREATE TABLE IF NOT EXISTS pitch_stats(
    pitcher_id INT,
    team_id INT,
    game_id INT,
    innings_pitched FLOAT,
    opp_hits INT,
    opp_AB INT,
    walks INT,
    HBP INT,
    intent_walk INT,
    plate_appearance INT,
    opp_HR INT,
    OBA FLOAT,
    thrown INT
)
;
INSERT INTO pitch_stats
SELECT
    pc.pitcher AS pitcher_id,
    pc.team_id AS team_id,
    pc.game_id AS game_id,
    pc.outsPlayed / 3 AS innings_pitched,
    pc.Hit AS opp_hits,
    pc.atBat AS opp_AB,
    pc.Walk AS walks,
    pc.Hit_By_Pitch AS HBP,
    pc.Intent_Walk AS intent_walk,
    pc.plateApperance AS plate_appearance,
    pc.Home_Run AS opp_HR,
    pc.Hit / NULLIF(pc.atBat, 0) AS OBA,
    pc.pitchesThrown AS thrown
FROM pitcher_counts pc
WHERE pc.startingPitcher = 1
;
