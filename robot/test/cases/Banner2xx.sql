$ExtractAndPatchOffer = Commercial::ExtractAndPatchOffer("bannerland");

SELECT $ExtractAndPatchOffer(
    SerializedOffer, ZoraCtx, Url, OriginalUrl, LastAccess) AS PatchedOffer
FROM Input;
