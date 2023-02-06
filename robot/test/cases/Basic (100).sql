/* syntax version 1 */
$textFeaturesRemap = Prewalrus::TextFeaturesRemap();

$calc = ($row) -> {

    $textFeaturesRemapResult = $textFeaturesRemap(
        $row.Language,
        $row.HttpCode,
        $row.MimeType,
        $row.HttpModTime,
        $row.Simhash,
        $row.DocSize,
        $row.MaxFreq,
        $row.LastAccess,
        $row.TitleFirstBreak,
        $row.TitleLastBreak,
        AsDict(
            AsTuple("Eshop", $row.Eshop),
            AsTuple("EshopV", $row.EshopV),
            AsTuple("Breaks", $row.Breaks),
            AsTuple("LongText", $row.LongText),
            AsTuple("NumForumPosts", $row.NumForumPosts),
            AsTuple("NumForumAuthors", $row.NumForumAuthors),
            AsTuple("Soft404", $row.Soft404),
            AsTuple("NumeralsPortion", $row.NumeralsPortion),
            AsTuple("ParticlesPortion", $row.ParticlesPortion),
            AsTuple("AdjPronounsPortion", $row.AdjPronounsPortion),
            AsTuple("AdvPronounsPortion", $row.AdvPronounsPortion),
            AsTuple("VerbsPortion", $row.VerbsPortion),
            AsTuple("FemAndMasNounsPortion", $row.FemAndMasNounsPortion),
            AsTuple("PornoV", $row.PornoV),
            AsTuple("Poetry", $row.Poetry),
            AsTuple("Poetry2", $row.Poetry2),
            AsTuple("IsComm", $row.IsComm),
            AsTuple("HasPayments", $row.HasPayments),
            AsTuple("IsSEO", $row.IsSEO),
            AsTuple("IsPorno", $row.IsPorno),
            AsTuple("SegmentAuxSpacesInText", $row.SegmentAuxSpacesInText),
            AsTuple("SegmentAuxAlphasInText", $row.SegmentAuxAlphasInText),
            AsTuple("SegmentContentCommasInText", $row.SegmentContentCommasInText),
            AsTuple("SegmentWordPortionFromMainContent", $row.SegmentWordPortionFromMainContent),
            AsTuple("IsShop", $row.IsShop),
            AsTuple("IsReview", $row.IsReview),
            AsTuple("Syn7bV", $row.Syn7bV),
            AsTuple("Syn8bV", $row.Syn8bV),
            AsTuple("Syn9aV", $row.Syn9aV),
            AsTuple("SynPercentBadWordPairs", $row.SynPercentBadWordPairs),
            AsTuple("SynNumBadWordPairs", $row.SynNumBadWordPairs),
            AsTuple("NumLatinLetters", $row.NumLatinLetters),
            AsTuple("TextF", $row.TextF),
            AsTuple("TextL", $row.TextL),
            AsTuple("RusWordsInText", $row.RusWordsInText),
            AsTuple("RusWordsInTitle", $row.RusWordsInTitle),
            AsTuple("MeanWordLength", $row.MeanWordLength),
            AsTuple("PercentWordsInLinks", $row.PercentWordsInLinks),
            AsTuple("PercentVisibleContent", $row.PercentVisibleContent),
            AsTuple("PercentFreqWords", $row.PercentFreqWords),
            AsTuple("PercentUsedFreqWords", $row.PercentUsedFreqWords),
            AsTuple("TrigramsProb", $row.TrigramsProb),
            AsTuple("TrigramsCondProb", $row.TrigramsCondProb),
            AsTuple("TitleBM25Ex", $row.TitleBM25Ex),
            AsTuple("IsEbookForRead", $row.IsEbookForRead),
            AsTuple("SmartSoft404", $row.SmartSoft404),
            AsTuple("HasUserReviewsH", $row.HasUserReviewsH),
            AsTuple("FreqDataArray", $row.FreqDataArray),
            AsTuple("RecD", $row.RecD),
            AsTuple("FirstPostDate", $row.FirstPostDate),
            AsTuple("LastPostDate", $row.LastPostDate),
            AsTuple("DaterDate", $row.DaterDate)
        )
    );

    return AsStruct(
        $row.Url AS Url,
        $textFeaturesRemapResult.DocDateMonth AS DocDateMonth,
        $textFeaturesRemapResult.DocDateYear AS DocDateYear,
        $textFeaturesRemapResult.DaterYear AS DaterYear,
        $textFeaturesRemapResult.DaterMonth AS DaterMonth,
        $textFeaturesRemapResult.DaterDay AS DaterDay,
        $textFeaturesRemapResult.DaterFrom AS DaterFrom,
        $textFeaturesRemapResult.DaterFrom1 AS DaterFrom1,
        Digest::Md5Hex($textFeaturesRemapResult.RemappedFeatures) AS RemappedFeaturesMd5,
        $textFeaturesRemapResult.Error AS Error
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

