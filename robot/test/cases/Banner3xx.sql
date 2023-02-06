$ExtractAndPatchOffer = Commercial::ExtractAndPatchOffer("bannerland");

SELECT
    $ExtractAndPatchOffer(NULL, ZoraCtx, Url, OriginalUrl, LastAccess) AS PatchedOffer,
    Description
FROM Input;
