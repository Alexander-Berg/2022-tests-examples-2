SELECT
    CAST(NewsThemes::ExtractThemeId(Yql::Unwrap(ZoraCtx)) AS Utf8) AS ThemeId
FROM Input
;