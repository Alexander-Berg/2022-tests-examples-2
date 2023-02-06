$productsOnPagesRegexClassifier = Commercial::ProductsOnPagesRegexClassifier(
    FilePath("config.json")
);

SELECT
    url,
    $productsOnPagesRegexClassifier(url) AS predicted
FROM Input;
