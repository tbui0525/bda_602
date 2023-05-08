# RUN THIS BEFORE PYTHON SCRIPT


USE baseball;
# COLLECTING DATA

CREATE TEMPORARY TABLE bat_stats(
    team_id INT,
    home_team INT,
    game_id INT,
    local_date DATE,
    Hits INT,
    Doubles INT,
    Triples INT,
    HR INT,
    Sac_Fly INT,
    team_K INT,
    atBats INT,
    XBH INT,
    runs INT,
    opp_runs INT,
    Score_Diff INT,
    Home_Team_Win INT
)
;
INSERT INTO bat_stats(
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
        tbc.Strikeout AS team_K,
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
)
;
CREATE INDEX IF NOT EXISTS idx
ON bat_stats (game_id)
;
CREATE INDEX IF NOT EXISTS idx2
ON bat_stats (team_id)
;
# Innings Pitched by Starting Pitcher Only


CREATE TEMPORARY TABLE pitch_stats(
    pitcher_id INT,
    team_id INT,
    game_id INT,
    innings_pitched FLOAT,
    opp_hits INT,
    opp_AB INT,
    walks INT,
    HBP INT,
    intent_walk INT,
    K INT,
    plate_appearance INT,
    opp_HR INT,
    OBA FLOAT,
    thrown INT
)
;
INSERT INTO pitch_stats(
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
        pc.Strikeout AS K,
        pc.plateApperance AS plate_appearance,
        pc.Home_Run AS opp_HR,
        pc.Hit / NULLIF(pc.atBat, 0) AS OBA,
        pc.pitchesThrown AS thrown
    FROM pitcher_counts pc
    WHERE pc.startingPitcher = 1
        AND pc.game_id != 175660
)
;
# Saw this in Luis' code with 2 starting pitchers
# During my Peer Review. I don't know if that's cheating but I wanted to be honest about it
# Didn't notice it hAS 2 starting pitchers when I first ran the code

CREATE INDEX idx
ON pitch_stats (game_id)
;
CREATE INDEX idx2
ON pitch_stats (team_id)
;
CREATE TEMPORARY TABLE team_stats (
    game_id INT,
    team_id INT,
    HBP INT,
    innings_pitched FLOAT,
    intent_walk INT,
    OBA FLOAT,
    opp_AB INT,
    opp_HR INT,
    opp_hits INT,
    plate_appearance INT,
    walks INT,
    thrown INT,
    opp_runs INT,
    home_team INT,
    local_date DATE,
    Hits INT,
    Doubles INT,
    Triples INT,
    HR INT,
    K INT,
    team_K INT,
    Sac_Fly INT,
    atBats INT,
    XBH INT,
    runs INT,
    Score_Diff INT,
    Home_Team_Win INT
)
;
INSERT INTO team_stats(
    SELECT
        ps.game_id AS game_id,
        ps.team_id AS team_id,
        ps.HBP AS HBP,
        ps.innings_pitched AS innings_pitched,
        ps.intent_walk AS intent_walk,
        ps.OBA AS OBA,
        ps.opp_AB AS opp_AB,
        ps.opp_HR AS opp_HR,
        ps.opp_hits AS opp_hits,
        ps.thrown AS thrown,
        ps.plate_appearance AS plate_appearance,
        ps.walks AS walks,
        bs.opp_runs AS opp_runs,
        bs.home_team AS home_team,
        bs.local_date AS local_date,
        bs.Hits AS Hits,
        bs.Doubles AS Doubles,
        bs.Triples AS Triples,
        bs.HR AS HR,
        ps.K AS K,
        bs.team_K AS team_K,
        bs.Sac_Fly AS Sac_Fly,
        bs.atBats AS atBats,
        bs.XBH AS XBH,
        bs.runs AS runs,
        bs.Score_Diff AS Score_Diff,
        bs.Home_Team_Win AS Home_Team_Win
    FROM
        pitch_stats ps
        JOIN bat_stats bs ON ps.game_id = bs.game_id
            AND bs.team_id = ps.team_id
)
;
CREATE INDEX idx
ON team_stats (game_id)
;

CREATE INDEX idx2
ON team_stats (team_id)
;


# ROLLING AVERAGE COMPUTATIONS

CREATE TABLE roll_avg(
    team_id INT,
    game_id INT,
    home_team INT,
    local_date DATE,
    BA FLOAT,
    OBA FLOAT,
    XBH FLOAT,
    Avg_Score_Diff FLOAT,
    innings_pitched FLOAT,
    thrown FLOAT,
    pitch_per_inning FLOAT,
    CERA FLOAT,
    PTB FLOAT,
    WHIP FLOAT,
    Pythag FLOAT,
    ISO FLOAT,
    OBP FLOAT,
    BABIP FLOAT,
    DICE FLOAT,
    Home_Team_Win INT
)
;
INSERT INTO roll_avg(
    SELECT
        ts1.team_id AS team_id,
        ts1.game_id AS game_id,
        ts1.home_team AS home_team,
        ts1.local_date AS local_date,
        SUM(ts2.Hits) / NULLIF(SUM(ts2.atBats), 0) AS BA,# 1
        SUM(ts2.opp_hits) / NULLIF(SUM(ts2.opp_AB), 0) AS OBA,# 2
        SUM(ts2.XBH) / COUNT(ts2.game_id) AS XBH, # No weights here  3
        SUM(ts2.Score_Diff) / COUNT(ts2.game_id) AS Avg_Score_Diff, # 4
        SUM(ts2.innings_pitched) / COUNT(ts2.game_id) AS innings_pitched, # 5
        SUM(ts2.thrown) / COUNT(ts2.game_id) AS thrown, # 6
        SUM(ts2.thrown) / NULLIF(SUM(ts2.innings_pitched), 0) AS pitch_per_inning,# 7
        9 * (SUM(ts2.opp_hits) + SUM(ts2.walks) + SUM(ts2.HBP))
        / NULLIF((SUM(ts2.opp_AB) + SUM(ts2.innings_pitched)), 0)
        * (0.89 * (1.255 * (SUM(ts2.opp_hits) - SUM(ts2.opp_HR)) + 4 * SUM(ts2.opp_HR)
        ) + 0.56 * (SUM(ts2.walks) + SUM(ts2.HBP) - SUM(ts2.intent_walk)))
        * 0.75 AS CERA, # Not real CERA b/c did not account ERC 8
        0.89 * (1.255 * (SUM(ts2.opp_hits) - SUM(ts2.opp_HR)) + 4 * SUM(ts2.opp_HR)
        ) + 0.56 * (SUM(ts2.walks) + SUM(ts2.HBP) - SUM(ts2.intent_walk))
        / NULLIF(COUNT(ts2.game_id), 0) AS PTB, # 9
        (SUM(ts2.walks) + SUM(ts2.opp_hits))
        / NULLIF(SUM(ts2.innings_pitched), 0) AS WHIP, # 10
        (SUM(ts2.runs) * SUM(ts2.runs))
        / NULLIF((SUM(ts2.runs) * SUM(ts2.runs)
            + SUM(ts2.opp_runs) * SUM(ts2.opp_runs)), 0) AS Pythag, # 11
        (SUM(ts2.Doubles) + 2 * SUM(ts2.Triples) + 3 * SUM(ts2.HR))
        / NULLIF(SUM(ts2.atBats), 0) AS ISO, # 12
        (ts2.Hits + ts2.walks + ts2.HBP)
        / NULLIF(ts2.atBats + ts2.walks + ts2.Sac_Fly + ts2.HBP, 0) AS OBP, # 13
        (SUM(ts2.Hits) - SUM(ts2.HR))
        / NULLIF(SUM(ts2.atBats) - SUM(ts2.team_K) - SUM(ts2.HR) + SUM(ts2.Sac_Fly), 0)
        AS BABIP, # 14
        3 + (13 * SUM(ts2.opp_HR) + 3 * (SUM(ts2.walks) + SUM(ts2.HBP)) - 2 * ts2.K)
        / NULLIF(ts2.innings_pitched, 0) AS DICE,
        ts2.Home_Team_Win AS Home_Team_Win
    FROM team_stats ts1
        JOIN team_stats ts2
            ON ts1.team_id = ts2.team_id
                AND ts2.local_date BETWEEN DATE_SUB(ts1.local_date, INTERVAL 366 DAY)
                AND DATE_SUB(ts1.local_date, INTERVAL 1 DAY)
    GROUP BY ts1.team_id, ts1.game_id
)
;



CREATE TEMPORARY TABLE home_team_stats(
    team_id INT,
    game_id INT,
    home_team INT,
    local_date DATE,
    BA FLOAT,# 1
    OBA FLOAT,# 2
    XBH FLOAT, # No weights here  3
    Avg_Score_Diff FLOAT, # 4
    innings_pitched FLOAT, # 5
    thrown FLOAT, # 6
    pitch_per_inning FLOAT,# 7
    CERA FLOAT, # Not real CERA b/c did not account ERC 8
    PTB FLOAT, # 9
    WHIP FLOAT, # 10
    Pythag FLOAT, # 11
    ISO FLOAT, # 12
    OBP FLOAT, # 13
    BABIP FLOAT, # 14
    DICE FLOAT,
    Home_Team_Win INT
)
;
INSERT INTO home_team_stats(
    SELECT * FROM roll_avg ra WHERE ra.home_team = 1
)
;
CREATE INDEX idx
ON home_team_stats (game_id)
;


CREATE TEMPORARY TABLE away_team_stats(
    opp_team_id INT,
    game_id INT,
    opp_BA FLOAT,
    opp_OBA FLOAT,
    opp_XBH FLOAT,
    opp_Score_Diff FLOAT,
    opp_innings_pitched FLOAT,
    opp_thrown FLOAT,
    opp_pitch_per_inning FLOAT,
    opp_CERA FLOAT,
    opp_PTB FLOAT,
    opp_WHIP FLOAT,
    opp_Pythag FLOAT,
    opp_ISO FLOAT,
    opp_OBP FLOAT,
    BABIP FLOAT,
    DICE FLOAT
)
;
INSERT INTO away_team_stats(
    SELECT
        ra.team_id AS opp_team_id,
        ra.game_id AS game_id,
        ra.BA AS opp_BA,# 1
        ra.OBA AS opp_OBA,# 2
        ra.XBH AS opp_XBH, # No weights here  3
        ra.Avg_Score_Diff AS opp_Score_Diff, # 4
        ra.innings_pitched AS opp_innings_pitched, # 5
        ra.thrown AS opp_thrown, # 6
        ra.pitch_per_inning AS opp_pitch_per_inning,# 7
        ra.CERA AS opp_CERA, # Not real CERA b/c did not account ERC 8
        ra.PTB AS opp_PTB, # 9
        ra.WHIP AS opp_WHIP, # 10
        ra.Pythag AS opp_Pythag, # 11
        ra.ISO AS opp_ISO, # 12
        ra.OBP AS opp_OBP, # 13
        ra.BABIP AS BABIP, #14
        ra.DICE AS DICE
    FROM roll_avg ra
    WHERE ra.home_team = 0
)
;

CREATE INDEX idx
ON away_team_stats (game_id)
;

CREATE TABLE final_table (
    team_id INT,
    game_id INT,
    local_date DATE,
    diff_BA FLOAT,
    diff_OBA FLOAT,
    diff_XBH FLOAT,
    diff_Score_Diff FLOAT,
    diff_inn_p FLOAT,
    diff_thrown FLOAT,
    diff_ppi FLOAT,
    diff_CERA FLOAT,
    diff_PTB FLOAT,
    diff_Pythag FLOAT,
    diff_ISO FLOAT,
    diff_WHIP FLOAT,
    diff_OBP FLOAT,
    diff_BABIP FLOAT,
    diff_DICE FLOAT,
    Home_Team_Win INT
)
;
INSERT INTO final_table(
    SELECT
        hts.team_id AS team_id,
        hts.game_id AS game_id,
        hts.local_date AS local_date,
        hts.BA - ats.opp_BA AS diff_BA, #1
        hts.OBA - ats.opp_OBA AS diff_OBA, #2
        hts.XBH - ats.opp_XBH AS diff_XBH, #3
        hts.Avg_Score_Diff - ats.opp_Score_Diff AS diff_Score_Diff, # 4
        hts.innings_pitched - ats.opp_innings_pitched AS diff_inn_p, # 5
        hts.thrown - ats.opp_thrown AS diff_thrown, # 6
        hts.pitch_per_inning - ats.opp_pitch_per_inning AS diff_ppi, # 7
        hts.CERA - ats.opp_CERA AS diff_CERA, # 8
        hts.PTB - ats.opp_PTB AS diff_PTB, # 9
        hts.Pythag - ats.opp_Pythag AS diff_Pythag,# 10
        hts.ISO - ats.opp_ISO AS diff_ISO, # 11
        hts.WHIP - ats.opp_WHIP AS diff_WHIP, # 12
        hts.OBP - ats.opp_OBP AS diff_OBP, # 13
        hts.BABIP - ats.BABIP AS diff_BABIP,
        hts.DICE - ats.DICE AS diff_DICE,
        hts.Home_Team_Win AS Home_Team_Win
    FROM home_team_stats hts
        JOIN away_team_stats ats ON hts.game_id = ats.game_id
    ORDER BY hts.local_date
)
;
