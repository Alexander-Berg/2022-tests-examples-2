/* syntax version 1 */
$nevasca = Nevasca::Nevasca(false);

$calc = ($row) -> {

    $url = NVL($row.Host, "") || NVL($row.Path, "");

    $nevascaResult = $nevasca(
        NVL($row.Arc, ""),
        True
    );

    return AsStruct(
        $url AS Url,
        $nevascaResult.Shingles AS Shingles
   );
};

SELECT * FROM (
    SELECT $calc(TableRow()) FROM Input
) FLATTEN COLUMNS
;
