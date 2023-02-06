/* syntax version 1 */
$authorJsonApi = Video::AuthorJsonApi(FolderPath("author_json_api"));
$authorToFactors = Video::AuthorToFactors();

$calc = ($row) -> {
    $result = $authorToFactors(
        $authorJsonApi($row.Url, NULL, $row.`Json`).Author,
        $row.LastAccess
    );

    return AsStruct(
        $row.Url AS Url,
        $result.AuthorId AS AuthorId,
        $result.Factors AS Factors,
        $result.Error AS Error
   );    
};


SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;
