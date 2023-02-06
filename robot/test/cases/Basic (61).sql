/* syntax version 1 */
$grammar = Prewalrus::Grammar(
    FilePath("porno_weights")
);
$dtConv = DtConv::DirectTextDeserializer();

$calc = ($row) -> {
    $directTextResult = $dtConv($row.DirectTextEntries);

    $grammarResult = $grammar(
        $directTextResult.DirectText
    );

    return AsStruct(
        $row.Url AS Url,
        $grammarResult.Soft404 AS Soft404,
        $grammarResult.NumeralsPortion AS NumeralsPortion,
        $grammarResult.ParticlesPortion AS ParticlesPortion,
        $grammarResult.AdjPronounsPortion AS AdjPronounsPortion,
        $grammarResult.AdvPronounsPortion AS AdvPronounsPortion,
        $grammarResult.VerbsPortion AS VerbsPortion,
        $grammarResult.FemAndMasNounsPortion AS FemAndMasNounsPortion,
        $grammarResult.PornoV AS PornoV,
        $grammarResult.Error AS Error 
    );
};

SELECT * FROM
   (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;
