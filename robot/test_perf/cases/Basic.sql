/* syntax version 1 */
$udf = Prewalrus::Parser(
);

SELECT
    is_error,
    COUNT(*) AS count
FROM Input
GROUP BY $udf(
    Html,
    Host || Path
).Error IS NOT NULL AS is_error;
