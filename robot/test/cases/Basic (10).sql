/* syntax version 1 */
$isMainUrl = Gemini::IsMainUrl();

SELECT
    Url,
    LastAccess,
    HttpCode
FROM Input
WHERE $isMainUrl(Url);
