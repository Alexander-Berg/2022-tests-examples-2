/* syntax version 1 */
$udf = ImagesHtml::MainContentParser(
);
$htmlParser = Prewalrus::Parser(
);

SELECT $udf(
    Host || Path,
    $htmlParser(Html, Host || Path).ParserChunks
) FROM Input;
