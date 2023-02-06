/* syntax version 1 */
$indexPage = Prewalrus::IndexPage();

$calc = ($row) -> {
    $indexPageResult = $indexPage($row.Url);

    return AsStruct(
        $row.Url AS Url,
        $indexPageResult.IsIndexPage AS IsIndexPage,
        $indexPageResult.IsIndexPageSoft AS IsIndexPageSoft,
        $indexPageResult.Error AS Error
    );
};

SELECT * FROM
   (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

