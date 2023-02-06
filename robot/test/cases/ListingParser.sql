$listingParser = Commercial::ListingParser(
    FilePath("listing_parser_config.json")
);

SELECT
    $listingParser(html, url, charset, /*title=*/"", EcomFeatures, /*wantJson=*/false, /*wantDebugString=*/true) AS Listing
FROM Input;
