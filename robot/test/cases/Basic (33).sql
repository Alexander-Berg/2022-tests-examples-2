/* syntax version 1 */
$ocrizePdf = ImagesOcr::OcrizePdf(
    FolderPath("YQL_PDF_OCR_PACKAGE"),
    FilePath("libpdfium.plugin")
);

$calc = ($row) -> {
    $pagesLimit = 10;

    $ocrizePdfResult = $ocrizePdf($row.PdfContent, $pagesLimit);

    return AsStruct(
        $ocrizePdfResult.Html as Html,
        $ocrizePdfResult.Error as Error
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

