IF OBJECT_ID('dbo.nbaPlayerCumulativeProgression', 'U') IS NOT NULL
    DROP TABLE dbo.nbaPlayerCumulativeProgression;
GO

-- Nieuwe tabel maken
SELECT
    player_name,
    team_code,
    Gtm,
    TRY_CAST(FGA AS INT) AS FGA,
    TRY_CAST(FG AS INT) AS FG,
    TRY_CAST(DRB AS INT) AS DRB,
    TRY_CAST(TRB AS INT) AS TRB,
    TRY_CAST(AST AS INT) AS AST,
    TRY_CAST(STL AS INT) AS STL,
    TRY_CAST(BLK AS INT) AS BLK,
    TRY_CAST(TOV AS INT) AS TOV,
    TRY_CAST(PF AS INT) AS PF,
    TRY_CAST(PTS AS INT) AS PTS,

    SUM(TRY_CAST(FGA AS INT)) OVER (PARTITION BY player_name, team_code ORDER BY TRY_CAST(Gtm AS INT)) AS cumulativeFGA,
    SUM(TRY_CAST(FG AS INT))  OVER (PARTITION BY player_name, team_code ORDER BY TRY_CAST(Gtm AS INT)) AS cumulativeFG,
    SUM(TRY_CAST(DRB AS INT)) OVER (PARTITION BY player_name, team_code ORDER BY TRY_CAST(Gtm AS INT)) AS cumulativeDRB,
    SUM(TRY_CAST(TRB AS INT)) OVER (PARTITION BY player_name, team_code ORDER BY TRY_CAST(Gtm AS INT)) AS cumulativeTRB,
    SUM(TRY_CAST(AST AS INT)) OVER (PARTITION BY player_name, team_code ORDER BY TRY_CAST(Gtm AS INT)) AS cumulativeAST,
    SUM(TRY_CAST(STL AS INT)) OVER (PARTITION BY player_name, team_code ORDER BY TRY_CAST(Gtm AS INT)) AS cumulativeSTL,
    SUM(TRY_CAST(BLK AS INT)) OVER (PARTITION BY player_name, team_code ORDER BY TRY_CAST(Gtm AS INT)) AS cumulativeBLK,
    SUM(TRY_CAST(TOV AS INT)) OVER (PARTITION BY player_name, team_code ORDER BY TRY_CAST(Gtm AS INT)) AS cumulativeTOV,
    SUM(TRY_CAST(PF AS INT))  OVER (PARTITION BY player_name, team_code ORDER BY TRY_CAST(Gtm AS INT)) AS cumulativePF,
    SUM(TRY_CAST(PTS AS INT)) OVER (PARTITION BY player_name, team_code ORDER BY TRY_CAST(Gtm AS INT)) AS cumulativePTS

INTO dbo.nbaPlayerCumulativeProgression
FROM dbo.nbaPlayerStats
WHERE player_name IS NOT NULL AND Gtm IS NOT NULL;
