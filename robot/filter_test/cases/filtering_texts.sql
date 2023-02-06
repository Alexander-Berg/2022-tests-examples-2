/* syntax version 1 */
$isAcceptedHost = AdvertisingWidget::IsAcceptedHost(FilePath("advertising_widget_clients_hosts.json"));

SELECT * FROM Input
WHERE Document IS NOT NULL
      AND Document != ""
      AND $isAcceptedHost(Document, Source)
;
