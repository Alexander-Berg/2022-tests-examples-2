/* syntax version 1 */
$favicon = Favicon::Favicon();

$calc = ($row) -> {
    $faviconResult = $favicon(
        $row.NumeratorEvents,
        $row.ZoneData,
        $row.Url
    );

    return AsStruct(
        $row.Url AS Url,
        $faviconResult.Links as Links,
        $faviconResult.IsDefault as IsDefault,
        $faviconResult.Error as Error
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;
