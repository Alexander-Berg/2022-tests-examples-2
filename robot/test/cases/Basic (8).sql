/* syntax version 1 */
$splitter = Common::SplitResponse();

SELECT
	Url,
	Splitted.Headers as Headers,
	Splitted.Body as Body,
	Splitted.Error AS Error
FROM (
	SELECT
		Url,
		$splitter(HttpResponse, true) as Splitted
	FROM Input
);
