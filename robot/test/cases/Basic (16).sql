/* syntax version 1 */
SELECT
    Url,
    ImagesHtml::ParseSchemaOrg(Url, NumeratorEvents) AS SchemaOrgProduct
FROM
    Input
;
