/* syntax version 1 */
$titleRanges = Prewalrus::TitleRanges();

$calc = ($row) -> {
    $titleRangesResult = $titleRanges(
        $row.TitleRawUTF8
    );

    return AsStruct(
        $row.Url AS Url,
        $titleRangesResult.GroupAttrs AS GroupAttrs,
        $titleRangesResult.Error AS Error
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

