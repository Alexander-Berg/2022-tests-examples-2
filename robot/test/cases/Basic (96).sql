/* syntax version 1 */
$tagArchive = Prewalrus::TagArchive();

$calc = ($row) -> {

    $tagArchiveResult = $tagArchive(
        $row.Flags,
        $row.IndexDate,
        $row.Language,
        $row.Language2,
        $row.MimeType,
        $row.Encoding,
        $row.Url,
        $row.OriginalDoc,
        $row.ConvHtml,
        $row.DocId,
        AsDict(
            AsTuple("RecD", $row.RecD),
            AsTuple("Eshop", $row.Eshop),
            AsTuple("EshopV", $row.EshopV),
            AsTuple("Breaks", $row.Breaks),
            AsTuple("LongText", $row.LongText),
            AsTuple("FooterTrigrams", $row.FooterTrigrams),
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
            AsTuple("HasUserReviewsL", $row.HasUserReviewsL),
            AsTuple("HasUserReviewsH", $row.HasUserReviewsH),
            AsTuple("NumXPathUserReviews", $row.NumXPathUserReviews),
            AsTuple("LastXPathUserReviewDate", $row.LastXPathUserReviewDate),
            AsTuple("AverageXPathUserReviewRate", $row.AverageXPathUserReviewRate),
            AsTuple("MaxXPathUserReviewUsefulness", $row.MaxXPathUserReviewUsefulness),
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
            AsTuple("Title", $row.Title),
            AsTuple("TitleCRC", $row.TitleCRC),
            AsTuple("FirstPostDate", $row.FirstPostDate),
            AsTuple("LastPostDate", $row.LastPostDate),
            AsTuple("NumForumPosts", $row.NumForumPosts),
            AsTuple("NumForumAuthors", $row.NumForumAuthors),
            AsTuple("TitleRawUTF8", $row.TitleRawUTF8),
            AsTuple("TitleNormalizedUTF8", $row.TitleNormalizedUTF8)
        )
    );

    return AsStruct(
        $row.Url AS Url,
        $tagArchiveResult.TagWoHtml AS TagWoHtml,
        $tagArchiveResult.TagAll AS TagAll,
        $tagArchiveResult.Error AS Error
   );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

