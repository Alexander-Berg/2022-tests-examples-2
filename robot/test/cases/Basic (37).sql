/* syntax version 1 */
$makeThumbnail = ImagesPic::MakeThumbnail(
    FilePath("iparser.cfg")
);

$calc = ($row) -> {
    $result = $makeThumbnail($row.Thumb, 0, "h=320&w=480");
    return AsStruct($result.Thumbnail as Thumbnail, $result.Error as Error);
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

