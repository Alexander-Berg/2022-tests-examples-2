SELECT ya_transaction_id
FROM contractor_merch_integration_api.mobi_transaction_mapping
WHERE contractor_merch_integration_api.mobi_transaction_mapping.mobi_transaction_id = %s
;