SELECT
    CAST(NewsProcessing::IsoNameByLanguage(Language ?? 0) AS Utf8) AS Language
FROM Input
;