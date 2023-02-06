SELECT
    NewsThemes::ValidateTheme(Yql::Unwrap(Url), HttpBody, ZoraCtx, Charset) AS ThemeAttributes
FROM Input
;