/* syntax version 1 */
$linkAlternate = Prewalrus::LinkAlternate();

$calc = ($row) -> {
    $charset = IF (LENGTH($row.Html) > 0, 13, $row.Charset);
    $linkAlternateResult = $linkAlternate($row.ParserChunks, $charset);

    return AsStruct(
        $row.Url AS Url,
        $linkAlternateResult.LinkAlternateData AS LinkAlternateData,
        $linkAlternateResult.LinkAmpHtmlData AS LinkAmpHtmlData,
        $linkAlternateResult.LinkAmpHref AS LinkAmpHref,
        $linkAlternateResult.LinkAlternateMobileHref AS LinkAlternateMobileHref,
        $linkAlternateResult.Error AS Error
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

